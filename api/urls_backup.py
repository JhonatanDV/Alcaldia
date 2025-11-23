"""
URL patterns for backup/restore endpoints.
"""
from django.urls import path
from .views_backup import (
    create_backup,
    list_backups,
    download_backup,
    restore_backup,
    delete_backup
)

urlpatterns = [
    path('create/', create_backup, name='create-backup'),
    path('list/', list_backups, name='list-backups'),
    path('download/<str:filename>/', download_backup, name='download-backup'),
    path('restore/<str:filename>/', restore_backup, name='restore-backup'),
    path('delete/<str:filename>/', delete_backup, name='delete-backup'),
]
