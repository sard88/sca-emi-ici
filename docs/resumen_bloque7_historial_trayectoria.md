# Bloque 7 - Historial académico y trayectoria

## Resultado general

El Bloque 7 queda implementado y validado como una primera versión funcional del historial académico y la trayectoria del discente.

Resultado: **APROBADO CON OBSERVACIONES NO BLOQUEANTES**.

Con el alcance actual, es posible pasar al siguiente bloque porque no existen bloqueantes técnicos detectados en las validaciones automáticas ni en el recorrido visual realizado con datos QA locales. Las observaciones pendientes corresponden a funcionalidades posteriores, como kárdex oficial, reportes, exportaciones o actas extraordinarias formales.

## Objetivo del bloque

El objetivo fue incorporar un módulo que permita consultar la trayectoria académica del discente usando información oficial ya consolidada, principalmente:

- Actas `FINAL` formalizadas.
- Campos oficiales de `InscripcionMateria`.
- Extraordinarios registrados por Estadística/Admin.
- Eventos de trayectoria, como baja temporal, baja definitiva y reingreso.

La captura preliminar y las actas no formalizadas siguen sin formar parte del historial oficial.

## Contexto previo

Antes de este bloque ya existían:

- Captura preliminar de calificaciones.
- Servicio de cálculo académico.
- Gestión formal de actas.
- Formalización de actas finales.
- Actualización de campos oficiales de `InscripcionMateria` solo al formalizar el acta final.

Todavía no existía un módulo de trayectoria que reuniera esos resultados para consulta histórica del discente.

## Qué se implementó

Se agregó la app/módulo `trayectoria` con los siguientes elementos:

- Catálogo de situaciones académicas.
- Catálogo de resultados académicos.
- Eventos de situación académica.
- Registro operativo de extraordinarios.
- Servicio de historial académico.
- Vistas para consulta y operación básica.
- Templates simples con Django.
- Admin técnico para revisión.
- Pruebas automatizadas del flujo principal.

## Modelos agregados

- `CatalogoSituacionAcademica`
- `CatalogoResultadoAcademico`
- `EventoSituacionAcademica`
- `Extraordinario`

## Catálogos de trayectoria

### Situaciones académicas

Se contemplan las situaciones base:

- `ACTIVO`: discente activo o regular.
- `BAJA_TEMPORAL`: baja temporal con posibilidad de reingreso.
- `BAJA_DEFINITIVA`: baja definitiva del discente.
- `REINGRESO`: reincorporación posterior a baja temporal.
- `EGRESADO`: cierre académico por egreso.

### Resultados académicos

Se contemplan resultados/marcas mínimas para el prototipo:

- `APROBADO`
- `REPROBADO`
- `APROBADO_EXTRAORDINARIO`
- `EE`
- `ACREDITADA`
- `APROBADO_NO_NUMERICO`
- `EXCEPTUADO`

## Cambios recientes incorporados

### Baja definitiva

Se agregó la opción **Baja definitiva** al formulario de registro de situación académica.

Motivo:

El flujo de trayectoria necesitaba distinguir una baja temporal, que puede cerrarse con reingreso, de una baja definitiva, que representa una situación académica distinta y más permanente.

Qué se hizo:

- Se agregó la clave `BAJA_DEFINITIVA`.
- Se creó una migración de datos para asegurar que el catálogo exista.
- Se ajustó el servicio para que, al registrar baja definitiva, `Discente.situacion_actual` cambie a `baja_definitiva`.

Qué se mantuvo:

- No se eliminó ninguna situación existente.
- No se modificó la lógica de baja temporal.
- No se modificó la lógica de reingreso.
- No se agregó un flujo complejo de dictamen o baja administrativa formal.

### Accesos operativos para jefatura

Se ocultaron los botones de:

- `Registrar extraordinario`
- `Registrar situación académica`

cuando el usuario entra como jefatura de carrera o jefe de subsección de Ejecución y Control.

Motivo:

La jefatura puede consultar historiales de su ámbito, pero no debe registrar extraordinarios ni situaciones académicas. Antes podía ver botones que terminaban en acceso denegado (`403`), lo cual era correcto a nivel backend pero confuso visualmente.

Qué se hizo:

- Se mantuvo la validación backend.
- Se ocultaron los accesos operativos en la vista de búsqueda/consulta de historial cuando el usuario no tiene permiso operativo de trayectoria.
- Se conservaron los accesos para Estadística/Admin.

Qué se mantuvo:

- Jefatura sigue pudiendo consultar historiales de su ámbito.
- Jefatura sigue bloqueada por backend si intenta entrar por URL directa a registrar extraordinarios o situaciones.
- Estadística/Admin siguen siendo los perfiles autorizados para operar trayectoria.

## Reglas principales implementadas

- El historial oficial se construye desde `InscripcionMateria` con acta `FINAL` formalizada.
- Las capturas preliminares no aparecen como resultados oficiales.
- Las actas en borrador, publicadas, remitidas o no formalizadas no aparecen como historial oficial.
- El extraordinario solo se permite cuando existe ordinario reprobatorio menor a 6.0.
- El extraordinario requiere acta `FINAL` formalizada.
- Solo se permite un extraordinario por inscripción.
- Si el extraordinario es aprobado, se refleja marca `EE`.
- Si el extraordinario es reprobado, se registra/habilita baja temporal.
- La evidencia ordinaria se conserva aunque exista extraordinario.
- El reingreso cierra la baja temporal abierta.
- La baja definitiva actualiza la situación actual del discente a baja definitiva.

## Permisos y perfiles

### Discente

- Consulta únicamente su propio historial.
- No puede consultar historial ajeno.
- No puede registrar extraordinarios.
- No puede registrar situaciones académicas.

### Estadística/Admin

- Consulta historiales.
- Registra extraordinarios.
- Registra situaciones académicas.
- Puede registrar baja temporal, baja definitiva y reingreso.

### Jefatura de carrera / Jefe de subsección de Ejecución y Control

- Consulta historiales de su ámbito.
- No registra extraordinarios.
- No registra situaciones académicas.
- No ve botones operativos que lo lleven a `403`.

### Jefatura académica / pedagógica

- Consulta según permisos institucionales definidos.
- No se le agregaron operaciones nuevas en este bloque.

## Rutas principales

- `GET /trayectoria/mi-historial/`
- `GET /trayectoria/historial/`
- `GET /trayectoria/historial/<id>/`
- `GET/POST /trayectoria/extraordinarios/registrar/`
- `GET/POST /trayectoria/situaciones/registrar/`

## Qué se mantuvo igual

- La captura preliminar sigue siendo preliminar.
- El historial no depende de borradores ni capturas preliminares.
- No se implementó kárdex oficial.
- No se implementaron reportes formales.
- No se implementaron exportaciones PDF/Excel.
- No se implementaron actas extraordinarias formales complejas.
- No se implementó rectificación de actas.
- No se implementó reapertura de actas.
- No se modificó el flujo principal de actas del Bloque 6.

## Validaciones realizadas

Comandos ejecutados:

```bash
docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test trayectoria
docker compose exec -T backend python manage.py test usuarios trayectoria
```

Resultados:

- `migrate`: OK.
- `check`: OK.
- `makemigrations --check`: OK, sin cambios pendientes.
- `test trayectoria`: OK, 14 pruebas.
- `test usuarios trayectoria`: OK, 91 pruebas.

## Validación visual realizada

Se validó en navegador con datos QA locales:

- Discente consulta su propio historial.
- Discente no consulta historial ajeno.
- Estadística registra extraordinario aprobado.
- Estadística registra extraordinario reprobado.
- El extraordinario aprobado refleja `EE`.
- El extraordinario reprobado genera baja temporal.
- Estadística registra baja temporal.
- Estadística registra reingreso.
- Jefatura consulta historial de su ámbito.
- Jefatura no consulta historial fuera de su ámbito.
- Jefatura ya no ve botones de registrar extraordinario ni registrar situación académica.
- Estadística sí ve la opción `Baja definitiva` en el formulario de situación académica.

## Archivos principales modificados

- `backend/trayectoria/models.py`
- `backend/trayectoria/services.py`
- `backend/trayectoria/views.py`
- `backend/trayectoria/forms.py`
- `backend/trayectoria/admin.py`
- `backend/trayectoria/urls.py`
- `backend/trayectoria/tests.py`
- `backend/trayectoria/templates/trayectoria/`
- `backend/trayectoria/migrations/0001_initial.py`
- `backend/trayectoria/migrations/0002_seed_catalogos_base.py`
- `backend/trayectoria/migrations/0003_seed_baja_definitiva.py`
- `backend/config/urls.py`
- `backend/usuarios/views.py`
- `backend/usuarios/signals.py`
- `README.md`
- `docs/resumen_bloque7_historial_trayectoria.md`

## Riesgos y observaciones no bloqueantes

- El catálogo oficial de resultados y marcas puede requerir ajustes institucionales más finos.
- El extraordinario actual es operativo y mínimo; no representa todavía un acta extraordinaria formal.
- La baja definitiva existe como evento de trayectoria, pero no se implementó un flujo documental formal de baja.
- El kárdex debe construirse después, cuando historial y trayectoria estén estables.
- La consolidación estadística y reportes formales quedan para bloques posteriores.
- Las reglas finales de egreso, baja definitiva documental y dictamen institucional pueden requerir definición adicional.

## Pendientes intencionales

- Kárdex oficial.
- Reportes PDF/Excel.
- Cuadros estadísticos.
- Actas extraordinarias formales.
- Rectificación o reapertura de actas.
- Consolidación estadística final.
- Flujo documental completo para baja definitiva.

## Conclusión

El Bloque 7 queda suficientemente estable para avanzar al siguiente bloque.

La implementación mantiene separadas las responsabilidades:

- Actas formalizadas como fuente oficial.
- Historial como consulta y trayectoria.
- Estadística/Admin como operadores de extraordinarios y situaciones.
- Jefatura como perfil de consulta por ámbito.

No se detectan bloqueantes técnicos. Se recomienda cerrar este bloque con commit y push antes de iniciar un siguiente bloque grande.
