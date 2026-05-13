# Bloque 8.5 - Cierre y apertura de periodo académico

## 1. Resultado general

El Bloque 8.5 queda implementado y validado como un proceso asistido para el cierre y apertura de periodo académico.

El resultado general es **aprobado con observaciones no bloqueantes**. Se puede continuar al siguiente bloque porque el flujo principal ya permite diagnosticar un periodo, cerrarlo si no existen bloqueantes, aperturar el siguiente periodo, promover únicamente discentes elegibles y dejar pendientes de asignación docente para jefatura.

No se implementaron exportaciones, reportes formales ni promoción automática ciega. La lógica se mantuvo controlada para proteger actas, resultados oficiales, historial, trayectoria y kárdex.

## 2. Objetivo del bloque

El objetivo fue crear un proceso seguro para:

- Diagnosticar si un periodo académico puede cerrarse.
- Bloquear el cierre si existen actas finales faltantes, actas vivas o resultados oficiales incompletos.
- Registrar evidencia del cierre por periodo y por discente.
- Abrir un periodo destino existente sin inventar fechas ni claves institucionales.
- Promover solo a discentes académicamente promovibles.
- Conservar evidencia previa, sin borrar adscripciones, inscripciones ni resultados.
- Listar asignaturas pendientes de docente para que jefatura de carrera continúe con el flujo normal de asignación docente.

## 3. Contexto previo

Antes de este bloque ya existían:

- Bloques 1 a 4.5 con usuarios, roles, cargos, catálogos, estructura académica, relaciones operativas y vista temporal por rol.
- Bloque 5 y 5.5 con captura preliminar y cálculo académico.
- Bloque 6 con actas formales, publicación, conformidad, remisión, validación y formalización.
- Bloque 7 con historial académico, trayectoria, extraordinarios, baja temporal, baja definitiva y reingreso.
- Bloque 8 con kárdex oficial como vista derivada institucional.

El sistema ya tenía resultados oficiales en `InscripcionMateria`, pero aún no existía un proceso controlado para cerrar un periodo y preparar el siguiente.

## 4. Qué se implementó

Se implementaron los siguientes elementos:

- Diagnóstico de cierre de periodo.
- Servicio transaccional de cierre de periodo.
- Servicio idempotente de apertura de periodo.
- Trazabilidad de cierre por proceso.
- Trazabilidad de cierre por discente.
- Trazabilidad de apertura de periodo.
- Consulta de pendientes de asignación docente.
- Vistas web simples para operar cierre y apertura.
- Permisos específicos para Estadística/Admin y consulta por jefatura.
- Admin técnico de solo revisión para detalles generados por el sistema.
- Pruebas automatizadas del flujo.
- Documentación técnica en README y en este documento.

## 5. Modelos creados

### ProcesoCierrePeriodo

Guarda el proceso general de cierre de un periodo.

Campos principales:

- Periodo.
- Estado del proceso.
- Usuario que ejecutó el cierre.
- Fecha y hora de ejecución.
- Resumen JSON.
- Observaciones.

### DetalleCierrePeriodoDiscente

Guarda la clasificación individual de cada discente durante el cierre.

Campos principales:

- Proceso de cierre.
- Discente.
- Grupo origen.
- Clasificación.
- Motivo.
- Indicador de promovible.
- Indicador de extraordinario pendiente.
- Situación detectada.

Este modelo no representa una captura manual. Es evidencia generada por el sistema durante el cierre.

### ProcesoAperturaPeriodo

Guarda la ejecución de apertura entre un periodo origen y un periodo destino.

Campos principales:

- Periodo origen.
- Periodo destino.
- Usuario que ejecutó la apertura.
- Fecha y hora de ejecución.
- Estado del proceso.
- Resumen JSON.
- Observaciones.

## 6. Ajuste en PeriodoEscolar

Se amplió el estado de `PeriodoEscolar` para soportar:

- `planificado`.
- `activo`, mostrado como periodo abierto para conservar compatibilidad.
- `cerrado`.
- `inactivo`.

Se conservó `activo` como valor operativo de periodo abierto porque ya era usado por filtros existentes en grupos, asignaciones docentes, adscripciones e inscripciones. Esto evita romper módulos ya funcionales.

## 7. Servicios creados

### ServicioDiagnosticoCierrePeriodo

Evalúa si un periodo puede cerrarse.

Revisa:

- Actas `FINAL` faltantes.
- Actas vivas pendientes.
- Inscripciones sin resultado oficial.
- Extraordinarios pendientes.
- Discentes en baja temporal.
- Discentes en baja definitiva.
- Adscripciones inconsistentes.
- Grupos y asignaciones del periodo.

Devuelve:

- Bloqueantes.
- Advertencias.
- Discentes promovibles.
- Discentes pendientes de extraordinario.
- Discentes en baja temporal.
- Discentes en baja definitiva.
- Discentes egresables.
- Resumen por grupo.

### ServicioCierrePeriodo

Ejecuta el cierre definitivo si el diagnóstico no tiene bloqueantes críticos.

Reglas:

- No cierra si faltan actas `FINAL` formalizadas.
- No cierra si existen actas vivas pendientes.
- No cierra si hay resultados oficiales faltantes.
- No cierra si existen extraordinarios pendientes.
- Cambia el periodo a `cerrado` solo si todo procede.
- Crea el proceso de cierre y los detalles por discente.
- Es transaccional: si falla una parte, no deja el periodo a medias.

### ServicioAperturaPeriodo

Ejecuta la apertura del periodo destino.

Reglas:

- El periodo origen debe estar cerrado.
- El periodo destino debe existir previamente.
- El periodo destino puede estar `planificado` o `activo`.
- Si el destino está `planificado`, se cambia a `activo`.
- Calcula el semestre destino como `semestre_origen + 1`.
- Crea grupos destino solo cuando corresponde.
- Cierra adscripciones anteriores de discentes promovibles.
- Crea nuevas adscripciones activas para discentes promovibles.
- No mueve discentes con baja temporal, baja definitiva o extraordinario pendiente.
- Es idempotente: si se ejecuta dos veces, no duplica grupos ni adscripciones.

### listar_pendientes_asignacion_docente

Lista programas de asignatura esperados para los grupos del nuevo periodo que aún no tienen docente asignado.

Este servicio no asigna docentes ni genera inscripciones. Solo informa los pendientes para que jefatura de carrera opere el flujo ya existente.

## 8. Vistas y rutas agregadas

Rutas principales:

- `/actas/periodos/`
- `/actas/periodos/<id>/diagnostico/`
- `/actas/periodos/<id>/cerrar/`
- `/actas/cierres/<id>/`
- `/actas/apertura/`
- `/actas/aperturas/<id>/`
- `/actas/pendientes-asignacion-docente/`

Vistas implementadas:

- Lista de periodos para cierre.
- Diagnóstico de cierre.
- Ejecución de cierre definitivo.
- Detalle del proceso de cierre.
- Formulario de apertura de periodo.
- Detalle del proceso de apertura.
- Pendientes de asignación docente.

## 9. Permisos implementados

Se agregaron permisos específicos para no reutilizar permisos demasiado amplios.

Reglas:

- Estadística puede diagnosticar, cerrar y abrir periodos.
- Admin/superusuario puede operar por soporte técnico.
- Jefatura académica puede consultar resultados de cierre.
- Jefatura de carrera puede consultar pendientes de asignación docente de su ámbito.
- Docente no puede cerrar ni abrir periodos.
- Discente no puede cerrar ni abrir periodos.
- Los permisos se validan en backend y no solo ocultando botones.

## 10. Ajustes en dashboard y menú

Se agregaron enlaces según perfil:

- Estadística/Admin ve cierre de periodo.
- Estadística/Admin ve apertura de periodo.
- Jefatura de carrera ve pendientes de asignación docente.
- Docente y discente no ven accesos operativos de cierre/apertura.

Esto evita enlaces que terminen en accesos denegados innecesarios.

## 11. Admin técnico

Se registraron los modelos de cierre y apertura en el admin.

El ajuste importante fue dejar `DetalleCierrePeriodoDiscente` como evidencia generada por el sistema:

- No se puede agregar manualmente desde admin.
- No se puede eliminar manualmente desde admin.
- Se muestra principalmente como consulta.
- Los detalles se generan al ejecutar el cierre.

Esto reduce riesgo de inconsistencias y aclara que Estadística no debe capturar uno por uno a los discentes en ese módulo.

## 12. Reglas de cierre implementadas

- No permitir cierre con actas `FINAL` faltantes.
- No permitir cierre con actas vivas pendientes.
- No permitir cierre con inscripciones sin resultado oficial.
- No permitir cierre con extraordinarios pendientes.
- Clasificar discentes antes de la apertura.
- Registrar evidencia por discente.
- No borrar eventos, adscripciones ni inscripciones anteriores.
- Cambiar el periodo a cerrado solo cuando el cierre sea válido.

## 13. Reglas de apertura implementadas

- El periodo origen debe estar cerrado.
- El periodo destino debe existir.
- El periodo destino puede estar planificado o abierto.
- Si está planificado, se activa durante la apertura.
- Solo se promueven discentes promovibles.
- No se promueven bajas temporales.
- No se promueven bajas definitivas.
- No se promueven discentes con extraordinario pendiente.
- Se crea grupo destino si no existe.
- Se reutiliza grupo destino si ya existe.
- Se cierra adscripción anterior.
- Se crea nueva adscripción activa.
- El proceso es idempotente.

## 14. Pendientes de asignación docente

La vista de pendientes de asignación docente permite identificar programas esperados para los grupos del nuevo periodo que todavía no tienen docente asignado.

Reglas:

- No asigna docentes automáticamente.
- No genera inscripciones automáticamente.
- Respeta el flujo ya existente de `AsignacionDocente`.
- Cuando jefatura crea la asignación docente, el sistema genera las inscripciones con el flujo previo.

Esto mantiene la responsabilidad institucional de jefatura de carrera sobre la asignación docente.

## 15. Validaciones automáticas ejecutadas

Se ejecutaron las validaciones principales del proyecto.

| Comando | Resultado |
| --- | --- |
| `docker compose exec -T backend python manage.py check` | OK |
| `docker compose exec -T backend python manage.py makemigrations --check` | OK |
| `docker compose exec -T backend python manage.py test actas` | OK, 11 pruebas |
| `docker compose exec -T backend python manage.py test actas catalogos relaciones evaluacion trayectoria usuarios` | OK, 285 pruebas |
| `docker compose exec -T backend python manage.py test` | OK, 285 pruebas |

## 16. Validaciones manuales realizadas por navegador

Se hizo recorrido visual y operativo en navegador con datos de prueba controlados.

| Caso | Resultado |
| --- | --- |
| Diagnóstico con acta FINAL faltante | El sistema mostró bloqueante y no permitió cerrar. |
| Diagnóstico limpio | El sistema permitió cerrar el periodo. |
| Cierre de periodo | El periodo cambió a cerrado y se creó `ProcesoCierrePeriodo`. |
| Detalle por discente | El proceso mostró clasificación individual por discente. |
| No promover baja temporal | El discente en baja temporal no fue promovido. |
| No promover baja definitiva | El discente en baja definitiva no fue promovido. |
| Promover aprobado | El discente promovible recibió adscripción en grupo destino. |
| Apertura idempotente | La segunda ejecución no duplicó grupos ni adscripciones. |
| Pendientes de docente | La vista listó programas esperados sin docente asignado. |
| Jefatura asigna docente después | Al crear asignación docente para el grupo destino, se generaron inscripciones con el flujo existente. |
| Docente intenta cerrar o abrir periodo | El acceso fue denegado. |
| Discente intenta cerrar o abrir periodo | El acceso fue denegado. |
| Estadística ejecuta cierre/apertura | El acceso fue permitido y el flujo funcionó. |
| Jefatura consulta pendientes | El acceso fue permitido solo para pendientes de asignación docente. |

## 17. Datos de prueba usados

Para las validaciones se crearon datos locales de QA con claves controladas.

Estos datos sirvieron para probar:

- Periodo con diagnóstico bloqueado.
- Periodo con diagnóstico limpio.
- Periodo destino.
- Grupo origen.
- Grupo destino.
- Discentes promovibles.
- Discentes en baja temporal.
- Discentes en baja definitiva.
- Programa de asignatura pendiente de docente.
- Asignación docente posterior a la apertura.

Estos datos son locales de prueba y no forman parte de una carga institucional definitiva.

## 18. Qué se mantuvo igual

- No se modificaron actas formalizadas.
- No se modificó el kárdex oficial.
- No se duplicaron resultados oficiales.
- No se asignaron docentes automáticamente.
- No se generaron inscripciones durante la apertura.
- No se borraron adscripciones anteriores.
- No se borraron inscripciones anteriores.
- No se implementaron reportes PDF/Excel.
- No se implementó reapertura de actas.
- No se implementó reapertura de periodos.

## 19. Qué queda fuera del bloque

Quedan fuera de este bloque:

- Exportación PDF.
- Exportación Excel.
- Reportes formales.
- Cuadros de aprovechamiento.
- Actas extraordinarias formales.
- Rectificación de actas.
- Reapertura de actas.
- Reapertura de periodos.
- Asignación automática de docentes.
- Consolidación estadística documental.
- Modificación del kárdex oficial desde cierre/apertura.

## 20. Riesgos y observaciones no bloqueantes

- Los datos QA quedan en la base local; no afectan el código ni el repositorio, pero pueden limpiarse si se requiere una base local más ordenada.
- El cierre/apertura ya es funcional, pero sigue siendo un proceso institucional delicado y debe ejecutarse con diagnóstico previo.
- La promoción depende de que existan resultados oficiales completos.
- La asignación docente sigue siendo responsabilidad de jefatura de carrera.
- La transición de reapertura o corrección posterior de periodo no está implementada y debe definirse en un bloque futuro si la institución la requiere.

## 21. Archivos principales modificados

### Actas

- `backend/actas/models.py`
- `backend/actas/services.py`
- `backend/actas/forms.py`
- `backend/actas/views.py`
- `backend/actas/permisos.py`
- `backend/actas/urls.py`
- `backend/actas/admin.py`
- `backend/actas/tests.py`
- `backend/actas/migrations/0001_initial.py`
- `backend/actas/templates/actas/periodos_cierre_list.html`
- `backend/actas/templates/actas/diagnostico_cierre.html`
- `backend/actas/templates/actas/proceso_cierre_detalle.html`
- `backend/actas/templates/actas/apertura_periodo.html`
- `backend/actas/templates/actas/proceso_apertura_detalle.html`
- `backend/actas/templates/actas/pendientes_asignacion_docente.html`

### Catálogos

- `backend/catalogos/models.py`
- `backend/catalogos/migrations/0018_alter_periodoescolar_estado.py`

### Configuración y navegación

- `backend/config/urls.py`
- `backend/usuarios/views.py`

### Documentación

- `README.md`
- `docs/resumen_bloque8_5_cierre_apertura_periodo.md`

## 22. Conclusión

El Bloque 8.5 queda implementado como un proceso asistido, trazable e idempotente. El sistema ya puede diagnosticar un periodo, bloquear cierres inseguros, cerrar periodos válidos, abrir un periodo destino y preparar grupos/adscripciones sin asignar docentes automáticamente.

Con las pruebas automáticas y validaciones manuales realizadas, el bloque queda listo para cerrarse en Git y continuar al siguiente bloque, manteniendo como pendientes intencionales las exportaciones, reportes formales, reapertura y reglas documentales avanzadas.
