# Bloque 10C-5 – Interfaces operativas de calificaciones y actas en portal

## Qué se implementó

Se integró en el portal Next.js el flujo operativo principal de calificaciones preliminares y actas, consumiendo APIs Django y reutilizando servicios existentes del Bloque 5/6.

El bloque cubre:

- asignaciones docentes;
- captura preliminar por corte;
- resumen de cálculo académico;
- actas docentes;
- consulta y conformidad del discente;
- validación por jefatura de carrera;
- formalización por jefatura académica;
- consulta operativa de actas para Estadística/Admin;
- exportación PDF/XLSX desde endpoints backend existentes.

## Archivos principales modificados

Backend:

- `backend/config/urls.py`
- `backend/evaluacion/api_urls.py`
- `backend/evaluacion/api_views.py`
- `backend/evaluacion/tests.py`

Frontend:

- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/operacion-actas/ActaActionPanels.tsx`
- `frontend/src/components/operacion-actas/ActaExportActions.tsx`
- `frontend/src/components/operacion-actas/ActaStatusBadge.tsx`
- `frontend/src/components/operacion-actas/ActaTables.tsx`
- `frontend/src/components/operacion-actas/ActasFilters.tsx`
- `frontend/src/components/operacion-actas/GradeCaptureGrid.tsx`
- `frontend/src/components/operacion-actas/OperationCards.tsx`
- `frontend/src/components/operacion-actas/StudentConformityForm.tsx`

Rutas frontend nuevas:

- `frontend/src/app/docente/asignaciones/page.tsx`
- `frontend/src/app/docente/asignaciones/[id]/page.tsx`
- `frontend/src/app/docente/asignaciones/[id]/captura/[corte]/page.tsx`
- `frontend/src/app/docente/asignaciones/[id]/resumen/page.tsx`
- `frontend/src/app/docente/actas/page.tsx`
- `frontend/src/app/docente/actas/[id]/page.tsx`
- `frontend/src/app/discente/actas/page.tsx`
- `frontend/src/app/discente/actas/[detalleId]/page.tsx`
- `frontend/src/app/jefatura-carrera/actas/page.tsx`
- `frontend/src/app/jefatura-carrera/actas/[id]/page.tsx`
- `frontend/src/app/jefatura-academica/actas/page.tsx`
- `frontend/src/app/jefatura-academica/actas/[id]/page.tsx`
- `frontend/src/app/estadistica/actas/page.tsx`
- `frontend/src/app/estadistica/actas/[id]/page.tsx`

Documentación:

- `README.md`
- `docs/resumen_bloque10c5_calificaciones_actas_portal.md`

## APIs creadas

Docente:

- `GET /api/docente/asignaciones/`
- `GET /api/docente/asignaciones/<id>/`
- `GET|POST /api/docente/asignaciones/<id>/captura/<corte>/`
- `GET /api/docente/asignaciones/<id>/resumen/`
- `POST /api/docente/asignaciones/<id>/actas/generar/`
- `GET /api/docente/actas/`
- `GET /api/docente/actas/<acta_id>/`
- `POST /api/docente/actas/<acta_id>/regenerar/`
- `POST /api/docente/actas/<acta_id>/publicar/`
- `POST /api/docente/actas/<acta_id>/remitir/`

Discente:

- `GET /api/discente/actas/`
- `GET /api/discente/actas/<detalle_id>/`
- `POST /api/discente/actas/<detalle_id>/conformidad/`

Jefatura de carrera:

- `GET /api/jefatura-carrera/actas/pendientes/`
- `GET /api/jefatura-carrera/actas/<acta_id>/`
- `POST /api/jefatura-carrera/actas/<acta_id>/validar/`

Jefatura académica:

- `GET /api/jefatura-academica/actas/pendientes/`
- `GET /api/jefatura-academica/actas/<acta_id>/`
- `POST /api/jefatura-academica/actas/<acta_id>/formalizar/`

Estadística/Admin:

- `GET /api/estadistica/actas/`
- `GET /api/estadistica/actas/<acta_id>/`

## Servicios reutilizados

No se creó un motor alterno de cálculo ni de actas. Las APIs invocan servicios existentes:

- `ServicioCalculoAcademico`
- `crear_o_regenerar_borrador_acta`
- `publicar_acta`
- `remitir_acta`
- `validar_acta_jefatura_carrera`
- `formalizar_acta_jefatura_academica`
- `registrar_conformidad_discente`

## Reglas implementadas en portal

- Captura preliminar por corte con grid editable.
- Campo vacío limpia captura preliminar.
- Valores fuera de 0.0 a 10.0 se rechazan por backend.
- Captura bloqueada si existe acta avanzada del corte.
- Resumen de cálculo académico en solo lectura.
- Acciones de acta visibles solo cuando backend las reporta como permitidas.
- Confirmación antes de publicar, remitir, validar y formalizar.
- Formalización muestra advertencia fuerte sobre oficialización.
- Discente solo consulta su propio detalle de acta.
- Inconformidad requiere comentario.
- Después de remisión, la conformidad queda en solo lectura.
- Estadística consulta en solo lectura.

## Permisos

- Docente: asignaciones propias, captura, resumen y actas propias.
- Discente: actas publicadas propias y conformidad de su detalle.
- Jefatura de carrera: actas remitidas de su ámbito.
- Jefatura académica: actas validadas para formalización.
- Estadística/Admin: consulta operativa de actas.
- Backend conserva la autoridad real de permisos.

## Privacidad

- No se expone matrícula militar por defecto.
- Los listados nominales muestran grado/empleo y nombre institucional cuando existe.
- Discente no ve datos de otros discentes.
- No se usan tokens en `localStorage`.
- Las mutaciones usan sesión Django y CSRF.

## Exportaciones

Las pantallas de acta reutilizan endpoints existentes:

- `GET /api/exportaciones/actas/<acta_id>/pdf/`
- `GET /api/exportaciones/actas/<acta_id>/xlsx/`

El frontend no genera PDF/XLSX. Las descargas siguen registrando `RegistroExportacion` en backend y muestran folio técnico cuando el header `X-Registro-Exportacion-Id` está disponible.

## Validaciones ejecutadas

- `docker compose exec -T backend python manage.py check`: OK.
- `docker compose exec -T backend python manage.py makemigrations`: OK, sin cambios detectados.
- `docker compose exec -T backend python manage.py migrate`: OK, sin migraciones pendientes.
- `docker compose exec -T backend python manage.py makemigrations --check`: OK.
- `docker compose exec -T backend python manage.py test evaluacion`: OK, 84 tests.
- `docker compose exec -T backend python manage.py test usuarios relaciones`: OK, 129 tests.
- `docker compose exec -T backend python manage.py test`: OK, 401 tests.
- `docker compose exec -T frontend npm run lint`: OK.
- `docker compose exec -T frontend npm run build`: OK.

## Limitaciones

- No se implementó rectificación posterior a formalización.
- No se implementó devolución/rechazo formal de actas.
- No se implementó reapertura de actas.
- No se implementó importación Excel.
- No se implementó cierre/apertura de periodo en React.
- No se implementó bitácora transversal completa.
- Las notificaciones automáticas quedan pendientes si se desea ampliar la experiencia operacional.

## Pendientes

- `10C-6`: trayectoria, movimientos y cierre/apertura en portal.
- `9K`: bitácora transversal de eventos críticos.
- `10D`: pulido UX/UI y validación manual exhaustiva por perfil.
- `10E`: QA integral end-to-end.
