# Resumen Bloque 10C-6 - Interfaces de trayectoria, movimientos y cierre/apertura

## Qué se implementó

Se integró en el portal Next.js la operación de trayectoria académica, movimientos académicos y cierre/apertura de periodo usando APIs Django. El frontend no recalcula reglas académicas: consume JSON, muestra formularios/tablas y dispara mutaciones hacia servicios existentes.

## Rutas frontend

- `/trayectoria`
- `/trayectoria/mi-historial`
- `/trayectoria/historial`
- `/trayectoria/historial/[discenteId]`
- `/trayectoria/extraordinarios`
- `/trayectoria/extraordinarios/nuevo`
- `/trayectoria/extraordinarios/[id]`
- `/trayectoria/situaciones`
- `/trayectoria/situaciones/nuevo`
- `/trayectoria/situaciones/[id]`
- `/movimientos-academicos`
- `/movimientos-academicos/nuevo`
- `/movimientos-academicos/[id]`
- `/movimientos-academicos/cambio-grupo`
- `/periodos`
- `/periodos/[id]/diagnostico`
- `/periodos/cierres`
- `/periodos/cierres/[id]`
- `/periodos/apertura`
- `/periodos/aperturas`
- `/periodos/aperturas/[id]`
- `/periodos/pendientes-asignacion-docente`

## APIs backend

Trayectoria:

- `GET /api/trayectoria/mi-historial/`
- `GET /api/trayectoria/historial/`
- `GET /api/trayectoria/historial/<discente_id>/`
- `GET|POST /api/trayectoria/extraordinarios/`
- `GET /api/trayectoria/extraordinarios/<id>/`
- `GET|POST /api/trayectoria/situaciones/`
- `GET /api/trayectoria/situaciones/<id>/`

Movimientos:

- `GET|POST /api/relaciones/movimientos/`
- `GET /api/relaciones/movimientos/<id>/`
- `POST /api/relaciones/movimientos/cambio-grupo/`

Periodos:

- `GET /api/periodos/`
- `GET /api/periodos/<id>/diagnostico-cierre/`
- `POST /api/periodos/<id>/cerrar/`
- `GET /api/cierres/`
- `GET /api/cierres/<id>/`
- `POST /api/aperturas/crear/`
- `GET /api/aperturas/`
- `GET /api/aperturas/<id>/`
- `GET /api/pendientes-asignacion-docente/`

## Componentes creados

- `TrajectoryHomeCards`
- `MyHistoryView`
- `InstitutionalHistorySearch`
- `InstitutionalHistoryDetail`
- `HistoryResultsTable`
- `HistoryEventsTable`
- `HistoryMovementsTable`
- `HistoryPrivacyNotice`
- `ExtraordinaryList`
- `ExtraordinaryForm`
- `ExtraordinaryDetail`
- `AcademicSituationList`
- `AcademicSituationForm`
- `AcademicSituationDetail`
- `AcademicMovementsList`
- `AcademicMovementForm`
- `AcademicMovementDetail`
- `ChangeGroupForm`
- `MovementImpactSummary`
- `MovementSafetyNotice`
- `PeriodsOperationalList`
- `PeriodStatusBadge`
- `ClosureDiagnosticPanel`
- `ClosureBlockersList`
- `ClosureStudentClassificationTable`
- `ClosePeriodActionPanel`
- `ClosureProcessDetail`
- `OpeningPeriodForm`
- `OpeningProcessDetail`
- `PendingTeacherAssignmentsTable`
- `OperationSuccessNotice`
- `OperationWarningNotice`
- `SensitiveInfoNotice`
- `AccessDeniedState`

## Archivos principales modificados

- `backend/config/urls.py`
- `backend/trayectoria/api_views.py`
- `backend/trayectoria/api_urls.py`
- `backend/relaciones/api_views.py`
- `backend/relaciones/api_urls.py`
- `backend/actas/api_views.py`
- `backend/actas/api_urls.py`
- `backend/trayectoria/tests.py`
- `backend/relaciones/tests.py`
- `backend/actas/tests.py`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/trayectoria-operativa/TrajectoryOperations.tsx`
- `frontend/src/app/trayectoria/**`
- `frontend/src/app/movimientos-academicos/**`
- `frontend/src/app/periodos/**`
- `README.md`

## Permisos

- Discente: consulta únicamente su historial propio desde `/trayectoria/mi-historial`.
- Estadística/Admin: consulta y operación de extraordinarios, situaciones, movimientos, cierre y apertura.
- Jefatura de carrera: consulta filtrada por ámbito en historial/movimientos/pendientes cuando existe carrera inferible.
- Jefatura académica/pedagógica: consulta institucional según permisos backend.
- Docente: sin acceso a trayectoria global ni cierre/apertura.

## Validaciones y reglas

- Las APIs requieren autenticación y responden JSON.
- Las mutaciones usan CSRF y sesión Django.
- No se muestra matrícula militar por defecto.
- No se usa `localStorage` ni JWT.
- Los formularios piden IDs internos autorizados cuando no existe buscador seguro.
- Las acciones críticas muestran confirmación visual.
- El backend sigue validando reglas reales.

## Limitaciones

- No se implementó búsqueda avanzada relacional de discentes/inscripciones; para esta iteración los formularios aceptan IDs internos.
- No se implementó bitácora transversal completa; queda para 9K.
- No se agregaron exportaciones nuevas; reportes XLSX siguen en módulos 9I-M-E/10C-3C.
- No se implementó asignación automática de docentes tras apertura.
- No se eliminan ni editan eventos/movimientos desde el portal.

## Validaciones ejecutadas

- `docker compose exec -T backend python manage.py check` - OK.
- `docker compose exec -T backend python manage.py makemigrations` - sin cambios.
- `docker compose exec -T backend python manage.py migrate` - sin migraciones pendientes.
- `docker compose exec -T backend python manage.py makemigrations --check` - OK.
- `docker compose exec -T backend python manage.py test trayectoria` - 56 tests OK.
- `docker compose exec -T backend python manage.py test relaciones` - 39 tests OK.
- `docker compose exec -T backend python manage.py test evaluacion` - 84 tests OK.
- `docker compose exec -T backend python manage.py test usuarios` - 92 tests OK.
- `docker compose exec -T backend python manage.py test trayectoria relaciones actas` - 122 tests OK.
- `docker compose exec -T backend python manage.py test` - 450 tests OK.
- `docker compose exec -T frontend npm run lint` - OK.
- `docker compose exec -T frontend npm run build` - OK.

## Pendientes

- 9K: bitácora transversal completa para operaciones críticas.
- 10D: pulido UX/UI, buscadores relacionales y confirmaciones enriquecidas.
- 10E: QA integral con datos realistas de varios perfiles y ámbitos.
