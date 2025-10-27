from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Equipment(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Maintenance(models.Model):
    MAINTENANCE_TYPES = [
        ('computer', 'Rutina Mantenimiento Preventivo de Equipos de Cómputo'),
        ('printer_scanner', 'Rutina de Mantenimiento Preventivo para Impresoras y Escáner'),
    ]

    equipment = models.ForeignKey(Equipment, related_name='maintenances', on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES, default='computer')
    description = models.TextField()
    maintenance_date = models.DateField()
    performed_by = models.CharField(max_length=100)
    sede = models.CharField(max_length=100, blank=True, null=True)
    dependencia = models.CharField(max_length=100, blank=True, null=True)
    oficina = models.CharField(max_length=100, blank=True, null=True)
    placa = models.CharField(max_length=100, blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_final = models.TimeField(blank=True, null=True)
    activities = models.JSONField(default=dict, blank=True, null=True)  # For checklist activities
    observaciones_generales = models.TextField(blank=True, null=True)
    observaciones_seguridad = models.TextField(blank=True, null=True)
    calificacion_servicio = models.CharField(max_length=20, choices=[
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
    ], blank=True, null=True)
    observaciones_usuario = models.TextField(blank=True, null=True)
    is_incident = models.BooleanField(default=False, help_text="Marcar si es una incidencia (ej. operador no permite mantenimiento)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Maintenance for {self.equipment.code} on {self.maintenance_date}"

class Photo(models.Model):
    maintenance = models.ForeignKey(Maintenance, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='maintenance_photos/')
    thumbnail = models.ImageField(upload_to='maintenance_photos/thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for maintenance {self.maintenance.id}"
    
    def save(self, *args, **kwargs):
        # Ensure we use MinIO storage for photos
        if not self.image.storage or self.image.storage.__class__.__name__ != 'MaintenancePhotoStorage':
            from core.storage import MaintenancePhotoStorage
            self.image.storage = MaintenancePhotoStorage()
        if self.thumbnail and (not self.thumbnail.storage or self.thumbnail.storage.__class__.__name__ != 'MaintenanceThumbnailStorage'):
            from core.storage import MaintenanceThumbnailStorage
            self.thumbnail.storage = MaintenanceThumbnailStorage()
        super().save(*args, **kwargs)

class Signature(models.Model):
    maintenance = models.OneToOneField(Maintenance, related_name='signature', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='maintenance_signatures/')
    thumbnail = models.ImageField(upload_to='maintenance_signatures/thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signature for maintenance {self.maintenance.id}"

    def save(self, *args, **kwargs):
        # Ensure we use MinIO storage for signatures
        if not self.image.storage or self.image.storage.__class__.__name__ != 'MaintenanceSignatureStorage':
            from core.storage import MaintenanceSignatureStorage
            self.image.storage = MaintenanceSignatureStorage()
        if self.thumbnail and (not self.thumbnail.storage or self.thumbnail.storage.__class__.__name__ != 'MaintenanceThumbnailStorage'):
            from core.storage import MaintenanceThumbnailStorage
            self.thumbnail.storage = MaintenanceThumbnailStorage()
        super().save(*args, **kwargs)

class SecondSignature(models.Model):
    maintenance = models.OneToOneField(Maintenance, related_name='second_signature', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='maintenance_second_signatures/')
    thumbnail = models.ImageField(upload_to='maintenance_second_signatures/thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Second signature for maintenance {self.maintenance.id}"

    def save(self, *args, **kwargs):
        # Ensure we use MinIO storage for second signatures
        if not self.image.storage or self.image.storage.__class__.__name__ != 'MaintenanceSecondSignatureStorage':
            from core.storage import MaintenanceSecondSignatureStorage
            self.image.storage = MaintenanceSecondSignatureStorage()
        if self.thumbnail and (not self.thumbnail.storage or self.thumbnail.storage.__class__.__name__ != 'MaintenanceThumbnailStorage'):
            from core.storage import MaintenanceThumbnailStorage
            self.thumbnail.storage = MaintenanceThumbnailStorage()
        super().save(*args, **kwargs)

class Report(models.Model):
    maintenance = models.OneToOneField(Maintenance, related_name='report', on_delete=models.SET_NULL, null=True)
    generated_by = models.ForeignKey(User, related_name='generated_reports', on_delete=models.SET_NULL, null=True)
    report_data = models.JSONField(default=dict)
    pdf_file = models.FileField(upload_to='maintenance_reports/', storage='core.storage.MaintenanceReportStorage')
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)
    file_size = models.PositiveIntegerField()  # Size in bytes

    def __str__(self):
        return f"Report for maintenance {self.maintenance.id if self.maintenance else 'None'}"

    def save(self, *args, **kwargs):
        # Ensure we use MinIO storage for reports
        if not self.pdf_file.storage or self.pdf_file.storage.__class__.__name__ != 'MaintenanceReportStorage':
            from core.storage import MaintenanceReportStorage
            self.pdf_file.storage = MaintenanceReportStorage()
        super().save(*args, **kwargs)

    def get_pdf_file_storage(self):
        if not self.pdf_file.storage or self.pdf_file.storage.__class__.__name__ != 'MaintenanceReportStorage':
            from core.storage import MaintenanceReportStorage
            return MaintenanceReportStorage()
        return self.pdf_file.storage

class AuditLog(models.Model):
    ACTIONS = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTIONS)
    model = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.model} {self.object_id} at {self.timestamp}"
