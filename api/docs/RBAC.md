# Control de Acceso Basado en Roles (RBAC)

## Roles
- **Admin**: Acceso completo a todos los recursos (CRUD en Equipment, Maintenance, Photo). Puede gestionar usuarios.
- **Tecnico**: Puede crear, leer, actualizar mantenimientos y fotos. Solo lectura en equipos.

## Permisos
- Equipment: Admin (CRUD), Tecnico (R)
- Maintenance: Admin (CRUD), Tecnico (CRUD)
- Photo: Admin (CRUD), Tecnico (CRUD)

## Implementacion
Usa Grupos de Django para roles. Permisos personalizados verifican membresia de grupo.

## Configuracion
Crear grupos en admin de Django o via comando de gestion:
- Admin
- Tecnico

Asignar usuarios a grupos.
