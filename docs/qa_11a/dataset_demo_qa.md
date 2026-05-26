# Dataset demo QA integral 11A

## Objetivo

El Bloque 11A agrega un dataset ficticio, idempotente y seguro para validar el Sistema de Control Académico EMI - ICI por perfil, sin usar datos reales ni modificar reglas académicas.

## Comando

```powershell
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small
docker compose exec -T backend python manage.py seed_demo_qa_integral --size medium
docker compose exec -T backend python manage.py seed_demo_qa_integral --size full
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small --dry-run
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small --reset-qa
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small --print-credentials
```

La contraseña se toma de `DEMO_QA_PASSWORD`. Si no existe, el entorno local usa un fallback demo. No debe usarse en producción.

## Tamaños

| Tamaño | Alcance |
| --- | --- |
| SMALL | 4 carreras, 2 antigüedades, 4 semestres, 1 grupo por semestre, 3 discentes por grupo, 2 asignaturas por semestre y 2 docentes por carrera. |
| MEDIUM | 4 carreras, 3 antigüedades, 8 semestres, 2 grupos por semestre, 5 discentes por grupo, 3 asignaturas por semestre y 3 docentes por carrera. |
| FULL | 4 carreras, 5 antigüedades, 12 semestres, 2 grupos por semestre, 5 discentes por grupo, 5 asignaturas por semestre y 3 docentes por carrera. |

## Datos generados

- Carreras QA: `QA_ICI`, `QA_ICE`, `QA_IC`, `QA_II`.
- Planes QA: `QA_PLAN_ICI_2026`, `QA_PLAN_ICE_2026`, `QA_PLAN_IC_2026`, `QA_PLAN_II_2026`.
- Antigüedades QA por carrera y año.
- Períodos: `QA_2025_2`, `QA_2026_1`, `QA_2026_2`.
- Grupos por carrera y semestre, por ejemplo `QA_ICI_4A`.
- Materias y programas de asignatura con clave `QA_*`.
- Esquemas de evaluación con 1, 2 o 3 parciales y variantes con o sin exención.
- Usuarios demo `qa_*` por rol.
- Asignaciones docentes, adscripciones, inscripciones, capturas preliminares, actas QA, eventos de trayectoria y auditoría.

## Seguridad de datos

- El seed solo crea o reutiliza datos QA.
- `--reset-qa` solo inactiva o archiva registros con prefijo `QA_` o usuarios `qa_*`.
- No borra datos reales.
- No usa nombres reales, matrículas reales ni documentos reales.
- Las secciones institucionales existentes se reutilizan sin actualizar datos reales; las subsecciones de prueba sí usan prefijo `QA_`.

## Escenarios preparados

| ID | Escenario | Propósito |
| --- | --- | --- |
| ESC-01 | Flujo completo aprobado | Captura, acta, publicación, conformidad, validación y formalización. |
| ESC-02 | Exención | Discentes con parciales altos para validar exención. |
| ESC-03 | Reprobado | Resultado final menor a 6 para extraordinario. |
| ESC-04 | Incompleto | Capturas faltantes para validar bloqueos. |
| ESC-05 | Cambio de grupo válido | Movimiento QA sin actas vivas bloqueantes. |
| ESC-06 | Cambio de grupo bloqueado | Movimiento con acta viva. |
| ESC-07 | Cierre bloqueado | Período con bloqueantes. |
| ESC-08 | Cierre exitoso | Período con resultados completos. |
| ESC-09 | Apertura | Promoción y pendientes de asignación docente. |
| ESC-10 | Reportes y auditoría | Datos para reportes y eventos críticos. |
