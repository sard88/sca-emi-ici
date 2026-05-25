# Bloque 10D-1 - Estabilizacion UX funcional del portal

## Objetivo

Se atendieron los hallazgos P1 del diagnostico 10D-0 para estabilizar la experiencia operativa del portal Next.js sin modificar reglas academicas, calculos, estados de actas, modelos ni migraciones. El backend Django sigue siendo la fuente de verdad; el frontend reduce errores de navegacion, permisos visuales y captura manual de identificadores.

## Hallazgos P1 corregidos

| ID | Estado | Correccion aplicada |
|---|---|---|
| 10D0-P1-001 | Atendido | `AppShell` ahora oculta el panel derecho por defecto; solo dashboards/home/perfil lo activan explicitamente. |
| 10D0-P1-002 | Atendido | Dashboard reemplaza enlaces a Django Admin por rutas Next.js existentes para usuarios, cargos, unidades y catalogos. |
| 10D0-P1-003 | Atendido | Kárdex institucional apunta a `/reportes/kardex`. |
| 10D0-P1-004 | Atendido | Jefatura pedagogica deja de enlazar la consulta Django antigua y usa reportes operativos/desempeno del portal. |
| 10D0-P1-005 | Atendido | Auditoria separa permisos visuales de exportaciones y eventos criticos. |
| 10D0-P1-006 | Atendido | Acciones de apertura/cierre se muestran solo a perfiles con operacion de trayectoria. |
| 10D0-P1-007 | Atendido | Extraordinarios y situaciones academicas usan selectores/buscadores autorizados. |
| 10D0-P1-008 | Atendido | Movimientos academicos y cambio de grupo usan selectores para discente, periodo y grupos. |
| 10D0-P1-009 | Atendido | Apertura de periodo usa selectores para origen cerrado y destino planificado/activo. |
| 10D0-P1-010 | Atendido | `RelationSelect` soporta filtros activos, busqueda, parametros contextuales y dependencias. |

## Archivos principales modificados

- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/dashboard/GeneralDashboard.tsx`
- `frontend/src/components/dashboard/ProfilePanel.tsx`
- `frontend/src/components/dashboard/DashboardCard.tsx`
- `frontend/src/components/dashboard/DashboardSidePanel.tsx`
- `frontend/src/components/layout/Topbar.tsx`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/lib/route-mapping.ts`
- `frontend/src/app/reportes/auditoria/page.tsx`
- `frontend/src/app/reportes/page.tsx`
- `frontend/src/components/admin-catalogos/RelationSelect.tsx`
- `frontend/src/components/admin-catalogos/FormFieldRenderer.tsx`
- `frontend/src/components/admin-catalogos/CatalogResourceForm.tsx`
- `frontend/src/components/admin-catalogos/CatalogResourcePage.tsx`
- `frontend/src/lib/admin-config.ts`
- `frontend/src/lib/catalogos-config.ts`
- `frontend/src/components/trayectoria-operativa/TrajectoryOperations.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `backend/trayectoria/api_views.py`
- `backend/trayectoria/api_urls.py`
- `backend/trayectoria/tests.py`
- `backend/catalogos/api_views.py`
- `backend/usuarios/admin_api_views.py`

## Cambios de layout

El panel derecho de actividad/calendario queda desactivado por defecto. Se activa explicitamente en:

- `/dashboard`
- dashboards/home por perfil
- `/perfil`

Las pantallas operativas, reportes densos, administracion, catalogos, actas, trayectoria, movimientos y periodos quedan en modo workspace sin panel derecho.

## Rutas antiguas reemplazadas

| Ruta heredada | Ruta portal |
|---|---|
| `/admin/usuarios/usuario/` | `/administracion/usuarios` |
| `/admin/usuarios/asignacioncargo/` | `/administracion/cargos` |
| `/admin/usuarios/unidadorganizacional/` | `/administracion/unidades` |
| `/admin/catalogos/` | `/catalogos` |
| `/trayectoria/kardex/` | `/reportes/kardex` |
| `/validacion/discente/carga/` | `/trayectoria/mi-historial` como mapeo defensivo; la tarjeta se retiro del dashboard discente. |
| `/evaluacion/actas/planeacion-evaluacion/consulta/` | `/reportes/operativos` |

`/admin/` se mantiene como acceso tecnico de Admin/soporte, no como flujo operativo principal.

## Permisos visuales ajustados

Se separaron tres capacidades:

- `canAccessAuditoriaEventos`
- `canAccessAuditoriaExportaciones`
- `canAccessAuditoria`

`/reportes/auditoria` muestra solo las pestanas que corresponden al perfil. Si el usuario no tiene ninguna capacidad, presenta acceso denegado. Esto evita que jefatura pedagogica vea una pestana de exportaciones que el backend puede rechazar con 403.

En periodos, `canOperateTrayectoria` gobierna botones criticos como abrir periodo, usar periodo como origen y cerrar periodo. Jefaturas conservan consulta y diagnostico si el backend lo permite, pero no ven acciones operativas de cierre/apertura.

## Formularios convertidos de texto libre a selectores

- Extraordinarios:
  - `inscripcion_materia_id` usa buscador de inscripciones candidatas a extraordinario.
  - `calificacion` usa numero con rango 0 a 10 y paso 0.1.

- Situaciones academicas:
  - `discente_id` usa buscador de historiales autorizados.
  - `situacion_codigo` usa catalogo activo.
  - `periodo_id` usa selector de periodos.

- Movimientos y cambio de grupo:
  - `discente_id` usa buscador autorizado.
  - `periodo_id` usa selector.
  - `tipo_movimiento` usa select de opciones validas del portal.
  - `grupo_origen_id` y `grupo_destino_id` usan selectores dependientes del periodo; destino excluye origen.

- Apertura de periodo:
  - `periodo_origen_id` muestra periodos cerrados.
  - `periodo_destino_id` muestra periodos planificados/activos.

## Endpoint read-only agregado

Se agrego:

- `GET /api/trayectoria/opciones/inscripciones-extraordinario/`

Caracteristicas:

- requiere autenticacion;
- solo perfiles que operan trayectoria;
- filtra por `q`, `periodo`, `carrera` y `grupo`;
- devuelve inscripciones candidatas con contexto academico minimo;
- no expone matricula militar;
- no modifica reglas academicas ni ejecuta mutaciones.

## Mejoras de RelationSelect

`RelationSelect` ahora soporta:

- `activeOnly`
- `queryParams`
- `searchEnabled`
- `minSearchLength`
- `disabledReason`
- dependencias desde `FormFieldRenderer`
- filtrado defensivo de registros activos en frontend si el backend no aplica el filtro.

Las configuraciones de administracion y catalogos usan opciones activas/contextuales para carreras, planes, antiguedades, periodos, materias, programas, usuarios, grados, unidades y cargos.

## Privacidad

El bloque conserva las reglas del diagnostico:

- no se muestra matricula militar por defecto;
- los buscadores de trayectoria usan endpoints autenticados;
- no se usan tokens ni cookies en pantalla;
- auditoria no expone payloads completos desde la navegacion visual;
- Django conserva permisos reales de dominio.

## Validaciones ejecutadas

- `docker compose exec -T frontend npm run lint` - OK
- `docker compose exec -T frontend npm run build` - OK
- `docker compose exec -T backend python manage.py check` - OK
- `docker compose exec -T backend python manage.py makemigrations --check` - OK
- `docker compose exec -T backend python manage.py test trayectoria` - OK
- `docker compose exec -T backend python manage.py test relaciones` - OK
- `docker compose exec -T backend python manage.py test catalogos usuarios` - OK
- `docker compose exec -T backend python manage.py test` - OK, 459 tests

Nota: un primer intento de `test trayectoria` fallo porque se lanzo en paralelo con otra suite y ambas compitieron por la misma base `test_sca_emi_ici`; se relanzo en solitario y paso correctamente.

## Pendientes para 10D-2 y 10D-3

- Reordenar sidebar y dashboard por intencion de uso.
- Consolidar tarjetas duplicadas o muy similares por perfil.
- Resolver pantalla especifica de carga academica del discente.
- Mejorar filtros de reportes con selectores graduales.
- Definir una consulta academica pedagogica dedicada si se requiere.
- Unificar terminologia, microcopy, estados vacios e iconografia.
