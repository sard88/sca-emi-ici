# Inventario de pantallas del portal - Bloque 10D-0

## Rutas Next.js detectadas

| Ruta | Módulo | Perfiles previstos | Estado | Dependencia backend | Problemas detectados | Prioridad | Bloque sugerido |
|---|---|---|---|---|---|---|---|
| `/` | Acceso | Público/autenticado | Implementada básica | Auth | Redirige según sesión | P3 | Ninguno |
| `/login` | Acceso | Público | Implementada completa | `/api/auth/*` | Sin hallazgos funcionales mayores | P3 | Ninguno |
| `/dashboard` | Inicio | Todos | Implementada completa | dashboard APIs | Menú/tarjetas con rutas antiguas por perfil | P1 | 10D-1 |
| `/perfil` | Perfil | Todos | Implementada básica | perfil API | Puede mantener panel derecho | P3 | 10D-3 |
| `/admin-soporte` | Perfil Admin | Admin | Implementada básica | dashboard config | Admin ve todos los perfiles/tarjetas | P2 | 10D-2 |
| `/administracion` | Administración | Admin, lectura institucional | Implementada completa | admin APIs | Panel derecho; diferencia lectura/escritura poco evidente | P1 | 10D-1 |
| `/administracion/[slug]` | Administración | Admin, lectura institucional | Implementada completa | admin APIs | Panel derecho; selects genéricos sin filtro activo | P1 | 10D-1 |
| `/administracion/[slug]/[id]` | Administración | Admin, lectura institucional | Implementada completa | admin APIs | Panel derecho; detalle debería ser full width | P1 | 10D-1 |
| `/catalogos` | Catálogos | Admin, Estadística, jefaturas lectura | Implementada completa | catálogos APIs | Panel derecho | P1 | 10D-1 |
| `/catalogos/[slug]` | Catálogos | Admin/Estadística escritura; jefaturas lectura | Implementada completa | catálogos APIs | Panel derecho; relations sin activo/cascada | P1 | 10D-1 |
| `/catalogos/[slug]/[id]` | Catálogos | Admin/Estadística escritura; jefaturas lectura | Implementada completa | catálogos APIs | Panel derecho; detalle/esquema requieren ancho | P1 | 10D-1 |
| `/docente` | Perfil docente | Docente | Implementada básica | dashboard config | Dashboard duplica asignaciones/captura | P2 | 10D-2 |
| `/docente/asignaciones` | Evaluación | Docente | Implementada completa | evaluación APIs | Panel derecho | P1 | 10D-1 |
| `/docente/asignaciones/[id]` | Evaluación | Docente | Implementada completa | evaluación APIs | Panel derecho | P1 | 10D-1 |
| `/docente/asignaciones/[id]/captura/[corte]` | Evaluación | Docente | Implementada completa | evaluación APIs | Full width correcto | P3 | Ninguno |
| `/docente/asignaciones/[id]/resumen` | Evaluación | Docente | Implementada completa | evaluación APIs | Full width correcto | P3 | Ninguno |
| `/docente/actas` | Actas | Docente | Implementada completa | actas APIs | Panel derecho | P1 | 10D-1 |
| `/docente/actas/[id]` | Actas | Docente | Implementada completa | actas APIs | Full width correcto | P3 | Ninguno |
| `/discente` | Perfil discente | Discente | Implementada básica | dashboard config | Tarjeta a ruta antigua de carga | P2 | 10D-2 |
| `/discente/actas` | Actas discente | Discente | Implementada completa | actas APIs | Panel derecho opcionalmente innecesario | P2 | 10D-2 |
| `/discente/actas/[detalleId]` | Conformidad | Discente | Implementada completa | actas APIs | Panel derecho; detalle debería full width | P1 | 10D-1 |
| `/estadistica` | Perfil estadística | Estadística | Implementada básica | dashboard config | Tarjetas duplicadas/antiguas | P1 | 10D-1 |
| `/estadistica/actas` | Actas consulta | Admin, Estadística | Implementada completa | actas APIs | Panel derecho | P1 | 10D-1 |
| `/estadistica/actas/[id]` | Actas consulta | Admin, Estadística | Implementada completa | actas APIs | Full width correcto | P3 | Ninguno |
| `/jefatura-carrera` | Perfil jefatura carrera | Jefatura carrera | Implementada básica | dashboard config | Enlace antiguo asignaciones docentes | P1 | 10D-1 |
| `/jefatura-carrera/actas` | Actas validación | Jefatura carrera | Implementada completa | actas APIs | Panel derecho | P1 | 10D-1 |
| `/jefatura-carrera/actas/[id]` | Actas validación | Jefatura carrera | Implementada completa | actas APIs | Full width correcto | P3 | Ninguno |
| `/jefatura-academica` | Perfil jefatura académica | Jefatura académica | Implementada básica | dashboard config | Duplicidad seguimiento/reportes | P2 | 10D-2 |
| `/jefatura-academica/actas` | Actas formalización | Jefatura académica | Implementada completa | actas APIs | Panel derecho | P1 | 10D-1 |
| `/jefatura-academica/actas/[id]` | Actas formalización | Jefatura académica | Implementada completa | actas APIs | Full width correcto | P3 | Ninguno |
| `/jefatura-pedagogica` | Perfil jefatura pedagógica | Jefatura pedagógica | Implementada básica | dashboard config | Enlace antiguo a consulta académica | P1 | 10D-1 |
| `/trayectoria` | Trayectoria | Discente/Admin/Estadística/Jefaturas | Implementada completa | trayectoria APIs | Discente puede ver home institucional si no se redirige | P2 | 10D-2 |
| `/trayectoria/mi-historial` | Trayectoria propia | Discente | Implementada completa | trayectoria APIs | Correcta | P3 | Ninguno |
| `/trayectoria/historial` | Historial institucional | Admin, Estadística, Jefaturas | Implementada completa | trayectoria APIs | Filtros texto libre | P2 | 10D-2 |
| `/trayectoria/historial/[discenteId]` | Historial institucional | Admin, Estadística, Jefaturas | Implementada completa | trayectoria APIs | Datos sensibles; requiere controles backend | P2 | 10D-2 |
| `/trayectoria/extraordinarios` | Extraordinarios | Admin, Estadística, Jefaturas consulta | Implementada completa | trayectoria APIs | Filtros texto libre | P2 | 10D-2 |
| `/trayectoria/extraordinarios/nuevo` | Extraordinarios | Admin, Estadística | Implementada básica | trayectoria APIs | IDs manuales | P1 | 10D-1 |
| `/trayectoria/extraordinarios/[id]` | Extraordinarios | Admin, Estadística, Jefaturas consulta | Implementada completa | trayectoria APIs | Correcta | P3 | Ninguno |
| `/trayectoria/situaciones` | Situaciones | Admin, Estadística, Jefaturas consulta | Implementada completa | trayectoria APIs | Filtros texto libre | P2 | 10D-2 |
| `/trayectoria/situaciones/nuevo` | Situaciones | Admin, Estadística | Implementada básica | trayectoria APIs | IDs/códigos manuales | P1 | 10D-1 |
| `/trayectoria/situaciones/[id]` | Situaciones | Admin, Estadística, Jefaturas consulta | Implementada completa | trayectoria APIs | Correcta | P3 | Ninguno |
| `/movimientos-academicos` | Movimientos | Admin, Estadística, Jefaturas consulta | Implementada completa | relaciones APIs | Filtros texto libre | P2 | 10D-2 |
| `/movimientos-academicos/nuevo` | Movimientos | Admin, Estadística | Implementada básica | relaciones APIs | IDs/códigos manuales | P1 | 10D-1 |
| `/movimientos-academicos/cambio-grupo` | Movimientos | Admin, Estadística | Implementada básica | relaciones APIs | IDs manuales | P1 | 10D-1 |
| `/movimientos-academicos/[id]` | Movimientos | Admin, Estadística, Jefaturas consulta | Implementada completa | relaciones APIs | Correcta | P3 | Ninguno |
| `/periodos` | Periodos | Admin, Estadística, Jefaturas consulta | Implementada completa | periodo APIs | Enlaces de acción visibles a consulta | P1 | 10D-1 |
| `/periodos/[id]/diagnostico` | Periodos | Admin, Estadística, Jefaturas consulta | Implementada completa | periodo APIs | Tabla densa, full width correcto | P2 | 10D-2 |
| `/periodos/apertura` | Periodos | Admin, Estadística | Implementada básica | periodo APIs | IDs manuales | P1 | 10D-1 |
| `/periodos/cierres` | Periodos | Admin, Estadística, Jefaturas consulta | Implementada completa | periodo APIs | Correcta | P3 | Ninguno |
| `/periodos/cierres/[id]` | Periodos | Admin, Estadística, Jefaturas consulta | Implementada completa | periodo APIs | Correcta | P3 | Ninguno |
| `/periodos/aperturas` | Periodos | Admin, Estadística, Jefaturas consulta | Implementada completa | periodo APIs | Correcta | P3 | Ninguno |
| `/periodos/aperturas/[id]` | Periodos | Admin, Estadística, Jefaturas consulta | Implementada completa | periodo APIs | Correcta | P3 | Ninguno |
| `/periodos/pendientes-asignacion-docente` | Periodos | Jefaturas/Admin/Estadística | Implementada completa | periodo APIs | Filtros texto libre | P2 | 10D-2 |
| `/reportes` | Reportes | Docente/Admin/Estadística/Jefaturas | Implementada completa | reportes APIs | Panel derecho, saturación conceptual | P1 | 10D-1 |
| `/reportes/actas` | Reportes actas | Docente/Admin/Estadística/Jefaturas | Implementada completa | exportaciones APIs | Panel derecho | P1 | 10D-1 |
| `/reportes/kardex` | Kárdex | Admin/Estadística/Jefaturas | Implementada completa | kárdex APIs | Panel derecho | P1 | 10D-1 |
| `/reportes/operativos` | Reportes operativos | Admin/Estadística/Jefaturas | Implementada completa | reportes APIs | Panel derecho | P1 | 10D-1 |
| `/reportes/operativos/[slug]` | Reportes operativos | Admin/Estadística/Jefaturas | Implementada completa | reportes APIs | Panel derecho, tablas densas | P1 | 10D-1 |
| `/reportes/desempeno` | Reportes desempeño | Admin/Estadística/Jefaturas | Implementada completa | reportes APIs | Panel derecho | P1 | 10D-1 |
| `/reportes/desempeno/[slug]` | Reportes desempeño | Admin/Estadística/Jefaturas | Implementada completa | reportes APIs | Panel derecho, tablas densas | P1 | 10D-1 |
| `/reportes/trayectoria` | Reportes trayectoria | Admin/Estadística/Jefaturas | Implementada completa | reportes APIs | Panel derecho | P1 | 10D-1 |
| `/reportes/trayectoria/[slug]` | Reportes trayectoria | Admin/Estadística/Jefaturas | Implementada completa | reportes APIs | Panel derecho, filtros de ID | P1 | 10D-1 |
| `/reportes/exportaciones` | Exportaciones | Usuarios autorizados | Implementada completa | exportaciones APIs | Panel derecho | P1 | 10D-1 |
| `/reportes/auditoria` | Auditoría | Admin/Estadística/autoridades | Implementada básica | auditoría/reportes APIs | Panel derecho; mismatch permisos tab exportaciones | P1 | 10D-1 |

## Pantallas backend antiguas detectadas desde frontend

| Ruta backend antigua | Clasificación | Acción recomendada |
|---|---|---|
| `/admin/` | Mantener como respaldo técnico | Visible solo Admin/soporte. |
| `/admin/usuarios/usuario/` | Reemplazar por frontend | Usar `/administracion/usuarios`. |
| `/admin/usuarios/asignacioncargo/` | Reemplazar por frontend | Usar `/administracion/cargos`. |
| `/admin/usuarios/unidadorganizacional/` | Reemplazar por frontend | Usar `/administracion/unidades`. |
| `/admin/catalogos/` | Reemplazar por frontend | Usar `/catalogos`, especialmente para Estadística. |
| `/validacion/discente/carga/` | Pendiente de migración | Crear pantalla "Mi carga académica" o retirar enlace. |
| `/validacion/jefatura/asignaciones-docentes/` | Pendiente funcional | Bloque futuro de asignación docente en portal. |
| `/evaluacion/actas/planeacion-evaluacion/consulta/` | Pendiente de reemplazo | Crear consulta pedagógica o reutilizar consulta de actas autorizada. |
| `/trayectoria/kardex/` | Obsoleta para portal | Reemplazar por `/reportes/kardex`. |
