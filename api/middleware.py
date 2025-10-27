from .models import AuditLog
from django.utils.deprecation import MiddlewareMixin

class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests for audit purposes.
    """

    def process_request(self, request):
        # Store request data for logging
        if hasattr(request, 'user') and request.user.is_authenticated:
            request._audit_user = request.user

    def process_response(self, request, response):
        # Log API calls if user is authenticated and it's an API endpoint
        if (hasattr(request, 'user') and
            request.user.is_authenticated and
            request.path.startswith('/api/') and
            request.method in ['POST', 'PUT', 'PATCH', 'DELETE']):

            # Extract model and action from URL/path
            path_parts = request.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'api':
                model_name = path_parts[1]  # e.g., 'maintenances', 'equipments'
                action = self._get_action_from_method(request.method)

                # Create audit log entry
                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    model=model_name,
                    object_id=self._extract_object_id(path_parts),
                    changes=self._get_request_changes(request)
                )

        return response

    def _get_action_from_method(self, method):
        """Map HTTP method to audit action."""
        method_map = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE'
        }
        return method_map.get(method, 'UNKNOWN')

    def _extract_object_id(self, path_parts):
        """Extract object ID from URL path."""
        # Look for numeric ID in path
        for part in path_parts:
            if part.isdigit():
                return int(part)
        return 0  # Default if no ID found

    def _get_request_changes(self, request):
        """Extract changes from request data for logging."""
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'data'):
            # Return a summary of changes
            return {
                'method': request.method,
                'data_keys': list(request.data.keys()) if hasattr(request.data, 'keys') else [],
                'has_files': bool(getattr(request, 'FILES', {}))
            }
        return None
