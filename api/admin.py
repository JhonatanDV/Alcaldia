from django.contrib import admin
from .models import Equipment, Maintenance, Photo, Signature, SecondSignature, Report, AuditLog

# Register your models here.
admin.site.register(Equipment)
admin.site.register(Maintenance)
admin.site.register(Photo)
admin.site.register(Signature)
admin.site.register(SecondSignature)
admin.site.register(Report)
admin.site.register(AuditLog)

# Customize Maintenance admin to show incident flag
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'maintenance_date', 'performed_by', 'is_incident', 'created_at')
    list_filter = ('is_incident', 'maintenance_type', 'maintenance_date')
    search_fields = ('equipment__code', 'equipment__name', 'performed_by')

admin.site.unregister(Maintenance)
admin.site.register(Maintenance, MaintenanceAdmin)
