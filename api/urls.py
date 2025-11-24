from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views_auth import CustomTokenObtainPairView
from .views import (
    UserInfoView,
    DashboardView,
    DashboardEquipmentView
)
from .views_dashboard import (
    DashboardStatsView,
    DashboardChartsView,
    DashboardRecentActivityView,
    DashboardDepartmentStatsView
)
from .views_templates import generate_pdf, generate_excel
from .views_template_manager import (
    upload_template,
    list_templates,
    get_template,
    generate_from_template,
    update_template,
    delete_template,
    sample_template_data,
)

from .views_user_management import UserManagementViewSet

router = DefaultRouter()
router.register('users', UserManagementViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/equipment/', DashboardEquipmentView.as_view(), name='dashboard-equipment'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/charts/', DashboardChartsView.as_view(), name='dashboard-charts'),
    path('dashboard/recent-activity/', DashboardRecentActivityView.as_view(), name='dashboard-recent-activity'),
    path('dashboard/department-stats/', DashboardDepartmentStatsView.as_view(), name='dashboard-department-stats'),
    path('generate-excel/', generate_excel, name='generate-excel'),
    path('generate-pdf/', generate_pdf, name='generate-pdf'),
    path('templates/', list_templates, name='list_templates'),
    path('templates/upload/', upload_template, name='upload_template'),
    path('templates/sample-data/', sample_template_data, name='sample_template_data'),
    path('templates/<int:template_id>/', get_template, name='get_template'),
    path('templates/<int:template_id>/generate/', generate_from_template, name='generate_from_template'),
    path('templates/<int:template_id>/update/', update_template, name='update_template'),
    path('templates/<int:template_id>/delete/', delete_template, name='delete_template'),
]
