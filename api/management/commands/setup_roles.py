"""
Management command to set up roles and permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Equipment, Maintenance, Photo, Signature, Report


class Command(BaseCommand):
    help = 'Configura roles y permisos para el sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Configurando roles y permisos...')

        # Crear grupo Admin si no existe
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Admin" creado'))
        else:
            self.stdout.write('- Grupo "Admin" ya existe')

        # Crear grupo Tecnico si no existe
        tecnico_group, created = Group.objects.get_or_create(name='Tecnico')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Tecnico" creado'))
        else:
            self.stdout.write('- Grupo "Tecnico" ya existe')

        # Obtener content types
        equipment_ct = ContentType.objects.get_for_model(Equipment)
        maintenance_ct = ContentType.objects.get_for_model(Maintenance)
        photo_ct = ContentType.objects.get_for_model(Photo)
        signature_ct = ContentType.objects.get_for_model(Signature)
        report_ct = ContentType.objects.get_for_model(Report)

        # Permisos para Admin (todos los permisos)
        admin_permissions = Permission.objects.filter(
            content_type__in=[
                equipment_ct, 
                maintenance_ct, 
                photo_ct, 
                signature_ct, 
                report_ct
            ]
        )
        admin_group.permissions.set(admin_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Asignados {admin_permissions.count()} permisos al grupo Admin'))

        # Permisos para Técnico (solo ver equipos, crear/editar/ver mantenimientos)
        tecnico_permissions = []
        
        # Equipment: solo view
        tecnico_permissions.extend(
            Permission.objects.filter(
                content_type=equipment_ct,
                codename__in=['view_equipment']
            )
        )
        
        # Maintenance: add, change, view (NO delete)
        tecnico_permissions.extend(
            Permission.objects.filter(
                content_type=maintenance_ct,
                codename__in=['add_maintenance', 'change_maintenance', 'view_maintenance']
            )
        )
        
        # Photo: add, view (para subir fotos)
        tecnico_permissions.extend(
            Permission.objects.filter(
                content_type=photo_ct,
                codename__in=['add_photo', 'view_photo']
            )
        )
        
        # Signature: add, view (para firmas)
        tecnico_permissions.extend(
            Permission.objects.filter(
                content_type=signature_ct,
                codename__in=['add_signature', 'view_signature']
            )
        )
        
        # Report: view (para ver reportes)
        tecnico_permissions.extend(
            Permission.objects.filter(
                content_type=report_ct,
                codename__in=['view_report']
            )
        )

        tecnico_group.permissions.set(tecnico_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Asignados {len(tecnico_permissions)} permisos al grupo Tecnico'))

        # Crear usuario técnico de ejemplo
        tecnico_username = 'tecnico'
        if not User.objects.filter(username=tecnico_username).exists():
            tecnico_user = User.objects.create_user(
                username=tecnico_username,
                email='tecnico@alcaldia.gov',
                password='tecnico123',
                first_name='Usuario',
                last_name='Técnico'
            )
            tecnico_user.groups.add(tecnico_group)
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario técnico creado: {tecnico_username} / tecnico123'))
        else:
            tecnico_user = User.objects.get(username=tecnico_username)
            tecnico_user.groups.add(tecnico_group)
            self.stdout.write(f'- Usuario técnico ya existe: {tecnico_username}')

        # Asegurar que el superuser esté en el grupo Admin
        superusers = User.objects.filter(is_superuser=True)
        for su in superusers:
            su.groups.add(admin_group)
            self.stdout.write(f'✓ Superuser "{su.username}" agregado al grupo Admin')

        self.stdout.write(self.style.SUCCESS('\n✅ Configuración de roles completada'))
        self.stdout.write('\nResumen de permisos:')
        self.stdout.write('  Admin:')
        self.stdout.write('    - Equipos: crear, editar, eliminar, ver')
        self.stdout.write('    - Mantenimientos: crear, editar, eliminar, ver')
        self.stdout.write('    - Reportes: crear, editar, eliminar, ver')
        self.stdout.write('    - Fotos y firmas: todas las operaciones')
        self.stdout.write('')
        self.stdout.write('  Técnico:')
        self.stdout.write('    - Equipos: solo ver (NO crear)')
        self.stdout.write('    - Mantenimientos: crear, editar, ver (NO eliminar)')
        self.stdout.write('    - Reportes: solo ver')
        self.stdout.write('    - Fotos y firmas: crear, ver')
        self.stdout.write('')
        self.stdout.write('Credenciales de usuario técnico:')
        self.stdout.write('  Usuario: tecnico')
        self.stdout.write('  Contraseña: tecnico123')
