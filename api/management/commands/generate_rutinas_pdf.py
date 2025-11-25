from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
import os
from django.conf import settings
import uuid
import traceback

from api.models import Maintenance, Report
from api.services_main import ReportGenerator
from core.storage import MaintenanceReportStorage
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Genera PDFs de rutinas para mantenimientos de equipos de cómputo (equipment_type=computer)'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Máximo de mantenimientos a procesar')
        parser.add_argument('--only-completed', action='store_true', help='Procesar solo mantenimientos con completion_date')

    def handle(self, *args, **options):
        limit = options.get('limit') or 10
        only_completed = options.get('only_completed', False)

        qs = Maintenance.objects.filter(equipment_type='computer')
        if only_completed:
            qs = qs.filter(completion_date__isnull=False)

        qs = qs.order_by('-completion_date')[:limit]

        generator = ReportGenerator()
        storage = MaintenanceReportStorage()
        User = get_user_model()

        for m in qs:
            self.stdout.write(f'Processing maintenance id={m.id} equipment={m.equipment}')
            try:
                user = m.technician or User.objects.filter(is_active=True).first()

                context = {
                    'equipment': m.equipment,
                    'maintenances': [m],
                    'start_date': m.maintenance_date,
                    'end_date': m.maintenance_date,
                    'generated_at': timezone.now(),
                    'generated_by': user.get_full_name() if user else 'system'
                }

                # Generate PDF bytes (if available). If PDF library missing, save rendered HTML instead.
                try:
                    pdf_bytes = generator.generate_report(context)
                    saved_as_html = False
                except ModuleNotFoundError as exc:
                    # Likely xhtml2pdf not installed in this environment - fallback to saving HTML
                    from api.services_main import ReportGenerator as RG
                    html_content = RG().render_template(context)
                    pdf_bytes = html_content.encode('utf-8')
                    saved_as_html = True

                # Create or update Report
                report, created = Report.objects.get_or_create(maintenance=m, defaults={
                    'generated_by': user if user else None,
                    'title': f'Reporte de Mantenimiento - {m.equipment.code if m.equipment else ""}'
                })

                report.generated_by = user if user else None
                report.generated_at = timezone.now()
                report.title = report.title or f'Reporte de Mantenimiento - {m.equipment.code if m.equipment else ""}'
                report.save()

                # Save PDF (or HTML fallback) to storage. If storage fails (e.g., MinIO unavailable),
                # fallback to writing the file locally under MEDIA_ROOT/maintenance-reports/ and
                # set the Report.pdf_file to the relative path so Django can serve it via MEDIA.
                ext = 'html' if saved_as_html else 'pdf'
                filename = f"reporte_mantenimiento_{m.id}_{uuid.uuid4()}.{ext}"
                try:
                    storage.save(filename, ContentFile(pdf_bytes))
                    report.pdf_file = filename
                    report.save()
                except Exception as save_exc:
                    # Couldn't save to remote storage; write to local media folder instead.
                    try:
                        local_dir = os.path.join(settings.MEDIA_ROOT or 'media', 'maintenance-reports')
                        os.makedirs(local_dir, exist_ok=True)
                        local_path = os.path.join(local_dir, filename)
                        with open(local_path, 'wb') as f:
                            f.write(pdf_bytes)

                        # Store relative path to MEDIA_ROOT so FileField can resolve it.
                        relative_path = os.path.join('maintenance-reports', filename)
                        report.pdf_file = relative_path
                        report.save()
                        self.stdout.write(self.style.WARNING(f'Storage unavailable, saved locally to {local_path}'))
                    except Exception as local_exc:
                        # If all fails, raise to be handled by outer exception catcher.
                        raise

                self.stdout.write(self.style.SUCCESS(f'Created report {report.id} for maintenance {m.id}'))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error processing maintenance {m.id}: {e}'))
                traceback.print_exc()
