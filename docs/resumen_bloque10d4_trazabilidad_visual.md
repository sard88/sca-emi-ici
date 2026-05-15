# Bloque 10D-4 - Trazabilidad visual y estados de proceso

## Objetivo

Se agregaron componentes visuales de trazabilidad al portal Next.js para hacer más comprensibles procesos críticos ya implementados: actas, conformidad, validaciones, trayectoria, movimientos, periodos, exportaciones y auditoría. El bloque no modifica reglas académicas, estados de acta, cálculos, kárdex, historial oficial, modelos ni migraciones.

## Componentes creados

Se creó `frontend/src/components/trazabilidad/` con componentes reutilizables:

- `ProcessTimeline` y `ProcessTimelineStep`.
- `ProcessStateBadge`.
- `AuditTrailPanel`, `AuditEventCard` y `AuditEventDetailDrawer`.
- `ValidationTimeline`.
- `ConformityTimeline` y `ConformitySummaryPanel`.
- `ExportTracePanel`.
- `OfficialStatusNotice` y `SensitiveTraceNotice`.
- `PeriodProcessStepper` y `PeriodBlockersPanel`.
- `MovementImpactTimeline`.
- `AcademicHistoryTimeline`.
- `TimelineEmptyState`.

## Pantallas actualizadas

- Actas: `/docente/actas/[id]`, `/estadistica/actas/[id]`, `/jefatura-carrera/actas/[id]`, `/jefatura-academica/actas/[id]`.
- Discente: `/discente/actas`, `/discente/actas/[detalleId]`, `/discente/carga-academica`.
- Trayectoria: `/trayectoria/mi-historial`, `/trayectoria/historial/[discenteId]`.
- Movimientos: `/movimientos-academicos/[id]`.
- Periodos: `/periodos`, `/periodos/[id]/diagnostico`, `/periodos/cierres/[id]`, `/periodos/apertura`, `/periodos/aperturas/[id]`, `/periodos/pendientes-asignacion-docente`.
- Reportes: `/reportes/exportaciones`, `/reportes/auditoria`.

## Timelines agregados

- Timeline de estado del acta con estados existentes: borrador, publicado, remitido, validado, formalizado y archivado.
- Timeline de validaciones con usuario, cargo y fecha cuando el backend lo entrega.
- Timeline personal de conformidad del discente, sin auditoría interna ni datos de otros discentes.
- Timeline cronológico de historial académico interno combinando resultados, extraordinarios, situaciones y movimientos sin recalcular reglas.
- Timeline de impacto de movimientos académicos con grupo origen/destino y evidencias de impacto sólo si el backend las entrega.
- Stepper de cierre/apertura de periodo: planificado, activo, diagnóstico, cierre, apertura y pendientes de asignación docente.

## Auditoría contextual

Se agregaron paneles contextuales de eventos críticos para objetos relevantes usando `GET /api/auditoria/eventos/` con filtros `objeto_tipo` y `objeto_id`.

El frontend agregó funciones:

- `getAuditoriaEventos(params)`.
- `getAuditoriaEventoDetalle(id)`.
- `getAuditoriaResumen(params)`.
- `getEventosCriticosPorObjeto(objetoTipo, objetoId, params)`.

Los paneles sólo se montan para perfiles con permiso visual a eventos críticos. Si el backend niega acceso, el panel se oculta o muestra aviso controlado según contexto.

## Exportaciones

`/reportes/exportaciones` ahora muestra tarjetas de trazabilidad documental con folio técnico, tipo documental, formato, estado, usuario, fecha, objeto, hash y tamaño cuando existen. No se muestran `filtros_json` ni `parametros_json` en la tabla principal.

`/reportes/auditoria` mantiene la exportación XLSX existente y agrega detalle visual de evento en drawer/modal sin mostrar payloads completos por defecto.

## Privacidad

- No se muestra matrícula militar por defecto.
- Discente ve sólo sus propios datos.
- Docente y discente no acceden a auditoría global ni solicitan bitácora contextual.
- Comentarios completos de inconformidad no aparecen en resúmenes.
- No se muestran `metadatos_json`, `cambios_json` ni payloads completos.
- IP sólo aparece en el detalle visual de auditoría para perfiles institucionales autorizados.
- El historial interno mantiene aviso de que no sustituye al kárdex oficial.

## Backend

No se modificó backend. No hubo modelos, migraciones, permisos ni endpoints nuevos. Django continúa como fuente de verdad.

## Validaciones ejecutadas

- `docker compose exec -T frontend npm run lint` - OK.
- `docker compose exec -T frontend npm run build` - OK.
- `docker compose exec -T backend python manage.py check` - OK.
- `docker compose exec -T backend python manage.py makemigrations --check` - OK, sin cambios detectados.
- `docker compose exec -T backend python manage.py test auditoria` - OK, 7 pruebas.
- `docker compose exec -T backend python manage.py test evaluacion` - OK, 86 pruebas.
- `docker compose exec -T backend python manage.py test trayectoria` - OK, 58 pruebas.
- `docker compose exec -T backend python manage.py test relaciones` - OK, 39 pruebas.
- `docker compose exec -T backend python manage.py test actas` - OK, 27 pruebas.
- `docker compose exec -T backend python manage.py test` - OK, 461 pruebas.

## Limitaciones

- No se implementa rectificación ni reapertura de actas.
- No se agregan reportes ni exportaciones nuevas.
- No se modifica el alcance de permisos backend.
- El detalle contextual de auditoría depende de permisos existentes y puede ocultarse para jefaturas sin acceso granular.
- El timeline usa fechas y evidencias disponibles; si el backend no entrega una fecha, el paso queda pendiente o sin fecha sin inventar datos.

## Pendientes

- 10D-3: terminología, microcopy, iconografía y estados vacíos.
- 10E: QA manual integral con datos realistas por perfil y revisión responsive.
- Backlog post-10D: filtros aún textuales, refinamientos visuales y decisiones funcionales pendientes documentadas en `docs/backlog_ajustes_ux_post_10d.md`.
