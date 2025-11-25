import json
from django.utils.deprecation import MiddlewareMixin
from django.contrib.contenttypes.models import ContentType
from api.models import AuditLog


class EarlyRequestLoggerMiddleware(MiddlewareMixin):
    """
    Middleware temporal para depuración: registra método, path, headers
    y un preview del body al comienzo del pipeline de middlewares.
    """
    def process_request(self, request):
        try:
            body_preview = request.body.decode('utf-8', errors='replace')[:2000]
        except Exception:
            body_preview = '<unavailable>'
        print('=== EarlyRequestLogger ===')
        print('METHOD:', request.method, 'PATH:', request.path)
        print('Origin header:', request.META.get('HTTP_ORIGIN'))
        print('Content-Type:', request.META.get('CONTENT_TYPE'))
        print('BODY PREVIEW:', body_preview)
        print('=== End EarlyRequestLogger ===')

    def process_exception(self, request, exception):
        # Log any exception caught during request processing
        try:
            import traceback
            print('=== EarlyRequestLogger caught exception ===')
            print('Exception type:', type(exception))
            print('Exception:', exception)
            traceback.print_exc()
            print('=== End exception ===')
        except Exception:
            pass


class SkipCSRFMiddleware(MiddlewareMixin):
    """Middleware to disable CSRF checks for requests authenticated via
    an Authorization header (Bearer token). Useful for APIs consumed by SPAs
    that authenticate with JWT in the Authorization header.

    IMPORTANT: This should only be used for token-based APIs and in
    development or when you have ensured tokens are handled securely.
    """
    def process_request(self, request):
        try:
            auth = request.META.get('HTTP_AUTHORIZATION') or ''
            if auth.startswith('Bearer '):
                # Instruct Django's CsrfViewMiddleware to skip CSRF checks
                request._dont_enforce_csrf_checks = True
                print('SkipCSRFMiddleware: disabled CSRF for Bearer token')
        except Exception:
            pass


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware para registrar automáticamente todas las peticiones en el log de auditoría
    """
    
    def process_response(self, request, response):
        """
        Registra la respuesta de cada petición
        """
        # Solo registrar si el usuario está autenticado
        if not request.user.is_authenticated:
            return response
        
        # Solo registrar métodos que modifican datos
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return response
        
        # Determinar la acción
        action_map = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        
        action = action_map.get(request.method, 'unknown')
        
        # Obtener el modelo desde la URL (ejemplo: /api/maintenances/)
        path_parts = request.path.strip('/').split('/')
        model_name = path_parts[-1] if len(path_parts) > 1 else 'unknown'
        
        # Crear el registro de auditoría sin content_type específico
        AuditLog.objects.create(
            user=request.user,
            action=action,
            changes=self._get_request_changes(request)
        )
        
        return response
    
    def _get_request_changes(self, request):
        """
        Extrae los cambios del request
        """
        try:
            if request.method in ['POST', 'PUT', 'PATCH']:
                if hasattr(request, 'body') and request.body:
                    body = json.loads(request.body.decode('utf-8'))
                    return json.dumps(body, indent=2)
        except:
            pass
        
        return f'{request.method} {request.path}'
