# Resumen Bloque 10C-2 - Integración de kárdex PDF en el portal

## Objetivo

El Bloque 10C-2 integra en el portal Next.js la exportación PDF del kárdex oficial implementada en el Bloque 9C.

El frontend no genera documentos, no construye el kárdex y no replica reglas académicas. El portal solo permite buscar o seleccionar discentes autorizados, disparar la descarga PDF contra el backend y mostrar la trazabilidad técnica de la exportación.

## Alcance implementado

Se implementó:

- endpoint backend read-only para listar discentes con kárdex exportable;
- cliente API frontend para consultar discentes exportables;
- cliente API frontend para descargar kárdex PDF;
- página `/reportes/kardex`;
- componentes visuales para búsqueda, tarjetas y descarga;
- navegación desde reportes, sidebar y dashboards autorizados;
- mensajes de éxito/error;
- lectura de `Content-Disposition`;
- lectura de `X-Registro-Exportacion-Id`;
- documentación técnica.

No se implementa kárdex Excel.

## Archivos modificados o creados

### Backend

- `backend/reportes/api_urls.py`
- `backend/reportes/api_views.py`
- `backend/reportes/tests.py`

### Frontend

- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/app/reportes/page.tsx`
- `frontend/src/app/reportes/kardex/page.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/reportes/ExportTraceInfo.tsx`
- `frontend/src/components/reportes/ReportCatalogCard.tsx`
- `frontend/src/components/reportes/KardexExportButton.tsx`
- `frontend/src/components/reportes/KardexExportCard.tsx`
- `frontend/src/components/reportes/KardexExportEmptyState.tsx`
- `frontend/src/components/reportes/KardexExportHelpText.tsx`
- `frontend/src/components/reportes/KardexExportSearch.tsx`

### Documentación

- `README.md`
- `docs/resumen_bloque10c2_integracion_kardex_pdf.md`

## APIs backend

### Listado de kárdex disponibles

`GET /api/exportaciones/kardex-disponibles/`

Parámetros opcionales:

- `q`: búsqueda por nombre, grado/empleo, carrera, grupo o ID interno.
- `carrera`: clave o ID de carrera.
- `situacion`: situación académica.
- `page_size`: límite de resultados.

Cada resultado incluye:

- `discente_id`
- `nombre_completo`
- `grado_empleo`
- `carrera`
- `plan_estudios`
- `antiguedad`
- `grupo_actual`
- `periodo_actual`
- `situacion_actual`
- `puede_exportar_pdf`
- `url_kardex_pdf`
- `motivo_no_disponible`

No incluye matrícula militar.

### Descarga PDF

`GET /api/exportaciones/kardex/<discente_id>/pdf/`

Este endpoint ya pertenece al Bloque 9C y se reutiliza sin reimplementar la generación documental.

Devuelve:

- `Content-Type: application/pdf`
- `Content-Disposition: attachment`
- `X-Registro-Exportacion-Id`

## Rutas frontend

### Kárdex oficial

`/reportes/kardex`

La página muestra:

- título y descripción institucional;
- texto de ayuda sobre uso institucional del kárdex;
- buscador de discentes;
- filtros de carrera y situación académica;
- tarjetas de discentes autorizados;
- botón `Exportar kárdex PDF`;
- folio técnico de auditoría cuando la descarga es exitosa;
- errores claros ante bloqueo o fallo.

### Reportes

`/reportes`

Se actualizó para mostrar:

- acceso rápido a `Kárdex oficial`;
- tarjeta de catálogo de `KARDEX_OFICIAL` con acción hacia `/reportes/kardex` cuando el backend lo devuelve como disponible.

## Componentes creados

### `KardexExportSearch`

Formulario de búsqueda con:

- texto libre;
- carrera;
- situación académica;
- botón de búsqueda.

### `KardexExportCard`

Tarjeta de discente exportable con:

- nombre;
- carrera;
- ID interno;
- plan;
- antigüedad;
- grupo vigente;
- situación académica;
- botón de descarga PDF.

### `KardexExportButton`

Botón especializado que reutiliza la infraestructura existente de exportación.

### `KardexExportEmptyState`

Estado vacío para resultados no encontrados o perfiles sin kárdex exportables.

### `KardexExportHelpText`

Texto institucional breve para explicar que el portal no genera el documento y que la salida queda auditada.

## Cambios en navegación

Se agregaron accesos para perfiles autorizados:

- Sidebar: acceso a `Kárdex oficial` dentro del módulo de reportes.
- Navegación móvil: acceso `Kárdex`.
- Dashboard Admin: tarjeta `Kárdex oficial`.
- Dashboard Estadística: tarjeta `Kárdex oficial PDF`.
- Dashboard Jefatura de carrera: tarjeta `Kárdex oficial`.
- Dashboard Jefatura académica: tarjeta `Kárdex oficial`.
- Dashboard Jefatura pedagógica: tarjeta `Kárdex oficial`.

No se agregó acceso a docentes ni discentes.

## Reglas de permisos

El frontend oculta la funcionalidad, pero el backend conserva la autoridad real.

### Permitidos visualmente

- Admin.
- Estadística.
- Jefatura de carrera.
- Jefatura académica.
- Jefatura pedagógica.

### No permitidos visualmente

- Discente.
- Docente.

### Backend

El endpoint `/api/exportaciones/kardex-disponibles/` devuelve resultados vacíos para perfiles no autorizados.

El endpoint `/api/exportaciones/kardex/<discente_id>/pdf/` bloquea usuarios no autorizados con `403`.

## Trazabilidad

Después de una descarga exitosa, la pantalla muestra:

- nombre del archivo;
- folio técnico de auditoría;
- tamaño aproximado.

La página `/reportes/exportaciones` continúa mostrando el `RegistroExportacion` generado por el Bloque 9C.

## Validaciones ejecutadas

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test reportes
docker compose exec -T backend python manage.py test trayectoria
docker compose exec -T backend python manage.py test
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
```

Resultados locales:

- `check`: OK.
- `makemigrations --check`: OK, sin cambios detectados.
- `test reportes`: 48 pruebas OK.
- `test trayectoria`: 25 pruebas OK.
- `test`: 348 pruebas OK.
- `frontend lint`: OK.
- `frontend build`: OK. La ruta `/reportes/kardex` se generó correctamente.

Nota: una ejecución inicial de `test trayectoria` chocó con la suite completa por creación simultánea de la base temporal `test_sca_emi_ici`. Se repitió aislada y pasó correctamente.

## Validación manual esperada

### Admin o Estadística

1. Iniciar sesión en el portal.
2. Entrar a `/reportes`.
3. Abrir `Kárdex oficial`.
4. Buscar un discente.
5. Descargar PDF.
6. Confirmar folio técnico visible.
7. Confirmar que la exportación aparece en `/reportes/exportaciones`.

### Jefatura de carrera

1. Entrar a `/reportes/kardex`.
2. Confirmar que solo aparecen discentes del ámbito autorizado.
3. Descargar un PDF autorizado.

### Docente

1. Confirmar que no aparece `Kárdex oficial`.
2. Intentar `/reportes/kardex`.
3. Debe mostrarse acceso denegado.

### Discente

1. Confirmar que no aparece `Reportes/Kárdex oficial`.
2. Intentar `/reportes/kardex`.
3. Debe mostrarse acceso denegado.
4. Si se prueba el endpoint directo, backend debe responder `403`.

## Limitaciones

La pantalla no muestra una previsualización del kárdex. Solo lista discentes autorizados y descarga el PDF oficial derivado.

El filtro por carrera depende de los resultados devueltos por el backend para el usuario actual.

No se genera notificación automática por cada descarga para evitar ruido operativo.

## Pendientes

Para bloques posteriores:

- kárdex Excel, si la institución lo autoriza;
- previsualización segura del kárdex, si se requiere;
- filtros avanzados por grupo/periodo;
- notificaciones o actividad reciente específica por exportación, si se decide;
- integración con folios institucionales definitivos;
- firma digital, QR o sello digital.

## Fuera de alcance

No se implementó:

- generación de kárdex en React;
- kárdex Excel;
- modelo `KardexOficial`;
- edición de kárdex;
- cambios a `ServicioKardex`;
- cambios a resultados oficiales;
- cambios a actas;
- cambios a historial;
- reportes de desempeño;
- reportes de situación académica;
- cuadro de aprovechamiento;
- importación Excel;
- firma digital;
- QR;
- sello digital;
- WebSockets;
- JWT;
- MFA/OTP.
