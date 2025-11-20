from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Creates initial roles and permissions for the system'

    def handle(self, *args, **kwargs):
        roles = [
            {
                'name': 'Administrador',
                'permissions': ['add', 'change', 'delete', 'view']
            },
            {
                'name': 'Tecnico',
                'permissions': ['add', 'change', 'view']
            },
        ]

        for role_data in roles:
            role_name = role_data['name']
            group, created = Group.objects.get_or_create(name=role_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {role_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Role already exists: {role_name}'))

        self.stdout.write(self.style.SUCCESS('Initial roles created successfully!'))