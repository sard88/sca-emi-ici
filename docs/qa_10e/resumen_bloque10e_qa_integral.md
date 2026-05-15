# Resumen Bloque 10E - QA integral y demo final

## Objetivo

Validar de punta a punta el MVP del Sistema de Control Academico EMI - ICI: backend Django, frontend Next.js, Docker Compose, permisos, flujos academicos, actas, reportes, kardex, trayectoria, movimientos, cierre/apertura, auditoria, UX final y documentacion de evidencia.

## Alcance ejecutado

- Validacion Docker Compose: build, up, ps, config y salud interna.
- Validacion backend: check, migraciones, showmigrations, suites por app y suite completa.
- Validacion frontend: lint, build, rutas principales y ausencia de suite `npm test`.
- Validacion anonima basica de APIs protegidas.
- Matriz de defectos con clasificacion P0/P1/P2.
- Correccion de defecto P1 de ambiente frontend demo.
- Checklists por perfil y modulo.
- Guia de demo final.

## Ambiente

- Fecha: 2026-05-15.
- Rama: `feature/bloque-10e-qa-integral-demo`.
- Base inicial: `620f44b`.
- Servicios Compose: `db`, `backend`, `frontend`.
- Backend: Django 5.1.15 segun log de runserver.
- Frontend: Next.js 15.5.18 segun lint/build/logs.

## Validaciones automaticas

| Area | Resultado |
|---|---|
| `docker compose build` | OK |
| `docker compose up -d` | OK |
| `docker compose ps` | OK, `db` healthy, backend/frontend arriba |
| Salud backend interna | OK, `/health/` 200 |
| Salud frontend interna | OK, `/login` 200 tras correccion |
| Backend check | OK |
| Migraciones pendientes | OK, `No changes detected` |
| Showmigrations | OK |
| Tests por app | OK: usuarios 92, catalogos 71, relaciones 39, evaluacion 86, actas 27, trayectoria 58, reportes 74, auditoria 7, core 7 |
| Suite backend completa | OK, 461 tests |
| Frontend lint | OK |
| Frontend build | OK, 46 paginas/rutas generadas |
| Frontend npm test | Sin suite definida; `npm test --if-present` termina OK |
| Rutas frontend principales | OK, 53/53 |
| APIs anonimas protegidas | OK, endpoints principales devuelven 401 sin sesion |

## Defectos encontrados

- `10E-P1-001`: `/login` respondia 500 despues de recrear frontend por chunk stale en volumen `.next`.
- `10E-ENV-001`: `curl` desde host sandbox no conecta a puertos publicados; no se reproduce dentro de contenedores.
- `10E-P2-001`: no hay dataset/credenciales QA documentadas para demo manual completa.
- `10E-P2-002`: no hay suite frontend `npm test`.
- `10E-P2-003`: responsive visual por viewport queda pendiente de evidencia con navegador/capturas.

## Defectos corregidos

| ID | Correccion | Archivo | Regresion |
|---|---|---|---|
| 10E-P1-001 | El comando frontend limpia el contenido del volumen `.next` antes de `next dev`, evitando chunks persistentes corruptos tras rebuild/recreate. | `compose.yaml` | `/login`, `/dashboard`, `/reportes/auditoria` OK; luego 53/53 rutas OK. |

## Validaciones manuales

No se ejecutaron operaciones manuales autenticadas completas porque el repositorio no documenta credenciales demo ni fixture QA idempotente. Para no crear datos reales ni nuevas funcionalidades fuera de alcance, los flujos manuales quedan en `guia_demo_final_10e.md` y checklists como validacion pendiente con datos ficticios.

## Privacidad

- Endpoints principales protegidos responden 401 sin sesion.
- No se generaron ni versionaron PDF/XLSX de prueba.
- No se agregaron datos reales ni credenciales.
- No se modificaron reglas, estados de acta, modelos, permisos backend ni calculos.

## Dictamen final

Aprobado con observaciones.

No hay P0 abiertos ni P1 abiertos. El MVP queda apto para demo tecnica controlada con dataset ficticio preparado. Antes de una demo funcional completa con usuarios finales se recomienda preparar credenciales/datos QA y ejecutar el recorrido manual por perfil.
