"""
Django management command for restoring the database from a backup.
"""
import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Restores the MySQL database from a backup file'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Path to the backup SQL file to restore'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm restoration without prompting'
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        confirm = options['confirm']

        # Verify backup file exists
        if not os.path.exists(backup_file):
            self.stdout.write(
                self.style.ERROR(f'✗ Backup file not found: {backup_file}')
            )
            return

        # Get database configuration
        db_config = settings.DATABASES['default']
        db_name = db_config['NAME']
        db_user = db_config['USER']
        db_password = db_config['PASSWORD']
        db_host = db_config['HOST']
        db_port = db_config['PORT']

        # Warning message
        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  WARNING: This will REPLACE the current database "{db_name}"!\n'
                    f'   All current data will be lost.\n'
                    f'   Backup file: {backup_file}\n'
                )
            )
            response = input('Are you sure you want to continue? (yes/no): ')
            if response.lower() != 'yes':
                self.stdout.write(self.style.NOTICE('Restore cancelled.'))
                return

        # Build mysql restore command
        restore_cmd = [
            'mysql',
            '-h', db_host,
            '-P', str(db_port),
            '-u', db_user,
            f'--password={db_password}',
            db_name
        ]

        try:
            self.stdout.write(
                self.style.NOTICE(f'Starting restore of database "{db_name}"...')
            )

            # Execute mysql restore
            with open(backup_file, 'r') as f:
                result = subprocess.run(
                    restore_cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Database restored successfully from {backup_file}'
                )
            )

        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Restore failed: {e.stderr}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Unexpected error: {str(e)}'
                )
            )
