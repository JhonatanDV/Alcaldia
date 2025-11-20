from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class that only allows admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff


class IsTechnician(permissions.BasePermission):
    """
    Permission class for technicians.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or
            request.user.groups.filter(name='Tecnico').exists()
        )

    def has_object_permission(self, request, view, obj):
        return request.user and (
            request.user.is_staff or
            request.user.groups.filter(name='Tecnico').exists()
        )


class IsAdminOrTechnician(permissions.BasePermission):
    """
    Permission class that allows admin or technician users.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or
            request.user.groups.filter(name='Tecnico').exists()
        )

    def has_object_permission(self, request, view, obj):
        return request.user and (
            request.user.is_staff or
            request.user.groups.filter(name='Tecnico').exists()
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows owners or admins.
    """
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_staff:
            return True
        
        # Check if user is owner
        if hasattr(obj, 'reportado_por'):
            return obj.reportado_por == request.user
        if hasattr(obj, 'tecnico_responsable'):
            return obj.tecnico_responsable == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class CanViewReports(permissions.BasePermission):
    """
    Permission for viewing reports.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or
            request.user.groups.filter(name__in=['Tecnico', 'Supervisor', 'Coordinador']).exists()
        )
