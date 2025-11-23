"""
Django management command for backing up the database.
"""
import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates a backup of the MySQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Output directory for backup file',
            default='backups'
        )

    def handle(self, *args, **options):
        # Get database configuration
        db_config = settings.DATABASES['default']
        db_name = db_config['NAME']
        db_user = db_config['USER']
        db_password = db_config['PASSWORD']
        db_host = db_config['HOST']
        db_port = db_config['PORT']

        # Create backup directory if it doesn't exist
        backup_dir = options['output']
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{db_name}_{timestamp}.sql')

        # Build mysqldump command
        dump_cmd = [
            'mysqldump',
            '-h', db_host,
            '-P', str(db_port),
            '-u', db_user,
            f'--password={db_password}',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--events',
            db_name
        ]

        try:
            self.stdout.write(self.style.NOTICE(f'Starting backup of database "{db_name}"...'))
            
            # Execute mysqldump and save to file
            with open(backup_file, 'w') as f:
                result = subprocess.run(
                    dump_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )

            # Verify backup file was created
            if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
                file_size = os.path.getsize(backup_file) / (1024 * 1024)  # MB
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Backup completed successfully!\n'
                        f'  File: {backup_file}\n'
                        f'  Size: {file_size:.2f} MB'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Backup file was not created or is empty')
                )

        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Backup failed: {e.stderr}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Unexpected error: {str(e)}'
                )
            )
