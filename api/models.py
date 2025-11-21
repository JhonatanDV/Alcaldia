from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Equipment(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    dependencia = models.CharField(max_length=255, null=True, blank=True)
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
    dependencia = models.CharField(max_length=255, null=True, blank=True)
    ubicacion = models.CharField(max_length=255, null=True, blank=True)
    
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


class MaintenanceTask(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='tasks')
    task_description = models.TextField()
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'maintenance_task'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Task for {self.maintenance} - {self.task_description[:50]}"


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


class MaintenanceReport(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='reports')
    report_file = models.FileField(upload_to='maintenance_reports/')
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_type = models.CharField(max_length=50, default='standard')
    file_size = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'maintenance_report'
        ordering = ['-generated_at']

    def __str__(self):
        return f"Report for {self.maintenance} - {self.generated_at}"


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


class Report(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='custom_reports')
    title = models.CharField(max_length=255)
    content = models.TextField()
    pdf_file = models.FileField(upload_to='reports/', null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report'
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.title} - {self.generated_at}"


class Signature(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='signatures')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True)
    signer_name = models.CharField(max_length=255)
    signer_role = models.CharField(max_length=100)
    signature_image = models.ImageField(upload_to='signatures/')
    thumbnail = models.ImageField(upload_to='signatures/thumbnails/', null=True, blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'signature'
        ordering = ['signed_at']

    def __str__(self):
        return f"{self.signer_name} - {self.signer_role}"


class SecondSignature(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='second_signatures')
    signer_name = models.CharField(max_length=255)
    signer_role = models.CharField(max_length=100)
    signature_image = models.ImageField(upload_to='signatures/second/')
    thumbnail = models.ImageField(upload_to='signatures/second/thumbnails/', null=True, blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'secondsignature'
        ordering = ['signed_at']

    def __str__(self):
        return f"{self.signer_name} - {self.signer_role} (Second)"


class Incident(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='incidents', db_column='equipment_id')
    maintenance = models.ForeignKey(Maintenance, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_incidents')
    incident_date = models.DateTimeField()
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ], default='medium')
    description = models.TextField()
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
