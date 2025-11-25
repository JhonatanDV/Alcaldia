"""
Management command para generar reportes Excel de impresoras y escáneres.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Maintenance, Report
from api.services.printer_scanner_excel_generator import PrinterScannerExcelGenerator
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Genera reportes Excel para mantenimientos de impresoras y escáneres'

    def add_arguments(self, parser):
        parser.add_argument(
            '--maintenance-id',
            type=int,
            help='ID específico de mantenimiento a generar'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Límite de mantenimientos a procesar'
        )
        parser.add_argument(
            '--only-completed',
            action='store_true',
            help='Solo procesar mantenimientos completados'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Directorio de salida personalizado'
        )

    def handle(self, *args, **options):
        maintenance_id = options.get('maintenance_id')
        limit = options.get('limit')
        only_completed = options.get('only_completed')
        output_dir = options.get('output_dir')

        # Configurar directorio de salida
        if output_dir:
            reports_dir = output_dir
        else:
            reports_dir = os.path.join(settings.MEDIA_ROOT, 'maintenance-reports')
        
        os.makedirs(reports_dir, exist_ok=True)

        # Construir queryset
        queryset = Maintenance.objects.all()

        if maintenance_id:
            queryset = queryset.filter(id=maintenance_id)
        else:
            # Filtrar por tipo de equipo: impresoras o escáneres
            queryset = queryset.filter(
                equipment__equipment_type__in=['printer', 'scanner', 'impresora', 'escaner']
            )
            
            if only_completed:
                queryset = queryset.filter(status='completed')
            
            if limit:
                queryset = queryset[:limit]

        if not queryset.exists():
            self.stdout.write(self.style.WARNING('No se encontraron mantenimientos para procesar'))
            return

        generator = PrinterScannerExcelGenerator()
        generated_files = []

        for maintenance in queryset:
            try:
                self.stdout.write(f"Procesando mantenimiento id={maintenance.id} equipo={maintenance.equipment}")
                
                # Generar Excel
                excel_bytes = generator.generate_report(maintenance)
                
                # Crear nombre de archivo
                equipment_code = maintenance.equipment.code or f'EQ-{maintenance.id}'
                timestamp = datetime.now().strftime('%Y%m%d')
                # Generar hash único corto
                import hashlib
                hash_str = hashlib.md5(f"{maintenance.id}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
                filename = f"rutina_impresora_escaner_{equipment_code}_{timestamp}_{hash_str}.xlsx"
                
                # Guardar archivo
                file_path = os.path.join(reports_dir, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(excel_bytes)
                
                generated_files.append(file_path)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Generado: {file_path}"))
                
                # Crear registro Report (opcional)
                try:
                    report, created = Report.objects.get_or_create(
                        maintenance=maintenance,
                        defaults={
                            'title': f'Reporte Impresora/Escáner - {equipment_code}',
                            'content': f'Reporte generado: {filename}',
                        }
                    )
                    if not created and report.pdf_file:
                        # Actualizar archivo existente
                        from django.core.files.base import ContentFile
                        report.pdf_file.save(filename, ContentFile(excel_bytes), save=True)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ! No se pudo crear registro Report: {e}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Error procesando mantenimiento {maintenance.id}: {e}"))
                import traceback
                traceback.print_exc()

        self.stdout.write(self.style.SUCCESS(f'\nSe generaron {len(generated_files)} archivos Excel:'))
        for file_path in generated_files:
            self.stdout.write(f"  - {file_path}")
