# Resumen Bloque 10C-3B - Integración visual de reportes de desempeño

## Objetivo

Integrar en el portal Next.js los reportes de desempeño académico y cuadro de aprovechamiento implementados en el Bloque 9G-H.

El frontend no genera XLSX, no genera PDF, no calcula métricas y no duplica reglas académicas. Solo consume APIs Django, muestra datos autorizados y dispara descargas auditadas.

## Qué Se Implementó

Se agregó un módulo visual de reportes de desempeño con:

- índice general de reportes de desempeño;
- ruta dinámica por reporte;
- vista previa JSON;
- filtros visuales compatibles con backend;
- tabla dinámica basada en columnas devueltas por Django;
- resumen de métricas cuando el backend entrega `resumen`;
- descarga XLSX con los mismos filtros aplicados;
- lectura de `Content-Disposition`;
- lectura de `X-Registro-Exportacion-Id`;
- mensaje de éxito con folio técnico;
- avisos de privacidad para reportes nominales;
- acceso desde `/reportes`, sidebar y dashboards autorizados.

## Rutas Frontend

- `/reportes/desempeno`
- `/reportes/desempeno/aprobados-reprobados`
- `/reportes/desempeno/promedios`
- `/reportes/desempeno/distribucion`
- `/reportes/desempeno/exentos`
- `/reportes/desempeno/docentes`
- `/reportes/desempeno/cohorte`
- `/reportes/desempeno/reprobados-nominal`
- `/reportes/desempeno/cuadro-aprovechamiento`

Ruta dinámica:

- `/reportes/desempeno/[slug]`

## Reportes Integrados

1. Aprobados y reprobados.
2. Promedios académicos.
3. Distribución de calificaciones.
4. Exentos por asignatura.
5. Desempeño por docente.
6. Desempeño por cohorte.
7. Reprobados nominal.
8. Cuadro de aprovechamiento académico.

## APIs Consumidas

### Vista Previa JSON

- `GET /api/reportes/desempeno/aprobados-reprobados/`
- `GET /api/reportes/desempeno/promedios/`
- `GET /api/reportes/desempeno/distribucion/`
- `GET /api/reportes/desempeno/exentos/`
- `GET /api/reportes/desempeno/docentes/`
- `GET /api/reportes/desempeno/cohorte/`
- `GET /api/reportes/desempeno/reprobados-nominal/`
- `GET /api/reportes/desempeno/cuadro-aprovechamiento/`

### Descarga XLSX

- `GET /api/exportaciones/reportes/aprobados-reprobados/xlsx/`
- `GET /api/exportaciones/reportes/promedios/xlsx/`
- `GET /api/exportaciones/reportes/distribucion/xlsx/`
- `GET /api/exportaciones/reportes/exentos/xlsx/`
- `GET /api/exportaciones/reportes/desempeno-docente/xlsx/`
- `GET /api/exportaciones/reportes/desempeno-cohorte/xlsx/`
- `GET /api/exportaciones/reportes/reprobados-nominal/xlsx/`
- `GET /api/exportaciones/reportes/cuadro-aprovechamiento/xlsx/`

## Archivos Modificados

### Frontend

- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/lib/reportes-desempeno.ts`
- `frontend/src/app/reportes/page.tsx`
- `frontend/src/app/reportes/desempeno/page.tsx`
- `frontend/src/app/reportes/desempeno/[slug]/page.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceMetricCard.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportBadge.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportCard.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportDownloadButton.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportFilters.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportPage.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportPrivacyNotice.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportSummaryBar.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportTable.tsx`

### Documentación

- `README.md`
- `docs/resumen_bloque10c3b_reportes_desempeno_portal.md`

## Componentes Creados

### `PerformanceReportCard`

Tarjeta del índice para cada reporte de desempeño. Muestra formato disponible, PDF pendiente, tipo agregado/nominal y aviso de privacidad si aplica.

### `PerformanceReportPage`

Pantalla genérica que consulta vista previa JSON, aplica filtros, muestra resumen, muestra tabla, descarga XLSX y presenta folio técnico de exportación.

### `PerformanceReportFilters`

Renderiza filtros dinámicos definidos por configuración.

### `PerformanceReportTable`

Tabla flexible basada en columnas devueltas por backend. Formatea booleanos, promedios, porcentajes y valores vacíos.

### `PerformanceReportDownloadButton`

Dispara descarga XLSX usando la infraestructura Blob existente y `credentials: "include"`.

### `PerformanceReportSummaryBar`

Muestra total de registros, columnas, disponibilidad y hasta cuatro métricas entregadas por `resumen`.

### `PerformanceReportPrivacyNotice`

Muestra aviso institucional para reportes nominales o sensibles.

### `PerformanceMetricCard`

Tarjeta compacta para métricas de resumen.

### `PerformanceReportBadge`

Badge visual para estados como XLSX disponible, PDF pendiente, nominal o agregado.

## Configuración De Reportes

Archivo:

- `frontend/src/lib/reportes-desempeno.ts`

Define para cada reporte:

- slug;
- título;
- descripción;
- ruta;
- tipo documental;
- endpoint JSON;
- endpoint XLSX;
- formatos disponibles;
- PDF pendiente;
- filtros aplicables;
- columnas destacadas;
- roles sugeridos;
- ayuda contextual;
- si es nominal o agregado;
- si contiene datos sensibles;
- aviso de privacidad.

## Filtros Implementados

- `periodo`
- `carrera`
- `grupo`
- `asignatura`
- `docente`
- `antiguedad`
- `anio_formacion`
- `semestre`
- `fecha_desde`
- `fecha_hasta`
- `incluir_no_numericas`
- `incluir_extraordinarios`
- `incluir_con_reprobadas`
- `rango_aprovechamiento`

Los filtros vacíos se eliminan antes de llamar al backend. La descarga XLSX utiliza los mismos filtros aplicados en pantalla.

## Reglas De Permisos

Pueden ver el módulo:

- Admin.
- Estadística.
- Jefatura académica.
- Jefatura pedagógica.
- Jefatura de carrera.

No ven el módulo:

- Docente.
- Discente.

Jefatura de carrera puede entrar al módulo, pero el backend filtra por ámbito institucional. El frontend no intenta resolver permisos académicos complejos.

## Privacidad

Los reportes nominales muestran aviso visual:

- Exentos por asignatura.
- Reprobados nominal.
- Cuadro de aprovechamiento.

El frontend no solicita matrícula militar ni datos adicionales por APIs alternas. Solo muestra lo que Django entrega para el perfil autenticado.

## Integración Con Navegación

Se agregó acceso a Reportes de desempeño en:

- `/reportes`;
- sidebar de Reportes y exportaciones;
- navegación móvil;
- dashboards de Admin, Estadística, Jefatura de carrera, Jefatura académica y Jefatura pedagógica.

No se agregó a dashboards de Docente ni Discente.

## Validaciones Ejecutadas

- `docker compose exec -T frontend npm run lint` - OK.
- `docker compose exec -T frontend npm run build` - OK.
- `docker compose exec -T backend python manage.py check` - OK.
- `docker compose exec -T backend python manage.py makemigrations --check` - OK, sin cambios detectados.
- `docker compose exec -T backend python manage.py test reportes` - OK, 65 pruebas.
- `docker compose exec -T backend python manage.py test` - OK, 365 pruebas.

## Limitaciones

- El PDF del cuadro de aprovechamiento permanece pendiente porque el Bloque 9G-H expone XLSX como formato implementado.
- No se agregaron gráficas ni dashboard BI.
- No se agregaron nuevos cálculos ni endpoints backend.
- La vista previa queda limitada a `limit=100`; el XLSX debe usarse para análisis completo.

## Pendientes

Para 9I-M-E y 10C-3C:

- reportes de situación académica;
- historial académico exportable;
- movimientos académicos;
- posibles visualizaciones o gráficas;
- integración de nuevos reportes cuando existan endpoints backend.
