from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers
from api.views import EquipmentViewSet, MaintenanceViewSet, ReportListView, ReportGenerateView
from api.views_auth import LogoutView, CustomTokenObtainPairView
from api.views_test_auth import TestAuthView, TestPublicView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import AuditLog
from api.views_user_management import PermissionViewSet
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/test/auth/', TestAuthView.as_view(), name='test-auth'),
    path('api/test/public/', TestPublicView.as_view(), name='test-public'),
    path('api/user-info/', user_info_view, name='user-info'),
    path('api/audit-logs/', audit_logs_view, name='audit-logs'),
    # Direct legacy route for permissions used by frontend
    path('api/permissions/', PermissionViewSet.as_view({'get': 'list'}), name='permissions-direct'),
    path('api/reports/', ReportListView.as_view(), name='reports'),
    path('api/reports/generate/', ReportGenerateView.as_view(), name='reports-generate'),
    path('api/', include(router.urls)),
    # Include main API url mappings (templates, template manager, etc.)
    path('api/', include('api.urls')),
    path('api/dashboard/', include('api.urls_dashboard')),
    path('api/admin/', include('api.urls_user_management')),
    # Alias path for legacy frontend routes expecting /api/user-management/
    path('api/user-management/', include('api.urls_user_management')),
    path('api/pdf-package/', include('api.urls_pdf_package')),
    path('api/config/', include('api.urls_config')),  # Nuevas rutas para configuración
    path('api/backups/', include('api.urls_backup')),  # Rutas para backup/restore
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
