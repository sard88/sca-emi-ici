# Matriz de resultados E2E 11A

| ID caso | Rol | Módulo | Estado | Resultado observado | Evidencia | Defecto asociado |
| --- | --- | --- | --- | --- | --- | --- |
| E2E-00 | Anónimo | Seguridad | OK | Rutas protegidas bloqueadas o con alerta institucional. | `npm run e2e:qa` | - |
| E2E-01 | Admin | Administración | OK | Dashboard, usuarios, catálogos y auditoría accesibles para Admin. | `npm run e2e:qa` | - |
| E2E-02 | Estadística | Reportes | OK | Actas vivas, períodos, reportes y movimientos accesibles. | `npm run e2e:qa` | - |
| E2E-03 | Docente | Actas | OK | Asignaciones y actas propias accesibles; administración no operativa. | `npm run e2e:qa` | - |
| E2E-04 | Discente | Conformidad | OK | Carga, actas e historial propios accesibles. | `npm run e2e:qa` | - |
| E2E-05 | Jefatura carrera | Validación | OK | Actas y pendientes de asignación disponibles sin borrador docente como estado principal. | `npm run e2e:qa` | - |
| E2E-06 | Jefatura académica | Formalización | OK | Pendientes y formalizadas accesibles sin 403 operativo. | `npm run e2e:qa` | - |
| E2E-07 | Estadística | Consolidado | OK | Reportes y consolidado por materia accesibles. | `npm run e2e:qa` | - |
| E2E-08 | Estadística | Trayectoria | OK | Trayectoria y movimientos accesibles. | `npm run e2e:qa` | - |
| E2E-09 | Estadística | Períodos | OK | Períodos y pendientes de asignación accesibles. | `npm run e2e:qa` | - |
| E2E-10 | Admin | Auditoría | OK | Auditoría visible sin secretos reales ni patrones de cookie/CSRF. | `npm run e2e:qa` | - |
| E2E-11 | Discente | Seguridad | OK | Discente no opera reportes globales. | `npm run e2e:qa` | - |
