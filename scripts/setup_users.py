"""
Script para resetear el usuario admin y crear grupos necesarios.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Crear grupos si no existen
admin_group, created = Group.objects.get_or_create(name='Admin')
if created:
    print('✅ Grupo Admin creado')
else:
    print('ℹ️  Grupo Admin ya existe')

tech_group, created = Group.objects.get_or_create(name='Técnico')
if created:
    print('✅ Grupo Técnico creado')
else:
    print('ℹ️  Grupo Técnico ya existe')

# Verificar o crear usuario admin
try:
    admin = User.objects.get(username='admin')
    print(f'\nℹ️  Usuario admin encontrado: {admin.username}')
except User.DoesNotExist:
    print('\n⚠️  Usuario admin no existe. Creando...')
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print('✅ Usuario admin creado')

# Resetear contraseña
admin.set_password('admin123')
admin.is_superuser = True
admin.is_staff = True
admin.is_active = True
admin.save()

# Agregar al grupo Admin
admin.groups.clear()
admin.groups.add(admin_group)

print(f'\n✅ Contraseña reseteada exitosamente')
print(f'\n📋 CREDENCIALES:')
print(f'   Usuario: admin')
print(f'   Contraseña: admin123')
print(f'   Email: {admin.email}')
print(f'   Superusuario: {admin.is_superuser}')
print(f'   Staff: {admin.is_staff}')
print(f'   Activo: {admin.is_active}')
print(f'   Grupos: {", ".join([g.name for g in admin.groups.all()])}')

# Crear usuario técnico de prueba
try:
    tecnico = User.objects.get(username='tecnico1')
    print(f'\nℹ️  Usuario tecnico1 encontrado')
except User.DoesNotExist:
    print(f'\n⚠️  Usuario tecnico1 no existe. Creando...')
    tecnico = User.objects.create_user(
        username='tecnico1',
        email='tecnico1@example.com',
        password='tecnico123'
    )
    print('✅ Usuario tecnico1 creado')

tecnico.set_password('tecnico123')
tecnico.is_staff = True
tecnico.is_active = True
tecnico.save()
tecnico.groups.clear()
tecnico.groups.add(tech_group)

print(f'\n✅ Usuario técnico configurado')
print(f'\n📋 CREDENCIALES TÉCNICO:')
print(f'   Usuario: tecnico1')
print(f'   Contraseña: tecnico123')

print('\n' + '='*50)
print('✅ Todos los usuarios configurados correctamente')
print('='*50)
