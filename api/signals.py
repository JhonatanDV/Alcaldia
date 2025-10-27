from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from .models import Equipment, Maintenance, Photo, Signature, AuditLog

User = get_user_model()

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
@receiver(post_save, sender=Maintenance)
@receiver(post_save, sender=Photo)
def audit_log_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    model_name = sender.__name__
    user = getattr(instance, '_audit_user', None)
    changes = None
    if not created and hasattr(instance, '_original_values'):
        changes = {}
        for field in instance._meta.fields:
            field_name = field.name
            if field_name in instance._original_values:
                old_value = str(instance._original_values[field_name])
                new_value = str(getattr(instance, field_name))
                if old_value != new_value:
                    changes[field_name] = {'old': old_value, 'new': new_value}
    AuditLog.objects.create(
        user=user,
        action=action,
        model=model_name,
        object_id=instance.pk,
        changes=changes
    )

@receiver(post_save, sender=Photo)
def create_photo_thumbnail(sender, instance, created, **kwargs):
    if created and instance.image:
        try:
            image = Image.open(instance.image.path)
            image.thumbnail((200, 200))
            thumb_io = BytesIO()
            image.save(thumb_io, format=image.format)
            thumb_io.seek(0)
            thumb_name = f"thumb_{instance.image.name.split('/')[-1]}"
            instance.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
            instance.save(update_fields=['thumbnail'])
        except Exception:
            # Skip thumbnail creation if image processing fails
            pass

@receiver(post_save, sender=Signature)
def create_signature_thumbnail(sender, instance, created, **kwargs):
    if created and instance.image:
        try:
            image = Image.open(instance.image.path)
            image.thumbnail((200, 200))
            thumb_io = BytesIO()
            image.save(thumb_io, format=image.format)
            thumb_io.seek(0)
            thumb_name = f"thumb_{instance.image.name.split('/')[-1]}"
            instance.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
            instance.save(update_fields=['thumbnail'])
        except Exception:
            # Skip thumbnail creation if image processing fails
            pass

@receiver(post_delete, sender=Equipment)
@receiver(post_delete, sender=Maintenance)
@receiver(post_delete, sender=Photo)
def audit_log_delete(sender, instance, **kwargs):
    model_name = sender.__name__
    user = getattr(instance, '_audit_user', None)
    AuditLog.objects.create(
        user=user,
        action='DELETE',
        model=model_name,
        object_id=instance.pk
    )
