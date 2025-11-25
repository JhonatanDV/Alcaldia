from django.core.management.base import BaseCommand
import json

from api.models import Maintenance


class Command(BaseCommand):
    help = 'Export up to N maintenances with equipment_type=computer as JSON'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=3, help='Number of records to export')

    def handle(self, *args, **options):
        limit = options.get('limit') or 3
        qs = Maintenance.objects.filter(equipment_type='computer').order_by('-completion_date')[:limit]
        out = []
        for m in qs:
            photos = []
            for p in m.photos.all():
                try:
                    photos.append(p.photo.url if p.photo and getattr(p.photo, 'url', None) else None)
                except Exception:
                    photos.append(None)

            signature_url = None
            try:
                if m.signature and getattr(m.signature, 'image', None) and getattr(m.signature.image, 'url', None):
                    signature_url = m.signature.image.url
            except Exception:
                signature_url = None

            second_signature_url = None
            try:
                if m.second_signature and getattr(m.second_signature, 'image', None) and getattr(m.second_signature.image, 'url', None):
                    second_signature_url = m.second_signature.image.url
            except Exception:
                second_signature_url = None

            out.append({
                'id': m.id,
                'equipment': {
                    'id': m.equipment.id if m.equipment else None,
                    'code': m.equipment.code if m.equipment else None,
                    'name': m.equipment.name if m.equipment else None,
                },
                'maintenance_date': str(m.maintenance_date) if m.maintenance_date else None,
                'scheduled_date': str(m.scheduled_date) if m.scheduled_date else None,
                'completion_date': str(m.completion_date) if m.completion_date else None,
                'hora_inicio': str(m.hora_inicio) if m.hora_inicio else None,
                'hora_final': str(m.hora_final) if m.hora_final else None,
                'performed_by': m.performed_by,
                'activities': m.activities,
                'observaciones_generales': m.observaciones_generales,
                'observaciones_seguridad': m.observaciones_seguridad,
                'calificacion_servicio': m.calificacion_servicio,
                'photos': photos,
                'signature': signature_url,
                'second_signature': second_signature_url,
            })

        self.stdout.write(json.dumps(out, ensure_ascii=False, indent=2))
