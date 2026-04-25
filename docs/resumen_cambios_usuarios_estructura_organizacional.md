# Resumen técnico: usuarios, estructura organizacional y cargos institucionales

## 1. Objetivo general del cambio

Este bloque incorporó una estructura organizacional formal al módulo de usuarios para separar con mayor claridad tres conceptos que antes podían mezclarse:

- Rol o grupo de Django: define qué puede hacer un usuario dentro de la plataforma.
- Cargo institucional: define qué puesto ocupa el usuario dentro de la institución.
- Unidad organizacional: define en qué parte de la estructura institucional se ejerce ese cargo.

El objetivo principal fue representar la estructura sección -> subsección sin romper compatibilidad con los datos existentes ni modificar todavía permisos, vistas o dashboards.

## 2. Cambios realizados

### Modelo organizacional

- Se creó el modelo `UnidadOrganizacional`.
- Se definieron dos tipos de unidad:
  - `SECCION`
  - `SUBSECCION`
- Se agregó relación jerárquica mediante `padre`, permitiendo representar sección -> subsección.
- Se agregó `carrera` opcional en `UnidadOrganizacional`, aplicable solo cuando la unidad sea una subsección por carrera.
- Se agregaron claves institucionales controladas:
  - `SEC_PEDAGOGICA`
  - `SEC_ACADEMICA`

### Asignación de cargos

- Se agregó el campo `unidad_organizacional` opcional en `AsignacionCargo`.
- Se conservó temporalmente el campo `carrera` en `AsignacionCargo` por compatibilidad.
- Se agregó el cargo `JEFE_SUBSECCION_PEDAGOGICA`.
- Se ajustó `JEFE_PEDAGOGICA` para que ya no sea tratado como cargo por carrera.
- Se mantuvo `JEFE_CARRERA` como cargo por carrera dentro de la Sección Académica.

### Administración Django

- Se registró `UnidadOrganizacional` en el admin.
- Se cambió la etiqueta visible de `padre` de `Unidad padre` a `Depende de (Sección)`.
- En `AsignacionCargoAdmin`, el dropdown de `unidad_organizacional` muestra jerarquía:
  - `Sección Académica`
  - `Sección Pedagógica`
  - `Sección Académica -> Subsección de Ejecución y Control ICI`
  - `Sección Pedagógica -> Subsección de Planeación y Evaluación ICI`
- Se agregó un ajuste visual para ocultar el campo `Carrera` cuando el cargo seleccionado no debe usar carrera.

### Comando de carga base

- Se creó el management command:

```bash
python manage.py seed_unidades_organizacionales
```

- El comando crea de forma idempotente:
  - `SEC_PEDAGOGICA`
  - `SEC_ACADEMICA`
  - `SUB_PLAN_EVAL_<CLAVE_CARRERA>` para carreras activas.
  - `SUB_EJEC_CTRL_<CLAVE_CARRERA>` para carreras activas.
- No duplica unidades existentes.
- No elimina unidades existentes.
- Reporta advertencias si encuentra unidades con la clave esperada pero datos incompatibles.

### Validaciones

- Se agregaron validaciones de estructura sección/subsección.
- Se agregaron validaciones de compatibilidad cargo/unidad.
- Se agregaron validaciones de titular y accidental.
- Se agregó validación mínima de compatibilidad entre rol/grupo y cargo institucional.
- Se agregaron y ajustaron tests en `usuarios`.
- Se ajustó un test de `relaciones` que creaba una asignación de cargo inválida bajo las nuevas reglas.

## 3. Razón de los cambios

### Separar rol, cargo y unidad organizacional

Antes, el sistema podía confundir el rol de acceso con el cargo institucional. Esto podía permitir datos incoherentes, por ejemplo, un usuario con rol `DISCENTE` recibiendo un cargo de jefatura.

La separación permite que:

- El rol siga controlando permisos de plataforma.
- El cargo represente el puesto institucional.
- La unidad organizacional represente dónde se ejerce ese cargo.

### Por qué no se eliminó `carrera`

El campo `carrera` en `AsignacionCargo` se conservó por compatibilidad. Aunque la carrera puede derivarse de algunas unidades organizacionales, eliminarla ahora implicaría una migración de datos más delicada.

Por ahora:

- `carrera` sigue existiendo.
- `unidad_organizacional` es opcional.
- Si ambos datos existen y la unidad tiene carrera, deben coincidir.

### Por qué se implementó por fases

El cambio afecta conceptos centrales del módulo de usuarios. Implementarlo por fases permitió:

- Crear primero la estructura sin migrar datos existentes.
- Validar reglas de unidad organizacional antes de conectarlas con cargos.
- Ajustar la interfaz administrativa sin tocar permisos.
- Evitar cambios destructivos.

### Por qué no se tocaron permisos, vistas ni dashboards

Los permisos, vistas y dashboards dependen de decisiones funcionales adicionales sobre alcance por carrera o unidad. Se dejaron intactos para no mezclar este bloque estructural con reglas de acceso o filtrado de información.

## 4. Reglas de negocio implementadas

### `JEFE_PEDAGOGICA`

- Es cargo único de la Sección Pedagógica.
- Debe asignarse a una unidad tipo `SECCION`.
- La unidad debe tener clave `SEC_PEDAGOGICA`.
- No debe tener carrera asignada.
- Requiere grupo compatible `JEFE_PEDAGOGICA`.

### `JEFE_ACADEMICO`

- Es cargo único de la Sección Académica.
- Debe asignarse a una unidad tipo `SECCION`.
- La unidad debe tener clave `SEC_ACADEMICA`.
- No debe tener carrera asignada.
- Acepta grupo `JEFE_ACADEMICO` o `JEFATURA_ACADEMICA`.

### `JEFE_CARRERA`

- Representa al responsable por carrera dentro de la Sección Académica.
- Debe asignarse a una unidad tipo `SUBSECCION`.
- La subsección debe depender de `SEC_ACADEMICA`.
- La unidad debe tener carrera asociada.
- Si también se captura `carrera` en `AsignacionCargo`, debe coincidir con la carrera de la unidad.
- Acepta grupo `JEFE_CARRERA` o `JEFATURA_CARRERA`.

### `JEFE_SUBSECCION_PEDAGOGICA`

- Representa al responsable de una subsección de la Sección Pedagógica por carrera.
- Debe asignarse a una unidad tipo `SUBSECCION`.
- La subsección debe depender de `SEC_PEDAGOGICA`.
- La unidad debe tener carrera asociada.
- Temporalmente acepta grupo `JEFE_PEDAGOGICA`, hasta que exista un rol propio.

### `DOCENTE`

- Requiere grupo `DOCENTE`.
- No debe tener carrera asignada directamente en `AsignacionCargo`.

### Designación titular

- No puede existir más de una jefatura titular activa para el mismo cargo y la misma unidad organizacional con vigencia traslapada.

### Designación accidental

- Puede coexistir con un titular activo.
- Debe tener `vigente_hasta`.
- No puede traslaparse con otra designación accidental equivalente para el mismo cargo y unidad.

### Compatibilidad con grupos/roles

- Un usuario con grupo `DISCENTE` no puede recibir cargos institucionales.
- Cada cargo valida que el usuario pertenezca a un grupo compatible.
- Esta regla evita datos incoherentes, pero no implementa permisos nuevos ni lógica de acceso.

## 5. Compatibilidad y migración

- No se eliminaron datos existentes.
- No se eliminó el campo `carrera` en `AsignacionCargo`.
- `unidad_organizacional` se agregó como campo opcional para conservar compatibilidad.
- No se migraron datos desde `AsignacionCargo.carrera` hacia `unidad_organizacional`.
- No se modificaron permisos.
- No se modificaron vistas.
- No se modificaron dashboards.
- Se agregaron migraciones no destructivas para crear la estructura y actualizar choices/labels necesarios.

## 6. Validaciones ejecutadas

Se ejecutaron las siguientes validaciones:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test usuarios
docker compose exec -T backend python manage.py test
```

Resultado:

- `manage.py check`: OK.
- `makemigrations --check`: OK, sin migraciones pendientes.
- `test usuarios`: OK.
- `test` completo: OK.

## 7. Riesgos o pendientes

- Migrar datos desde `AsignacionCargo.carrera` hacia `unidad_organizacional` cuando la estructura esté validada institucionalmente.
- Filtrar permisos, vistas o dashboards por unidad organizacional o carrera, si el negocio lo requiere.
- Mejorar la UX dinámica del admin para filtrar `unidad_organizacional` según el cargo seleccionado.
- Crear un rol específico para `JEFE_SUBSECCION_PEDAGOGICA`.
- Revisar datos locales o legacy incompatibles, por ejemplo usuarios con cargo institucional pero sin grupo compatible.
- Revisar si el campo `carrera` debe ocultarse o derivarse automáticamente en más escenarios del admin.

