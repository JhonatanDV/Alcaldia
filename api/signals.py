from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import json
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

from .models import Equipment, Maintenance, Photo, Signature, AuditLog


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(pre_save, sender=Equipment)
@receiver(pre_save, sender=Maintenance)
@receiver(pre_save, sender=Photo)
def store_original_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_values = {}
            for field in instance._meta.fields:
                instance._original_values[field.name] = getattr(original, field.name)
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=Equipment)
def equipment_post_save(sender, instance, created, **kwargs):
    """Log equipment creation/update"""
    action = 'CREATE' if created else 'UPDATE'
    
    # Get request from thread local if available
    request = getattr(instance, '_request', None)
    user = request.user if request and hasattr(request, 'user') else None
    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
    
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name='Equipment',
        object_id=instance.id,
        object_repr=str(instance),
        ip_address=ip_address,
        user_agent=user_agent,
    )


@receiver(post_delete, sender=Equipment)
def equipment_post_delete(sender, instance, **kwargs):
    """Log equipment deletion"""
    request = getattr(instance, '_request', None)
    user = request.user if request and hasattr(request, 'user') else None
    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
    
    AuditLog.objects.create(
        user=user,
        action='DELETE',
        model_name='Equipment',
        object_id=instance.id,
        object_repr=str(instance),
        ip_address=ip_address,
        user_agent=user_agent,
    )


@receiver(post_save, sender=Maintenance)
def maintenance_post_save(sender, instance, created, **kwargs):
    """Log maintenance creation/update and update equipment last maintenance date"""
    action = 'CREATE' if created else 'UPDATE'
    
    request = getattr(instance, '_request', None)
    user = request.user if request and hasattr(request, 'user') else None
    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
    
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name='Maintenance',
        object_id=instance.id,
        object_repr=str(instance),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Update equipment last maintenance date
    if instance.equipo:
        instance.equipo.ultimo_mantenimiento = instance.fecha_mantenimiento
        instance.equipo.save(update_fields=['ultimo_mantenimiento'])


@receiver(post_delete, sender=Maintenance)
def maintenance_post_delete(sender, instance, **kwargs):
    """Log maintenance deletion"""
    request = getattr(instance, '_request', None)
    user = request.user if request and hasattr(request, 'user') else None
    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
    
    AuditLog.objects.create(
        user=user,
        action='DELETE',
        model_name='Maintenance',
        object_id=instance.id,
        object_repr=str(instance),
        ip_address=ip_address,
        user_agent=user_agent,
    )


@receiver(post_save, sender=Photo)
def photo_post_save(sender, instance, created, **kwargs):
    """Log photo upload"""
    if created:
        request = getattr(instance, '_request', None)
        user = request.user if request and hasattr(request, 'user') else None
        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
        
        AuditLog.objects.create(
            user=user,
            action='CREATE',
            model_name='Photo',
            object_id=instance.id,
            object_repr=str(instance),
            ip_address=ip_address,
            user_agent=user_agent,
        )


@receiver(post_save, sender=Signature)
def signature_post_save(sender, instance, created, **kwargs):
    """Log signature creation"""
    if created:
        request = getattr(instance, '_request', None)
        user = request.user if request and hasattr(request, 'user') else None
        ip_address = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None
        
        AuditLog.objects.create(
            user=user,
            action='CREATE',
            model_name='Signature',
            object_id=instance.id,
            object_repr=str(instance),
            ip_address=ip_address,
            user_agent=user_agent,
        )
