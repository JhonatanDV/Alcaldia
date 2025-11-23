"""
User management views for handling users, roles, and permissions from frontend.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .permissions import IsAdmin
from .serializers import UserSerializer, RoleSerializer, UserCreateSerializer, UserUpdateSerializer
from rest_framework import serializers


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users, roles, and permissions.
    """
    queryset = User.objects.all().order_by('username')
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('username')
        # Filter by role if specified
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(groups__name=role)
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change password for a specific user."""
        user = self.get_object()
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({
                'error': 'Both new_password and confirm_password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({
                'error': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({
            'message': 'Password changed successfully'
        })

    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Assign a role (group) to a user."""
        user = self.get_object()
        role_name = request.data.get('role')

        if not role_name:
            return Response({
                'error': 'Role name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return Response({
                'error': f'Role "{role_name}" does not exist'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.groups.add(group)
        user.save()

        return Response({
            'message': f'Role "{role_name}" assigned successfully to user {user.username}'
        })

    @action(detail=True, methods=['post'])
    def remove_role(self, request, pk=None):
        """Remove a role (group) from a user."""
        user = self.get_object()
        role_name = request.data.get('role')

        if not role_name:
            return Response({
                'error': 'Role name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return Response({
                'error': f'Role "{role_name}" does not exist'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.groups.remove(group)
        user.save()

        return Response({
            'message': f'Role "{role_name}" removed successfully from user {user.username}'
        })

    @action(detail=False, methods=['get'])
    def roles(self, request):
        """Get all available roles (groups)."""
        groups = Group.objects.all().order_by('name')
        serializer = RoleSerializer(groups, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_role(self, request):
        """Create a new role (group)."""
        role_name = request.data.get('name')

        if not role_name:
            return Response({
                'error': 'Role name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Group.objects.filter(name=role_name).exists():
            return Response({
                'error': f'Role "{role_name}" already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        group = Group.objects.create(name=role_name)

        return Response({
            'message': f'Role "{role_name}" created successfully',
            'role': RoleSerializer(group).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def delete_role(self, request):
        """Delete a role (group)."""
        role_name = request.data.get('name')

        if not role_name:
            return Response({
                'error': 'Role name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return Response({
                'error': f'Role "{role_name}" does not exist'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if any users are assigned to this role
        if group.user_set.exists():
            return Response({
                'error': f'Cannot delete role "{role_name}" because it is assigned to users'
            }, status=status.HTTP_400_BAD_REQUEST)

        group.delete()

        return Response({
            'message': f'Role "{role_name}" deleted successfully'
        })

    @action(detail=False, methods=['post'])
    def bulk_assign_role(self, request):
        """Assign a role to multiple users."""
        user_ids = request.data.get('user_ids', [])
        role_name = request.data.get('role')

        if not user_ids or not role_name:
            return Response({
                'error': 'user_ids and role are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return Response({
                'error': f'Role "{role_name}" does not exist'
            }, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(id__in=user_ids)
        assigned_count = 0

        for user in users:
            if not user.groups.filter(name=role_name).exists():
                user.groups.add(group)
                assigned_count += 1

        return Response({
            'message': f'Role "{role_name}" assigned to {assigned_count} users'
        })

    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        """Get user statistics."""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superuser_users = User.objects.filter(is_superuser=True).count()

        # Users by role
        roles_stats = []
        for group in Group.objects.all():
            count = group.user_set.count()
            roles_stats.append({
                'role': group.name,
                'count': count
            })

        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'superuser_users': superuser_users,
            'roles_stats': roles_stats,
        })


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for groups/roles.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Django permissions"""
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing all available permissions in the system.
    """
    queryset = Permission.objects.all().select_related('content_type')
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        """Filter permissions for relevant models only"""
        relevant_models = [
            'equipment', 'maintenance', 'incident', 'report',
            'sede', 'dependencia', 'subdependencia', 'user', 'group'
        ]
        return Permission.objects.filter(
            content_type__model__in=relevant_models
        ).select_related('content_type').order_by('content_type__model', 'codename')


class RolePermissionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing role permissions.
    Extends GroupViewSet to allow updating permissions.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def retrieve(self, request, pk=None):
        """Get a role with its permissions"""
        try:
            role = self.get_object()
            permissions = role.permissions.all()
            return Response({
                'id': role.id,
                'name': role.name,
                'permissions': [p.id for p in permissions]
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, pk=None):
        """Update role permissions"""
        try:
            role = self.get_object()
            permission_ids = request.data.get('permissions', [])
            
            # Validate permission IDs
            permissions = Permission.objects.filter(id__in=permission_ids)
            if len(permissions) != len(permission_ids):
                return Response(
                    {'error': 'Some permission IDs are invalid'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update permissions
            role.permissions.set(permissions)
            
            return Response({
                'message': f'Permissions updated for role "{role.name}"',
                'permissions': [p.id for p in role.permissions.all()]
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
