# Mapa de URLs del Sistema de Mantenimiento

## 🌐 Frontend (Next.js - http://localhost:3000)

```
/                           → Página principal (Login o Home con tabs)
├── /dashboard              → Dashboard con estadísticas y gráficos (Admin only)
├── /admin/users            → Gestión de usuarios y roles (Admin only)
├── /admin/groups           → Gestión de grupos (Admin only) [futuro]
└── /maintenance/new        → Formulario de nuevo mantenimiento (nueva ventana)
```

---

## 🔌 Backend API (Django - http://localhost:8000)

### Autenticación y Sesión
```
POST   /api/token/                     → Obtener token JWT
POST   /api/token/refresh/             → Refrescar token
POST   /api/logout/                    → Cerrar sesión (blacklist token)
GET    /api/user-info/                 → Información del usuario actual
```

### Perfil de Usuario
```
GET    /api/profile/                   → Ver perfil del usuario actual
PUT    /api/profile/update/            → Actualizar perfil (email, nombre)
POST   /api/profile/change-password/   → Cambiar contraseña propia
```

### Dashboard (Autenticado)
```
GET    /api/dashboard/                 → Estadísticas generales
       └── Response: {
           summary: { total_maintenances, total_equipments, total_reports, total_incidents },
           maintenances_by_type: [...],
           maintenances_by_dependency: [...],
           maintenances_by_sede: [...],
           maintenances_by_month: [...],
           recent_maintenances: [...],
           top_equipment: [...],
           ratings_distribution: [...]
       }

GET    /api/dashboard/equipment/       → Estadísticas de equipos
       └── Response: {
           equipment_with_last_maintenance: [...],
           equipment_without_maintenance: [...]
       }

GET    /api/dashboard/timeline/        → Timeline de mantenimientos
       └── Query params: ?year=2024&month=11
       └── Response: { maintenances: [...] }
```

### Administración de Usuarios (Admin only)
```
GET    /api/admin/users/                              → Listar todos los usuarios
POST   /api/admin/users/                              → Crear usuario
       └── Body: {
           username, email, password, first_name, last_name,
           is_active, is_staff, is_superuser, group_ids: [1, 2]
       }

GET    /api/admin/users/{id}/                         → Ver usuario
PUT    /api/admin/users/{id}/                         → Actualizar usuario
DELETE /api/admin/users/{id}/                         → Eliminar usuario

POST   /api/admin/users/{id}/assign_groups/           → Asignar grupos
       └── Body: { group_ids: [1, 2, 3] }

POST   /api/admin/users/{id}/change_password/         → Cambiar contraseña
       └── Body: { password: "new_password" }

POST   /api/admin/users/{id}/toggle_active/           → Activar/desactivar usuario
```

### Administración de Grupos (Admin only)
```
GET    /api/admin/groups/                             → Listar grupos
POST   /api/admin/groups/                             → Crear grupo
GET    /api/admin/groups/{id}/                        → Ver grupo
PUT    /api/admin/groups/{id}/                        → Actualizar grupo
DELETE /api/admin/groups/{id}/                        → Eliminar grupo

GET    /api/admin/groups/{id}/users/                  → Listar usuarios del grupo
POST   /api/admin/groups/{id}/add_user/               → Agregar usuario
       └── Body: { user_id: 123 }
POST   /api/admin/groups/{id}/remove_user/            → Remover usuario
       └── Body: { user_id: 123 }
```

### Equipos (Autenticado)
```
GET    /api/equipments/                               → Listar equipos
       └── Query params: ?search=TI-001&dependencia=SALUD
POST   /api/equipments/                               → Crear equipo
GET    /api/equipments/{id}/                          → Ver equipo
PUT    /api/equipments/{id}/                          → Actualizar equipo
DELETE /api/equipments/{id}/                          → Eliminar equipo
```

### Mantenimientos (Autenticado)
```
GET    /api/maintenances/                             → Listar mantenimientos
       └── Query params (filtros):
           ?date_from=2024-01-01
           &date_to=2024-12-31
           &dependencia=SECRETARIA DE SALUD
           &sede=SEDE PRINCIPAL
           &oficina=OFICINA 101
           &placa=TI-001
           &maintenance_type=preventivo
           &is_incident=false

POST   /api/maintenances/                             → Crear mantenimiento
GET    /api/maintenances/{id}/                        → Ver mantenimiento
PUT    /api/maintenances/{id}/                        → Actualizar mantenimiento
DELETE /api/maintenances/{id}/                        → Eliminar mantenimiento
```

### Reportes Básicos (Autenticado)
```
GET    /api/reports/                                  → Listar reportes
POST   /api/reports/generate/                         → Generar reporte básico
       └── Body: { equipment_id: 1, date: "2024-11-20" }
```

### Reportes Avanzados (Autenticado)
```
GET    /api/reports/maintenance/{maintenance_id}/                    → Generar reporte por defecto
POST   /api/reports/maintenance/{maintenance_id}/custom/             → Generar reporte personalizado
       └── Body: {
           header_params: {
               codigo: "GTI-F-015",
               version: "01",
               vigencia: "2024-01-01",
               organization: "Mi Organización",
               department: "Tecnología",
               logo_path: "/path/to/logo.png"
           }
       }

GET    /api/reports/maintenance/{maintenance_id}/download/           → Descargar reporte (attachment)
GET    /api/reports/maintenance/{maintenance_id}/preview/            → Vista previa (inline)

POST   /api/reports/batch/                                           → Generación por lotes
       └── Body: {
           maintenance_ids: [1, 2, 3, 4],
           header_params: { ... }
       }

GET    /api/reports/computer/{maintenance_id}/                       → Reporte formato computador (GTI-F-015)
GET    /api/reports/printer-scanner/{maintenance_id}/                → Reporte formato impresora/escáner (GTI-F-016)
```

### Empaquetado de PDFs (Admin only)
```
POST   /api/reports/package/                          → Empaquetar por IDs
       └── Body: {
           report_ids: [1, 2, 3, 4, 5],
           filename: "reportes_mayo_2024.zip"  // Opcional
       }
       └── Response: ZIP file download

POST   /api/reports/package/filter/                   → Empaquetar por filtros
       └── Body: {
           date_from: "2024-01-01",
           date_to: "2024-12-31",
           dependencia: "SECRETARIA DE SALUD",
           sede: "SEDE PRINCIPAL",
           oficina: "OFICINA 101",
           placa: "TI-001",
           maintenance_type: "preventivo",
           filename: "reportes_filtrados.zip"
       }
       └── Response: ZIP file download

GET    /api/reports/package/info/                     → Información de reportes disponibles
       └── Response: {
           total_reports: 150,
           by_type: [...],
           by_dependency: [...]
       }
```

### Logs de Auditoría (Autenticado)
```
GET    /api/audit-logs/                               → Ver logs de auditoría
       └── Response: [
           {
               user: "admin",
               action: "create",
               model: "Maintenance",
               object_id: 123,
               timestamp: "2024-11-20T10:30:00Z",
               changes: { ... }
           }
       ]
```

---

## 🔑 Permisos por Endpoint

| Endpoint | Permisos Requeridos |
|----------|---------------------|
| `/api/token/` | Público |
| `/api/user-info/` | IsAuthenticated |
| `/api/profile/*` | IsAuthenticated |
| `/api/dashboard/*` | IsAuthenticated |
| `/api/admin/*` | IsAdmin |
| `/api/equipments/*` | IsAuthenticated |
| `/api/maintenances/*` | IsAuthenticated (Create: IsAdmin o IsAdminOrTechnician) |
| `/api/reports/*` (basic) | IsAuthenticated |
| `/api/reports/package/*` | IsAdmin |
| `/api/audit-logs/` | IsAuthenticated |

---

## 📋 Códigos de Estado HTTP

| Código | Significado | Cuándo se usa |
|--------|-------------|---------------|
| 200 | OK | Operación exitosa (GET, PUT, PATCH) |
| 201 | Created | Recurso creado (POST) |
| 204 | No Content | Eliminación exitosa (DELETE) |
| 400 | Bad Request | Datos inválidos en el body |
| 401 | Unauthorized | Token faltante o inválido |
| 403 | Forbidden | Sin permisos para la acción |
| 404 | Not Found | Recurso no encontrado |
| 500 | Internal Server Error | Error del servidor |

---

## 🔐 Autenticación

### Obtener Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Usar Token en Requests
```bash
curl -X GET http://localhost:8000/api/dashboard/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 📊 Ejemplos de Uso

### 1. Listar mantenimientos con filtros
```bash
GET /api/maintenances/?date_from=2024-01-01&date_to=2024-12-31&dependencia=SALUD
```

### 2. Crear usuario
```bash
POST /api/admin/users/
{
  "username": "tecnico1",
  "email": "tecnico1@example.com",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "is_active": true,
  "group_ids": [2]  # ID del grupo "Técnico"
}
```

### 3. Empaquetar reportes
```bash
POST /api/reports/package/
{
  "report_ids": [1, 2, 3, 4, 5],
  "filename": "reportes_noviembre.zip"
}
```

### 4. Ver estadísticas del dashboard
```bash
GET /api/dashboard/
```

---

## 🌍 Variables de Entorno

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env o settings.py)
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOWED_ORIGINS = ['http://localhost:3000']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'maintenance_db',
        # ...
    }
}

# MinIO
AWS_ACCESS_KEY_ID = 'minioadmin'
AWS_SECRET_ACCESS_KEY = 'minioadmin'
AWS_STORAGE_BUCKET_NAME = 'maintenance-photos'
AWS_S3_ENDPOINT_URL = 'http://localhost:9000'
```

---

**Última actualización:** 20 de Noviembre, 2024
