"""
URL patterns for dashboard API endpoints.
"""

from django.urls import path
from .views_dashboard import (
    DashboardStatsView,
    DashboardChartsView,
    DashboardRecentActivityView,
    DashboardDepartmentStatsView,
)

app_name = 'api_dashboard'

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('charts/', DashboardChartsView.as_view(), name='dashboard-charts'),
    path('recent-activity/', DashboardRecentActivityView.as_view(), name='dashboard-recent-activity'),
    path('department-stats/', DashboardDepartmentStatsView.as_view(), name='dashboard-department-stats'),
]
