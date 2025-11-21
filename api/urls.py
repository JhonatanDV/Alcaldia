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

router = DefaultRouter()
router.register('users', UserViewSet)

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
]
