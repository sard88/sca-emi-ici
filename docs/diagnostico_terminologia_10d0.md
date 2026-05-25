# Diagnóstico terminológico - Bloque 10D-0

## Criterio

No se corrigió texto del frontend. Esta matriz registra inconsistencias visibles o documentales que conviene normalizar en 10D-2/10D-3. Se prioriza la terminología ya consolidada por los bloques 10C y 9K.

| Término encontrado | Archivo | Contexto | Término recomendado | Prioridad | Observación |
|---|---|---|---|---|---|
| `Generacion` | `README.md` | Documentación histórica de modelos | `Antigüedad` o `Cohorte/antigüedad` según contexto | P2 | En frontend actual predomina `Antigüedad`. |
| `Materia` | `frontend/src/lib/catalogos-config.ts` | Catálogo y programa de asignatura | `Materia` o `Asignatura` de forma consistente | P2 | Reportes usan `Asignatura`; catálogos usan `Materias`. Elegir uno institucional. |
| `Unidad de aprendizaje` | `frontend/src/lib/reportes-*.ts` | Placeholder de filtros de asignatura | `Asignatura/Materia` según glosario final | P3 | No es grave, pero agrega tercer término. |
| `Inscripción materia ID` | `TrajectoryOperations.tsx` | Label de formulario extraordinario | `Inscripción a asignatura` | P2 | Evita exponer nombre técnico del modelo. |
| `Discente ID` | `TrajectoryOperations.tsx` | Formularios y filtros | `Discente` con buscador | P1 | El problema es funcional: pide ID manual. |
| `Aprobado true/false` | `TrajectoryOperations.tsx` | Filtro de extraordinarios | `Aprobado` con selector Sí/No | P2 | Texto técnico visible. |
| `Tipo movimiento` | `TrajectoryOperations.tsx` | Formularios y tablas | `Tipo de movimiento` | P3 | Microcopy. |
| `Trayectoria de mi carrera` | `frontend/src/lib/dashboard.ts` | Dos tarjetas de jefatura carrera | Diferenciar `Trayectoria operativa` y `Reportes de trayectoria` | P2 | Duplicidad causa ambigüedad. |
| `Seguimiento de trayectoria` | `frontend/src/lib/dashboard.ts` | Dos tarjetas de jefatura académica | Diferenciar módulo operativo y reportes | P2 | Duplicidad similar. |
| `Auditoría de exportaciones` | `frontend/src/lib/dashboard.ts` | Tarjeta Admin a `/reportes/auditoria` | `Auditoría institucional` | P2 | La página ahora contiene exportaciones y eventos críticos. |
| `Consulta institucional` | `frontend/src/lib/dashboard.ts` | Jefatura pedagógica a reportes operativos | `Reportes operativos` | P3 | Título amplio con poca especificidad. |
| `Kárdex institucional` | `frontend/src/lib/dashboard.ts` | Enlace antiguo `/trayectoria/kardex/` | `Kárdex oficial PDF` | P1 | Además debe cambiar la ruta. |
| `Mi carga académica` | `frontend/src/lib/dashboard.ts` | Discente a ruta antigua | `Mi carga académica` si se crea pantalla Next; si no, retirar | P2 | El término es correcto, la ruta no. |
| `Catálogos` y `Catálogos académicos` | `frontend/src/lib/dashboard.ts` | Estadística tiene ambas tarjetas | Solo `Catálogos académicos` | P2 | Una apunta a Django Admin y otra a Next. |
| `Jefe de Pedagógica` | `frontend/src/lib/admin-config.ts` | Label de cargo | `Jefatura pedagógica` | P2 | Homologar cargo con perfiles. |
| `Año escolar` | `frontend/src/lib/catalogos-config.ts` | Periodos | `Año escolar` | P3 | Correcto; evitar `Año escolar número` en nuevas pantallas. |
| `Kardex` sin tilde | Varias referencias técnicas/componentes | Nombres de componentes/imports | `Kárdex` en UI, `Kardex` solo identificadores técnicos | P3 | UI ya usa mayormente `Kárdex`. |

## Glosario sugerido

| Concepto | Término recomendado en UI |
|---|---|
| Estudiante militar/académico | Discente |
| Materia/asignatura | Elegir `Asignatura` para operación/reportes y `Materia` solo si el catálogo institucional lo exige |
| Programa | Programa de asignatura |
| Cohorte/generación | Antigüedad |
| Periodo | Periodo académico |
| Semestre operativo | Periodo académico o semestre, según campo real |
| Kárdex | Kárdex oficial |
| Jefe carrera | Jefatura de carrera |
| Encargado estadística | Estadística |
