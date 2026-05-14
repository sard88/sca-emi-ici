# Matriz layout y panel derecho - Bloque 10D-0

## Hallazgo base

`frontend/src/components/layout/AppShell.tsx` define `showRightPanel = true` por defecto y renderiza `DashboardSidePanel` en una columna fija de 340/350 px. Varias pantallas operativas llaman `<AppShell>` sin desactivar el panel, mientras que trayectoria y algunos detalles de actas ya usan `showRightPanel={false}`.

El panel contiene actividad reciente, calendario institucional y eventos próximos. Es valioso en home/dashboard, pero reduce espacio útil en tablas, grillas, filtros, auditoría y flujos de operación.

## Matriz

| Ruta | Componente/página | Layout actual | Layout recomendado | Impacto | Prioridad | Observación |
|---|---|---:|---:|---|---|---|
| `/dashboard` | `GeneralDashboard` | Panel derecho visible | Dashboard con panel | Correcto | P3 | Es el caso natural para actividad/calendario/agenda. |
| `/admin-soporte` | `ProfilePanel` | Panel derecho visible | Dashboard con panel opcional | Bajo | P3 | Es home de perfil, puede conservar panel. |
| `/docente` | `ProfilePanel` | Panel derecho visible | Dashboard con panel opcional | Bajo | P3 | Home de perfil, no workspace. |
| `/discente` | `ProfilePanel` | Panel derecho visible | Dashboard con panel opcional | Bajo | P3 | Home de perfil, no workspace. |
| `/estadistica` | `ProfilePanel` | Panel derecho visible | Dashboard con panel opcional | Bajo | P3 | Home de perfil, aunque suele enlazar a módulos densos. |
| `/jefatura-carrera` | `ProfilePanel` | Panel derecho visible | Dashboard con panel opcional | Bajo | P3 | Home de perfil. |
| `/jefatura-academica` | `ProfilePanel` | Panel derecho visible | Dashboard con panel opcional | Bajo | P3 | Home de perfil. |
| `/jefatura-pedagogica` | `ProfilePanel` | Panel derecho visible | Dashboard con panel opcional | Bajo | P3 | Home de perfil. |
| `/perfil` | `PerfilPage` | Panel derecho visible | Panel opcional | Bajo | P3 | Puede mantenerse si el perfil es breve. |
| `/administracion` | `AdminCatalogIndex` | Panel derecho visible | Workspace sin panel | Medio | P1 | El índice ya tiene tarjetas administrativas; el panel agrega ruido. |
| `/administracion/[slug]` | `CatalogResourcePage` | Panel derecho visible | Workspace sin panel | Alto | P1 | Tabla, filtros y modal/formulario pierden ancho. |
| `/administracion/[slug]/[id]` | `CatalogResourcePage` | Panel derecho visible | Full width | Alto | P1 | Detalle y edición necesitan lectura horizontal clara. |
| `/catalogos` | `AdminCatalogIndex` | Panel derecho visible | Workspace sin panel | Medio | P1 | Índice funcional, no dashboard personal. |
| `/catalogos/[slug]` | `CatalogResourcePage` | Panel derecho visible | Workspace sin panel | Alto | P1 | Tablas de catálogo y formularios necesitan ancho. |
| `/catalogos/[slug]/[id]` | `CatalogResourcePage` | Panel derecho visible | Full width | Alto | P1 | Componentes de evaluación en detalle requieren espacio. |
| `/docente/asignaciones` | `DocenteAsignacionesPage` | Panel derecho visible | Workspace sin panel | Medio | P1 | Lista operativa de asignaciones. |
| `/docente/asignaciones/[id]` | `DocenteAsignacionDetallePage` | Panel derecho visible | Workspace sin panel | Medio | P1 | Detalle de cortes/actas debe priorizar operación. |
| `/docente/asignaciones/[id]/captura/[corte]` | `CapturaPage` | Full width | Full width | Correcto | P3 | La grilla ya desactiva panel. |
| `/docente/asignaciones/[id]/resumen` | `ResumenPage` | Full width | Full width | Correcto | P3 | Resumen de cálculo tiene espacio completo. |
| `/docente/actas` | `DocenteActasPage` | Panel derecho visible | Workspace sin panel | Medio | P1 | Lista de actas y estados. |
| `/docente/actas/[id]` | `DocenteActaDetailPage` | Full width | Full width | Correcto | P3 | Detalle de acta ya desactiva panel. |
| `/discente/actas` | `DiscenteActasPage` | Panel derecho visible | Workspace sin panel | Medio | P2 | Lista personal; puede ser sin panel para consistencia. |
| `/discente/actas/[detalleId]` | `DiscenteActaDetallePage` | Panel derecho visible | Full width | Medio | P1 | Conformidad y detalle individual requieren foco. |
| `/estadistica/actas` | `EstadisticaActasPage` | Panel derecho visible | Workspace sin panel | Alto | P1 | Tabla de actas operativas. |
| `/estadistica/actas/[id]` | `EstadisticaActaDetailPage` | Full width | Full width | Correcto | P3 | Detalle ya desactiva panel. |
| `/jefatura-carrera/actas` | `JefaturaCarreraActasPage` | Panel derecho visible | Workspace sin panel | Alto | P1 | Bandeja de validación. |
| `/jefatura-carrera/actas/[id]` | `JefaturaCarreraActaDetailPage` | Full width | Full width | Correcto | P3 | Validación de acta ya usa ancho completo. |
| `/jefatura-academica/actas` | `JefaturaAcademicaActasPage` | Panel derecho visible | Workspace sin panel | Alto | P1 | Bandeja de formalización. |
| `/jefatura-academica/actas/[id]` | `JefaturaAcademicaActaDetailPage` | Full width | Full width | Correcto | P3 | Formalización ya usa ancho completo. |
| `/trayectoria` | `TrajectoryHomeCards` | Full width | Workspace sin panel | Correcto | P3 | Todo el módulo de trayectoria usa `AccessPage` sin panel. |
| `/trayectoria/**` | `TrajectoryOperations` | Full width | Full width | Correcto | P3 | Formularios, tablas e historial ya están sin panel. |
| `/movimientos-academicos/**` | `TrajectoryOperations` | Full width | Full width | Correcto | P3 | Flujo crítico sin panel. |
| `/periodos/**` | `TrajectoryOperations` | Full width | Full width | Correcto | P3 | Diagnóstico/cierre/apertura sin panel. |
| `/reportes` | `ReportesPage` | Panel derecho visible | Workspace sin panel | Medio | P1 | Página índice con varias tarjetas y tablas recientes. |
| `/reportes/actas` | `ReportesActasPage` | Panel derecho visible | Full width | Alto | P1 | Filtros y exportables necesitan ancho. |
| `/reportes/kardex` | `KardexPage` | Panel derecho visible | Full width | Alto | P1 | Buscador y tarjetas de exportación. |
| `/reportes/operativos` | `OperativeReportsIndex` | Panel derecho visible | Workspace sin panel | Medio | P1 | Índice funcional de reportes. |
| `/reportes/operativos/[slug]` | `OperativeReportPage` | Panel derecho visible | Full width | Alto | P1 | Tablas XLSX y filtros quedan comprimidos. |
| `/reportes/desempeno` | `PerformanceReportsIndex` | Panel derecho visible | Workspace sin panel | Medio | P1 | Índice funcional de reportes. |
| `/reportes/desempeno/[slug]` | `PerformanceReportPage` | Panel derecho visible | Full width | Alto | P1 | Tablas de desempeño requieren ancho. |
| `/reportes/trayectoria` | `TrajectoryReportsIndex` | Panel derecho visible | Workspace sin panel | Medio | P1 | Índice funcional de reportes. |
| `/reportes/trayectoria/[slug]` | `TrajectoryReportPage` | Panel derecho visible | Full width | Alto | P1 | Historial interno y reportes nominales son densos. |
| `/reportes/exportaciones` | `ExportacionesPage` | Panel derecho visible | Full width | Alto | P1 | Historial documental debe priorizar tabla. |
| `/reportes/auditoria` | `AuditoriaExportacionesPage` | Panel derecho visible | Full width | Alto | P1 | Eventos críticos y exportación XLSX necesitan ancho y privacidad visual. |

## Recomendación para 10D-1

Centralizar una política de layout por ruta o por variante de página: `dashboard`, `workspace` y `full-width`. El cambio prioritario es que todos los módulos operativos y reportes llamen `AppShell showRightPanel={false}` o usen un wrapper equivalente, sin alterar reglas backend.
