# Ubicacion excepcional de programas de asignatura

## Objetivo

Se incorporo una regla controlada para materias que no siguen la estructura normal de un solo semestre, como el caso de Desarrollo Humano u otras materias transversales que puedan cursarse en distintos semestres segun la antiguedad.

El cambio se hizo sin reemplazar el modelo actual. La regla general sigue siendo que un Programa de asignatura pertenece a un semestre especifico. La excepcion solo aplica cuando se activa explicitamente en el programa.

## Comportamiento normal

Para materias ordinarias, el sistema conserva la validacion existente:

- El Programa de asignatura tiene un `semestre_numero`.
- El `anio_formacion` se calcula automaticamente desde el semestre.
- La Asignacion docente solo puede guardar el programa si el semestre del programa coincide con el semestre del grupo.

Esto mantiene estable el flujo actual de catalogos, grupos academicos, asignaciones docentes e inscripciones generadas.

## Comportamiento excepcional

Se agrego el campo `ubicacion_excepcional` en Programa de asignatura.

Cuando esta desactivado, el sistema usa la regla normal por semestre.

Cuando esta activado, el programa puede tener ubicaciones excepcionales por:

- Programa de asignatura
- Antiguedad
- Semestre
- Estado activo

Esto permite representar casos como:

- Una antiguedad que cursa la materia una sola vez.
- Otra antiguedad que la cursa en tres semestres distintos.
- Otra antiguedad que la cursa en todos los semestres aplicables.

## Validaciones implementadas

- No se pueden registrar ubicaciones excepcionales si el programa no tiene activada la opcion `ubicacion_excepcional`.
- La antiguedad de una ubicacion debe pertenecer al mismo plan de estudios del programa.
- El semestre de la ubicacion debe estar entre 1 y 12.
- La asignacion docente valida contra ubicaciones excepcionales solo si el programa tiene activada la excepcion.
- Si no existe una ubicacion activa para la antiguedad y semestre del grupo, no se permite guardar la asignacion docente.
- Para programas normales, se conserva la validacion anterior de semestre directo.

## Archivos afectados

- `backend/catalogos/models.py`
- `backend/catalogos/admin.py`
- `backend/catalogos/forms.py`
- `backend/relaciones/models.py`
- `backend/catalogos/tests.py`
- `backend/relaciones/tests.py`
- `backend/catalogos/migrations/0017_programaasignatura_ubicacion_excepcional_and_more.py`

## Migracion

Se creo una migracion nueva, sin modificar migraciones anteriores:

`catalogos.0017_programaasignatura_ubicacion_excepcional_and_more`

La migracion agrega:

- Campo `ubicacion_excepcional` en Programa de asignatura.
- Modelo `ProgramaAsignaturaUbicacion`.

## Riesgos y pendientes

- La plantilla de carga masiva todavia debe ajustarse si se quieren cargar ubicaciones excepcionales desde Excel.
- La configuracion incorrecta de ubicaciones podria hacer que una materia aparezca o no aparezca para un grupo especifico; por eso la excepcion queda apagada por defecto.
- No se modificaron actas, calificaciones ni flujos oficiales.
- No se cambiaron nombres fisicos de tablas existentes.
