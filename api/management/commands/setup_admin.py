"""
Management command to create or configure the admin user 'alcaldia'
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Create or configure the alcaldia admin user'

    def handle(self, *args, **options):
        # Get or create the Admin group
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        
        # Get or create the alcaldia user
        user, created = User.objects.get_or_create(
            username='alcaldia',
            defaults={
                'email': 'admin@alcaldia.gov',
                'first_name': 'Alcaldía',
                'last_name': 'Municipal',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
            }
        )
        
        if created:
            # Set password for new user
            user.set_password('alcaldia123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario "alcaldia" creado con contraseña: alcaldia123'))
        else:
            # Update existing user to ensure it has admin privileges
            user.is_staff = True
            user.is_active = True
            user.email = 'admin@alcaldia.gov'
            user.first_name = 'Alcaldía'
            user.last_name = 'Municipal'
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario "alcaldia" actualizado'))
        
        # Add user to Admin group
        if not user.groups.filter(name='Admin').exists():
            user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario "alcaldia" agregado al grupo Admin'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario "alcaldia" ya pertenece al grupo Admin'))
        
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('=== CONFIGURACIÓN COMPLETADA ==='))
        self.stdout.write(self.style.SUCCESS(f'Usuario: alcaldia'))
        self.stdout.write(self.style.SUCCESS(f'Contraseña: alcaldia123 (si fue creado)'))
        self.stdout.write(self.style.SUCCESS(f'Rol: Administrador'))
        self.stdout.write(self.style.SUCCESS(f'is_staff: {user.is_staff}'))
        self.stdout.write(self.style.SUCCESS(f'Grupos: {", ".join([g.name for g in user.groups.all()])}'))
