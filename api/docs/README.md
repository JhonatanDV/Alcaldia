# API de Mantenimiento de Equipos

[![Estado del Pipeline](https://gitlab.com/Luisceron0/mantenimiento/badges/main/pipeline.svg)](https://gitlab.com/Luisceron0/mantenimiento/-/commits/main)
[![Cobertura](https://gitlab.com/Luisceron0/mantenimiento/badges/main/coverage.svg)](https://gitlab.com/Luisceron0/mantenimiento/-/commits/main)

## Resumen
Esta API REST de Django gestiona registros de mantenimiento de equipos, incluyendo operaciones CRUD para equipos, mantenimientos y fotos asociadas. Incluye autenticacion JWT, control de acceso basado en roles (RBAC), registro de auditoria y carga de fotos a MinIO.

## Caracteristicas
- **Autenticacion**: Basada en JWT con tokens de acceso y refresco.
- **Gestion de Equipos**: CRUD para elementos de equipo.
- **Registros de Mantenimiento**: Vinculados a equipos, con descripciones y fechas.
- **Carga de Fotos**: Cargas del lado del servidor a MinIO para fotos de mantenimiento.
- **RBAC**: Roles - Admin (acceso completo), Tecnico (operaciones de mantenimiento), Visor (solo lectura).
- **Registro de Auditoria**: Rastrea todos los cambios en los modelos.
- **CI/CD**: GitLab CI con etapas de prueba, construccion y despliegue.

## Inicio Rapido
1. Clona el repositorio.
2. Instala dependencias: `pip install -r requirements.txt`
3. Ejecuta migraciones: `python manage.py migrate`
4. Inicia MinIO: Usa `docker-compose.ci.yml` o MinIO independiente.
5. Ejecuta el servidor: `python manage.py runserver`
6. Autentica via POST /api/token/

## Endpoints de API
Ver `docs/API_SPEC.md` para especificaciones detalladas.

## Documentacion
- `docs/API_SPEC.md`: Endpoints y especificaciones de API.
- `docs/RBAC.md`: Detalles de control de acceso basado en roles.
- `docs/AUDIT_LOG.md`: Resumen de registro de auditoria.
- `docs/ER_DIAGRAM.md`: Diagrama de relacion de entidades.
- `docs/DATABASE_SCHEMA.md`: Esquema de base de datos.
- `docs/decisions/ADR-001-upload-strategy.md`: Decision de estrategia de carga.
- `docs/CI_CD.md`: Detalles del pipeline CI/CD.

## Despliegue
Ver `docs/DEPLOYMENT.md`.

## Solucion de Problemas
Ver `docs/TROUBLESHOOTING.md`.
