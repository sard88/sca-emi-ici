# Matriz permisos, menú y dashboard - Bloque 10D-0

## Resumen

El `Sidebar` usa funciones de permiso centralizadas de `frontend/src/lib/dashboard.ts` y en general oculta módulos a Docente/Discente. El mayor ruido está en las tarjetas de dashboard por perfil, donde persisten enlaces antiguos, duplicidades y accesos que dependen de backend aunque el módulo ya migró a Next.js.

## Matriz por perfil

| Perfil | Ruta/opción | Ubicación | Visible actualmente | Debería ser visible | Motivo | Acción recomendada | Prioridad | Observación |
|---|---|---|---:|---:|---|---|---|---|
| Admin | Panel general | Sidebar/dashboard | Sí | Sí | Entrada institucional | Mantener | P3 | Correcto. |
| Admin | Usuarios `/admin/usuarios/usuario/` | Dashboard | Sí | No como primario | Ya existe `/administracion/usuarios` | Reemplazar por portal; dejar Django Admin solo soporte | P1 | Reduce salidas a backend. |
| Admin | Administración `/administracion` | Sidebar/dashboard | Sí | Sí | Gestión portal 10C-4 | Mantener | P3 | Correcto. |
| Admin | Catálogos `/catalogos` | Sidebar/dashboard | Sí | Sí | Gestión portal 10C-4 | Mantener | P3 | Correcto. |
| Admin | Django Admin `/admin/` | Dashboard | Sí | Sí, solo técnico | Soporte avanzado | Mantener como acceso técnico claro | P2 | Separarlo de flujo operativo. |
| Admin | Estado técnico `/health/` | Dashboard | Sí | Sí, solo técnico | Diagnóstico backend | Mantener solo Admin/soporte | P3 | No debe aparecer a otros perfiles. |
| Estadística | Catálogos `/admin/catalogos/` | Dashboard | Sí | No | Ya existe `/catalogos` y Django Admin no es flujo funcional | Reemplazar | P1 | Probable error/acceso denegado para no staff. |
| Estadística | Catálogos académicos `/catalogos` | Sidebar/dashboard | Sí | Sí | Rol puede operar catálogos | Mantener | P3 | Correcto. |
| Estadística | Usuarios académicos `/administracion/usuarios` | Dashboard | Sí | Sí, lectura | Backend limita escritura | Mantener con copy de consulta | P2 | Evitar prometer administración plena. |
| Estadística | Kárdex institucional `/trayectoria/kardex/` | Dashboard | Sí | No | Ruta antigua; existe `/reportes/kardex` | Reemplazar | P1 | Duplicada con Kárdex oficial PDF. |
| Estadística | Cierre y apertura `/periodos` | Sidebar/dashboard | Sí | Sí | Operación institucional | Mantener | P3 | Correcto. |
| Docente | Mis asignaciones | Sidebar/dashboard | Sí | Sí | Operación docente propia | Mantener | P3 | Correcto. |
| Docente | Captura de calificaciones | Dashboard | Sí | Sí | Misma ruta que asignaciones | Mantener, pero evitar duplicidad en 10D-2 | P2 | Dos tarjetas apuntan a `/docente/asignaciones`. |
| Docente | Mis actas | Sidebar/dashboard | Sí | Sí | Operación docente propia | Mantener | P3 | Correcto. |
| Docente | Exportar mis actas `/reportes/actas` | Dashboard | Sí | Sí | Reportes propios autorizados | Mantener | P3 | Backend debe seguir filtrando. |
| Docente | Reportes globales | Sidebar | Parcial: solo `/reportes` | No global | Reportes index filtra opciones | Mantener si index no muestra globales | P2 | Revisar textos para que no sugieran reportes institucionales. |
| Discente | Mi carga académica `/validacion/discente/carga/` | Dashboard | Sí | Dudoso | Ruta antigua, no Next.js | Reemplazar por vista propia o retirar | P2 | No hay pantalla Next.js específica de carga. |
| Discente | Mis actas publicadas | Sidebar/dashboard | Sí | Sí | Datos propios | Mantener | P3 | Correcto. |
| Discente | Mi historial académico | Sidebar/dashboard | Sí | Sí | Datos propios | Mantener | P3 | Correcto. |
| Discente | Trayectoria académica `/trayectoria` | Sidebar móvil/desktop vía `canAccessTrayectoriaOperativa` | Sí | Parcial | Puede duplicar "Mi historial" | Limitar a mi historial o home discente específico | P2 | Evitar que parezca módulo institucional. |
| Jefatura de carrera | Asignaciones docentes `/validacion/jefatura/asignaciones-docentes/` | Dashboard | Sí | Pendiente | Vista antigua sin equivalente Next completo | Crear/reemplazar en bloque posterior | P1 | Flujo crítico aún fuera del portal. |
| Jefatura de carrera | Actas por validar | Sidebar/dashboard | Sí | Sí | Rol de validación | Mantener | P3 | Correcto. |
| Jefatura de carrera | Trayectoria de mi carrera | Dashboard | Sí | Sí | Consulta de ámbito | Mantener, renombrar para diferenciar reportes | P2 | Hay dos tarjetas con el mismo título. |
| Jefatura de carrera | Reportes de trayectoria | Dashboard | Sí | Sí | Consulta de ámbito | Mantener, ajustar título | P2 | Duplicidad terminológica. |
| Jefatura de carrera | Cierre y apertura `/periodos` | Sidebar | Sí | Consulta parcial | Puede ver periodos; acciones no siempre autorizadas | Ocultar botones operativos si no puede operar | P1 | `OpeningPeriodForm` usa `canOperateTrayectoria`, pero index muestra "Abrir periodo". |
| Jefatura académica | Actas por formalizar | Sidebar/dashboard | Sí | Sí | Rol de formalización | Mantener | P3 | Correcto. |
| Jefatura académica | Reportes y auditoría | Dashboard/reportes | Sí | Sí, según backend | Mantener | P2 | Auditoría eventos permitida; exportaciones también por backend. |
| Jefatura académica | Cierres de periodo | Dashboard/sidebar | Sí | Consulta | No debe parecer operador si no ejecuta | Ajustar copy y acciones | P1 | Distinguir consulta de operación. |
| Jefatura pedagógica | Consulta académica `/evaluacion/actas/planeacion-evaluacion/consulta/` | Dashboard | Sí | No como backend antiguo | Debe existir consulta Next o ruta autorizada | Reemplazar/crear pantalla | P1 | Principal salida antigua para este perfil. |
| Jefatura pedagógica | Auditoría institucional `/reportes/auditoria` | Reportes | Sí | Parcial | Eventos críticos permitidos, exportaciones no por backend | Separar permiso de pestañas | P1 | `canAccessAuditoriaExportaciones` incluye pedagogía, `puede_auditar_exportaciones` no. |
| Todos autorizados | Reportes y exportaciones | Sidebar/dashboard | Sí | Sí, con segmentación | Módulo amplio | Reorganizar en 10D-2 | P2 | Menú de reportes está saturado. |

## Recomendación conceptual

Para 10D-1 conviene limpiar los accesos que ya tienen equivalente Next.js y bloquear visualmente las acciones operativas cuando el rol solo consulta. Para 10D-2 conviene rediseñar la agrupación conceptual:

| Sección propuesta | Entradas |
|---|---|
| Inicio | Panel general, perfil |
| Mi espacio | Mis asignaciones, mis actas, mi historial |
| Operación académica | Actas, trayectoria, movimientos, periodos, pendientes docentes |
| Gestión institucional | Administración, catálogos |
| Reportes y auditoría | Reportes, exportaciones, auditoría, kárdex |
