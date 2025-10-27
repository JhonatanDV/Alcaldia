# Solucion de Problemas

## Problemas Comunes

### Errores de Autenticacion
- Asegurar que token JWT sea valido y no expirado.
- Verificar cabecera `Authorization: Bearer <token>`.

### Fallos de Carga
- Verificar que MinIO este ejecutandose y accesible.
- Verificar que bucket exista (`maintenance-photos`).
- Asegurar tamano de archivo < 10MB.

### Permiso Denegado
- Confirmar rol de usuario (Admin, Tecnico, Viewer).
- Verificar asignaciones de grupo en admin de Django.

### Errores de Base de Datos
- Ejecutar `python manage.py migrate` despues de cambios en modelos.
- Verificar DATABASE_URL en configuraciones.

### Fallos CI/CD
- Revisar logs de GitLab CI.
- Asegurar que servicios (Postgres, MinIO) inicien correctamente.
- Verificar variables de entorno.

## Problemas Especificos CI/CD

### Badge de Estado de Pipeline No Verde
- Verificar estado de pipeline en GitLab CI/CD > Pipelines.
- Verificar logs de trabajos fallidos.
- Asegurar que todas las variables esten configuradas en Settings > CI/CD > Variables.

### Errores de Servicio No Listo
- Para Postgres: Agregar espera en before_script:
  ```
  before_script:
    - apt-get update && apt-get install -y postgresql-client
    - until pg_isready -h postgres -U $POSTGRES_USER; do sleep 1; done
  ```
- Para MinIO: Agregar verificacion de salud:
  ```
  before_script:
    - apt-get update && apt-get install -y curl
    - until curl -f http://minio:9000/minio/health/live; do sleep 1; done
  ```

### Variables No Definidas
- Hacer echo de variables en script para verificar:
  ```
  script:
    - echo "DB: $POSTGRES_DB"
    - echo "User: $POSTGRES_USER"
  ```
- Si vacias, configurar en GitLab Settings > CI/CD > Variables.

## Logs
- Logs de app: salida de `python manage.py runserver`.
- Logs de auditoria: consultar modelo AuditLog.
- Logs MinIO: logs de Docker para contenedor MinIO.
- Logs CI: GitLab CI/CD > Pipelines > logs de trabajo.

## Soporte
- Verificar `docs/risk_log.csv` para riesgos conocidos.
- Contactar equipo dev para problemas no resueltos.
