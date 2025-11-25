#!/usr/bin/env python
"""
Script para crear las plantillas de reportes en la base de datos.
Las plantillas corresponden a los archivos Excel en la carpeta plantillas/.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Template, ReportTemplate


def create_templates():
    """Crea las plantillas de reportes en la base de datos."""
    
    templates_data = [
        {
            'name': 'Rutina Mantenimiento Equipos de Cómputo',
            'type': 'excel',
            'description': 'Plantilla Excel para rutinas de mantenimiento preventivo de equipos de cómputo (torres, monitores, teclados, etc.)',
            'html_content': '',
            'css_content': '',
            'fields_schema': {
                'sede': {'map_to': 'sede'},
                'dependencia': {'map_to': 'dependencia'},
                'oficina': {'map_to': 'oficina'},
                'placa': {'map_to': 'equipment_code'},
                'fecha_mantenimiento': {'map_to': 'scheduled_date'},
                'hora_inicio': {'map_to': 'hora_inicio'},
                'hora_final': {'map_to': 'hora_final'},
                'activities': {'map_to': 'activities'},
                'observaciones_generales': {'map_to': 'observaciones_generales'},
                'observaciones_seguridad': {'map_to': 'observaciones_seguridad'},
                'elaborado_por': {'map_to': 'elaborado_por'},
                'revisado_por': {'map_to': 'revisado_por'},
            }
        },
        {
            'name': 'Rutina Mantenimiento Impresoras y Escáneres',
            'type': 'excel',
            'description': 'Plantilla Excel para rutinas de mantenimiento preventivo de impresoras y escáneres',
            'html_content': '',
            'css_content': '',
            'fields_schema': {
                'sede': {'map_to': 'sede'},
                'dependencia': {'map_to': 'dependencia'},
                'oficina': {'map_to': 'oficina'},
                'placa': {'map_to': 'equipment_code'},
                'fecha_mantenimiento': {'map_to': 'scheduled_date'},
                'hora_inicio': {'map_to': 'hora_inicio'},
                'hora_final': {'map_to': 'hora_final'},
                'activities': {'map_to': 'activities'},
                'observaciones_generales': {'map_to': 'observaciones_generales'},
                'elaborado_por': {'map_to': 'elaborado_por'},
                'revisado_por': {'map_to': 'revisado_por'},
            }
        },
    ]
    
    created = 0
    updated = 0
    
    for tpl_data in templates_data:
        tpl, is_new = Template.objects.update_or_create(
            name=tpl_data['name'],
            defaults={
                'type': tpl_data['type'],
                'description': tpl_data['description'],
                'html_content': tpl_data['html_content'],
                'css_content': tpl_data['css_content'],
                'fields_schema': tpl_data['fields_schema'],
            }
        )
        if is_new:
            created += 1
            print(f"✅ Creada: {tpl.name} (id={tpl.id})")
        else:
            updated += 1
            print(f"🔄 Actualizada: {tpl.name} (id={tpl.id})")
    
    # También crear un ReportTemplate activo como fallback
    report_tpl, is_new = ReportTemplate.objects.update_or_create(
        name='Plantilla PDF por Defecto',
        defaults={
            'description': 'Plantilla PDF generada con ReportLab para reportes de mantenimiento',
            'is_active': True,
        }
    )
    if is_new:
        print(f"✅ ReportTemplate activo creado: {report_tpl.name}")
    else:
        print(f"🔄 ReportTemplate actualizado: {report_tpl.name}")
    
    print(f"\n📊 Resumen: {created} plantillas creadas, {updated} actualizadas")
    print("\n📋 Plantillas disponibles:")
    for t in Template.objects.all():
        print(f"   - [{t.id}] {t.name} ({t.type})")


if __name__ == '__main__':
    create_templates()
