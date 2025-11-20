from django.contrib import admin
from .models import (
    Equipment,
    Maintenance,
    Incident,
    MaintenanceReport,
    Photo,
    Signature,
    SecondSignature,
    Report,
    AuditLog
)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['placa', 'tipo', 'marca', 'modelo', 'dependencia', 'estado']
    list_filter = ['estado', 'tipo', 'dependencia']
    search_fields = ['placa', 'tipo', 'marca', 'modelo', 'serial']


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'tipo_mantenimiento', 'fecha_mantenimiento', 'tecnico_responsable']
    list_filter = ['tipo_mantenimiento', 'fecha_mantenimiento']
    search_fields = ['equipo__placa', 'descripcion_trabajo']
    date_hierarchy = 'fecha_mantenimiento'


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'tipo_incidente', 'estado', 'prioridad', 'fecha_reporte', 'reportado_por']
    list_filter = ['estado', 'tipo_incidente', 'prioridad']
    search_fields = ['equipo__placa', 'descripcion']
    date_hierarchy = 'fecha_reporte'


@admin.register(MaintenanceReport)
class MaintenanceReportAdmin(admin.ModelAdmin):
    list_display = ['maintenance', 'codigo_formato', 'version', 'generated_at', 'generated_by']
    list_filter = ['generated_at', 'codigo_formato']
    date_hierarchy = 'generated_at'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['maintenance', 'descripcion', 'uploaded_at']
    list_filter = ['uploaded_at']


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ['maintenance', 'tipo', 'firmante', 'fecha']
    list_filter = ['tipo', 'fecha']


@admin.register(SecondSignature)
class SecondSignatureAdmin(admin.ModelAdmin):
    list_display = ['maintenance', 'tipo', 'firmante', 'fecha']
    list_filter = ['tipo', 'fecha']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'generado_por', 'fecha_generacion']
    list_filter = ['tipo', 'fecha_generacion']
    search_fields = ['titulo']
    date_hierarchy = 'fecha_generacion'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'timestamp', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'object_repr', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr', 
                       'changes', 'ip_address', 'user_agent', 'timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
