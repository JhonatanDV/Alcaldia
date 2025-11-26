# Registro de Auditoria

## Resumen
El registro de auditoria rastrea todas las operaciones de crear, actualizar y eliminar en modelos Equipment, Maintenance y Photo. Los registros incluyen usuario, accion, modelo, ID de objeto, timestamp y cambios.

## Implementacion
- Usa senales de Django para registrar cambios automaticamente.
- Modelo AuditLog almacena entradas de registro.
- Accesible via admin o API (futuro).

## Modelo
AuditLog:
- user: FK a User
- action: CharField (CREATE, UPDATE, DELETE)
- model: CharField (nombre del modelo)
- object_id: PositiveIntegerField
- timestamp: DateTimeField
- changes: JSONField (valores antiguos/nuevos para actualizaciones)

## Configuracion
Senales conectadas en api/apps.py. Registros creados automaticamente al guardar/eliminar modelo.
