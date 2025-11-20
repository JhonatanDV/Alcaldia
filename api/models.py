from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Equipment(models.Model):
    """Model for equipment/devices"""
    ESTADO_CHOICES = [
        ('OPERATIVO', 'Operativo'),
        ('EN_MANTENIMIENTO', 'En Mantenimiento'),
        ('DAÑADO', 'Dañado'),
        ('FUERA_DE_SERVICIO', 'Fuera de Servicio'),
    ]

    placa = models.CharField(max_length=50, unique=True, verbose_name='Placa')
    tipo = models.CharField(max_length=100, verbose_name='Tipo de Equipo')
    marca = models.CharField(max_length=100, verbose_name='Marca')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    serial = models.CharField(max_length=100, blank=True, null=True, verbose_name='Serial')
    
    # Location
    dependencia = models.CharField(max_length=200, verbose_name='Dependencia')
    sede = models.CharField(max_length=200, blank=True, null=True, verbose_name='Sede')
    oficina = models.CharField(max_length=200, blank=True, null=True, verbose_name='Oficina')
    
    # Status
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='OPERATIVO')
    fecha_adquisicion = models.DateField(blank=True, null=True, verbose_name='Fecha de Adquisición')
    ultimo_mantenimiento = models.DateField(blank=True, null=True, verbose_name='Último Mantenimiento')
    
    # Additional info
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['-created_at']
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return f"{self.placa} - {self.tipo}"


class Maintenance(models.Model):
    """Model for maintenance records"""
    TIPO_MANTENIMIENTO_CHOICES = [
        ('PREVENTIVO', 'Preventivo'),
        ('CORRECTIVO', 'Correctivo'),
        ('PREDICTIVO', 'Predictivo'),
    ]

    equipo = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenances')
    tipo_mantenimiento = models.CharField(max_length=20, choices=TIPO_MANTENIMIENTO_CHOICES)
    fecha_mantenimiento = models.DateField(verbose_name='Fecha de Mantenimiento')
    
    tecnico_responsable = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='maintenances_performed',
        verbose_name='Técnico Responsable'
    )
    
    descripcion_trabajo = models.TextField(verbose_name='Descripción del Trabajo')
    repuestos_utilizados = models.TextField(blank=True, null=True, verbose_name='Repuestos Utilizados')
    costo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Costo')
    
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    proximo_mantenimiento = models.DateField(blank=True, null=True, verbose_name='Próximo Mantenimiento')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'maintenance'
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-fecha_mantenimiento']
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return f"{self.equipo.placa} - {self.tipo_mantenimiento} - {self.fecha_mantenimiento}"


class Incident(models.Model):
    """Model for incident reports"""
    ESTADO_CHOICES = [
        ('REPORTADO', 'Reportado'),
        ('EN_REVISION', 'En Revisión'),
        ('EN_PROCESO', 'En Proceso'),
        ('RESUELTO', 'Resuelto'),
        ('CERRADO', 'Cerrado'),
    ]

    TIPO_INCIDENTE_CHOICES = [
        ('FALLA_HARDWARE', 'Falla de Hardware'),
        ('FALLA_SOFTWARE', 'Falla de Software'),
        ('FALLA_RED', 'Falla de Red'),
        ('OTRO', 'Otro'),
    ]

    equipo = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='incidents')
    tipo_incidente = models.CharField(max_length=50, choices=TIPO_INCIDENTE_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='REPORTADO')
    
    fecha_reporte = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Reporte')
    fecha_resolucion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Resolución')
    
    reportado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='incidents_reported',
        verbose_name='Reportado Por'
    )
    
    asignado_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents_assigned',
        verbose_name='Asignado A'
    )
    
    descripcion = models.TextField(verbose_name='Descripción del Incidente')
    solucion = models.TextField(blank=True, null=True, verbose_name='Solución Aplicada')
    
    prioridad = models.CharField(
        max_length=10,
        choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta'), ('CRITICA', 'Crítica')],
        default='MEDIA'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'incident'
        verbose_name = 'Incidente'
        verbose_name_plural = 'Incidentes'
        ordering = ['-fecha_reporte']
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return f"Incidente {self.id} - {self.equipo.placa} - {self.estado}"


class MaintenanceReport(models.Model):
    """Model for maintenance reports/PDFs"""
    maintenance = models.OneToOneField(
        Maintenance,
        on_delete=models.CASCADE,
        related_name='report'
    )
    
    pdf_file = models.FileField(upload_to='maintenance_reports/', blank=True, null=True)
    codigo_formato = models.CharField(max_length=50, default='GTI-F-015', verbose_name='Código de Formato')
    version = models.CharField(max_length=10, default='01', verbose_name='Versión')
    vigencia = models.DateField(verbose_name='Vigencia')
    
    observaciones_tecnico = models.TextField(blank=True, null=True)
    firma_tecnico = models.ImageField(upload_to='signatures/', blank=True, null=True)
    firma_supervisor = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'maintenance_report'
        verbose_name = 'Reporte de Mantenimiento'
        verbose_name_plural = 'Reportes de Mantenimiento'
        ordering = ['-generated_at']
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return f"Reporte {self.id} - {self.maintenance.equipo.placa}"


class Photo(models.Model):
    """Model for maintenance photos"""
    maintenance = models.ForeignKey(
        Maintenance,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    image = models.ImageField(upload_to='maintenance_photos/')
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'maintenance_photo'
        verbose_name = 'Foto de Mantenimiento'
        verbose_name_plural = 'Fotos de Mantenimiento'
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return f"Foto {self.id} - {self.maintenance.equipo.placa}"


class Signature(models.Model):
    """Model for signatures"""
    maintenance = models.ForeignKey(
        Maintenance,
        on_delete=models.CASCADE,
        related_name='signatures'
    )
    tipo = models.CharField(
        max_length=20,
        choices=[('TECNICO', 'Técnico'), ('SUPERVISOR', 'Supervisor'), ('USUARIO', 'Usuario')]
    )
    firma_imagen = models.ImageField(upload_to='signatures/')
    firmante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'signature'
        verbose_name = 'Firma'
        verbose_name_plural = 'Firmas'
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return f"{self.tipo} - {self.firmante}"


class SecondSignature(models.Model):
    """Model for additional signatures"""
    maintenance = models.ForeignKey(
        Maintenance,
        on_delete=models.CASCADE,
        related_name='second_signatures'
    )
    tipo = models.CharField(max_length=50)
    firma_imagen = models.ImageField(upload_to='signatures/')
    firmante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'second_signature'
        verbose_name = 'Firma Secundaria'
        verbose_name_plural = 'Firmas Secundarias'
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return f"{self.tipo} - {self.firmante}"


class Report(models.Model):
    """Model for general reports"""
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50)
    archivo = models.FileField(upload_to='reports/')
    generado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-fecha_generacion']
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return self.titulo


class AuditLog(models.Model):
    """Model for audit logging"""
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('VIEW', 'Ver'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Usuario')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='Acción')
    model_name = models.CharField(max_length=100, default='Unknown', verbose_name='Modelo')
    object_id = models.IntegerField(verbose_name='ID del Objeto')
    object_repr = models.CharField(max_length=200, verbose_name='Representación del Objeto')
    changes = models.JSONField(blank=True, null=True, verbose_name='Cambios')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Dirección IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora')

    class Meta:
        db_table = 'audit_log'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']
        # Force InnoDB
        db_table_comment = 'ENGINE=InnoDB'

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} ({self.timestamp})"
