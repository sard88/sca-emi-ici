# Matriz de rutas frontend/backend - Bloque 10D-0

## Resumen

La navegación principal ya usa rutas Next.js para la mayoría de módulos migrados en 10C. Los enlaces antiguos se concentran en `frontend/src/lib/dashboard.ts` y en elementos dinámicos que pueden venir del backend (`DashboardSidePanel`, `Topbar`). No se detectaron enlaces visibles que usen `localhost:8000` directamente; ese valor aparece como base técnica en `frontend/src/lib/api.ts`.

## Matriz de enlaces relevantes

| Archivo | Línea aproximada | Texto/ruta encontrada | Tipo | ¿Existe equivalente Next.js? | Ruta Next.js sugerida | Acción recomendada | Prioridad | Observación |
|---|---:|---|---|---|---|---|---|---|
| `frontend/src/lib/dashboard.ts` | 28 | `/admin/usuarios/usuario/` | Django Admin | Sí | `/administracion/usuarios` | Reemplazar en tarjeta principal; dejar Django Admin como soporte técnico Admin | P1 | Administración de usuarios ya existe en portal. |
| `frontend/src/lib/dashboard.ts` | 34 | `/admin/usuarios/asignacioncargo/` | Django Admin | Sí | `/administracion/cargos` | Reemplazar | P1 | Asignaciones de cargo ya tienen recurso en portal. |
| `frontend/src/lib/dashboard.ts` | 35 | `/admin/usuarios/unidadorganizacional/` | Django Admin | Sí | `/administracion/unidades` | Reemplazar | P1 | Unidades organizacionales ya migraron. |
| `frontend/src/lib/dashboard.ts` | 42 | `/admin/` | Django Admin | Parcial | N/A | Mantener solo Admin/soporte técnico | P2 | Puede quedar como acceso técnico explícito, no como flujo operativo. |
| `frontend/src/lib/dashboard.ts` | 52 | `/admin/catalogos/` | Django Admin | Sí | `/catalogos` | Reemplazar y ocultar Admin a Estadística | P1 | Estadística no debería salir a Django Admin si existe portal. |
| `frontend/src/lib/dashboard.ts` | 61 | `/trayectoria/kardex/` | Vista Django antigua | Sí | `/reportes/kardex` | Reemplazar | P1 | El portal ya tiene kárdex oficial PDF. |
| `frontend/src/lib/dashboard.ts` | 88 | `/validacion/discente/carga/` | Vista Django antigua | Parcial | `/discente/actas` y `/trayectoria/mi-historial` | Dejar pendiente o crear pantalla de carga propia | P2 | No hay ruta Next.js específica de carga académica; evitar enlace viejo si no es necesario. |
| `frontend/src/lib/dashboard.ts` | 101 | `/validacion/jefatura/asignaciones-docentes/` | Vista Django antigua | No completa | Pendiente 10D/funcional | Mantener solo si es respaldo, señalando salida a backend | P1 | La operación de asignación docente no tiene pantalla Next.js equivalente evidente. |
| `frontend/src/lib/dashboard.ts` | 137 | `/evaluacion/actas/planeacion-evaluacion/consulta/` | Vista Django antigua | Parcial | `/estadistica/actas` o nueva ruta de consulta pedagógica | Reemplazar cuando exista permiso/route equivalente | P1 | Jefatura pedagógica queda enviada a vista antigua. |
| `frontend/src/lib/api.ts` | 52 | `http://localhost:8000` | Base API backend | N/A | N/A | Mantener como fallback técnico local | P3 | No es enlace visible. |
| `frontend/src/lib/api.ts` | varias | `/api/...` | API backend | N/A | N/A | Mantener | P3 | Usado correctamente como datos/descargas, no como páginas visibles. |
| `frontend/src/components/dashboard/DashboardSidePanel.tsx` | 96 | `backendUrl(item.url)` | Enlace backend dinámico | Variable | Variable | Sanitizar catálogo de URLs destino en backend o mapear rutas conocidas | P2 | Actividad reciente puede abrir rutas backend si `item.backend` llega true. |
| `frontend/src/components/dashboard/DashboardSidePanel.tsx` | 183 | `backendUrl(evento.url_destino)` | Enlace backend dinámico | Variable | Variable | Revisar origen de `url_destino` | P2 | Eventos de calendario pueden dirigir a backend antiguo. |
| `frontend/src/components/layout/Topbar.tsx` | 141 | `backendUrl(item.url)` | Enlace backend dinámico | Variable | Variable | Mapear resultados de búsqueda a rutas Next cuando existan | P2 | El buscador/topbar puede reintroducir rutas Django. |
| `frontend/src/components/layout/Topbar.tsx` | 215 | `backendUrl(item.url_destino)` | Enlace backend dinámico | Variable | Variable | Revisar notificaciones/calendario | P2 | Mantener backend solo para recursos sin pantalla Next. |

## Rutas Next.js existentes que requieren mejor enlace

| Ruta | Estado | Hallazgo | Acción recomendada | Prioridad |
|---|---|---|---|---|
| `/movimientos-academicos/nuevo` | Existe | No aparece como tarjeta principal en trayectoria; solo se usa desde listado si el usuario puede operar. | Mantener, pero aclarar diferencia con cambio de grupo. | P2 |
| `/reportes/exportaciones` | Existe | Enlazada desde reportes, pero no destacada claramente frente a auditoría. | Separar "Historial de exportaciones" de "Auditoría institucional". | P2 |
| `/reportes/auditoria` | Existe | Enlazada como auditoría institucional, pero con permisos visuales compartidos para exportaciones/eventos. | Dividir permisos visuales por pestaña o adaptar tabs. | P1 |
| `/estadistica/actas` | Existe | Puede servir como reemplazo parcial de consultas antiguas de actas. | Evaluar si jefatura pedagógica debe tener una ruta propia de consulta. | P1 |
| `/periodos/apertura` | Existe | Enlace visible para perfiles que pueden ver periodos, pero la acción real solo corresponde a operador. | Ocultar acción de apertura a consulta no operativa. | P1 |

## Clasificación de rutas antiguas

| Ruta antigua | Clasificación | Recomendación |
|---|---|---|
| `/admin/**` | Respaldo técnico | Mantener solo para Admin/soporte, no como flujo primario de perfiles institucionales. |
| `/validacion/discente/carga/` | Pendiente de migración o retiro visual | Evitar para discente salvo que se confirme que no hay equivalente Next.js. |
| `/validacion/jefatura/asignaciones-docentes/` | Pendiente funcional | Requiere pantalla Next.js o módulo específico posterior. |
| `/evaluacion/actas/planeacion-evaluacion/consulta/` | Pendiente de reemplazo | Crear consulta pedagógica o mapear a actas institucionales autorizadas. |
| `/trayectoria/kardex/` | Obsoleta para portal | Reemplazar por `/reportes/kardex`. |
