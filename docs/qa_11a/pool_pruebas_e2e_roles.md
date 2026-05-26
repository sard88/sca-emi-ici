# Pool de pruebas E2E por rol 11A

| ID | Rol | Módulo | Objetivo | Precondición | Resultado esperado | Tipo |
| --- | --- | --- | --- | --- | --- | --- |
| E2E-00 | Anónimo | Seguridad | Bloquear rutas protegidas | Sin sesión | Redirección a login o acceso restringido | Negativo |
| E2E-01 | Admin | Administración | Consultar usuarios y catálogos | `qa_admin` activo | Vista institucional sin secretos | Positivo |
| E2E-02 | Estadística | Reportes | Consultar actas vivas, períodos y reportes | Dataset QA cargado | Rutas frontend sin backend directo | Positivo |
| E2E-03 | Docente | Actas | Ver asignaciones y actas propias | Asignaciones QA | No ve auditoría global ni asignaciones ajenas | Mixto |
| E2E-04 | Discente | Conformidad | Ver carga, actas e historial | Inscripciones QA | Solo información propia | Positivo |
| E2E-05 | Jefatura carrera | Validación | Consultar actas y pendientes | Actas remitidas QA | No se muestran borradores docentes como actividad principal | Positivo |
| E2E-06 | Jefatura académica | Formalización | Consultar pendientes y formalizadas | Actas QA | No depende de actas operativas ni 403 | Positivo |
| E2E-07 | Estadística | Consolidado | Abrir reporte consolidado | Actas formalizadas QA | Vista institucional sin texto técnico | Positivo |
| E2E-08 | Estadística | Trayectoria | Consultar trayectoria y movimientos | Eventos QA | Rutas disponibles sin error de cliente | Positivo |
| E2E-09 | Estadística | Períodos | Consultar cierre/apertura | Períodos QA | Vista de períodos disponible | Positivo |
| E2E-10 | Admin | Auditoría | Consultar auditoría | Eventos QA | No expone passwords, tokens ni CSRF | Negativo |
| E2E-11 | Discente | Seguridad | Intentar reportes globales | Sesión discente | Sin acceso operativo a reportes globales | Negativo |
