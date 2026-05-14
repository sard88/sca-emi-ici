# Diagnóstico de permisos visuales - Bloque 10D-0

## Funciones existentes

La capa visual concentra buena parte de sus reglas en `frontend/src/lib/dashboard.ts`.

| Función | Perfiles principales | Módulo protegido | Observación |
|---|---|---|---|
| `getProfilesForUser` | Todos, Admin ve todos | Homes de perfil | Admin visualiza todos los perfiles; útil para soporte, pero puede cargar tarjetas irrelevantes. |
| `canAccessProfile` | Perfil asignado o Admin | Panel de perfil | Correcta como regla general. |
| `canAccessReportes` | Admin, Estadística, Docente, Jefaturas | `/reportes` | Permite Docente por actas propias; el índice debe ocultar reportes globales. |
| `canAccessKardexPdf` | Admin, Estadística, Jefaturas | `/reportes/kardex` | Coherente con bloque 9C/10C-2; Discente queda fuera. |
| `canAccessReportesOperativos` | Admin, Estadística, Jefaturas | `/reportes/operativos` | Correcto si backend filtra ámbito. |
| `canAccessReportesDesempeno` | Admin, Estadística, Jefaturas | `/reportes/desempeno` | Excluye Docente y Discente. |
| `canAccessReportesTrayectoria` | Admin, Estadística, Jefaturas | `/reportes/trayectoria` | Excluye Docente y Discente. |
| `canAccessAdministracionPortal` | Admin, Estadística y Jefaturas | Sidebar de administración | Más amplio que escritura; debe distinguir lectura/escritura en UI. |
| `canAccessCatalogosPortal` | Igual que administración portal | Sidebar de catálogos | Catálogos sí permiten escritura a Estadística por backend. |
| `canAccessDocenteOperacion` | Docente y Admin | Mis asignaciones/actas | Admin ve operación docente; útil para soporte, pero puede ser ruido si no está contextualizado. |
| `canAccessDiscenteActas` | Discente | Mis actas | Correcto. |
| `canAccessMiHistorialAcademico` | Discente | Mi historial | Correcto. |
| `canAccessTrayectoriaOperativa` | Discente, Admin, Estadística, Jefaturas | `/trayectoria` | Mezcla home personal y módulo institucional. |
| `canAccessTrayectoriaInstitucional` | Admin, Estadística, Jefaturas | Historial institucional | Correcto a nivel visual si backend filtra ámbito. |
| `canOperateTrayectoria` | Admin, Estadística | Alta de extraordinarios, situaciones, movimientos, apertura | Correcto como separación operación/consulta. |
| `canAccessPeriodosOperativos` | Admin, Estadística, jefaturas carrera/académica | `/periodos` | Visualmente muestra proceso completo aunque solo Admin/Estadística operan apertura/cierre. |
| `canAccessJefaturaCarreraActas` | Admin, Jefatura carrera | Actas por validar | Correcto. |
| `canAccessJefaturaAcademicaActas` | Admin, Jefatura académica | Actas por formalizar | Correcto. |
| `canAccessEstadisticaActas` | Admin, Estadística | Consulta actas estadística | Correcto; no cubre Jefatura pedagógica. |
| `canAccessAuditoriaExportaciones` | Admin, Estadística, Jefatura académica, Jefatura pedagógica | `/reportes/auditoria` | Mismatch: backend permite eventos a pedagogía, pero auditoría de exportaciones no. |

## Duplicidades y huecos

| Hallazgo | Evidencia | Riesgo | Recomendación |
|---|---|---|---|
| Permiso único para `/reportes/auditoria` mezcla dos capacidades. | Frontend usa `canAccessAuditoriaExportaciones`; backend `BitacoraEventoCritico` permite jefatura pedagógica, `RegistroExportacion` no. | Jefatura pedagógica puede ver página y recibir 403 en tab Exportaciones. | Separar `canAccessAuditoriaEventos` y `canAccessAuditoriaExportaciones` en 10D-1. |
| Administración portal usa permiso amplio para ver, pero solo Admin escribe. | `admin-config.ts` tiene `canReadAdministracion` institucional y `canWriteAdministracion` Admin. | Usuarios pueden interpretar que pueden administrar cuando solo consultan. | Ajustar textos, botones y estados read-only. |
| Periodos operativos muestra enlaces globales a apertura/cierre desde el índice. | `PeriodsOperationalList` muestra `Abrir periodo` si entra al módulo. | Jefaturas de consulta pueden entrar a una acción que luego se bloquea. | Ocultar enlaces de acción con `canOperateTrayectoria`; mantener consultas. |
| Trayectoria operativa incluye Discente. | `canAccessTrayectoriaOperativa` contiene `DISCENTE`. | Discente ve "Trayectoria académica" además de "Mi historial"; puede parecer acceso institucional. | Redirigir/limitar Discente a `/trayectoria/mi-historial`. |
| Dashboard de Admin carga tarjetas de todos los perfiles. | `getProfilesForUser` retorna todos para Admin. | Puede ver "Mi carga académica" o flujos de rol no aplicables. | En 10D-2 separar soporte/impersonación de menú operativo. |

## Riesgos

| Severidad | Riesgo | Alcance |
|---|---|---|
| P1 | Opción visible que termina en 403 para jefatura pedagógica en auditoría/exportaciones. | UX funcional y trazabilidad. |
| P1 | Acciones de periodo visibles a perfiles de consulta. | Confusión operativa en cierre/apertura. |
| P1 | Enlaces a Django Admin para Estadística y rutas antiguas de actas/kárdex. | Salida del portal y errores de permiso. |
| P2 | Duplicidad de funciones entre dashboard, sidebar y tarjetas. | Navegación saturada. |
| P2 | Permisos visuales dispersos entre dashboard, config de recursos y páginas. | Mantenimiento riesgoso. |

## Propuesta de centralización para 10D-1

Crear una matriz visual central, sin tocar permisos backend, con estas capacidades:

| Capacidad visual | Perfiles sugeridos |
|---|---|
| `portal.dashboard.view` | autenticados |
| `portal.admin.read` | Admin, Estadística, jefaturas autorizadas |
| `portal.admin.write` | Admin |
| `portal.catalogos.read` | Admin, Estadística, jefaturas autorizadas |
| `portal.catalogos.write` | Admin, Estadística |
| `portal.actas.docente` | Docente, Admin soporte |
| `portal.actas.discente` | Discente |
| `portal.actas.validar` | Jefatura carrera, Admin |
| `portal.actas.formalizar` | Jefatura académica, Admin |
| `portal.actas.consulta` | Admin, Estadística, autoridades autorizadas |
| `portal.trayectoria.read` | Admin, Estadística, jefaturas |
| `portal.trayectoria.own` | Discente |
| `portal.trayectoria.operate` | Admin, Estadística |
| `portal.periodos.read` | Admin, Estadística, jefaturas |
| `portal.periodos.operate` | Admin, Estadística |
| `portal.auditoria.eventos` | Admin, Estadística, Jefatura académica, Jefatura pedagógica |
| `portal.auditoria.exportaciones` | Admin, Estadística, Jefatura académica |

La regla importante: frontend solo oculta/ordena; backend sigue siendo autoridad.
