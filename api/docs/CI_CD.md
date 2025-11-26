# Pipeline CI/CD

## Resumen
El pipeline CI/CD usa GitLab CI para automatizar pruebas, construccion y despliegue de la API de Mantenimiento de Equipos.

## Etapas
- **Probar**: Ejecuta pytest con servicios Postgres y MinIO.
- **Construir**: Construye imagen Docker.
- **Desplegar**: Despliega a staging/produccion.

## Servicios
- Postgres: Base de datos para pruebas.
- MinIO: Almacenamiento simulado para cargas.

## Variables
- POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
- MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT
- CI_REGISTRY_IMAGE

## Pruebas Locales
Usar `docker-compose.ci.yml` para simular entorno CI localmente.
