# Diagnóstico Bloque 10D-0 - UX funcional del portal Next.js

## 1. Resumen ejecutivo

El portal Next.js ya cubre la mayoría de módulos migrados en 10C: administración, catálogos, reportes, actas, trayectoria, movimientos, periodos y auditoría 9K. El diagnóstico detecta que el problema principal ya no es ausencia de pantallas, sino estabilización funcional de UX: layout operativo, enlaces antiguos, permisos visuales demasiado amplios, formularios con IDs manuales y selectores relacionales sin filtros suficientes.

No se modificó funcionalidad en este bloque. Los cambios recomendados deben ejecutarse en 10D-1 y 10D-2, manteniendo Django como fuente de verdad.

## 2. Alcance revisado

Se revisaron:

- `frontend/src/app/**`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/dashboard/DashboardSidePanel.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/dashboard.ts`
- `frontend/src/lib/admin-config.ts`
- `frontend/src/lib/catalogos-config.ts`
- componentes de administración, reportes, actas y trayectoria
- APIs backend relevantes de reportes, auditoría, usuarios, catálogos y trayectoria
- documentación reciente de 10C y 9K

## 3. Hallazgos principales

| ID | Hallazgo | Severidad | Documento de detalle |
|---|---|---|---|
| H-01 | El panel derecho aparece en muchas pantallas operativas porque `AppShell` lo activa por defecto. | P1 | `matriz_layout_panel_derecho_10d0.md` |
| H-02 | Persisten enlaces visibles a Django Admin y vistas Django antiguas en dashboards. | P1 | `matriz_rutas_front_backend_10d0.md` |
| H-03 | Auditoría visual mezcla permisos de exportaciones y eventos críticos. | P1 | `diagnostico_permisos_visuales_10d0.md` |
| H-04 | Formularios de trayectoria, movimientos y apertura piden IDs/códigos como texto libre. | P1 | `matriz_campos_front_backend_10d0.md` |
| H-05 | Selectores relacionales de administración/catálogos no filtran activos ni contexto. | P1 | `matriz_campos_front_backend_10d0.md` |
| H-06 | Acciones operativas de periodos pueden verse desde perfiles de consulta. | P1 | `matriz_permisos_menu_10d0.md` |
| H-07 | Reportes y auditoría requieren ancho completo y mejor separación conceptual. | P1/P2 | `inventario_pantallas_portal_10d0.md` |
| H-08 | Hay duplicidades terminológicas y tarjetas repetidas en dashboards. | P2 | `diagnostico_terminologia_10d0.md` |

## 4. Hallazgos críticos

No se confirmó un P0 de seguridad explotable desde la revisión estática. Sí hay P1 que pueden generar errores de acceso, confusión operativa o exposición innecesaria de pantallas:

- Jefatura pedagógica puede ver `/reportes/auditoria`, pero el tab de exportaciones depende de un permiso backend que no incluye pedagogía.
- Dashboard de Estadística apunta a `/admin/catalogos/`, aunque existe `/catalogos`.
- Dashboard de Jefatura pedagógica apunta a una vista antigua de evaluación.
- Formularios críticos de trayectoria/movimientos/periodos permiten captura manual de IDs internos.

## 5. Layout y panel derecho

`AppShell` recibe `showRightPanel = true` por defecto y renderiza `DashboardSidePanel`. Algunas pantallas críticas ya lo desactivan, como captura de calificaciones, detalle de acta y toda la familia `TrajectoryOperations`. Sin embargo, administración, catálogos, reportes, auditoría y varias listas de actas aún lo muestran.

Recomendación 10D-1: usar layout `workspace` o `full-width` para:

- `/reportes/**`
- `/catalogos/**`
- `/administracion/**`
- `/docente/asignaciones/**`
- `/docente/actas/**`
- `/discente/actas/**`
- `/estadistica/actas/**`
- `/jefatura-carrera/actas/**`
- `/jefatura-academica/actas/**`

## 6. Navegación/sidebar/dashboard

El `Sidebar` ya está razonablemente centralizado y usa funciones de permiso. Los dashboards por perfil conservan más deuda:

- Admin tiene tarjetas a Django Admin aunque ya hay portal.
- Estadística tiene dos entradas de catálogos, una de ellas a Django Admin.
- Estadística tiene kárdex antiguo y kárdex PDF nuevo.
- Jefatura carrera y académica tienen tarjetas duplicadas de trayectoria.
- Discente mantiene "Mi carga académica" hacia una ruta antigua.
- Jefatura pedagógica mantiene consulta académica en ruta antigua.

## 7. Rutas y enlaces frontend/backend

Los enlaces antiguos detectados están documentados en la matriz de rutas. La regla propuesta:

- Si existe pantalla Next.js equivalente, reemplazar.
- Si es Django Admin, mantener solo para Admin/soporte técnico.
- Si es vista Django antigua sin equivalente, marcar pendiente y no presentarla como flujo moderno.
- Si es API, no debe aparecer como enlace visible.

## 8. Permisos visuales por perfil

La capa visual debe separar lectura, escritura y operación crítica. Los puntos más importantes:

- `canAccessAuditoriaExportaciones` debe separarse en eventos críticos vs exportaciones.
- `canAccessPeriodosOperativos` permite ver periodos a jefaturas, pero acciones como apertura deben depender de `canOperateTrayectoria`.
- `canAccessTrayectoriaOperativa` incluye Discente; conviene limitar su experiencia a mi historial.
- Administración requiere copy/controles claros entre lectura institucional y escritura Admin.

## 9. Formularios y campos

Administración y catálogos usan un esquema configurable aceptable, pero `RelationSelect` no filtra registros activos ni contexto. En operaciones críticas, varios formularios usan texto libre:

- `inscripcion_materia_id`
- `discente_id`
- `situacion_codigo`
- `periodo_id`
- `tipo_movimiento`
- `grupo_origen_id`
- `grupo_destino_id`
- `periodo_origen_id`
- `periodo_destino_id`

Recomendación 10D-1: empezar por selectores básicos para los flujos mutables antes de mejorar filtros de reportes.

## 10. Datos sensibles y privacidad

No se observaron tokens/contraseñas expuestos como texto visible. Buenas señales:

- El login usa campo password.
- La tabla de auditoría no muestra `metadatos_json` ni `cambios_json`.
- Reportes de trayectoria filtran columnas con matrícula.
- Hay avisos de privacidad en historial y auditoría.

Riesgos a controlar:

- Comentarios de inconformidad en reportes autorizados.
- Historial interno y diagnóstico de cierre con datos nominales.
- Formularios con IDs manuales que pueden inducir captura de matrícula o nombres.

## 11. Terminología

Hay convivencia de `Materia`, `Asignatura`, `Unidad de aprendizaje`, `Antigüedad`, `Generación`, `Kardex/Kárdex` y títulos repetidos de trayectoria. No bloquea operación, pero sí debe normalizarse después de los P1.

## 12. Reportes y auditoría

El módulo de reportes está completo, pero saturado. El usuario debe distinguir:

- reportes para consulta/exportación;
- historial de exportaciones;
- auditoría institucional de eventos críticos;
- kárdex oficial.

El panel derecho estorba especialmente en reportes con tablas y filtros. Auditoría 9K debe quedar full width y con permisos separados por tab.

## 13. Pantallas faltantes o incompletas

Pantallas faltantes o pendientes:

- Mi carga académica del discente en Next.js, si se mantiene como flujo.
- Asignaciones docentes de jefatura en Next.js.
- Consulta académica específica para Jefatura pedagógica.
- Selectores/buscadores operativos para trayectoria, movimientos y periodos.

Pantallas existentes pero con corrección UX:

- administración/catálogos;
- reportes completos;
- auditoría;
- listas de actas;
- formularios de trayectoria y movimientos.

## 14. Priorización

P0: no confirmado.

P1:

- layout operativo sin panel derecho;
- reemplazo de rutas antiguas con equivalentes Next.js;
- separación de permisos de auditoría;
- formularios críticos sin IDs manuales;
- ocultar acciones de periodo a perfiles de consulta;
- selectores relacionales con filtros activos/contextuales.

P2:

- reorganización de dashboard/sidebar;
- filtros de reportes más guiados;
- pantalla de carga académica o retiro del enlace;
- normalización de comentarios sensibles.

P3:

- terminología fina;
- iconografía;
- estados vacíos;
- microcopy visual.

## 15. Recomendación de implementación

Conviene hacer una corrección inmediata 10D-1 antes del pulido visual. El primer paquete debe ser pequeño y verificable: layout, enlaces antiguos, permisos visuales de auditoría/periodos y formularios críticos con selectores básicos.

## 16. Propuesta de alcance para 10D-1

1. Pasar pantallas operativas/reportes a `showRightPanel={false}`.
2. Reemplazar enlaces antiguos con equivalentes Next.js existentes.
3. Separar permisos visuales de auditoría de eventos y exportaciones.
4. Ocultar botones de apertura/cierre a perfiles de consulta.
5. Crear selectores mínimos para extraordinarios, situaciones, movimientos y apertura.
6. Filtrar activos en `RelationSelect` o permitir parámetros por campo.

## 17. Qué dejar para 10D-2 / 10D-3 / 10D-4 / 10E

| Bloque | Contenido recomendado |
|---|---|
| 10D-2 | Reordenar menú/dashboard, consolidar tarjetas, resolver carga académica y consulta pedagógica. |
| 10D-3 | Pulido visual, terminología, estados vacíos, densidad responsive. |
| 10D-4 | Integración frontend más rica de auditoría si se requiere detalle/resumen. |
| 10E | Tableros analíticos, BI y visualizaciones avanzadas. |

## 18. Validaciones ejecutadas

| Comando | Resultado |
|---|---|
| `docker compose exec -T backend python manage.py check` | OK. `System check identified no issues`. |
| `docker compose exec -T backend python manage.py makemigrations --check` | OK. `No changes detected`. |
| `docker compose exec -T backend python manage.py test auditoria` | OK. 7 pruebas ejecutadas. |
| `docker compose exec -T backend python manage.py test reportes` | OK. 74 pruebas ejecutadas. |
| `docker compose exec -T backend python manage.py test` | OK. 457 pruebas ejecutadas. |
| `docker compose exec -T frontend npm run lint` | OK. ESLint sin warnings. |
| `docker compose exec -T frontend npm run build` | OK. Build Next.js generado correctamente. |

## 19. Limitaciones del diagnóstico

- Revisión principalmente estática de código y documentación.
- No se corrigió código por restricción del bloque.
- No se ejecutó navegación manual por perfil en navegador.
- No se alteraron permisos backend.
- Los hallazgos de ámbito por jefatura dependen de la inferencia real en backend y deben validarse con usuarios sintéticos.

## Conclusión

Sí conviene corrección inmediata. Primero deben corregirse layout, rutas antiguas y permisos visuales que generan errores o confusión. No deben tocarse reglas académicas, modelos, migraciones ni lógica backend en 10D-1 salvo que una corrección visual revele un defecto backend confirmado.
