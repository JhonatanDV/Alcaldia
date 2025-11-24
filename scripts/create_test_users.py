import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
import sys
# Ensure project root is on sys.path so Django can import `core`
sys.path.insert(0, os.getcwd())
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command

# Create superuser
username = 'admin'
email = 'admin@local'
password = 'admin123'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser created: {username} / {password}')
else:
    print(f'Superuser already exists: {username}')

# Run setup_roles management command to create groups and a tecnico user
try:
    call_command('setup_roles')
    print('setup_roles executed (groups and tecnico created/updated).')
except Exception as e:
    print('Error running setup_roles:', e)
