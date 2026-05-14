# Bloque 10C-4 - Interfaces administrativas y catálogos académicos

## Objetivo

Implementar en el portal Next.js una primera interfaz operativa para administración institucional y catálogos académicos, consumiendo APIs Django y conservando Django Admin como respaldo técnico.

El bloque no reemplaza Django Admin, no modifica reglas de negocio académicas y no incorpora flujos de actas, cierre/apertura, importación Excel ni bitácora transversal.

## Qué se implementó

- Módulo `/administracion` para usuarios, grado/empleo, unidades organizacionales, asignaciones de cargo y roles de solo lectura.
- Módulo `/catalogos` para carreras, planes, antigüedades, periodos, grupos, materias, programas de asignatura, esquemas de evaluación, componentes, situaciones académicas y resultados académicos.
- APIs JSON backend para listados, detalle, creación, edición e inactivación lógica donde aplica.
- Cliente API genérico en Next.js para recursos administrativos y catálogos.
- Componentes reutilizables para índices, tarjetas, tablas, filtros, formularios, selects relacionales, errores backend y acciones de activación/inactivación.
- Integración de navegación en Sidebar y dashboards para perfiles autorizados.
- Pruebas backend de permisos y validaciones críticas.

## Rutas frontend

Administración:

- `/administracion`
- `/administracion/[slug]`
- `/administracion/[slug]/[id]`

Recursos configurados:

- `/administracion/usuarios`
- `/administracion/grados-empleos`
- `/administracion/unidades`
- `/administracion/cargos`
- `/administracion/roles`

Catálogos:

- `/catalogos`
- `/catalogos/[slug]`
- `/catalogos/[slug]/[id]`

Recursos configurados:

- `/catalogos/carreras`
- `/catalogos/planes`
- `/catalogos/antiguedades`
- `/catalogos/periodos`
- `/catalogos/grupos`
- `/catalogos/materias`
- `/catalogos/programas-asignatura`
- `/catalogos/esquemas-evaluacion`
- `/catalogos/situaciones-academicas`
- `/catalogos/resultados-academicos`

## Endpoints backend

Administración:

- `GET|POST /api/admin/usuarios/`
- `GET|PATCH /api/admin/usuarios/<id>/`
- `POST /api/admin/usuarios/<id>/activar/`
- `POST /api/admin/usuarios/<id>/inactivar/`
- `GET|POST /api/admin/grados-empleos/`
- `GET|PATCH /api/admin/grados-empleos/<id>/`
- `POST /api/admin/grados-empleos/<id>/activar/`
- `POST /api/admin/grados-empleos/<id>/inactivar/`
- `GET|POST /api/admin/unidades-organizacionales/`
- `GET|PATCH /api/admin/unidades-organizacionales/<id>/`
- `POST /api/admin/unidades-organizacionales/<id>/activar/`
- `POST /api/admin/unidades-organizacionales/<id>/inactivar/`
- `GET|POST /api/admin/asignaciones-cargo/`
- `GET|PATCH /api/admin/asignaciones-cargo/<id>/`
- `POST /api/admin/asignaciones-cargo/<id>/cerrar/`
- `POST /api/admin/asignaciones-cargo/<id>/activar/`
- `POST /api/admin/asignaciones-cargo/<id>/inactivar/`
- `GET /api/admin/roles/`

Catálogos:

- `GET|POST /api/catalogos/<slug>/`
- `GET|PATCH /api/catalogos/<slug>/<id>/`
- `POST /api/catalogos/<slug>/<id>/activar/`
- `POST /api/catalogos/<slug>/<id>/inactivar/`
- `GET|POST /api/catalogos/esquemas-evaluacion/<id>/componentes/`
- `GET|PATCH /api/catalogos/esquemas-evaluacion/<id>/componentes/<componente_id>/`

## Componentes creados

- `AdminCatalogIndex`
- `AdminCatalogCard`
- `CatalogResourcePage`
- `CatalogResourceTable`
- `CatalogResourceFilters`
- `CatalogResourceForm`
- `CatalogResourceDetail`
- `CatalogActionButtons`
- `CatalogStatusBadge`
- `CatalogBooleanBadge`
- `CatalogEmptyState`
- `CatalogErrorState`
- `CatalogLoadingState`
- `ConfirmActionDialog`
- `FormFieldRenderer`
- `BackendValidationErrors`
- `RelationSelect`
- `EvaluationComponentsPanel`

## Configuraciones creadas

- `frontend/src/lib/admin-config.ts`
- `frontend/src/lib/catalogos-config.ts`

La configuración define slug, ruta, endpoint, columnas, campos de formulario, filtros, acciones y permisos visuales.

## Archivos modificados o creados

Backend:

- `backend/config/urls.py`
- `backend/usuarios/admin_api_views.py`
- `backend/usuarios/admin_api_urls.py`
- `backend/catalogos/api_views.py`
- `backend/catalogos/api_urls.py`
- `backend/catalogos/tests_api_10c4.py`
- `backend/usuarios/tests_api_10c4.py`

Frontend:

- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/lib/admin-config.ts`
- `frontend/src/lib/catalogos-config.ts`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/admin-catalogos/*`
- `frontend/src/app/administracion/*`
- `frontend/src/app/catalogos/*`

Documentación:

- `README.md`
- `docs/resumen_bloque10c4_admin_catalogos_portal.md`

## Permisos

Backend:

- Admin/superusuario: lectura y escritura en administración y catálogos.
- Estadística: lectura de administración y escritura de catálogos académicos.
- Jefaturas: consulta según perfil y, en jefatura de carrera, filtrado por ámbito cuando puede inferirse carrera.
- Docente y Discente: sin acceso a administración/catálogos.

Frontend:

- Oculta módulos a Docente y Discente.
- Muestra acceso denegado ante URL directa sin perfil autorizado.
- No confía en frontend para reglas finales.

## Validaciones cubiertas

- Usuario no autenticado recibe 401.
- Docente y Discente reciben 403.
- Admin lista y crea recursos.
- Estadística lista catálogos y no tiene escritura administrativa técnica.
- Clave inválida se rechaza por backend.
- Materia calcula créditos en backend.
- Programa calcula año de formación en backend.
- Periodo rechaza fechas inválidas.
- Grupo rechaza cupo inválido.
- Esquema de un parcial rechaza exención.
- Asignación de cargo rechaza usuario discente.
- Inactivación lógica no elimina físicamente registros.
- Errores de validación se devuelven como JSON y el portal los muestra.

## Seguridad y privacidad

- No se exponen hashes ni contraseñas.
- La contraseña temporal solo se acepta al crear usuario y no se devuelve.
- No se usa `localStorage` para tokens.
- Mutaciones usan sesión Django, cookies y CSRF.
- No hay eliminación física desde portal para recursos principales.
- RegistroExportacion no se usa porque estas acciones no son exportaciones.

## Limitaciones

- La edición de grupos Django permanece como solo lectura en portal.
- Los componentes de esquema se agregan desde el detalle del esquema; la edición avanzada sigue respaldada por Django Admin.
- La bitácora transversal de mutaciones queda pendiente para 9K.
- La operación profunda de asignaciones docentes, actas y cierre/apertura queda fuera.

## Pendientes

- 10C-5: interfaces operativas de calificaciones y actas.
- 10C-6: trayectoria, movimientos y cierre/apertura en portal.
- 9K: bitácora transversal de eventos críticos.
- 10D: pulido UX/UI y QA visual integral.

## Validaciones ejecutadas

- `docker compose exec -T backend python manage.py check` - OK.
- `docker compose exec -T backend python manage.py makemigrations --check` - OK, sin cambios.
- `docker compose exec -T backend python manage.py test catalogos usuarios` - OK, 163 pruebas.
- `docker compose exec -T frontend npm run lint` - OK.
- `docker compose exec -T frontend npm run build` - OK.

- `docker compose exec -T backend python manage.py test relaciones evaluacion trayectoria` - OK, 134 pruebas.
- `docker compose exec -T backend python manage.py test` - OK, 389 pruebas.
