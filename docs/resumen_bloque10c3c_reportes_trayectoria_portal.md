# Resumen Bloque 10C-3C - Integración visual de reportes de trayectoria y situación académica

## Objetivo

Integrar en el portal Next.js los reportes de situación académica, movimientos académicos e historial académico interno implementados en el Bloque 9I-M-E.

El portal no genera XLSX, no calcula reportes, no genera PDF y no modifica datos académicos. Consume APIs Django, muestra datos autorizados y dispara descargas XLSX auditadas.

## Alcance implementado

Se agregó el módulo visual:

- `/reportes/trayectoria`
- `/reportes/trayectoria/[slug]`

Reportes integrados:

- Extraordinarios registrados.
- Situación académica actual.
- Bajas temporales.
- Bajas definitivas.
- Reingresos.
- Egresables / egresados.
- Situación académica agregada.
- Movimientos académicos.
- Cambios de grupo.
- Historial académico interno institucional.
- Historial interno por discente.

## Archivos modificados

- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/lib/reportes-trayectoria.ts`
- `frontend/src/app/reportes/page.tsx`
- `frontend/src/app/reportes/trayectoria/page.tsx`
- `frontend/src/app/reportes/trayectoria/[slug]/page.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportsIndex.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportPage.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportCard.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportFilters.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportTable.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportSummaryBar.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportDownloadButton.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportBadge.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportPrivacyNotice.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryMetricCard.tsx`
- `frontend/src/components/reportes/trayectoria/InternalHistoryDiscenteSelector.tsx`
- `README.md`
- `docs/resumen_bloque10c3c_reportes_trayectoria_portal.md`

## Rutas frontend

- `GET /reportes/trayectoria`
- `GET /reportes/trayectoria/extraordinarios`
- `GET /reportes/trayectoria/situacion-actual`
- `GET /reportes/trayectoria/bajas-temporales`
- `GET /reportes/trayectoria/bajas-definitivas`
- `GET /reportes/trayectoria/reingresos`
- `GET /reportes/trayectoria/egresables`
- `GET /reportes/trayectoria/situacion-agregado`
- `GET /reportes/trayectoria/movimientos-academicos`
- `GET /reportes/trayectoria/cambios-grupo`
- `GET /reportes/trayectoria/historial-interno`
- `GET /reportes/trayectoria/historial-interno-discente`

La ruta dinámica `/reportes/trayectoria/[slug]` resuelve cada reporte desde configuración centralizada.

## Configuración de reportes

Se creó `frontend/src/lib/reportes-trayectoria.ts` con:

- slug;
- título;
- descripción;
- ruta;
- tipo documental;
- endpoint JSON;
- endpoint XLSX;
- formatos disponibles;
- estado PDF pendiente;
- filtros aplicables;
- columnas destacadas;
- roles sugeridos;
- ayuda contextual;
- indicador nominal/agregado;
- indicador de datos sensibles;
- aviso de privacidad;
- bandera `requiereDiscenteId` para historial interno por discente.

## APIs consumidas

Vista previa JSON:

- `GET /api/reportes/situacion/extraordinarios/`
- `GET /api/reportes/situacion/actual/`
- `GET /api/reportes/situacion/bajas-temporales/`
- `GET /api/reportes/situacion/bajas-definitivas/`
- `GET /api/reportes/situacion/reingresos/`
- `GET /api/reportes/situacion/egresables/`
- `GET /api/reportes/situacion/agregado/`
- `GET /api/reportes/movimientos/`
- `GET /api/reportes/movimientos/cambios-grupo/`
- `GET /api/reportes/historial-interno/`
- `GET /api/reportes/historial-interno/<discente_id>/`

Descarga XLSX:

- `GET /api/exportaciones/reportes/extraordinarios/xlsx/`
- `GET /api/exportaciones/reportes/situacion-actual/xlsx/`
- `GET /api/exportaciones/reportes/bajas-temporales/xlsx/`
- `GET /api/exportaciones/reportes/bajas-definitivas/xlsx/`
- `GET /api/exportaciones/reportes/reingresos/xlsx/`
- `GET /api/exportaciones/reportes/egresables/xlsx/`
- `GET /api/exportaciones/reportes/situacion-agregado/xlsx/`
- `GET /api/exportaciones/reportes/movimientos-academicos/xlsx/`
- `GET /api/exportaciones/reportes/cambios-grupo/xlsx/`
- `GET /api/exportaciones/reportes/historial-interno/xlsx/`
- `GET /api/exportaciones/reportes/historial-interno/<discente_id>/xlsx/`

La descarga usa `credentials: "include"`, lee `Content-Disposition`, lee `X-Registro-Exportacion-Id`, crea un `Blob`, dispara la descarga y libera la URL temporal.

## Filtros implementados

- `periodo`
- `carrera`
- `grupo`
- `plan`
- `antiguedad`
- `anio_formacion`
- `semestre`
- `asignatura`
- `docente`
- `discente`
- `discente_id`
- `situacion`
- `tipo_movimiento`
- `grupo_origen`
- `grupo_destino`
- `aprobado`
- `baja_abierta`
- `fecha_desde`
- `fecha_hasta`
- `incluir_extraordinarios`
- `incluir_eventos`
- `incluir_movimientos`

Los filtros vacíos se eliminan antes de consultar o descargar. La descarga usa los mismos filtros aplicados en la vista previa.

## Reglas de permisos

Pueden ver el módulo:

- Admin.
- Estadística.
- Jefatura académica.
- Jefatura pedagógica.
- Jefatura de carrera.

No pueden ver el módulo:

- Docente.
- Discente.

La restricción visual se implementa con `canAccessReportesTrayectoria(user)`, pero el backend sigue siendo la autoridad real.

## Reglas de privacidad

- Los reportes nominales muestran aviso de información académica sensible.
- Historial interno institucional e historial por discente indican que no son kárdex oficial.
- No se acepta matrícula militar como identificador principal para historial interno por discente.
- La tabla oculta defensivamente columnas cuyo `key` contenga `matricula`.
- El frontend no consulta datos nominales por APIs alternas.

## Historial interno por discente

El reporte `historial-interno-discente` usa la misma ruta dinámica:

- `/reportes/trayectoria/historial-interno-discente`

Comportamiento:

- requiere capturar `discente_id`;
- no consulta el backend sin `discente_id`;
- no descarga XLSX sin `discente_id`;
- usa `GET /api/reportes/historial-interno/<discente_id>/`;
- descarga desde `GET /api/exportaciones/reportes/historial-interno/<discente_id>/xlsx/`;
- muestra aviso de que el historial interno no es kárdex oficial.

## Navegación

Se agregó acceso a:

- `/reportes/trayectoria` desde `/reportes`;
- sidebar de escritorio;
- navegación móvil;
- dashboards de Admin, Estadística, Jefatura académica, Jefatura pedagógica y Jefatura de carrera.

No se agregó a Docente ni Discente.

## Validaciones ejecutadas

- `docker compose exec -T frontend npm run lint`: OK.
- `docker compose exec -T frontend npm run build`: OK.
- `docker compose exec -T backend python manage.py check`: OK.
- `docker compose exec -T backend python manage.py makemigrations --check`: OK, sin cambios pendientes.
- `docker compose exec -T backend python manage.py test reportes`: OK, 74 tests.
- `docker compose exec -T backend python manage.py test`: OK, 374 tests.

## Limitaciones

- No se implementaron nuevos reportes backend.
- No se implementó PDF.
- No se implementó kárdex Excel.
- No se implementó importación Excel.
- No se implementó bitácora transversal completa.
- No se implementó edición de eventos o movimientos desde React.
- No se implementaron gráficas.

## Pendientes

- Bloques futuros pueden integrar bitácora transversal completa.
- Bloques futuros pueden agregar importación Excel si se autoriza.
- Bloques futuros pueden agregar reportes PDF institucionales si existen plantillas aprobadas.
