# Resumen plantilla VERSION7, roles y cargos institucionales 


El trabajo se hizo de forma conservadora:

- No se eliminaron datos existentes.
- No se elimino `JEFE_CARRERA`.
- No se tocaron permisos avanzados, vistas ni dashboards.
- No se cambio la estructura real de la base de datos.
- La plantilla se corrigio en una nueva version para no sobrescribir versiones previas.


La plantilla ya estaba intentando representar una estructura mas precisa que la que el backend reconocia originalmente.

En el backend existian cargos como:

- `JEFE_CARRERA`
- `JEFE_ACADEMICO`
- `JEFE_PEDAGOGICA`
- `JEFE_SUBSECCION_PEDAGOGICA`
- `DOCENTE`

Pero la plantilla necesitaba distinguir dos responsabilidades por carrera:

- Jefe de subseccion de Planeacion y Evaluacion.
- Jefe de subseccion de Ejecucion y Control.

Por eso aparecian codigos como:

- `JEFE_SUB_PLAN_EVAL`
- `JEFE_SUB_EJEC_CTR`

El problema era que esos codigos no existian aun en el backend, por lo que Django no los aceptaba como valores validos para `cargo_codigo` ni como roles/grupos base.

## Diferencia entre rol, cargo y unidad organizacional

Para evitar confusiones se separaron tres conceptos:

### Rol

El rol responde a la pregunta:

> Que puede hacer este usuario dentro de la plataforma?

Ejemplos:

- `DOCENTE`
- `DISCENTE`
- `ENCARGADO_ESTADISTICA`
- `JEFE_SUB_PLAN_EVAL`
- `JEFE_SUB_EJEC_CTR`

Los roles se implementan como grupos de Django y se usan para permisos.

### Cargo institucional

El cargo responde a la pregunta:

> Que puesto institucional ocupa esta persona

Ejemplos:

- `JEFE_ACADEMICO`
- `JEFE_PEDAGOGICA`
- `JEFE_SUB_PLAN_EVAL`
- `JEFE_SUB_EJEC_CTR`
- `DOCENTE`

El cargo puede tener vigencia, tipo de designacion y unidad organizacional asociada.

### Unidad organizacional

La unidad organizacional responde a la pregunta:

> En que parte de la estructura institucional ejerce ese cargo?

Ejemplos:

- `SEC_ACADEMICA`
- `SEC_PEDAGOGICA`
- `SUB_PLAN_EVAL_ICI`
- `SUB_EJEC_CTRL_ICI`

Esto permite representar la jerarquia:

- Seccion Academica -> Subseccion de Ejecucion y Control por carrera.
- Seccion Pedagogica -> Subseccion de Planeacion y Evaluacion por carrera.

## Que paso con JEFE_CARRERA

`JEFE_CARRERA` no se elimino.

Se conserva por compatibilidad porque ya estaba presente en el sistema, en pruebas y posiblemente en datos existentes. Eliminarlo de golpe podria romper registros previos, validaciones o flujos que ya funcionaban.

Antes, `JEFE_CARRERA` se estaba usando como una forma generica de representar al responsable por carrera en la parte academica.

Con el analisis institucional, ese caso queda mejor descrito como:

- `JEFE_SUB_EJEC_CTR`
- Jefe de subseccion de Ejecucion y Control.
- Depende de `SEC_ACADEMICA`.
- Aplica por carrera.

Entonces:

- `JEFE_CARRERA` queda como compatibilidad temporal.
- La plantilla nueva usa `JEFE_SUB_EJEC_CTR` para expresar mejor la estructura institucional.
- En una fase futura se puede decidir si `JEFE_CARRERA` se migra, se conserva como alias o se retira cuando ya no existan datos dependientes.

## Cambios realizados en backend

Se agregaron dos roles/cargos nuevos:

```text
JEFE_SUB_PLAN_EVAL
JEFE_SUB_EJEC_CTR
```

### JEFE_SUB_PLAN_EVAL

Representa:

- Jefe de subseccion de Planeacion y Evaluacion.
- Debe asignarse a una unidad tipo subseccion.
- La subseccion debe depender de `SEC_PEDAGOGICA`.
- La subseccion debe tener carrera asociada.
- El usuario debe tener rol compatible `JEFE_SUB_PLAN_EVAL`.

### JEFE_SUB_EJEC_CTR

Representa:

- Jefe de subseccion de Ejecucion y Control.
- Debe asignarse a una unidad tipo subseccion.
- La subseccion debe depender de `SEC_ACADEMICA`.
- La subseccion debe tener carrera asociada.
- El usuario debe tener rol compatible `JEFE_SUB_EJEC_CTR`.

### Compatibilidad

Se mantuvieron:

- `JEFE_CARRERA`
- `JEFATURA_CARRERA`
- `JEFE_SUBSECCION_PEDAGOGICA`
- `JEFE_PEDAGOGICA`
- `JEFE_ACADEMICO`
- `DOCENTE`

Esto evita romper comportamientos previos.

### Permisos

No se crearon permisos nuevos. Se reutilizaron perfiles existentes:

- `JEFE_SUB_EJEC_CTR` usa permisos similares a jefatura de carrera.
- `JEFE_SUB_PLAN_EVAL` usa permisos de consulta/jefatura academica por ahora.

Esto se hizo para no mezclar el cambio de estructura con un rediseño de permisos.

## Cambios realizados en la plantilla VERSION7

Cambios principales:

- Se corrigieron unidades organizacionales de subseccion.
- Se usaron cargos especificos:
  - `JEFE_SUB_PLAN_EVAL`
  - `JEFE_SUB_EJEC_CTR`
- Estadistica se dejo como rol/grupo, no como cargo institucional.
- Se agregaron grupos faltantes de `2025-2026-S2`.
- Se corrigieron discentes para que su `clave_plan` y `clave_antiguedad` coincidan con el grupo donde estan adscritos.
- Se corrigio `yosafat.moscoso2` por `yosafat.moscoso` en asignaciones docentes.

## Estadistica

Estadistica se manejo como rol, no como cargo institucional en esta fase.

Esto significa:

- El usuario puede tener rol `ENCARGADO_ESTADISTICA`.
- Puede recibir permisos de consulta/operacion definidos para estadistica.
- No se registra todavia como `AsignacionCargo`.

La razon es que aun falta decidir si Estadistica debe modelarse formalmente como cargo institucional con unidad, vigencia y tipo de designacion.

Pendiente futuro:

- Evaluar si `ENCARGADO_ESTADISTICA` debe agregarse tambien como cargo institucional.
- Definir si depende de una unidad organizacional especifica.
- Definir si requiere titular/accidental y vigencia como las jefaturas.

## Validaciones realizadas

### Backend

Se ejecutaron validaciones con Docker:

```text
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test usuarios
docker compose exec -T backend python manage.py test
```

Resultado:

```text
OK
```

Tambien se reviso la migracion `0015` con:

```text
python manage.py sqlmigrate usuarios 0015
```

Resultado:

```text
no-op
```

Esto significa que la migracion no modifica datos ni columnas; solo registra el cambio de opciones permitidas por Django.

### Plantilla

Se valido la plantilla VERSION7:
- Validacion interna contra backend actual:

```text
TOTAL_ISSUES=0
```

## Por que se hizo asi

Se eligio esta ruta porque es la mas segura para el prototipo:

- Permite que la plantilla cargue datos con terminologia institucional mas precisa.
- Evita romper datos existentes que aun usen `JEFE_CARRERA`.
- Evita mezclar este ajuste con cambios grandes de permisos.
- Mantiene separada la logica de roles, cargos y unidades.
- Deja claro que Estadistica funciona como rol por ahora.

En vez de reemplazar todo de golpe, se hizo una fase de compatibilidad.

## Pendientes

Quedan pendientes para fases futuras:

- Decidir que hacer definitivamente con `JEFE_CARRERA`.
- Evaluar si se migran datos antiguos de `JEFE_CARRERA` hacia `JEFE_SUB_EJEC_CTR`.
- Definir si `JEFE_SUBSECCION_PEDAGOGICA` se conserva o se reemplaza por `JEFE_SUB_PLAN_EVAL`.
- Definir si `ENCARGADO_ESTADISTICA` debe existir tambien como cargo institucional.
- Revisar permisos especificos por subseccion cuando el prototipo avance.
- Revisar dashboards y filtros por unidad organizacional/carrera.
- Crear proceso formal de importacion de la plantilla si aun no existe.

## Resumen corto

La plantilla VERSION7 queda lista para pruebas de carga con el backend actualizado.

El backend ahora reconoce los nuevos cargos y roles institucionales por subseccion. `JEFE_CARRERA` se conserva para compatibilidad, pero la nueva plantilla usa `JEFE_SUB_EJEC_CTR` para representar mejor al responsable academico por carrera dentro de la Seccion Academica.

Estadistica queda como rol por ahora, no como cargo institucional.
