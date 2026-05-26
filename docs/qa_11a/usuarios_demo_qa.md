# Usuarios demo QA 11A

La contraseña demo no se documenta como secreto real. Definirla con `DEMO_QA_PASSWORD` para el seed y `E2E_QA_PASSWORD` para Playwright.

| Usuario | Rol/perfil | Propósito |
| --- | --- | --- |
| `qa_admin` | Administrador | Preparación y verificación del universo QA. |
| `qa_estadistica` | Estadística | Reportes, trayectoria, períodos y auditoría funcional. |
| `qa_jefatura_academica` | Jefatura académica | Formalización y consulta académica. |
| `qa_jefatura_pedagogica` | Jefatura pedagógica | Consulta de reportes y seguimiento pedagógico. |
| `qa_jefe_carrera_ici` | Jefatura de carrera ICI | Validación de actas en ámbito ICI. |
| `qa_jefe_carrera_ice` | Jefatura de carrera ICE | Validación de actas en ámbito ICE. |
| `qa_jefe_carrera_ic` | Jefatura de carrera IC | Validación de actas en ámbito IC. |
| `qa_jefe_carrera_ii` | Jefatura de carrera II | Validación de actas en ámbito II. |
| `qa_docente_ici_01` | Docente ICI | Captura y actas de asignaciones propias. |
| `qa_docente_ici_02` | Docente ICI | Validación negativa de asignaciones ajenas. |
| `qa_docente_ici_03` | Docente ICI | Escenarios alternos. |
| `qa_discente_ici_4a_01` | Discente ICI | Carga académica, actas y conformidad. |

Los usuarios docentes y discentes se repiten por carrera, grupo y tamaño seleccionado con prefijo `qa_`.
