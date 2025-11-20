from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
from api.views import EquipmentViewSet, MaintenanceViewSet, ReportListView, ReportGenerateView
from api.views_auth import LogoutView
from api.views_admin import (
    UserAdminViewSet, GroupAdminViewSet, 
    current_user_profile, update_user_profile, change_own_password
)
from api.views_dashboard import dashboard_stats, dashboard_equipment_stats, dashboard_maintenance_timeline
from api import views_reports
from api.views_package import package_reports, package_reports_by_filter, package_info
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import AuditLog
from django.contrib.auth.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs_view(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    data = [
        {
            'user': log.user.username if log.user else 'Anonymous',
            'action': log.action,
            'model': log.model,
            'object_id': log.object_id,
            'timestamp': log.timestamp,
            'changes': log.changes
        } for log in logs
    ]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    user = request.user
    groups = list(user.groups.values_list('name', flat=True))
    return Response({
        'id': user.id,
        'username': user.username,
        'groups': groups
    })

router = routers.DefaultRouter()
router.register(r'equipments', EquipmentViewSet)
router.register(r'maintenances', MaintenanceViewSet)
router.register(r'admin/users', UserAdminViewSet, basename='admin-users')
router.register(r'admin/groups', GroupAdminViewSet, basename='admin-groups')

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/user-info/', user_info_view, name='user-info'),
    
    # User profile
    path('api/profile/', current_user_profile, name='current-user-profile'),
    path('api/profile/update/', update_user_profile, name='update-user-profile'),
    path('api/profile/change-password/', change_own_password, name='change-own-password'),
    
    # Dashboard
    path('api/dashboard/', dashboard_stats, name='dashboard-stats'),
    path('api/dashboard/equipment/', dashboard_equipment_stats, name='dashboard-equipment'),
    path('api/dashboard/timeline/', dashboard_maintenance_timeline, name='dashboard-timeline'),
    
    # Audit logs
    path('api/audit-logs/', audit_logs_view, name='audit-logs'),
    
    # Reports - Basic
    path('api/reports/', ReportListView.as_view(), name='reports'),
    path('api/reports/generate/', ReportGenerateView.as_view(), name='reports-generate'),
    
    # Reports - Advanced endpoints from views_reports.py
    path('api/reports/maintenance/<int:maintenance_id>/', 
         views_reports.generate_maintenance_report_default, 
         name='generate-maintenance-report'),
    path('api/reports/maintenance/<int:maintenance_id>/custom/', 
         views_reports.generate_maintenance_report_custom, 
         name='generate-maintenance-report-custom'),
    path('api/reports/maintenance/<int:maintenance_id>/download/', 
         views_reports.download_maintenance_report, 
         name='download-maintenance-report'),
    path('api/reports/maintenance/<int:maintenance_id>/preview/', 
         views_reports.preview_maintenance_report, 
         name='preview-maintenance-report'),
    path('api/reports/batch/', 
         views_reports.batch_generate_reports, 
         name='batch-generate-reports'),
    path('api/reports/computer/<int:maintenance_id>/', 
         views_reports.generate_computer_maintenance_report, 
         name='generate-computer-report'),
    path('api/reports/printer-scanner/<int:maintenance_id>/', 
         views_reports.generate_printer_scanner_report, 
         name='generate-printer-scanner-report'),
    
    # Reports - Packaging (ZIP)
    path('api/reports/package/', package_reports, name='package-reports'),
    path('api/reports/package/filter/', package_reports_by_filter, name='package-reports-filter'),
    path('api/reports/package/info/', package_info, name='package-info'),
    
    # Router URLs (equipments, maintenances, admin/users, admin/groups)
    path('api/', include(router.urls)),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
