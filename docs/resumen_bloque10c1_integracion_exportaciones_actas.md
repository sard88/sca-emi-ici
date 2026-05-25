# Resumen Bloque 10C-1 - Integración de exportaciones de actas en el portal

## Objetivo

El Bloque 10C-1 integra visualmente en el portal Next.js las exportaciones de actas ya implementadas en los Bloques 9A y 9B. El frontend no genera documentos; solo consume APIs Django, lista documentos autorizados y dispara descargas PDF/XLSX con auditoría.

## Qué se implementó

- Página `/reportes` para catálogo documental e historial reciente.
- Página `/reportes/actas` para listar actas exportables por perfil y descargar PDF/XLSX.
- Página `/reportes/exportaciones` para historial de exportaciones.
- Página `/reportes/auditoria` para consulta institucional de exportaciones en perfiles autorizados.
- Endpoint read-only `/api/exportaciones/actas-disponibles/` para listar actas que el usuario puede ver/exportar.
- Lectura de `Content-Disposition` y `X-Registro-Exportacion-Id` en descargas desde el portal.
- Exposición CORS segura de `Content-Disposition` y `X-Registro-Exportacion-Id` sin abrir orígenes arbitrarios.
- Componentes visuales reutilizables para catálogo, estados, historial, tarjetas de acta y acciones de exportación.
- Navegación y accesos rápidos actualizados para reemplazar placeholders de reportes.

## Archivos modificados

- `backend/core/middleware.py`
- `backend/core/portal_services.py`
- `backend/reportes/api_urls.py`
- `backend/reportes/api_views.py`
- `backend/reportes/tests.py`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/reportes/*`
- `frontend/src/app/reportes/*`
- `README.md`

## Rutas frontend

- `/reportes`
- `/reportes/actas`
- `/reportes/exportaciones`
- `/reportes/auditoria`

## APIs consumidas

- `GET /api/reportes/catalogo/`
- `GET /api/exportaciones/`
- `GET /api/auditoria/exportaciones/`
- `GET /api/exportaciones/actas-disponibles/`
- `GET /api/exportaciones/actas/<acta_id>/pdf/`
- `GET /api/exportaciones/actas/<acta_id>/xlsx/`
- `GET /api/exportaciones/asignaciones/<asignacion_docente_id>/calificacion-final/pdf/`
- `GET /api/exportaciones/asignaciones/<asignacion_docente_id>/calificacion-final/xlsx/`

## Backend nuevo

Se agregó el endpoint:

```text
GET /api/exportaciones/actas-disponibles/
```

Devuelve solo actas exportables para el usuario autenticado:

- Docente: actas propias.
- Estadística/Admin/Jefaturas académicas/pedagógicas: actas autorizadas de consulta amplia.
- Jefatura de carrera: actas de su ámbito de carrera cuando se puede inferir.
- Discente: no lista actas completas de grupo.

El endpoint no devuelve matrícula ni datos sensibles de discentes.

## Componentes frontend creados

- `ReportCatalogCard`
- `ExportHistoryTable`
- `ExportActionButton`
- `ExportFormatMenu`
- `DownloadStatusToast`
- `ExportStatusBadge`
- `DocumentStateBadge`
- `ReportAvailabilityBadge`
- `ExportTraceInfo`
- `ActaExportCard`
- `EmptyExportsState`

## Descargas

Las descargas usan `fetch` con:

- `credentials: "include"`
- sesión Django existente;
- sin tokens en `localStorage`;
- blob temporal del navegador;
- liberación con `URL.revokeObjectURL`;
- lectura de `Content-Disposition` para nombre de archivo;
- lectura de `X-Registro-Exportacion-Id` para mostrar folio técnico.

## Reglas de permisos

El frontend oculta opciones no permitidas, pero el backend sigue siendo la autoridad real.

- Admin ve catálogo, actas, historial y auditoría.
- Estadística ve catálogo, actas e historial/auditoría institucional según permisos.
- Docente ve solo sus actas exportables.
- Jefatura de carrera ve actas del ámbito autorizado.
- Jefatura académica/pedagógica ve consulta documental autorizada.
- Discente no ve reportes globales, kárdex oficial ni actas completas de grupo.

## Pendientes para 10C completo / 9C

- Integrar kárdex PDF cuando exista Bloque 9C.
- Integrar reportes de desempeño, situación académica y cuadros de aprovechamiento cuando existan sus generadores.
- Convertir actividad reciente de exportaciones en una fuente institucional más completa si se requiere.
- Añadir filtros avanzados y paginación formal en tablas de exportaciones.
- Integrar notificaciones automáticas por exportación solo si la política institucional lo solicita.

## Validación manual final

El 13 de mayo de 2026 se validó manualmente el acceso al portal después de reiniciar el contenedor frontend por una caché temporal de Next.js.

Resultado:

- `db`, `backend` y `frontend` arriba en Docker Compose.
- `GET http://localhost:8000/health/`: `200 OK`.
- `GET http://localhost:3000/login`: `200 OK`.
- Portal accesible desde navegador.
- Usuario pudo probar el flujo visual y confirmó que funciona.

El incidente observado fue:

- `Cannot find module './873.js'` en frontend.

Acción aplicada:

- Reinicio del contenedor `frontend`.

Conclusión:

- El error correspondía a caché `.next` inconsistente durante desarrollo, no a falla funcional del Bloque 10C-1.
- El Bloque 10C-1 queda cerrado funcionalmente.

## Validaciones

Validaciones esperadas:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test reportes
docker compose exec -T backend python manage.py test
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
```

Resultados locales:

- `backend python manage.py check`: OK.
- `backend python manage.py makemigrations --check`: OK, sin migraciones pendientes.
- `backend python manage.py test reportes`: 31 pruebas OK.
- `backend python manage.py test`: 331 pruebas OK.
- `frontend npm run lint`: OK.
- `frontend npm run build`: OK, rutas `/reportes`, `/reportes/actas`, `/reportes/exportaciones` y `/reportes/auditoria` compiladas.
- `docker compose ps`: `db`, `backend` y `frontend` arriba; `db` saludable.
