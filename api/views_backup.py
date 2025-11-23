"""
Views for database backup and restore operations.
"""
import os
import subprocess
from datetime import datetime
from django.conf import settings
from django.http import FileResponse, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdmin


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def create_backup(request):
    """
    Create a database backup and return information about it.
    """
    try:
        # Get database configuration
        db_config = settings.DATABASES['default']
        db_name = db_config['NAME']
        db_user = db_config['USER']
        db_password = db_config['PASSWORD']
        db_host = db_config['HOST']
        db_port = db_config['PORT']

        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{db_name}_{timestamp}.sql'
        backup_file = os.path.join(backup_dir, backup_filename)

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

        # Execute mysqldump
        with open(backup_file, 'w') as f:
            subprocess.run(
                dump_cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

        # Verify backup was created
        if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
            file_size = os.path.getsize(backup_file)
            return Response({
                'success': True,
                'message': 'Backup created successfully',
                'filename': backup_filename,
                'size': file_size,
                'created_at': timestamp
            })
        else:
            return Response({
                'success': False,
                'error': 'Backup file was not created or is empty'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except subprocess.CalledProcessError as e:
        return Response({
            'success': False,
            'error': f'Backup failed: {e.stderr}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def list_backups(request):
    """
    List all available backup files.
    """
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        if not os.path.exists(backup_dir):
            return Response({'backups': []})

        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.sql'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })

        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)

        return Response({'backups': backups})
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def download_backup(request, filename):
    """
    Download a specific backup file.
    """
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_file = os.path.join(backup_dir, filename)

        # Security: prevent directory traversal
        if not os.path.abspath(backup_file).startswith(os.path.abspath(backup_dir)):
            return Response({
                'error': 'Invalid filename'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not os.path.exists(backup_file):
            return Response({
                'error': 'Backup file not found'
            }, status=status.HTTP_404_NOT_FOUND)

        response = FileResponse(
            open(backup_file, 'rb'),
            content_type='application/sql',
            as_attachment=True,
            filename=filename
        )
        return response
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def restore_backup(request, filename):
    """
    Restore database from a backup file.
    """
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_file = os.path.join(backup_dir, filename)

        # Security: prevent directory traversal
        if not os.path.abspath(backup_file).startswith(os.path.abspath(backup_dir)):
            return Response({
                'error': 'Invalid filename'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not os.path.exists(backup_file):
            return Response({
                'error': 'Backup file not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get database configuration
        db_config = settings.DATABASES['default']
        db_name = db_config['NAME']
        db_user = db_config['USER']
        db_password = db_config['PASSWORD']
        db_host = db_config['HOST']
        db_port = db_config['PORT']

        # Build mysql restore command
        restore_cmd = [
            'mysql',
            '-h', db_host,
            '-P', str(db_port),
            '-u', db_user,
            f'--password={db_password}',
            db_name
        ]

        # Execute restore
        with open(backup_file, 'r') as f:
            subprocess.run(
                restore_cmd,
                stdin=f,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

        return Response({
            'success': True,
            'message': f'Database restored successfully from {filename}'
        })

    except subprocess.CalledProcessError as e:
        return Response({
            'success': False,
            'error': f'Restore failed: {e.stderr}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_backup(request, filename):
    """
    Delete a backup file.
    """
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_file = os.path.join(backup_dir, filename)

        # Security: prevent directory traversal
        if not os.path.abspath(backup_file).startswith(os.path.abspath(backup_dir)):
            return Response({
                'error': 'Invalid filename'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not os.path.exists(backup_file):
            return Response({
                'error': 'Backup file not found'
            }, status=status.HTTP_404_NOT_FOUND)

        os.remove(backup_file)

        return Response({
            'success': True,
            'message': f'Backup {filename} deleted successfully'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
