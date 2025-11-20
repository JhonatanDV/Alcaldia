"""
Admin views for user and role management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.permissions import IsAdmin


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Django Group model."""
    
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'user_count']
    
    def get_user_count(self, obj):
        return obj.user_set.count()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django User model."""
    
    groups = GroupSerializer(many=True, read_only=True)
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'groups', 'group_ids', 'password'
        ]
        read_only_fields = ['date_joined']
    
    def create(self, validated_data):
        group_ids = validated_data.pop('group_ids', [])
        password = validated_data.pop('password', None)
        
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        if group_ids:
            groups = Group.objects.filter(id__in=group_ids)
            user.groups.set(groups)
        
        return user
    
    def update(self, instance, validated_data):
        group_ids = validated_data.pop('group_ids', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        if group_ids is not None:
            groups = Group.objects.filter(id__in=group_ids)
            instance.groups.set(groups)
        
        return instance


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users (admin only).
    
    Endpoints:
        GET /api/admin/users/ - List all users
        POST /api/admin/users/ - Create new user
        GET /api/admin/users/{id}/ - Get user details
        PUT /api/admin/users/{id}/ - Update user
        DELETE /api/admin/users/{id}/ - Delete user
        POST /api/admin/users/{id}/assign_groups/ - Assign groups to user
        POST /api/admin/users/{id}/change_password/ - Change user password
    """
    
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    
    @action(detail=True, methods=['post'])
    def assign_groups(self, request, pk=None):
        """
        Assign groups to a user.
        
        Body: {
            "group_ids": [1, 2, 3]
        }
        """
        user = self.get_object()
        group_ids = request.data.get('group_ids', [])
        
        if not isinstance(group_ids, list):
            return Response(
                {'error': 'group_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        groups = Group.objects.filter(id__in=group_ids)
        user.groups.set(groups)
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """
        Change user password.
        
        Body: {
            "password": "new_password"
        }
        """
        user = self.get_object()
        password = request.data.get('password')
        
        if not password:
            return Response(
                {'error': 'password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 8:
            return Response(
                {'error': 'password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(password)
        user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle user active status."""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class GroupAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing groups (admin only).
    
    Endpoints:
        GET /api/admin/groups/ - List all groups
        POST /api/admin/groups/ - Create new group
        GET /api/admin/groups/{id}/ - Get group details
        PUT /api/admin/groups/{id}/ - Update group
        DELETE /api/admin/groups/{id}/ - Delete group
        GET /api/admin/groups/{id}/users/ - Get users in group
    """
    
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsAdmin]
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users in this group."""
        group = self.get_object()
        users = group.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_user(self, request, pk=None):
        """
        Add a user to this group.
        
        Body: {
            "user_id": 123
        }
        """
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            user.groups.add(group)
            return Response({'message': f'User {user.username} added to group {group.name}'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_user(self, request, pk=None):
        """
        Remove a user from this group.
        
        Body: {
            "user_id": 123
        }
        """
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            user.groups.remove(group)
            return Response({'message': f'User {user.username} removed from group {group.name}'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_profile(request):
    """
    Get current user profile information.
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update current user profile (email, first_name, last_name).
    """
    user = request.user
    
    # Users can only update their own profile fields
    allowed_fields = ['email', 'first_name', 'last_name']
    
    for field in allowed_fields:
        if field in request.data:
            setattr(user, field, request.data[field])
    
    user.save()
    
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_own_password(request):
    """
    Change current user's password.
    
    Body: {
        "old_password": "current_password",
        "new_password": "new_password"
    }
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response(
            {'error': 'old_password and new_password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.check_password(old_password):
        return Response(
            {'error': 'old_password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 8:
        return Response(
            {'error': 'new_password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.set_password(new_password)
    user.save()
    
    return Response({'message': 'Password changed successfully'})
