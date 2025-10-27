# Guia de Despliegue

## Prerrequisitos
- Docker y Docker Compose
- GitLab CI/CD (para despliegue automatizado)

## Desarrollo Local
1. Usar `docker-compose.ci.yml` para ejecutar servicios (DB, MinIO).
2. Ejecutar `python manage.py runserver` para la app.

## Despliegue en Produccion
1. Construir imagen Docker usando `Dockerfile.test`.
2. Desplegar a staging/produccion via GitLab CI.
3. Establecer variables de entorno:
   - DATABASE_URL
   - MINIO_ENDPOINT
   - MINIO_ACCESS_KEY
   - MINIO_SECRET_KEY
   - SECRET_KEY
   - DEBUG=False

## Variables CI/CD
- POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
- MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT
- CI_REGISTRY_IMAGE

## Escalado
- Usar Kubernetes para escalado.
- MinIO para almacenamiento escalable.
