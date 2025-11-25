# -*- coding: utf-8 -*-
"""
Management command para generar reportes Excel de rutinas de mantenimiento.
Usa la plantilla original y la rellena con datos de los mantenimientos.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import os
import uuid

from api.models import Maintenance, Report
from api.services.excel_report_generator import ExcelReportGenerator
from django.conf import settings
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Genera reportes Excel de rutinas de mantenimiento para equipos de cómputo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', 
            type=int, 
            default=10, 
            help='Máximo de mantenimientos a procesar'
        )
        parser.add_argument(
            '--only-completed', 
            action='store_true', 
            help='Procesar solo mantenimientos completados (con completion_date)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Directorio de salida para los archivos Excel (default: media/maintenance-reports/)'
        )
        parser.add_argument(
            '--maintenance-id',
            type=int,
            default=None,
            help='ID específico de un mantenimiento a procesar'
        )

    def handle(self, *args, **options):
        limit = options.get('limit') or 10
        only_completed = options.get('only_completed', False)
        output_dir = options.get('output_dir')
        maintenance_id = options.get('maintenance_id')

        # Configurar directorio de salida
        if not output_dir:
            output_dir = os.path.join(settings.MEDIA_ROOT or 'media', 'maintenance-reports')
        os.makedirs(output_dir, exist_ok=True)

        # Construir queryset
        if maintenance_id:
            qs = Maintenance.objects.filter(id=maintenance_id)
        else:
            qs = Maintenance.objects.filter(equipment_type='computer')
            if only_completed:
                qs = qs.filter(completion_date__isnull=False)
            qs = qs.order_by('-completion_date')[:limit]

        if not qs.exists():
            self.stdout.write(self.style.WARNING('No se encontraron mantenimientos para procesar'))
            return

        # Inicializar generador
        try:
            generator = ExcelReportGenerator()
        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return

        User = get_user_model()
        generated_files = []

        for maintenance in qs:
            self.stdout.write(f'Procesando mantenimiento id={maintenance.id} equipo={maintenance.equipment}')
            
            try:
                # Generar Excel
                excel_bytes = generator.generate_report(maintenance)

                # Generar nombre de archivo
                fecha_str = maintenance.maintenance_date.strftime('%Y%m%d') if maintenance.maintenance_date else 'sin_fecha'
                equipo_code = maintenance.equipment.code or f'eq{maintenance.equipment.id}'
                filename = f"rutina_mantenimiento_{equipo_code}_{fecha_str}_{uuid.uuid4().hex[:8]}.xlsx"
                filepath = os.path.join(output_dir, filename)

                # Guardar archivo
                with open(filepath, 'wb') as f:
                    f.write(excel_bytes)

                generated_files.append(filepath)

                # Crear/actualizar registro Report
                user = maintenance.technician or User.objects.filter(is_active=True).first()
                report, created = Report.objects.get_or_create(
                    maintenance=maintenance,
                    defaults={
                        'generated_by': user,
                        'title': f'Rutina Mantenimiento - {equipo_code} - {fecha_str}'
                    }
                )
                
                # Actualizar con la nueva ruta del archivo
                report.pdf_file = os.path.join('maintenance-reports', filename)
                report.generated_by = user
                report.title = f'Rutina Mantenimiento - {equipo_code} - {fecha_str}'
                report.save()

                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Generado: {filepath}'
                ))

            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f'  ✗ Error procesando mantenimiento {maintenance.id}: {e}'
                ))
                import traceback
                traceback.print_exc()

        # Resumen final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Se generaron {len(generated_files)} archivos Excel:'))
        for f in generated_files:
            self.stdout.write(f'  - {f}')
