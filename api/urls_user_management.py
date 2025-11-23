"""
URL patterns for user management endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_user_management import (
    UserManagementViewSet, 
    GroupViewSet, 
    PermissionViewSet,
    RolePermissionsViewSet
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'roles', RolePermissionsViewSet, basename='role-permissions')

urlpatterns = [
    path('', include(router.urls)),
    path('permissions/', PermissionViewSet.as_view({'get': 'list'}), name='permissions-list'),
]
