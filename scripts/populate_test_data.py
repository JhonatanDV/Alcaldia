"""
Script para poblar la base de datos con datos de prueba
Mantiene lógica: no crea reportes generados, pero sí datos para todas las demás tablas
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta, date
import random
from decimal import Decimal

from api.models import (
    Sede, Dependencia, Subdependencia, Equipment, Maintenance,
    AuditLog, ReportTemplate, Template, Incident, SiteConfiguration
)


def create_users_and_groups():
    """Crear usuarios y grupos con permisos"""
    print("📝 Creando grupos y permisos...")
    
    # Crear grupos
    admin_group, _ = Group.objects.get_or_create(name='Administradores')
    tech_group, _ = Group.objects.get_or_create(name='Técnicos')
    
    # Asignar todos los permisos a admin
    admin_group.permissions.set(Permission.objects.all())
    
    # Permisos específicos para técnicos
    tech_permissions = Permission.objects.filter(
        codename__in=[
            'view_equipment', 'add_equipment', 'change_equipment',
            'view_maintenance', 'add_maintenance', 'change_maintenance',
            'view_incident', 'add_incident', 'change_incident',
        ]
    )
    tech_group.permissions.set(tech_permissions)
    
    print("✅ Grupos creados: Administradores, Técnicos")
    
    # Crear usuarios
    users_data = [
        ('admin1', 'admin@alcaldia.gov.co', 'Admin123!', True, True, admin_group),
        ('admin2', 'admin2@alcaldia.gov.co', 'Admin123!', True, False, admin_group),
        ('tecnico1', 'tecnico1@alcaldia.gov.co', 'Tech123!', False, False, tech_group),
        ('tecnico2', 'tecnico2@alcaldia.gov.co', 'Tech123!', False, False, tech_group),
        ('tecnico3', 'tecnico3@alcaldia.gov.co', 'Tech123!', False, False, tech_group),
    ]
    
    created_users = []
    for username, email, password, is_staff, is_super, group in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': is_staff,
                'is_superuser': is_super,
                'first_name': username.capitalize(),
                'last_name': 'Usuario'
            }
        )
        if created:
            user.set_password(password)
            user.save()
            user.groups.add(group)
            created_users.append(username)
    
    print(f"✅ Usuarios creados: {', '.join(created_users)}")
    return User.objects.all()


def create_sedes():
    """Crear 20 sedes"""
    print("\n🏢 Creando sedes...")
    
    sedes_data = [
        ('Sede Central', 'Calle 10 #15-20, Centro', '601-1234567', 'SC-001'),
        ('Sede Norte', 'Av. Caracas #150-30', '601-1234568', 'SN-002'),
        ('Sede Sur', 'Calle 5 Sur #25-10', '601-1234569', 'SS-003'),
        ('Sede Oriente', 'Carrera 7 Este #40-15', '601-1234570', 'SO-004'),
        ('Sede Occidente', 'Av. Boyacá #80-25', '601-1234571', 'SOC-005'),
        ('Sede Chapinero', 'Calle 63 #10-50', '601-1234572', 'SCH-006'),
        ('Sede Usaquén', 'Calle 116 #7-15', '601-1234573', 'SU-007'),
        ('Sede Suba', 'Calle 127 #91-20', '601-1234574', 'SSU-008'),
        ('Sede Kennedy', 'Av. Ciudad de Cali #86-30', '601-1234575', 'SK-009'),
        ('Sede Engativá', 'Calle 80 #100-15', '601-1234576', 'SE-010'),
        ('Sede Fontibón', 'Calle 13 #96-20', '601-1234577', 'SF-011'),
        ('Sede Bosa', 'Autopista Sur #65-30', '601-1234578', 'SB-012'),
        ('Sede Tunjuelito', 'Av. Boyacá Sur #48-20', '601-1234579', 'ST-013'),
        ('Sede Rafael Uribe', 'Calle 30 Sur #18-10', '601-1234580', 'SRU-014'),
        ('Sede San Cristóbal', 'Av. 1 de Mayo #20-50', '601-1234581', 'SSC-015'),
        ('Sede Usme', 'Calle 137 Sur #13-20', '601-1234582', 'SUS-016'),
        ('Sede Sumapaz', 'Vereda Nazareth', '601-1234583', 'SSP-017'),
        ('Sede Teusaquillo', 'Calle 37 #24-10', '601-1234584', 'STE-018'),
        ('Sede Barrios Unidos', 'Calle 72 #52-15', '601-1234585', 'SBU-019'),
        ('Sede Santa Fe', 'Carrera 4 #26-30', '601-1234586', 'SSF-020'),
    ]
    
    sedes = []
    for nombre, direccion, telefono, codigo in sedes_data:
        sede, created = Sede.objects.get_or_create(
            nombre=nombre,
            defaults={
                'direccion': direccion,
                'telefono': telefono,
                'codigo': codigo,
                'activo': True
            }
        )
        sedes.append(sede)
    
    print(f"✅ {len(sedes)} sedes creadas")
    return sedes


def create_dependencias(sedes):
    """Crear 20 dependencias distribuidas en las sedes"""
    print("\n📂 Creando dependencias...")
    
    dependencias_data = [
        'Sistemas y Tecnología', 'Recursos Humanos', 'Contabilidad',
        'Tesorería', 'Jurídica', 'Planeación', 'Obras Públicas',
        'Servicios Públicos', 'Educación', 'Salud', 'Cultura',
        'Deportes', 'Medio Ambiente', 'Movilidad', 'Seguridad',
        'Inspección', 'Archivo', 'Comunicaciones', 'Compras',
        'Almacén'
    ]
    
    dependencias = []
    for i, nombre in enumerate(dependencias_data):
        sede = sedes[i % len(sedes)]  # Distribuir entre sedes
        dep, created = Dependencia.objects.get_or_create(
            sede=sede,
            nombre=nombre,
            defaults={
                'codigo': f'DEP-{i+1:03d}',
                'responsable': f'Responsable {nombre}',
                'email': f'{nombre.lower().replace(" ", ".")}@alcaldia.gov.co',
                'activo': True
            }
        )
        dependencias.append(dep)
    
    print(f"✅ {len(dependencias)} dependencias creadas")
    return dependencias


def create_subdependencias(dependencias):
    """Crear 20 subdependencias"""
    print("\n📁 Creando subdependencias...")
    
    subdeps_templates = [
        'Coordinación', 'Soporte', 'Gestión', 'Operaciones',
        'Desarrollo', 'Control', 'Supervisión', 'Atención al Usuario'
    ]
    
    subdependencias = []
    for i, dep in enumerate(dependencias[:20]):  # Primeras 20 dependencias
        nombre = f"{subdeps_templates[i % len(subdeps_templates)]} - {dep.nombre}"
        subdep, created = Subdependencia.objects.get_or_create(
            dependencia=dep,
            nombre=nombre,
            defaults={
                'codigo': f'SUBDEP-{i+1:03d}',
                'responsable': f'Coordinador {nombre}',
                'activo': True
            }
        )
        subdependencias.append(subdep)
    
    print(f"✅ {len(subdependencias)} subdependencias creadas")
    return subdependencias


def create_equipment(sedes, dependencias, subdependencias):
    """Crear 20 equipos"""
    print("\n💻 Creando equipos...")
    
    equipment_types = [
        ('Computador de Escritorio', 'Dell', 'OptiPlex'),
        ('Laptop', 'HP', 'ProBook'),
        ('Impresora', 'Canon', 'ImageClass'),
        ('Servidor', 'Dell', 'PowerEdge'),
        ('Router', 'Cisco', 'ISR'),
        ('Switch', 'Cisco', 'Catalyst'),
        ('Escáner', 'Epson', 'WorkForce'),
        ('UPS', 'APC', 'Smart-UPS'),
        ('Proyector', 'Epson', 'PowerLite'),
        ('Teléfono IP', 'Cisco', 'SPA'),
    ]
    
    equipments = []
    base_date = date.today() - timedelta(days=365*3)  # 3 años atrás
    
    for i in range(20):
        eq_type, brand, model = equipment_types[i % len(equipment_types)]
        sede = sedes[i % len(sedes)]
        dep = dependencias[i % len(dependencias)]
        subdep = subdependencias[i % len(subdependencias)] if subdependencias else None
        
        purchase_date = base_date + timedelta(days=random.randint(0, 900))
        warranty_expiry = purchase_date + timedelta(days=365*2)  # 2 años garantía
        
        equipment, created = Equipment.objects.get_or_create(
            code=f'EQ-{i+1:04d}',
            defaults={
                'name': f'{eq_type} {i+1}',
                'serial_number': f'SN{random.randint(100000, 999999)}',
                'model': f'{model}-{random.randint(100, 999)}',
                'brand': brand,
                'location': f'Oficina {i+1}',
                'sede_rel': sede,
                'dependencia_rel': dep,
                'subdependencia': subdep,
                'purchase_date': purchase_date,
                'warranty_expiry': warranty_expiry,
                'notes': f'Equipo asignado a {dep.nombre}'
            }
        )
        equipments.append(equipment)
    
    print(f"✅ {len(equipments)} equipos creados")
    return equipments


def create_maintenances(equipments, users, sedes, dependencias, subdependencias):
    """Crear 20 mantenimientos (sin generar reportes)"""
    print("\n🔧 Creando mantenimientos...")
    
    maintenance_types = ['preventivo', 'correctivo', 'predictivo']
    statuses = ['pending', 'in_progress', 'completed']
    
    maintenances = []
    base_date = date.today() - timedelta(days=180)
    
    for i in range(20):
        equipment = equipments[i % len(equipments)]
        technician = random.choice([u for u in users if not u.is_superuser])
        
        scheduled_date = base_date + timedelta(days=random.randint(0, 150))
        status = random.choice(statuses)
        completion_date = scheduled_date + timedelta(days=random.randint(1, 7)) if status == 'completed' else None
        
        maintenance, created = Maintenance.objects.get_or_create(
            equipment=equipment,
            scheduled_date=scheduled_date,
            defaults={
                'maintenance_type': maintenance_types[i % len(maintenance_types)],
                'technician': technician,
                'description': f'Mantenimiento {maintenance_types[i % len(maintenance_types)]} programado',
                'observations': f'Equipo en condiciones {"óptimas" if status == "completed" else "pendientes"}',
                'status': status,
                'cost': Decimal(random.randint(50000, 500000)),
                'completion_date': completion_date,
                'codigo': f'MAN-{i+1:04d}',
                'version': '1.0',
                'vigencia': scheduled_date + timedelta(days=365),
                'sede_rel': equipment.sede_rel,
                'dependencia_rel': equipment.dependencia_rel,
                'subdependencia': equipment.subdependencia,
                'oficina': f'Oficina {i+1}',
                'placa': f'PLA-{random.randint(1000, 9999)}',
                'hora_inicio': f'{random.randint(8, 12):02d}:00',
                'hora_final': f'{random.randint(13, 17):02d}:00',
                'activities': {
                    'limpieza': True,
                    'revision': True,
                    'actualizacion': random.choice([True, False])
                },
                'observaciones_generales': f'Mantenimiento realizado según protocolo {i+1}',
                'calificacion_servicio': random.choice(['excelente', 'bueno', 'regular']),
                'is_incident': random.choice([True, False]),
                'equipment_type': 'computer',
                'elaborado_por': technician.get_full_name() or technician.username,
            }
        )
        maintenances.append(maintenance)
    
    print(f"✅ {len(maintenances)} mantenimientos creados")
    return maintenances


def create_incidents(equipments, users, maintenances):
    """Crear 20 incidentes"""
    print("\n⚠️ Creando incidentes...")
    
    severities = ['low', 'medium', 'high', 'critical']
    statuses = ['open', 'in_progress', 'resolved', 'closed']
    
    incident_descriptions = [
        'Equipo no enciende', 'Pantalla azul recurrente', 'Lentitud extrema',
        'Sin conexión a internet', 'Disco duro con ruido', 'Sobrecalentamiento',
        'Teclado no funciona', 'Mouse no responde', 'Puerto USB dañado',
        'Ventilador hace ruido', 'No detecta impresora', 'Error de memoria',
        'Sistema operativo corrupto', 'Virus detectado', 'Pérdida de datos',
        'Batería no carga', 'Pantalla rota', 'Derrame de líquido',
        'Botón de encendido roto', 'Puerto de red dañado'
    ]
    
    incidents = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(20):
        equipment = equipments[i % len(equipments)]
        reporter = random.choice(users)
        status = random.choice(statuses)
        
        incident_date = base_date + timedelta(days=random.randint(0, 85))
        resolved_at = incident_date + timedelta(hours=random.randint(1, 72)) if status in ['resolved', 'closed'] else None
        
        incident, created = Incident.objects.get_or_create(
            equipment=equipment,
            incident_date=incident_date,
            defaults={
                'reported_by': reporter,
                'severity': severities[i % len(severities)],
                'description': incident_descriptions[i],
                'resolution': f'Se procedió a reparar {incident_descriptions[i].lower()}' if status in ['resolved', 'closed'] else '',
                'status': status,
                'resolved_at': resolved_at,
                'maintenance': maintenances[i % len(maintenances)] if random.choice([True, False]) else None
            }
        )
        incidents.append(incident)
    
    print(f"✅ {len(incidents)} incidentes creados")
    return incidents


def create_templates():
    """Crear 20 plantillas"""
    print("\n📄 Creando plantillas...")
    
    template_types = ['pdf', 'excel']
    template_names = [
        'Reporte de Mantenimiento Preventivo', 'Reporte de Mantenimiento Correctivo',
        'Inventario de Equipos', 'Hoja de Vida del Equipo', 'Control de Incidentes',
        'Reporte Mensual de Actividades', 'Certificado de Mantenimiento',
        'Orden de Trabajo', 'Acta de Entrega', 'Solicitud de Repuestos',
        'Reporte de Costos', 'Evaluación de Servicio', 'Plan de Mantenimiento',
        'Informe Técnico', 'Bitácora de Equipos', 'Control de Garantías',
        'Reporte de Disponibilidad', 'Análisis de Fallas', 'Cronograma de Mantenimiento',
        'Lista de Verificación'
    ]
    
    templates = []
    for i, name in enumerate(template_names):
        template, created = Template.objects.get_or_create(
            name=name,
            defaults={
                'type': template_types[i % len(template_types)],
                'description': f'Plantilla para {name.lower()}',
                'html_content': f'<h1>{name}</h1><p>Contenido de la plantilla {i+1}</p>',
                'css_content': 'body { font-family: Arial; }',
                'fields_schema': {
                    'title': 'string',
                    'date': 'date',
                    'equipment': 'string',
                    'technician': 'string'
                }
            }
        )
        templates.append(template)
    
    print(f"✅ {len(templates)} plantillas creadas")
    return templates


def create_report_templates():
    """Crear 20 plantillas de reporte"""
    print("\n📋 Creando plantillas de reporte...")
    
    report_templates = []
    for i in range(20):
        template, created = ReportTemplate.objects.get_or_create(
            name=f'Plantilla de Reporte {i+1}',
            defaults={
                'description': f'Configuración para reportes tipo {i+1}',
                'header_config': {
                    'logo_enabled': True,
                    'title': f'ALCALDÍA MUNICIPAL - REPORTE {i+1}',
                    'subtitle': 'Sistema de Gestión de Mantenimiento'
                },
                'footer_config': {
                    'show_page_numbers': True,
                    'text': f'Documento generado automáticamente - {date.today().year}'
                },
                'is_active': True
            }
        )
        report_templates.append(template)
    
    print(f"✅ {len(report_templates)} plantillas de reporte creadas")
    return report_templates


def create_audit_logs(users):
    """Crear 20 registros de auditoría"""
    print("\n📊 Creando registros de auditoría...")
    
    actions = ['create', 'update', 'delete', 'view']
    models = ['Equipment', 'Maintenance', 'Incident', 'Template', 'User']
    
    audit_logs = []
    base_time = timezone.now() - timedelta(days=30)
    
    for i in range(20):
        user = random.choice(users)
        action = random.choice(actions)
        model_name = random.choice(models)
        
        log, created = AuditLog.objects.get_or_create(
            user=user,
            action=action,
            model_name=model_name,
            timestamp=base_time + timedelta(days=random.randint(0, 29)),
            defaults={
                'object_id': random.randint(1, 100),
                'object_repr': f'{model_name} #{random.randint(1, 100)}',
                'changes': {
                    'field_changed': 'status',
                    'old_value': 'pending',
                    'new_value': 'completed'
                },
                'ip_address': f'192.168.1.{random.randint(1, 254)}'
            }
        )
        audit_logs.append(log)
    
    print(f"✅ {len(audit_logs)} registros de auditoría creados")
    return audit_logs


def create_site_configuration():
    """Crear configuración del sitio"""
    print("\n⚙️ Creando configuración del sitio...")
    
    config, created = SiteConfiguration.objects.get_or_create(
        id=1,
        defaults={
            'config': {
                'site_name': 'Sistema de Gestión de Mantenimiento',
                'maintenance_interval_days': 90,
                'email_notifications': True,
                'backup_enabled': True,
                'max_file_size_mb': 10,
                'allowed_file_types': ['pdf', 'xlsx', 'jpg', 'png'],
                'theme': 'default',
                'language': 'es',
                'timezone': 'America/Bogota'
            }
        }
    )
    
    print(f"✅ Configuración del sitio {'creada' if created else 'actualizada'}")
    return config


def main():
    """Función principal para ejecutar la población de datos"""
    print("\n" + "="*60)
    print("🚀 INICIANDO POBLACIÓN DE DATOS DE PRUEBA")
    print("="*60)
    
    try:
        # 1. Usuarios y grupos
        users = create_users_and_groups()
        
        # 2. Estructura jerárquica
        sedes = create_sedes()
        dependencias = create_dependencias(sedes)
        subdependencias = create_subdependencias(dependencias)
        
        # 3. Equipos
        equipments = create_equipment(sedes, dependencias, subdependencias)
        
        # 4. Mantenimientos (sin reportes generados)
        maintenances = create_maintenances(equipments, users, sedes, dependencias, subdependencias)
        
        # 5. Incidentes
        incidents = create_incidents(equipments, users, maintenances)
        
        # 6. Plantillas
        templates = create_templates()
        report_templates = create_report_templates()
        
        # 7. Auditoría
        audit_logs = create_audit_logs(users)
        
        # 8. Configuración
        site_config = create_site_configuration()
        
        print("\n" + "="*60)
        print("✅ POBLACIÓN DE DATOS COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\n📊 Resumen:")
        print(f"   • Usuarios: {User.objects.count()}")
        print(f"   • Grupos: {Group.objects.count()}")
        print(f"   • Sedes: {Sede.objects.count()}")
        print(f"   • Dependencias: {Dependencia.objects.count()}")
        print(f"   • Subdependencias: {Subdependencia.objects.count()}")
        print(f"   • Equipos: {Equipment.objects.count()}")
        print(f"   • Mantenimientos: {Maintenance.objects.count()}")
        print(f"   • Incidentes: {Incident.objects.count()}")
        print(f"   • Plantillas: {Template.objects.count()}")
        print(f"   • Plantillas de Reporte: {ReportTemplate.objects.count()}")
        print(f"   • Registros de Auditoría: {AuditLog.objects.count()}")
        print("\n💡 Credenciales de acceso:")
        print("   Admin: admin1 / Admin123!")
        print("   Técnico: tecnico1 / Tech123!")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error durante la población de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
