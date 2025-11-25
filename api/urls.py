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
from .views_dashboard import FilterOptionsView
from .views_templates import generate_pdf, generate_excel
from importlib import import_module


def lazy_view(module_path, attr_name):
    """Return a view callable that imports `module_path.attr_name` on first call
    and delegates the request to it. This avoids import-time failures during
    Django autoreload when the target module may be in a transient state.
    """
    def _delegate(request, *args, **kwargs):
        module = import_module(module_path)
        view_obj = getattr(module, attr_name)
        # If it's a class-based view, call as_view() to get a callable
        if hasattr(view_obj, 'as_view'):
            view_callable = view_obj.as_view()
        else:
            view_callable = view_obj
        return view_callable(request, *args, **kwargs)

    return _delegate

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
    path('reports/generate/', lazy_view('api.views_template_manager', 'generate_report'), name='generate_report'),
    path('reports/', lazy_view('api.views_template_manager', 'list_reports'), name='list_reports'),
    path('templates/', lazy_view('api.views_template_manager', 'ListTemplatesView'), name='list_templates'),
    path('templates/upload/', lazy_view('api.views_template_manager', 'upload_template'), name='upload_template'),
    path('templates/sample-data/', lazy_view('api.views_template_manager', 'sample_template_data'), name='sample_template_data'),
    path('templates/active/', lazy_view('api.views_template_manager', 'active_template'), name='active_template'),
    # Accept either numeric id or textual key (name/slug). Backend will resolve.
    path('templates/<str:template_key>/', lazy_view('api.views_template_manager', 'get_template'), name='get_template'),
    path('templates/<str:template_key>/generate/', lazy_view('api.views_template_manager', 'generate_from_template'), name='generate_from_template'),
    path('templates/<str:template_key>/update/', lazy_view('api.views_template_manager', 'update_template'), name='update_template'),
    path('templates/<str:template_key>/delete/', lazy_view('api.views_template_manager', 'delete_template'), name='delete_template'),
    path('templates/<str:template_key>/suggest-mappings/', lazy_view('api.views_template_manager', 'suggest_mappings'), name='suggest_mappings'),
    # Dashboard filter options
    path('dashboard/filter-options/', FilterOptionsView.as_view(), name='dashboard-filter-options'),
]
