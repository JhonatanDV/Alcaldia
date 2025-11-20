"""
URL patterns for user management endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_user_management import UserManagementViewSet, GroupViewSet

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')

urlpatterns = [
    path('', include(router.urls)),
]
