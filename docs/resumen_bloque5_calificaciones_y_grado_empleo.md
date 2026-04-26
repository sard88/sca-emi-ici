# Resumen tecnico: Bloque 5, privacidad docente y grado/empleo institucional

## Objetivo general

Este bloque incorpora la captura basica de calificaciones preliminares y el calculo academico preliminar, sin implementar todavia el flujo formal de actas.

Tambien se agregan ajustes de privacidad y presentacion para vistas docentes:

- Ocultar la matricula militar en pantallas docentes.
- Mostrar una identificacion institucional mediante grado/empleo cuando exista.
- Mantener separados rol, cargo institucional y grado/empleo.

La intencion es validar el calculo academico antes de construir actas oficiales, historial, kardex o reportes formales.

## Cambios principales realizados

### 1. Captura preliminar de calificaciones

Se creo el modelo `CapturaCalificacionPreliminar` en la app `evaluacion`.

Registra:

- inscripcion a asignatura (`InscripcionMateria`);
- componente de evaluacion (`ComponenteEvaluacion`);
- corte academico;
- valor capturado;
- usuario que captura;
- fecha de creacion y actualizacion.

Esta captura es preliminar. No es acta formal y no actualiza datos oficiales.

### 2. Servicio de calculo academico

Se agrego `ServicioCalculoAcademico` en `backend/evaluacion/services.py`.

Calcula:

- resultado por corte;
- promedio de parciales;
- exencion preliminar;
- evaluacion final;
- resultado final preliminar;
- estado preliminar: aprobatorio, reprobatorio o incompleto.

La formula base respeta los pesos configurados en `EsquemaEvaluacion`.

Por omision se conserva 45/55, pero el servicio usa los valores guardados en el esquema.

### 3. Precision del calculo

Se ajusto la precision para evitar errores por redondeos tempranos.

Regla aplicada:

- Internamente se conserva precision con `Decimal`.
- No se redondean cortes, promedio ni resultado final intermedio.
- Solo se redondea a un decimal para visualizacion.

Ejemplos de visualizacion:

- `8.9999` se muestra como `9.0`.
- `8.94` se muestra como `8.9`.
- `8.95` se muestra como `9.0`.

### 4. Exencion preliminar

La exencion solo aplica cuando:

- el esquema permite exencion;
- la materia tiene 2 o 3 parciales;
- el promedio de parciales interno es mayor o igual a 9.0;
- existe componente de examen en el corte `FINAL`.

Para evitar confusion visual, el corte `FINAL` se muestra en la interfaz como `Evaluacion final`.

### 5. Vistas docentes temporales

Se agregaron rutas en `evaluacion`:

- `/evaluacion/docente/asignaciones/<id>/captura/<corte>/`
- `/evaluacion/docente/asignaciones/<id>/resumen/`

Se enlazaron desde las vistas temporales de docente.

Las pantallas permiten:

- capturar calificaciones por corte;
- ver resultado calculado por corte;
- consultar resumen por discente;
- revisar promedio de parciales, exencion, evaluacion final, resultado final preliminar y estado preliminar.

### 6. Permisos de captura

La captura queda restringida en backend:

- el docente solo puede capturar sus propias asignaciones;
- el administrador/superusuario puede acceder por soporte tecnico;
- otros perfiles no capturan en nombre del docente.

Esto no se implemento solo ocultando botones; se valida en las vistas.

### 7. Campos oficiales no modificados

Este bloque no actualiza automaticamente:

- `InscripcionMateria.calificacion_final`;
- `InscripcionMateria.codigo_resultado_oficial`;
- `InscripcionMateria.codigo_marca`;
- `InscripcionMateria.cerrado_en`.

Estos campos quedan reservados para actas y consolidacion oficial posterior.

### 8. Admin tecnico

Se registro `CapturaCalificacionPreliminar` en Django Admin para revision tecnica.

Los campos derivados como corte y fechas se mantienen como lectura cuando corresponde.

### 9. Correccion del alta de usuario desde popup

Se corrigio un error al crear usuarios desde el popup del admin, por ejemplo desde el formulario de `Discente`.

El problema era que `UsuarioAdmin` heredaba de Django 5.1 un campo `usable_password` que no existe en el formulario personalizado del proyecto.

Se definieron explicitamente los campos de alta:

- `username`;
- `password1`;
- `password2`;
- datos adicionales;
- rol.

### 10. Privacidad en vistas docentes

Se oculto la matricula del discente en vistas docentes porque se considera informacion militar sensible.

Se quito la matricula en:

- captura por corte;
- resultado por corte;
- resumen por discente;
- detalle de asignacion docente.

La matricula no fue eliminada del modelo ni del admin. Sigue disponible donde puede ser necesaria para trazabilidad administrativa.

### 11. Catalogo simple de grado/empleo

Se agrego el modelo `GradoEmpleo` en la app `usuarios`.

Campos:

- `clave`;
- `abreviatura`;
- `nombre`;
- `tipo`;
- `activo`.

Tipos:

- `MILITAR_ACTIVO`;
- `MILITAR_RETIRADO`;
- `CIVIL`;
- `OTRO`.

No se agrego `orden` en esta fase para mantener el alcance minimo solicitado.

### 12. Grado/empleo en Usuario

Se agrego `Usuario.grado_empleo` como FK opcional a `GradoEmpleo`.

La razon de ubicarlo en `Usuario` y no en `Discente` es que el grado/empleo puede aplicar a:

- discentes;
- docentes militares;
- docentes militares retirados;
- jefe academico;
- jefe pedagogico;
- jefes de carrera;
- encargados de subsecciones.

No se mezclo con roles ni cargos institucionales.

### 13. Visualizacion institucional en vistas docentes

En vistas docentes se muestran columnas separadas:

- `Grado y empleo`;
- `Nombre`.

Si el usuario tiene grado/empleo, se muestra la abreviatura.

Si no tiene grado/empleo, se muestra `-`.

La columna de nombre muestra solo el nombre visible del usuario.

## Por que se implemento asi

### Separar captura preliminar de actas

El sistema aun no debe consolidar resultados oficiales. Por eso la captura preliminar queda en un modelo separado y no escribe en campos oficiales de `InscripcionMateria`.

Esto permite probar reglas academicas sin comprometer el flujo formal de actas.

### Mantener precision interna

Si se redondea antes de tiempo, pueden cambiar decisiones como exencion o aprobacion. Por eso el calculo conserva precision interna y solo redondea al mostrar.

### Ocultar matricula solo en vistas docentes

La matricula puede seguir siendo necesaria para admin, estadistica o jefaturas. El cambio de privacidad aplica solo donde el profesor no necesita verla para capturar calificaciones.

### Grado/empleo en Usuario

Poner grado/empleo solo en `Discente` hubiera obligado a duplicar la solucion para docentes y jefaturas. Al colocarlo en `Usuario`, se evita repetir datos y se conserva coherencia institucional.

### No tocar permisos ni cargos

El grado/empleo no define acceso al sistema. Los permisos siguen dependiendo de roles/grupos y cargos institucionales.

## Migraciones creadas

- `backend/evaluacion/migrations/0005_capturacalificacionpreliminar.py`
- `backend/usuarios/migrations/0014_gradoempleo_usuario_grado_empleo.py`

Ambas migraciones ya fueron aplicadas localmente en Docker.

## Archivos principales modificados

- `backend/config/urls.py`
- `backend/evaluacion/models.py`
- `backend/evaluacion/forms.py`
- `backend/evaluacion/views.py`
- `backend/evaluacion/urls.py`
- `backend/evaluacion/services.py`
- `backend/evaluacion/admin.py`
- `backend/evaluacion/tests.py`
- `backend/evaluacion/templates/evaluacion/captura_calificaciones.html`
- `backend/evaluacion/templates/evaluacion/resumen_calculo.html`
- `backend/usuarios/models.py`
- `backend/usuarios/forms.py`
- `backend/usuarios/admin.py`
- `backend/usuarios/tests.py`
- `backend/usuarios/templates/usuarios/validacion/docente_asignaciones.html`
- `backend/usuarios/templates/usuarios/validacion/docente_asignacion_detalle.html`
- `README.md`

## Validaciones ejecutadas

Durante el bloque se ejecutaron validaciones parciales y completas.

Validaciones relevantes:

```bash
docker compose exec -T backend python manage.py makemigrations
docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test evaluacion
docker compose exec -T backend python manage.py test evaluacion usuarios
docker compose exec -T backend python manage.py test
```

Resultados antes del commit:

- `check`: OK.
- `makemigrations --check`: sin cambios pendientes.
- suite completa: OK.

## Pendientes recomendados

### Carga inicial de grados/empleos

El catalogo `GradoEmpleo` queda vacio inicialmente.

Debe cargarse por admin o mediante una estrategia posterior controlada.

Ejemplos:

- `CADETE`;
- `TTE_INF`;
- `TTE_PAS_ICI`;
- `CAP_2_INFRA`;
- `TTE_COR_ICI`;
- `MYR_RET_ICI`.

### Revision visual con datos reales

Conviene revisar en navegador:

- captura por corte;
- resultado por corte;
- resumen de calculo;
- detalle de asignacion docente.

### Fase posterior: actas oficiales

Este bloque no crea:

- actas;
- detalle de acta;
- validacion jerarquica;
- historial academico;
- kardex;
- reportes formales;
- exportaciones.

Eso debe implementarse en un bloque separado.

### Fase posterior: carga masiva o fixture de GradoEmpleo

Si la lista institucional de grados ya esta definida, conviene crear un comando o fixture idempotente para cargarla sin depender de captura manual.

### Fase posterior: revisar vistas no docentes

Las vistas de estadistica, admin y discente propio pueden seguir mostrando matricula segun necesidad operativa. Si se requiere una politica de privacidad mas estricta, debe analizarse aparte.

## Riesgos conocidos

- Si no se captura `grado_empleo`, el docente vera `-` en la columna de grado/empleo.
- El catalogo no tiene `orden` todavia; el ordenamiento queda por tipo y abreviatura.
- No hay historial de ascensos, por diseno MVP.
- El resultado calculado sigue siendo preliminar y no debe usarse como calificacion oficial.

## Estado final del bloque

El bloque queda listo para revision del equipo.

No se hizo commit ni push hasta despues de generar este documento.
