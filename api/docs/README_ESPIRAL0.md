# Espiral 0 — Viabilidad
## Resumen
Objetivo: validar la viabilidad técnica del stack (Django + DRF + SimpleJWT, Postgres), implementar POC de autenticación JWT (access + refresh), CRUD básico de Equipment, pipeline CI que ejecute tests y producir artefactos mínimos (README, API_SPEC, Postman, risk_log). Duración estimada: 1 semana.

## Entregables mínimos

Endpoints: /api/token/ y /api/token/refresh/
CRUD: /api/equipments/ con tests unitarios
.gitlab-ci.yml que ejecute pytest en MRs
.env.example con placeholders
docs/postman_collection.json, docs/API_SPEC.md
.gitlab/issue_templates/espiral_with_risk.md
docs/risk_log.csv con R1
Issue de cierre con decisión GO / NO‑GO

## Equipo y responsabilidades
Dev: implementación backend, tests, Postman, MRs, código.
Doc (DevOps / Analista / Docs): GitLab, CI/CD, variables, plantillas, risk_log, coordinación demo.

## Plan diario (resumen)
Día 1 — Kick‑off y scaffold repo (Dev + Doc)
Día 2 — POC auth JWT (Dev); .env.example + variables CI (Doc)
Día 3 — CRUD Equipment + tests iniciales (Dev); verificar runners + crear issues (Doc)
Día 4 — Pipeline en MR y corrección de fallos (Dev + Doc)
Día 5 — Documentación final, demo y decisión GO/NO‑GO (Dev + Doc)


## Checklists (copiar/usar)
### Checklist Dev (antes de demo)
 /api/token/ y /api/token/refresh/ funcionando
 CRUD Equipment implementado y probado
 Tests unitarios (pytest) green localmente
 Postman collection exportada a docs/
 MR(s) abiertos y pipeline ejecutado

### Checklist Doc (antes de demo)
 Milestone Espiral 0 — Viabilidad creado
 Labels esenciales creados
 .gitlab/issue_templates/espiral_with_risk.md en repo
 docs/risk_log.csv con R1 creado
 .env.example agregado y CI variables configuradas en GitLab
 .gitlab-ci.yml presente y runner verificado
 Issues Espiral 0 creados y asignados

## GO / NO‑GO — criterios finales
Marcar GO si:

Auth (access + refresh) funciona con Postman
CRUD básico y tests unitarios pasan
Pipeline en MR ejecuta pytest y pasa
README / API_SPEC / Postman / risk_log subidos y actualizados
Si NO‑GO:

Documentar causas en docs/risk_log.csv y crear issues P0 con pasos reproducibles. Priorizar correcciones en Espiral 1 día 1.

## Archivos clave y rutas
.gitlab/issue_templates/espiral_with_risk.md
docs/risk_log.csv
docs/README_ESPIRAL0.md (este archivo)
docs/API_SPEC.md
docs/postman_collection.json
.env.example
.gitlab-ci.yml

## Comandos útiles (resumen)
Crear branch:
bash
Copy
git checkout -b feature/espiral0-dev
Commit & push:
bash
Copy
git add .
git commit -m "feat(espiral0): ..."
git push origin feature/espiral0-dev
Ejecutar tests local:
bash
Copy
cd backend
source .venv/bin/activate
pytest -q
Obtener token JWT (curl):
bash
Copy
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tu_usuario","password":"tu_password"}'
