from rest_framework import permissions

class IsAdminOrTechnician(permissions.BasePermission):
    """
    Custom permission to only allow admins or technicians to access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name__in=['Admin', 'Technician', 'Técnico']).exists()

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Admin').exists()

class IsTechnician(permissions.BasePermission):
    """
    Custom permission to only allow technicians to access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name__in=['Technician', 'Técnico']).exists()

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners (who created the maintenance) or admins to edit/delete.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admins can do anything
        if request.user.groups.filter(name='Admin').exists():
            return True

        # For Maintenance objects, check if user is the one who performed it
        # Since we don't have a direct user field, we'll check the performed_by field
        # In a real app, you'd want a proper user relationship
        if hasattr(obj, 'performed_by'):
            # This is a simple check - in production, use proper user relationships
            return obj.performed_by == request.user.get_full_name() or obj.performed_by == request.user.username

        return False
