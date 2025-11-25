from django.db import models
import os
import re
import unicodedata
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Sede(models.Model):
    """Modelo para gestionar las sedes de la alcaldía"""
    nombre = models.CharField(max_length=255, unique=True)
    direccion = models.CharField(max_length=500, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    codigo = models.CharField(max_length=50, unique=True, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sede'
        ordering = ['nombre']
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'

    def __str__(self):
        return self.nombre


class Dependencia(models.Model):
    """Modelo para gestionar las dependencias asociadas a una sede"""
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='dependencias')
    nombre = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, null=True, blank=True)
    responsable = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dependencia'
        ordering = ['nombre']
        verbose_name = 'Dependencia'
        verbose_name_plural = 'Dependencias'
        unique_together = ['sede', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.sede.nombre}"


class Subdependencia(models.Model):
    """Modelo para gestionar las subdependencias asociadas a una dependencia"""
    dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE, related_name='subdependencias')
    nombre = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, null=True, blank=True)
    responsable = models.CharField(max_length=255, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subdependencia'
        ordering = ['nombre']
        verbose_name = 'Subdependencia'
        verbose_name_plural = 'Subdependencias'
        unique_together = ['dependencia', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.dependencia.nombre}"


class Equipment(models.Model):
    code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    
    # Campo legacy (mantener durante migración)
    dependencia = models.CharField(max_length=255, null=True, blank=True, db_column='dependencia_legacy')
    
    # Nuevos campos de relaciones jerárquicas
    sede_rel = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipments')
    dependencia_rel = models.ForeignKey(Dependencia, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipments')
    subdependencia = models.ForeignKey(Subdependencia, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipments')
    
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.serial_number or 'N/A'})"


class Maintenance(models.Model):
    MAINTENANCE_TYPES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('predictivo', 'Predictivo'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenances')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    scheduled_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances')
    description = models.TextField(blank=True, default='')
    observations = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campos adicionales para el formato
    codigo = models.CharField(max_length=50, null=True, blank=True)
    version = models.CharField(max_length=20, null=True, blank=True)
    vigencia = models.DateField(null=True, blank=True)
    
    # Relaciones jerárquicas
    sede_rel = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances')
    dependencia_rel = models.ForeignKey(Dependencia, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances')
    subdependencia = models.ForeignKey(Subdependencia, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances')
    
    # Campos legacy para migración
    dependencia = models.CharField(max_length=255, null=True, blank=True)
    ubicacion = models.CharField(max_length=255, null=True, blank=True)
    sede = models.CharField(max_length=255, null=True, blank=True)

    # Campos del formulario
    oficina = models.CharField(max_length=255, null=True, blank=True)
    placa = models.CharField(max_length=100, null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_final = models.TimeField(null=True, blank=True)
    activities = models.JSONField(default=dict, blank=True)
    observaciones_generales = models.TextField(blank=True, default='')
    observaciones_seguridad = models.TextField(blank=True, default='')
    calificacion_servicio = models.CharField(max_length=20, null=True, blank=True)
    observaciones_usuario = models.TextField(blank=True, default='')
    is_incident = models.BooleanField(default=False)
    incident_notes = models.TextField(blank=True, default='')
    equipment_type = models.CharField(max_length=20, default='computer')

    # Firmas
    elaborado_por = models.CharField(max_length=255, null=True, blank=True)
    elaborado_firma = models.ImageField(upload_to='signatures/', null=True, blank=True)
    revisado_por = models.CharField(max_length=255, null=True, blank=True)
    revisado_firma = models.ImageField(upload_to='signatures/', null=True, blank=True)
    aprobado_por = models.CharField(max_length=255, null=True, blank=True)
    aprobado_firma = models.ImageField(upload_to='signatures/', null=True, blank=True)

    class Meta:
        db_table = 'maintenance'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.equipment.name} - {self.get_maintenance_type_display()} - {self.scheduled_date}"


class Photo(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='maintenance_photos/')
    caption = models.CharField(max_length=255, blank=True, default='')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'maintenance_photo'
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Photo for {self.maintenance} - {self.caption or 'No caption'}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, default='', blank=True)
    changes = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.user or 'Unknown'}"


class ReportTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    header_config = models.JSONField(default=dict, blank=True)
    footer_config = models.JSONField(default=dict, blank=True)
    logo = models.ImageField(upload_to='report_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'report_template'
        ordering = ['name']

    def __str__(self):
        return self.name


class Template(models.Model):
    TEMPLATE_TYPES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True)

    # For HTML-based templates
    html_content = models.TextField(blank=True, help_text="HTML template with Django template variables")
    css_content = models.TextField(blank=True, help_text="Optional CSS for the template")

    # Optional uploaded file (e.g., base xlsx or pdf)
    # Normalize filenames on upload to avoid unexpected tokens / unsafe chars
    def _normalize_filename(filename: str) -> str:
        """Return a safe, normalized filename.

        - Decode percent-encoding if present
        - Remove diacritics
        - Replace spaces with underscores
        - Remove unsafe characters
        - Strip trailing underscore+token before extension (e.g. `_RibwlEF`)
        """
        try:
            # Take basename
            name = os.path.basename(filename or '')
            # If URL-encoded, decode percent-escapes
            try:
                name = re.sub(r'%20', ' ', name)
                from urllib.parse import unquote

                name = unquote(name)
            except Exception:
                pass

            # Split name and extension
            base, ext = os.path.splitext(name)

            # Strip trailing underscore+token before extension
            base = re.sub(r'_[A-Za-z0-9]+$','', base)

            # Normalize unicode to remove accents
            nkfd = unicodedata.normalize('NFKD', base)
            ascii_base = ''.join([c for c in nkfd if not unicodedata.combining(c)])

            # Replace spaces and unsafe chars with underscore
            ascii_base = re.sub(r'[^A-Za-z0-9._-]+', '_', ascii_base).strip('_')

            # Ensure there's at least something
            if not ascii_base:
                ascii_base = 'file'

            # Lowercase for consistency
            final = f"{ascii_base}{ext}"
            return final
        except Exception:
            return filename

    def _templates_upload_to(instance, filename):
        safe_name = Template._normalize_filename(filename)
        return os.path.join('templates', safe_name)

    template_file = models.FileField(upload_to=_templates_upload_to, blank=True, null=True)

    # Schema of variables expected by the template
    fields_schema = models.JSONField(default=dict, help_text='JSON schema describing template variables')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'template'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.type})"


class Report(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='custom_reports', null=True, blank=True)
    title = models.CharField(max_length=255, default='Reporte sin título')
    content = models.TextField(default='')
    pdf_file = models.FileField(upload_to='reports/', null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report'
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.title} - {self.generated_at}"


class Signature(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='signatures', null=True, blank=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True)
    signer_name = models.CharField(max_length=255, default='Sin nombre')
    signer_role = models.CharField(max_length=100, default='Técnico')
    signature_image = models.ImageField(upload_to='signatures/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='signatures/thumbnails/', null=True, blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'signature'
        ordering = ['signed_at']

    def __str__(self):
        return f"{self.signer_name} - {self.signer_role}"


class SecondSignature(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='second_signatures', null=True, blank=True)
    signer_name = models.CharField(max_length=255, default='Sin nombre')
    signer_role = models.CharField(max_length=100, default='Usuario')
    signature_image = models.ImageField(upload_to='signatures/second/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='signatures/second/thumbnails/', null=True, blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'secondsignature'
        ordering = ['signed_at']

    def __str__(self):
        return f"{self.signer_name} - {self.signer_role} (Second)"


class Incident(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='incidents', db_column='equipment_id', null=True, blank=True)
    maintenance = models.ForeignKey(Maintenance, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_incidents')
    incident_date = models.DateTimeField(default=timezone.now)
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ], default='medium')
    description = models.TextField(default='')
    resolution = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('open', 'Abierto'),
        ('in_progress', 'En Progreso'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado'),
    ], default='open')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'incident'
        ordering = ['-incident_date']

    def __str__(self):
        return f"Incident - {self.equipment.name} - {self.incident_date}"


class SiteConfiguration(models.Model):
    """Singleton-style model to store site-wide configuration as JSON."""
    config = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'site_configuration'

    def __str__(self):
        return 'Site configuration'
