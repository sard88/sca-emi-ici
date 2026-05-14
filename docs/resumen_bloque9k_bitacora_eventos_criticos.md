# Bloque 9K - Bitacora transversal de eventos criticos

## Que se implemento

Se agrego una auditoria institucional append-only para registrar eventos criticos del sistema sin reemplazar `RegistroExportacion`. La nueva bitacora registra mutaciones operativas, transiciones de estado, bloqueos y exportaciones resumidas. `RegistroExportacion` continua como fuente detallada de salidas documentales PDF/XLSX/CSV.

## Archivos principales

- `backend/auditoria/models.py`
- `backend/auditoria/eventos.py`
- `backend/auditoria/services.py`
- `backend/auditoria/admin.py`
- `backend/auditoria/api_views.py`
- `backend/auditoria/api_urls.py`
- `backend/auditoria/migrations/0001_initial.py`
- `backend/usuarios/api_views.py`
- `backend/usuarios/admin_api_views.py`
- `backend/catalogos/api_views.py`
- `backend/evaluacion/api_views.py`
- `backend/evaluacion/services.py`
- `backend/trayectoria/api_views.py`
- `backend/relaciones/api_views.py`
- `backend/actas/api_views.py`
- `backend/reportes/services.py`
- `frontend/src/app/reportes/auditoria/page.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`

## Modelo

`BitacoraEventoCritico` guarda usuario, snapshots de usuario, rol/cargo de contexto, modulo, codigo/nombre de evento, severidad, resultado, objeto, estados anterior/nuevo, resumen, JSON sanitizado, request id, correlacion, IP, user agent, ruta, metodo HTTP y fecha de creacion.

El modelo bloquea `save()` sobre instancias existentes y `delete()` ordinario. El admin es de consulta, sin alta, cambio, borrado ni acciones masivas.

## Servicio

`auditoria.services` expone:

- `ServicioBitacoraEventos`
- `registrar_evento_critico`
- `registrar_evento_exitoso`
- `registrar_evento_fallido`
- `registrar_evento_bloqueado`
- `limpiar_payload_auditoria`
- `extraer_contexto_request`
- `construir_repr_objeto`
- `auditar_accion`
- `contexto_auditoria`

La auditoria no rompe el flujo principal salvo que `AUDITORIA_STRICT=True`.

## Eventos

Se definio catalogo en `backend/auditoria/eventos.py` para autenticacion, administracion, catalogos, evaluacion, actas, conformidad, trayectoria, movimientos, periodos, reportes y exportaciones.

## Endpoints

- `GET /api/auditoria/eventos/`
- `GET /api/auditoria/eventos/<id>/`
- `GET /api/auditoria/eventos/resumen/`
- `GET /api/exportaciones/auditoria/eventos/xlsx/`

El XLSX crea `RegistroExportacion` tipo `AUDITORIA_EVENTOS` y registra `AUDITORIA_EVENTOS_EXPORTADA` en `BitacoraEventoCritico`.

## Permisos

Backend autoriza consulta/exportacion para Admin, Estadistica, Jefatura academica y Jefatura pedagogica. Docente y Discente no acceden a la bitacora general.

## Privacidad

La sanitizacion enmascara llaves como `password`, `token`, `cookie`, `session`, `authorization`, `csrf`, `api_key`, `credential`, `firma` y `private_key`. No se guardan payloads completos de calificaciones, actas, historiales o reportes. Las integraciones guardan IDs, estados, conteos y resúmenes.

## Integraciones

- Autenticacion: login exitoso/fallido y logout.
- Administracion: usuarios, grados, unidades y cargos.
- Catalogos: recursos academicos, esquemas y componentes.
- Evaluacion: captura preliminar guardada, borrada y bloqueada.
- Actas: borrador, regeneracion, publicacion, remision, validacion, formalizacion y bloqueos.
- Conformidad: acuse, conforme, inconforme, rechazo sin comentario y bloqueo por remision.
- Trayectoria: extraordinarios, situaciones, bajas y reingresos.
- Movimientos: movimientos academicos y cambio de grupo.
- Periodos: diagnostico, cierre y apertura.
- Exportaciones: solicitud, generacion y fallo resumidos.

## Frontend minimo

`/reportes/auditoria` ahora muestra pestañas de Exportaciones y Eventos criticos. La pestaña de eventos permite filtrar por fecha, usuario, modulo, evento, resultado y severidad, y descarga XLSX mostrando el folio tecnico devuelto por backend.

## Pruebas ejecutadas

- `docker compose exec -T backend python manage.py check`
- `docker compose exec -T backend python manage.py migrate`
- `docker compose exec -T backend python manage.py makemigrations --check`
- `docker compose exec -T backend python manage.py test auditoria`
- `docker compose exec -T backend python manage.py test usuarios catalogos evaluacion actas trayectoria relaciones reportes`
- `docker compose exec -T backend python manage.py test`
- `docker compose exec -T frontend npm run lint`
- `docker compose exec -T frontend npm run build`

## Limitaciones

- No se implementa SIEM externo ni logs de infraestructura.
- No se audita cada consulta GET comun.
- No se guardan archivos exportados en la bitacora.
- No se implementan rectificacion/reapertura de actas, importacion Excel, firma digital, QR ni sello digital.
- Para jefatura de carrera se conserva restriccion institucional general de la API de bitacora; el filtrado fino por ambito queda pendiente si se requiere una matriz de autorizacion mas granular.

## Pendientes para 10D y 10E

- Refinar vistas por ambito para jefaturas de carrera si la institucion define reglas de alcance auditables por carrera/unidad.
- Agregar filtros visuales avanzados y detalle modal en frontend sin exponer payloads sensibles.
- Endurecer inmutabilidad a nivel base de datos si el despliegue institucional requiere controles adicionales fuera de Django.
