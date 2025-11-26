# Espiral 1 — Reportes en PDF
## Resumen
Objetivo: implementar generación de reportes en PDF para mantenimientos de equipos, incluyendo endpoint API, almacenamiento seguro y pipeline E2E. Duración estimada: 1 semana.

## Entregables mínimos

Endpoint: POST /api/reports/ que genera PDF con datos de equipo y mantenimientos
Librería: WeasyPrint para conversión HTML→PDF
Almacenamiento: PDFs en MinIO con URLs prefirmadas de corta duración
CI/CD: Job E2E con Playwright para smoke tests
Docs: API_SPEC actualizado, runbook E2E, diagrama arquitectura

## Equipo y responsabilidades
Dev: implementación backend (modelo, vista, servicio), tests, Postman.
DevOps: CI/CD, variables, MinIO, seguridad bucket.

## Plan diario (resumen)
Día 1 — Spike y ADR (Dev + DevOps)
Día 2 — Endpoint reports + Postman (Dev)
Día 3 — Frontend flow + seguridad (DevOps)
Día 4 — E2E pipeline + runbook (Dev + DevOps)
Día 5 — Release + docs finales (Dev + DevOps)

## Decisiones Técnicas
- **Librería PDF**: WeasyPrint (ADR-002) - conversión HTML/CSS a PDF.
- **Patrón ReportGenerator**: Clase servicio para encapsular lógica de generación.
- **Almacenamiento**: MinIO con presigned URLs (expiran en 1h).
- **Modelo Report**: Persistencia de metadatos de reportes generados.
- **Seguridad**: URLs prefirmadas, permisos Admin/Tecnico.

## Checklists
### Checklist Dev
- [ ] POST /api/reports/ implementado y probado
- [ ] ReportGenerator genera PDFs válidos
- [ ] Tests unitarios para generación de reportes
- [ ] Postman collection actualizada

### Checklist DevOps
- [ ] Variables CI configuradas (MinIO, Playwright)
- [ ] Job E2E en .gitlab-ci.yml
- [ ] Bucket policies validadas
- [ ] Runbook E2E documentado

## GO / NO‑GO — criterios finales
Marcar GO si:
- PDF generado correctamente con datos reales
- Endpoint responde con URL prefirmada válida
- Pipeline E2E ejecuta smoke tests exitosamente
- Docs actualizados y risk_log cerrado

Si NO‑GO: documentar en risk_log y crear issues P0.

## Archivos clave
docs/decisions/ADR-002-pdf-library.md
docs/ARCHITECTURE_DIAGRAM_REPORTGENERATOR.md
docs/API_SPEC.md (actualizado)
docs/postman_collection.json (actualizado)
docs/runbook.md
docs/risk_log.csv (actualizado)
