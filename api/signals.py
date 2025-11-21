from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import json

from .models import (
    Equipment,
    Maintenance,
    Photo,
    AuditLog
)


def get_model_changes(instance, created=False):
    """Capture changes made to a model instance"""
    if created:
        return {'created': True}
    
    changes = {}
    if hasattr(instance, '_original_state'):
        for field in instance._meta.fields:
            field_name = field.name
            old_value = instance._original_state.get(field_name)
            new_value = getattr(instance, field_name)
            
            if old_value != new_value:
                changes[field_name] = {
                    'old': str(old_value) if old_value is not None else None,
                    'new': str(new_value) if new_value is not None else None
                }
    
    return changes


@receiver(pre_save, sender=Equipment)
@receiver(pre_save, sender=Maintenance)
def store_original_state(sender, instance, **kwargs):
    """Store original state before save"""
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_state = {
                field.name: getattr(original, field.name)
                for field in sender._meta.fields
            }
        except sender.DoesNotExist:
            instance._original_state = {}
    else:
        instance._original_state = {}


@receiver(post_save, sender=Equipment)
def log_equipment_changes(sender, instance, created, **kwargs):
    """Log equipment create/update actions"""
    action = 'create' if created else 'update'
    changes = get_model_changes(instance, created)
    
    AuditLog.objects.create(
        user=getattr(instance, '_current_user', None),
        action=action,
        model_name='Equipment',
        object_id=instance.pk,
        object_repr=str(instance),
        changes=changes,
        ip_address=getattr(instance, '_current_ip', None)
    )


@receiver(post_save, sender=Maintenance)
def log_maintenance_changes(sender, instance, created, **kwargs):
    """Log maintenance create/update actions"""
    action = 'create' if created else 'update'
    changes = get_model_changes(instance, created)
    
    AuditLog.objects.create(
        user=getattr(instance, '_current_user', None),
        action=action,
        model_name='Maintenance',
        object_id=instance.pk,
        object_repr=str(instance),
        changes=changes,
        ip_address=getattr(instance, '_current_ip', None)
    )


@receiver(post_save, sender=Photo)
def log_photo_upload(sender, instance, created, **kwargs):
    """Log photo upload actions"""
    if created:
        AuditLog.objects.create(
            user=instance.uploaded_by,
            action='upload_photo',
            model_name='Photo',
            object_id=instance.pk,
            object_repr=str(instance),
            changes={'photo': str(instance.photo)},
            ip_address=getattr(instance, '_current_ip', None)
        )


@receiver(post_delete, sender=Equipment)
@receiver(post_delete, sender=Maintenance)
@receiver(post_delete, sender=Photo)
def log_deletion(sender, instance, **kwargs):
    """Log deletion actions"""
    AuditLog.objects.create(
        user=getattr(instance, '_current_user', None),
        action='delete',
        model_name=sender.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        changes={'deleted': True},
        ip_address=getattr(instance, '_current_ip', None)
    )


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Log user create/update actions"""
    # Skip logging if tables don't exist yet (during migrations)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'audit_log'")
        if not cursor.fetchone():
            return
    
    action = 'create_user' if created else 'update_user'
    changes = get_model_changes(instance, created)
    
    # Don't log password changes
    if 'password' in changes:
        changes['password'] = {'old': '***', 'new': '***'}
    
    AuditLog.objects.create(
        user=getattr(instance, '_current_user', None),
        action=action,
        model_name='User',
        object_id=instance.pk,
        object_repr=str(instance),
        changes=changes,
        ip_address=getattr(instance, '_current_ip', None)
    )
