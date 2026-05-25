# Plan de correcciones 10D-1 / 10D-2 / 10D-3

## Matriz priorizada

| ID | Descripción | Evidencia | Módulo | Perfil afectado | Severidad | Esfuerzo | Bloque recomendado | Recomendación |
|---|---|---|---|---|---|---|---|---|
| 10D0-P1-001 | Panel derecho aparece en pantallas operativas y reportes densos. | `<AppShell>` sin `showRightPanel={false}` en reportes, administración, catálogos, listas de actas. | Layout | Todos los perfiles operativos | P1 | Bajo | 10D-1 | Aplicar layout `workspace/full-width` a rutas operativas. |
| 10D0-P1-002 | Dashboard conserva enlaces a Django Admin donde ya existe pantalla Next.js. | `/admin/usuarios/usuario/`, `/admin/usuarios/asignacioncargo/`, `/admin/usuarios/unidadorganizacional/`, `/admin/catalogos/`. | Navegación | Admin, Estadística | P1 | Bajo | 10D-1 | Reemplazar por `/administracion/**` y `/catalogos`. |
| 10D0-P1-003 | Kárdex de Estadística apunta a ruta antigua. | `/trayectoria/kardex/` en `dashboard.ts`. | Reportes | Estadística | P1 | Bajo | 10D-1 | Reemplazar por `/reportes/kardex`. |
| 10D0-P1-004 | Jefatura pedagógica usa consulta académica antigua. | `/evaluacion/actas/planeacion-evaluacion/consulta/`. | Actas | Jefatura pedagógica | P1 | Medio | 10D-1/10D-2 | Crear ruta Next autorizada o mapear a consulta existente si backend lo permite. |
| 10D0-P1-005 | Auditoría visual mezcla permisos de exportaciones y eventos críticos. | Frontend permite jefatura pedagógica; backend de exportaciones no. | Auditoría | Jefatura pedagógica | P1 | Bajo | 10D-1 | Separar tabs/capacidades visuales. |
| 10D0-P1-006 | Acciones de apertura/cierre visibles en módulo de periodos para perfiles de consulta. | `PeriodsOperationalList` muestra `/periodos/apertura` a quien puede ver periodos. | Periodos | Jefaturas | P1 | Bajo | 10D-1 | Mostrar acciones solo con `canOperateTrayectoria`. |
| 10D0-P1-007 | Formularios de trayectoria capturan IDs y códigos como texto libre. | `TrajectoryOperations.tsx` `FormPage` con `TextField`. | Trayectoria | Admin, Estadística | P1 | Medio | 10D-1 | Selectores/buscadores para discente, inscripción, periodo, situación. |
| 10D0-P1-008 | Movimientos académicos y cambio de grupo capturan IDs manuales. | Campos `discente_id`, `grupo_origen_id`, `grupo_destino_id`. | Movimientos | Admin, Estadística | P1 | Medio | 10D-1 | Selectores dependientes por periodo/carrera/grupo. |
| 10D0-P1-009 | Apertura de periodo captura periodo origen/destino como texto libre. | `OpeningPeriodForm` usa `periodo_origen_id`, `periodo_destino_id` en `TextField`. | Periodos | Admin, Estadística | P1 | Medio | 10D-1 | Selectores de periodos elegibles. |
| 10D0-P1-010 | Selectores relacionales no filtran activos ni ámbito. | `RelationSelect` carga `page_size=100&limit=100`. | Administración/Catálogos | Admin, Estadística | P1 | Medio | 10D-1 | Añadir filtros activos/contextuales y buscador paginado. |
| 10D0-P2-001 | Discente ve ruta antigua de "Mi carga académica". | `/validacion/discente/carga/`. | Discente | Discente | P2 | Medio | 10D-2 | Crear pantalla Next o retirar tarjeta. |
| 10D0-P2-002 | Dashboard docente duplica asignaciones y captura. | Dos tarjetas apuntan a `/docente/asignaciones`. | Dashboard | Docente | P2 | Bajo | 10D-2 | Consolidar en una tarjeta con acciones secundarias. |
| 10D0-P2-003 | Jefatura carrera tiene dos tarjetas con el mismo título. | `Trayectoria de mi carrera` repetido. | Dashboard | Jefatura carrera | P2 | Bajo | 10D-2 | Diferenciar operación vs reportes. |
| 10D0-P2-004 | Jefatura académica duplica "Seguimiento de trayectoria". | Dos tarjetas similares. | Dashboard | Jefatura académica | P2 | Bajo | 10D-2 | Diferenciar operación vs reportes. |
| 10D0-P2-005 | Reportes están saturados y mezclan catálogo, exportaciones y auditoría. | `/reportes` + sidebar + tarjetas. | Reportes | Autorizados | P2 | Medio | 10D-2 | Agrupar por intención: consultar, exportar, auditar. |
| 10D0-P2-006 | Filtros de reportes usan texto libre para IDs. | reportes operativos/desempeño/trayectoria. | Reportes | Autorizados | P2 | Medio | 10D-2 | Selectores graduales para periodo/carrera/grupo/asignatura. |
| 10D0-P2-007 | Comentarios de inconformidad pueden necesitar tratamiento especial en reportes. | Reporte operativo indica comentario visible a autorizados. | Privacidad | Autoridades | P2 | Bajo/medio | 10D-2 | Truncar por defecto o mover a detalle. |
| 10D0-P2-008 | Administración de usuarios muestra password temporal también en edición. | `admin-config.ts` campo password. | Administración | Admin | P2 | Bajo | 10D-2 | Separar alta/restablecimiento de edición ordinaria. |
| 10D0-P2-009 | Discente puede ver "Trayectoria académica" además de "Mi historial". | `canAccessTrayectoriaOperativa` incluye `DISCENTE`. | Navegación | Discente | P2 | Bajo | 10D-2 | Redirigir o limitar a vista personal. |
| 10D0-P3-001 | Terminología Materia/Asignatura/Unidad de aprendizaje no está unificada. | Configs y reportes. | Terminología | Todos | P3 | Bajo | 10D-3 | Definir glosario y aplicar copy. |
| 10D0-P3-002 | Iconografía de sidebar es manual SVG, no lucide. | `Sidebar.tsx`. | UI | Todos | P3 | Medio | 10D-3 | Migrar a iconos de sistema si se adopta librería. |
| 10D0-P3-003 | Estados vacíos y ayudas aparecen con tonos/textos dispares. | Reportes, trayectoria, admin. | UI | Todos | P3 | Medio | 10D-3 | Normalizar componentes de estados vacíos. |

## Alcance recomendado para 10D-1

1. Ocultar panel derecho en pantallas operativas/reportes.
2. Sustituir enlaces antiguos que ya tienen equivalente Next.js.
3. Separar permiso visual de auditoría eventos/exportaciones.
4. Ocultar acciones operativas de periodos a roles de consulta.
5. Cambiar formularios críticos de trayectoria/movimientos/periodos de texto libre a selectores básicos.
6. Añadir filtros de activos a selectores relacionales de administración/catálogos.

## Estado posterior al Bloque 10D-1

| ID | Estado | Evidencia de atención |
|---|---|---|
| 10D0-P1-001 | Atendido | `AppShell` oculta el panel derecho por defecto; dashboards/home/perfil lo activan explicitamente. |
| 10D0-P1-002 | Atendido | `dashboard.ts` reemplaza enlaces de usuarios, cargos, unidades y catalogos por rutas Next.js. |
| 10D0-P1-003 | Atendido | Kárdex institucional apunta a `/reportes/kardex`. |
| 10D0-P1-004 | Atendido | Jefatura pedagogica usa reportes del portal en lugar de la consulta Django antigua. |
| 10D0-P1-005 | Atendido | Se separaron `canAccessAuditoriaEventos`, `canAccessAuditoriaExportaciones` y `canAccessAuditoria`. |
| 10D0-P1-006 | Atendido | Las acciones de cierre/apertura se muestran solo con `canOperateTrayectoria`. |
| 10D0-P1-007 | Atendido | Formularios de extraordinarios/situaciones usan selectores y buscadores autorizados. |
| 10D0-P1-008 | Atendido | Movimientos y cambio de grupo usan selectores dependientes para discente, periodo y grupos. |
| 10D0-P1-009 | Atendido | Apertura de periodo usa selectores de periodos origen/destino elegibles. |
| 10D0-P1-010 | Atendido | `RelationSelect` soporta busqueda, activos, parametros y dependencias contextuales. |

Detalle tecnico: `docs/resumen_bloque10d1_estabilizacion_ux_funcional.md`.

## Alcance recomendado para 10D-2

1. Reordenar menú y dashboard por intención.
2. Consolidar tarjetas duplicadas.
3. Crear o retirar "Mi carga académica" en Discente.
4. Mejorar filtros de reportes con selectores.
5. Definir pantalla de consulta académica para Jefatura pedagógica.
6. Ajustar privacidad de comentarios sensibles.

## Alcance recomendado para 10D-3

1. Pulido visual, densidad, estados vacíos y microcopy.
2. Glosario institucional aplicado a pantallas.
3. Iconografía y consistencia de botones/controles.
4. Mejoras responsive posteriores al ajuste funcional.

## Fuera de 10D

| Tema | Bloque sugerido |
|---|---|
| Nuevo módulo completo de asignación docente en portal | Bloque funcional futuro |
| Cambios en reglas académicas de cierre/apertura | No tocar desde 10D |
| Reglas backend de permisos | Bloque backend específico si se detecta brecha real |
| BI, gráficas avanzadas o dashboard analítico | 10E |
