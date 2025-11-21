from django.contrib import admin
from .models import (
    Equipment,
    Maintenance,
    MaintenanceTask,
    Photo,
    Signature,
    SecondSignature,
    Report,
    Incident,
    MaintenanceReport,
    AuditLog,
    ReportTemplate,
)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'serial_number', 'brand', 'model', 'location', 'dependencia', 'created_at']
    list_filter = ['brand', 'location', 'dependencia', 'created_at']
    search_fields = ['name', 'serial_number', 'brand', 'model']
    date_hierarchy = 'created_at'


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'maintenance_type', 'scheduled_date', 'status', 'technician', 'cost']
    list_filter = ['maintenance_type', 'status', 'scheduled_date', 'dependencia']
    search_fields = ['equipment__name', 'description', 'codigo']
    date_hierarchy = 'scheduled_date'
    raw_id_fields = ['equipment', 'technician']


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ['maintenance', 'task_description', 'is_completed', 'completed_by', 'order']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['task_description', 'notes']
    raw_id_fields = ['maintenance', 'completed_by']
    ordering = ['maintenance', 'order']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['maintenance', 'caption', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['caption', 'maintenance__equipment__name']
    raw_id_fields = ['maintenance', 'uploaded_by']
    date_hierarchy = 'uploaded_at'


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ['signer_name', 'signer_role', 'maintenance', 'signed_at']
    list_filter = ['signer_role', 'signed_at']
    search_fields = ['signer_name', 'signer_role']
    date_hierarchy = 'signed_at'
    raw_id_fields = ['maintenance', 'equipment']


@admin.register(SecondSignature)
class SecondSignatureAdmin(admin.ModelAdmin):
    list_display = ['signer_name', 'signer_role', 'maintenance', 'signed_at']
    list_filter = ['signer_role', 'signed_at']
    search_fields = ['signer_name', 'signer_role']
    date_hierarchy = 'signed_at'
    raw_id_fields = ['maintenance']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'maintenance', 'generated_by', 'generated_at']
    list_filter = ['generated_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'generated_at'
    raw_id_fields = ['maintenance', 'generated_by']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'severity', 'status', 'incident_date', 'reported_by']
    list_filter = ['severity', 'status', 'incident_date']
    search_fields = ['equipment__name', 'description']
    date_hierarchy = 'incident_date'
    raw_id_fields = ['equipment', 'maintenance', 'reported_by']


@admin.register(MaintenanceReport)
class MaintenanceReportAdmin(admin.ModelAdmin):
    list_display = ['maintenance', 'report_type', 'generated_by', 'generated_at', 'file_size']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['maintenance__equipment__name']
    raw_id_fields = ['maintenance', 'generated_by']
    date_hierarchy = 'generated_at'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'timestamp', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'object_repr', 'model_name']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'timestamp', 'ip_address']


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'
