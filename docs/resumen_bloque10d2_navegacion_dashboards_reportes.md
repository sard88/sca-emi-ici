# Bloque 10D-2 - Navegacion, dashboards y reportes

## Objetivo

Se atendieron los hallazgos P2 del diagnostico 10D-0 pendientes despues de 10D-1. El bloque organiza la navegacion por intencion, aclara dashboards por perfil, separa reportes/exportaciones/auditoria, mejora filtros visuales y reduce exposicion de informacion sensible, sin cambiar reglas academicas, calculos, estados de actas, modelos ni migraciones.

## Hallazgos P2 corregidos

| ID | Estado | Correccion aplicada |
|---|---|---|
| 10D0-P2-001 | Atendido | Se implemento `/discente/carga-academica` y `GET /api/discente/carga-academica/` para carga personal sin matricula militar. |
| 10D0-P2-002 | Atendido | Dashboard docente consolida asignaciones y captura en una sola tarjeta. |
| 10D0-P2-003 | Atendido | Jefatura de carrera diferencia trayectoria operativa y reportes de trayectoria. |
| 10D0-P2-004 | Atendido | Jefatura academica diferencia seguimiento institucional, reportes y procesos de cierre. |
| 10D0-P2-005 | Atendido | `/reportes` queda agrupado por documentos oficiales, reportes institucionales, exportaciones y auditoria. |
| 10D0-P2-006 | Atendido parcial | Filtros comunes de reportes usan selectores graduales cuando existe fuente segura; filtros nominales libres quedan como texto con placeholder. |
| 10D0-P2-007 | Atendido | Comentarios de inconformidad se truncan en vista previa web; XLSX autorizado se mantiene sin cambios. |
| 10D0-P2-008 | Atendido | `password` temporal es `createOnly` y no aparece en edicion ordinaria de usuarios. |
| 10D0-P2-009 | Atendido | Discente ve experiencia personal en `/trayectoria` y sidebar, no la home institucional. |

## Archivos principales modificados

- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/app/reportes/page.tsx`
- `frontend/src/app/reportes/auditoria/page.tsx`
- `frontend/src/components/reportes/ReportFilterField.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportFilters.tsx`
- `frontend/src/components/reportes/desempeno/PerformanceReportFilters.tsx`
- `frontend/src/components/reportes/trayectoria/TrajectoryReportFilters.tsx`
- `frontend/src/components/reportes/operativos/OperativeReportTable.tsx`
- `frontend/src/lib/reportes-operativos.ts`
- `frontend/src/lib/reportes-desempeno.ts`
- `frontend/src/lib/reportes-trayectoria.ts`
- `frontend/src/components/admin-catalogos/CatalogResourceForm.tsx`
- `frontend/src/components/admin-catalogos/AdminCatalogIndex.tsx`
- `frontend/src/components/admin-catalogos/CatalogResourcePage.tsx`
- `frontend/src/app/discente/carga-academica/page.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `backend/evaluacion/api_views.py`
- `backend/evaluacion/api_urls.py`
- `backend/evaluacion/tests.py`

## Sidebar

El menu lateral y la navegacion movil se organizan por secciones:

- Inicio.
- Mi espacio.
- Operacion academica.
- Gestion institucional.
- Reportes y auditoria.
- Soporte tecnico.

No se renderizan encabezados vacios. Docente y discente conservan enlaces personales; perfiles institucionales ven operacion/reportes segun permiso. Django Admin y health quedan en soporte tecnico solo para Admin.

## Dashboards

- Admin queda como soporte/operacion institucional, sin tarjetas personales tipo "Mi".
- Estadistica mantiene operacion academica, periodos, reportes y auditoria sin duplicidad de catalogos.
- Docente consolida "Mis asignaciones y captura".
- Discente incorpora "Mi carga academica", "Mis actas" y "Mi historial academico".
- Jefatura de carrera separa operacion de trayectoria y reportes.
- Jefatura academica separa formalizacion, seguimiento, reportes y procesos de cierre.
- Jefatura pedagogica queda orientada a seguimiento y analisis, sin rutas Django antiguas.

## Experiencia del discente

Nueva ruta:

- `/discente/carga-academica`

Nuevo endpoint:

- `GET /api/discente/carga-academica/`

Reglas:

- requiere autenticacion;
- solo perfil Discente;
- devuelve solo inscripciones propias;
- no expone matricula militar;
- no modifica datos;
- muestra asignatura, docente, grupo, periodo, estado de inscripcion y resumen de actas.

En `/trayectoria`, el discente ve una experiencia personal con historial, carga academica y actas publicadas, no tarjetas institucionales.

## Reportes

`/reportes` queda agrupado por intencion:

- Documentos oficiales y academicos.
- Reportes institucionales.
- Exportaciones.
- Auditoria.

Historial de exportaciones y auditoria institucional quedan separados conceptualmente:

- `RegistroExportacion`: archivos generados y folios tecnicos.
- `BitacoraEventoCritico`: eventos criticos transversales.

## Filtros de reportes

Se agrego `ReportFilterField` para soportar:

- selects de choices existentes;
- selectores relacionales con endpoints seguros;
- busqueda cuando hay muchas opciones;
- preservacion de nombres de querystring backend.

Se aplico en reportes operativos, desempeno y trayectoria para periodo, carrera, grupo, asignatura, docente, antiguedad, situacion, tipo documental y tipo de movimiento cuando aplica. Los filtros nominales o sin endpoint seguro se mantienen como texto libre.

## Privacidad

- La vista previa web de inconformidades trunca comentarios a 120 caracteres e indica que existe comentario registrado.
- El XLSX autorizado no se modifica en este bloque.
- La carga academica del discente no expone matricula militar ni datos de otros discentes.
- Auditoria sigue sin mostrar payloads completos.

## Administracion de usuarios

El campo "Contraseña temporal" se marca como `createOnly`, aparece al crear usuario y se oculta en edicion ordinaria. La edicion muestra aviso de que el cambio de contraseña requiere flujo especifico de restablecimiento.

## Validaciones ejecutadas

- `docker compose exec -T frontend npm run lint` - OK
- `docker compose exec -T frontend npm run build` - OK
- `docker compose exec -T backend python manage.py check` - OK
- `docker compose exec -T backend python manage.py makemigrations --check` - OK
- `docker compose exec -T backend python manage.py test evaluacion` - OK
- `docker compose exec -T backend python manage.py test usuarios` - OK
- `docker compose exec -T backend python manage.py test` - OK, 461 pruebas

## Pendientes para 10D-3, 10D-4 y 10E

- 10D-3: glosario terminologico, microcopy fino, estados vacios e iconografia.
- 10D-4: trazabilidad visual/timelines y ayudas contextuales.
- 10E: QA integral, pruebas manuales amplias y ajustes responsive finos.
- Futuro: filtros de cascada profunda en reportes y flujo seguro de restablecimiento de contrasena.
