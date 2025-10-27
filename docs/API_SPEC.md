# ESPECIFICACIONES DE API — Espiral 0 (minimo)

## Autenticacion
POST /api/token/
- Cuerpo: { "username": "...", "password": "..." }
- Respuesta: { "access": "...", "refresh": "..." }

POST /api/token/refresh/
- Cuerpo: { "refresh": "..." }
- Respuesta: { "access": "..." }

## Autorizacion
Usa RBAC con roles: Admin, Tecnico. Permisos basados en grupos de usuarios. Ver RBAC.md para detalles.

## Equipos
GET /api/equipments/
- Cabeceras: Authorization: Bearer <access_token>
- Parametros de consulta: ?page=1

POST /api/equipments/
- Cuerpo (JSON): { "code":"EQ-001", "name":"Bombillo", "location":"Bodega" }
- Criterios de aceptacion: 201 Created, devuelve objeto con id y timestamps

PUT /api/equipments/{id}/
DELETE /api/equipments/{id}/

## Mantenimientos
GET /api/maintenances/
- Cabeceras: Authorization: Bearer <access_token>
- Parametros de consulta: ?equipment={id}&page=1

POST /api/maintenances/
- Cuerpo (JSON): { "equipment": 1, "description": "Reemplazo de bombillo", "maintenance_date": "2023-10-01", "performed_by": "Tecnico A" }
- Criterios de aceptacion: 201 Created, devuelve objeto con id y timestamps

PUT /api/maintenances/{id}/
DELETE /api/maintenances/{id}/

GET /api/equipments/{equipment_id}/maintenances/
- Cabeceras: Authorization: Bearer <access_token>
- Parametros de consulta: ?page=1
- Devuelve lista paginada de mantenimientos para equipo especifico

GET /api/maintenances/{id}/photos/
- Devuelve lista de fotos para el mantenimiento

POST /api/maintenances/{id}/photos/
- Cuerpo: multipart/form-data con archivo 'image'
- Criterios de aceptacion: 201 Created, devuelve objeto photo con URL de imagen

## Estrategia de Carga
Las fotos para mantenimientos se cargan del lado del servidor via POST /api/maintenances/{id}/photos/ con multipart/form-data. Archivos almacenados en MinIO (compatible con S3). Ver ADR-001-upload-strategy.md.

## Ejemplos cURL
- Obtener token:
curl -X POST http://localhost:8000/api/token/ -H "Content-Type: application/json" -d '{"username":"u","password":"p"}'

- Llamada protegida:
curl -H "Authorization: Bearer <ACCESS>" http://localhost:8000/api/equipments/
