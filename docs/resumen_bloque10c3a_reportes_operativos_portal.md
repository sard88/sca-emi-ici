# Resumen Bloque 10C-3A - Integración visual de reportes operativos

## Objetivo

Integrar en el portal Next.js los reportes operativos de actas, validaciones y exportaciones realizadas implementados en el Bloque 9F-J-L.

El frontend no genera XLSX, no calcula reportes y no duplica permisos. Solo consume APIs Django, muestra datos autorizados y dispara descargas auditadas.

## Qué Se Implementó

Se agregó una sección visual para reportes operativos:

- Índice general de reportes operativos.
- Página dinámica para cada reporte.
- Vista previa JSON con tabla dinámica.
- Filtros visuales compatibles con backend.
- Descarga XLSX con los mismos filtros aplicados.
- Lectura de `Content-Disposition`.
- Lectura de `X-Registro-Exportacion-Id`.
- Mensaje de éxito con folio técnico.
- Mensajes claros de error y acceso denegado.
- Accesos desde `/reportes`, sidebar y dashboards autorizados.

## Rutas Frontend

- `/reportes/operativos`
- `/reportes/operativos/actas-estado`
- `/reportes/operativos/actas-pendientes`
- `/reportes/operativos/inconformidades`
- `/reportes/operativos/sin-conformidad`
- `/reportes/operativos/actas-formalizadas`
- `/reportes/operativos/validaciones-acta`
- `/reportes/operativos/exportaciones-realizadas`

La ruta específica usa una pantalla dinámica:

- `/reportes/operativos/[slug]`

## Reportes Integrados

1. Actas por estado.
2. Actas pendientes de validación.
3. Actas con inconformidades.
4. Actas sin conformidad de discentes.
5. Actas formalizadas.
6. Historial de validaciones de acta.
7. Exportaciones realizadas.

## APIs Consumidas

### Vista Previa JSON

- `GET /api/reportes/operativos/actas-estado/`
- `GET /api/reportes/operativos/actas-pendientes/`
- `GET /api/reportes/operativos/inconformidades/`
- `GET /api/reportes/operativos/sin-conformidad/`
- `GET /api/reportes/operativos/actas-formalizadas/`
- `GET /api/reportes/operativos/validaciones-acta/`
- `GET /api/reportes/operativos/exportaciones-realizadas/`

### Descarga XLSX

- `GET /api/exportaciones/reportes/actas-estado/xlsx/`
- `GET /api/exportaciones/reportes/actas-pendientes/xlsx/`
- `GET /api/exportaciones/reportes/inconformidades/xlsx/`
- `GET /api/exportaciones/reportes/sin-conformidad/xlsx/`
- `GET /api/exportaciones/reportes/actas-formalizadas/xlsx/`
- `GET /api/exportaciones/reportes/validaciones-acta/xlsx/`
- `GET /api/exportaciones/reportes/exportaciones-realizadas/xlsx/`

## Archivos Modificados

### Frontend

- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/lib/reportes-operativos.ts`
- `frontend/src/app/reportes/page.tsx`
- `frontend/src/app/reportes/operativos/page.tsx`
- `frontend/src/app/reportes/operativos/[slug]/page.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportBadge.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportCard.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportDownloadButton.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportFilters.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportPage.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportSummaryBar.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportTable.tsx`

### Documentación

- `README.md`
- `docs/resumen_bloque10c3a_reportes_operativos_portal.md`

## Componentes Creados

### `OperativeReportCard`

Tarjeta del índice para cada reporte operativo.

### `OperativeReportPage`

Pantalla genérica que:

- consulta vista previa JSON;
- aplica filtros;
- muestra resumen;
- muestra tabla;
- descarga XLSX;
- muestra folio técnico de exportación.

### `OperativeReportFilters`

Renderiza filtros dinámicos por configuración de reporte.

### `OperativeReportTable`

Tabla flexible basada en columnas devueltas por backend.

### `OperativeReportDownloadButton`

Dispara descarga XLSX con `credentials: "include"` usando la infraestructura de Blob existente.

### `OperativeReportSummaryBar`

Muestra total de registros, columnas y disponibilidad.

### `OperativeReportBadge`

Badge visual para estados como XLSX disponible y PDF pendiente.

## Configuración De Reportes

Archivo:

- `frontend/src/lib/reportes-operativos.ts`

Define:

- slug;
- título;
- descripción;
- ruta;
- tipo documental;
- endpoint JSON;
- endpoint XLSX;
- filtros;
- columnas destacadas;
- roles sugeridos;
- ayuda contextual.

Esto evita duplicar lógica en siete páginas distintas.

## Filtros Implementados

### Comunes De Actas

- `periodo`
- `carrera`
- `grupo`
- `asignatura`
- `docente`
- `corte`
- `estado_acta`
- `fecha_desde`
- `fecha_hasta`

### Pendientes

- filtros comunes;
- `tipo_pendiente`

### Validaciones

- `periodo`
- `carrera`
- `grupo`
- `usuario`
- `etapa_validacion`
- `accion`
- `cargo`
- `fecha_desde`
- `fecha_hasta`

### Exportaciones Realizadas

- `fecha_desde`
- `fecha_hasta`
- `usuario`
- `tipo_documento`
- `formato`
- `estado_exportacion`

Los filtros vacíos se eliminan antes de llamar al backend.

## Permisos Visuales

Se agregó `canAccessReportesOperativos`.

Pueden ver la sección:

- Admin.
- Estadística.
- Jefatura de carrera.
- Jefatura académica.
- Jefatura pedagógica.

No ven la sección:

- Discente.
- Docente.

Docente conserva `/reportes/actas` para actas propias.

El backend sigue bloqueando usuarios no autorizados aunque intenten entrar por URL directa o llamar endpoints manualmente.

## Integración Con Navegación

Se agregó acceso a Reportes operativos en:

- `/reportes`;
- sidebar desktop;
- navegación móvil;
- dashboards por perfil autorizado.

También se enlazan tarjetas del catálogo cuando el backend devuelve reportes operativos como disponibles.

## Descargas y Auditoría

La descarga XLSX:

- usa `fetch` con `credentials: "include"`;
- conserva filtros aplicados;
- recibe Blob desde backend;
- dispara descarga local;
- libera URL temporal;
- lee nombre de archivo desde `Content-Disposition`;
- lee folio desde `X-Registro-Exportacion-Id`;
- muestra el folio técnico en pantalla.

El historial `/reportes/exportaciones` continúa mostrando el `RegistroExportacion` generado por backend.

## Validaciones Ejecutadas

Frontend:

- `docker compose exec -T frontend npm run lint`
- `docker compose exec -T frontend npm run build`

Backend:

- `docker compose exec -T backend python manage.py check`
- `docker compose exec -T backend python manage.py makemigrations --check`
- `docker compose exec -T backend python manage.py test reportes`
- `docker compose exec -T backend python manage.py test`

Resultados:

- Frontend lint: OK.
- Frontend build: OK.
- Backend check: OK.
- Migraciones pendientes: OK, sin cambios.
- `test reportes`: 57 pruebas OK.
- Suite backend completa: 357 pruebas OK.

## Limitaciones

- No se implementa PDF para reportes operativos.
- No se crean reportes nuevos.
- No se implementa paginación visual avanzada.
- No se cargan catálogos para selects dinámicos; cuando no hay endpoint de opciones, se usan campos de texto o selects simples.
- No se agregan gráficas ni indicadores.

## Pendientes Para 9G-H, 9I-M-E y 10C-3B/C

- Reportes de desempeño académico.
- Cuadro de aprovechamiento.
- Reportes de situación académica.
- Historial académico exportable.
- Kárdex Excel.
- PDF de reportes operativos.
- Visualizaciones o gráficas institucionales.
- Filtros con catálogos vivos para periodo, carrera, grupo y asignatura.
