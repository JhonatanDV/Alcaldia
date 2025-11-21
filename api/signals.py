from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from api.models import Maintenance, Equipment, Incident, AuditLog

@receiver(post_save, sender=Maintenance)
@receiver(post_save, sender=Equipment)
@receiver(post_save, sender=Incident)
def log_save(sender, instance, created, **kwargs):
    """
    Registra creaciones y actualizaciones en el log de auditoría
    """
    action = 'create' if created else 'update'
    content_type = ContentType.objects.get_for_model(sender)

    AuditLog.objects.create(
        model_name=content_type.model,
        object_id=instance.id,
        object_repr=str(instance),
        action=action,
        user=getattr(instance, '_current_user', None),
        changes=getattr(instance, '_change_message', '')
    )

@receiver(post_delete, sender=Maintenance)
@receiver(post_delete, sender=Equipment)
@receiver(post_delete, sender=Incident)
def log_delete(sender, instance, **kwargs):
    """
    Registra eliminaciones en el log de auditoría
    """
    content_type = ContentType.objects.get_for_model(sender)

    AuditLog.objects.create(
        model_name=content_type.model,
        object_id=instance.id,
        object_repr=str(instance),
        action='delete',
        user=getattr(instance, '_current_user', None),
        changes=f'Deleted {sender.__name__}: {str(instance)}'
    )
