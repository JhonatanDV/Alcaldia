from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Photo

def validate_file_size(value):
    """Validate file size (max 5MB)."""
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if value.size > max_size:
        raise ValidationError(_('File size cannot exceed 5MB.'))

def validate_file_type(value):
    """Validate file type (images only)."""
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if hasattr(value, 'content_type') and value.content_type not in allowed_types:
        raise ValidationError(_('Only image files (JPEG, PNG, GIF, WebP) are allowed.'))

def validate_photo_limit(maintenance):
    """Validate photo limit per maintenance (max 10)."""
    if maintenance.photos.count() >= 10:
        raise ValidationError(_('Maximum 10 photos allowed per maintenance.'))

def validate_signature_required(maintenance):
    """Validate that signature is required for certain maintenance types."""
    # Example: require signature for critical maintenances
    if 'critical' in maintenance.description.lower() and not hasattr(maintenance, 'signature'):
        raise ValidationError(_('Signature is required for critical maintenances.'))

def validate_maintenance_date(value):
    """Validate maintenance date is not in the future."""
    from django.utils import timezone
    if value > timezone.now().date():
        raise ValidationError(_('Maintenance date cannot be in the future.'))

def validate_equipment_code(value):
    """Validate equipment code format."""
    import re
    if not re.match(r'^[A-Z]{2}\d{4}$', value):
        raise ValidationError(_('Equipment code must be in format AA1234 (2 letters + 4 digits).'))
