import json
from django.utils.deprecation import MiddlewareMixin
from django.contrib.contenttypes.models import ContentType
from api.models import AuditLog

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
