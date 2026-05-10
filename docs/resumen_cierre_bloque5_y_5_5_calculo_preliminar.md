# Resumen de cierre: Bloque 5 y Bloque 5.5

## Objetivo general

El Bloque 5 se implemento para permitir la captura basica de calificaciones y validar el calculo academico preliminar antes de construir el flujo formal de actas.

La idea principal fue separar claramente dos conceptos:

- Captura preliminar: sirve para que el docente registre calificaciones por componente y para que el sistema calcule resultados preliminares.
- Acta oficial: queda pendiente para un bloque posterior y sera el flujo que consolide, cierre y oficialice calificaciones.

Esto permite probar las reglas academicas sin comprometer todavia historial, kardex, actas, firmas, validaciones oficiales o reportes formales.

## Alcance original del Bloque 5

El alcance original contemplaba:

- Crear una estructura para almacenar capturas preliminares de calificacion.
- Capturar calificaciones por inscripcion a asignatura y componente de evaluacion.
- Calcular resultado por corte.
- Calcular promedio de parciales.
- Determinar si aplica exencion.
- Calcular evaluacion final.
- Calcular resultado final preliminar.
- Redondear la visualizacion a un decimal.
- Restringir la escala valida de 0.0 a 10.0.
- Crear vistas temporales para docentes.
- Evitar que se actualicen campos oficiales de `InscripcionMateria`.
- Agregar pruebas minimas del calculo y permisos.
- Documentar el bloque en el README tecnico.

## Implementacion original realizada

### Captura preliminar de calificaciones

Se creo el modelo `CapturaCalificacionPreliminar` en la app `evaluacion`.

Este modelo guarda:

- `inscripcion_materia`
- `componente`
- `corte_codigo`
- `valor`
- `capturado_por`
- fechas de creacion y actualizacion

La captura se definio como preliminar. No representa acta, no cierra calificaciones y no escribe automaticamente resultados oficiales.

### Servicio de calculo academico

Se agrego `ServicioCalculoAcademico` para centralizar la logica de calculo.

El servicio calcula:

- resultado por corte
- promedio de parciales
- exencion preliminar
- evaluacion final
- resultado final preliminar
- estado preliminar: `APROBATORIO`, `REPROBATORIO` o `INCOMPLETO`

La formula base usada es:

```text
resultado final preliminar =
promedio de parciales * peso_parciales +
evaluacion final * peso_final
```

Los pesos se toman desde `EsquemaEvaluacion`, por lo que no quedan fijos en codigo. Por omision se mantiene el comportamiento esperado 45/55, pero el sistema respeta esquemas con otros pesos.

### Vistas docentes temporales

Se agregaron pantallas simples con Django templates:

- Mis asignaciones del docente.
- Captura preliminar por asignacion docente y corte.
- Resumen de calculo por asignacion docente.

Estas vistas permiten que el docente capture y revise resultados, pero sin generar actas oficiales.

### Permisos de captura

La captura se restringio en backend:

- El docente solo puede capturar asignaciones propias.
- El administrador puede acceder por soporte tecnico.
- Otros perfiles no capturan en nombre del docente.
- Discente no puede capturar ni modificar.

Esto se valido en backend y no solo ocultando botones.

### Campos oficiales protegidos

El Bloque 5 no actualiza:

- `InscripcionMateria.calificacion_final`
- `InscripcionMateria.codigo_resultado_oficial`
- `InscripcionMateria.codigo_marca`
- `InscripcionMateria.cerrado_en`

Estos campos quedan reservados para el flujo formal de actas.

## Ajustes posteriores del Bloque 5.5

Despues de probar el flujo, se hicieron ajustes necesarios para dejar el bloque consistente antes de avanzar.

### Precision interna del calculo

Se ajusto el calculo para conservar precision interna con `Decimal`.

Regla final:

- No se truncan valores.
- No se redondean resultados intermedios.
- El resultado interno conserva precision.
- Solo la visualizacion se redondea a un decimal.

Esto evita errores academicos por redondear antes de tiempo.

Ejemplos de visualizacion:

- `8.9999` se muestra como `9.0`.
- `8.94` se muestra como `8.9`.
- `8.95` se muestra como `9.0`.

### Visualizacion a un decimal

Se ajustaron las pantallas para que todas las calificaciones visibles al docente se muestren con un decimal.

Esto aplica a:

- resultado por corte
- promedio de parciales
- evaluacion final
- resultado final preliminar

El objetivo fue evitar que el usuario vea mezclas como `8.125`, `8.030` y `8.1` en la misma tabla.

### Terminologia de evaluacion final

Para evitar confusion entre el corte `FINAL` y el resultado final del curso, se ajusto la terminologia visible:

- `Final` se muestra como `Evaluacion final`.
- `Calificacion final preliminar` se muestra como `Resultado final preliminar`.

La razon fue distinguir:

- Evaluacion final: corte o etapa donde puede existir examen final u otros componentes.
- Resultado final preliminar: calculo global preliminar del alumno en la asignatura.

### Exencion basada en el esquema

Se corrigio la regla de exencion para que use el valor configurado en `EsquemaEvaluacion.umbral_exencion`.

Antes, la logica podia quedar demasiado fija alrededor de un umbral institucional en codigo.

Ahora:

- El esquema define el umbral.
- Si no hubiera valor, se conserva fallback institucional de `9.0`.
- El default del modelo queda alineado a `9.00`.

Esto permite que el umbral sea configurable por esquema y mantiene coherencia con la escala de calificacion de 0 a 10.

### Migracion del umbral de exencion

Se creo una migracion nueva, sin modificar migraciones antiguas:

- `backend/evaluacion/migrations/0006_alter_esquemaevaluacion_umbral_exencion.py`

Esta migracion ajusta el default de `umbral_exencion` a `9.00`.

No es destructiva y no elimina datos.

### Limpieza de capturas al dejar campos vacios

Se corrigio el comportamiento de la captura cuando un docente deja vacio un campo que antes tenia calificacion.

Antes podia quedar una captura previa guardada, aunque visualmente el profesor hubiera borrado el dato.

Ahora:

- Si el campo queda vacio y ya existia captura, la captura preliminar se elimina.
- Si el campo tiene valor valido, se crea o actualiza.
- Esto aplica solo a capturas preliminares.
- No afecta campos oficiales.

Esto es importante para que el formulario represente realmente lo que el docente ve y guarda.

### Exencion en evaluacion final

Se hizo mas claro el caso en que un discente queda exento.

Cuando aplica exencion:

- El componente marcado como examen en `Evaluacion final` puede quedar vacio.
- El calculo preliminar sustituye ese examen por el promedio de parciales.
- La interfaz muestra que la exencion aplica.

Esto evita que el usuario piense que el formulario esta incompleto cuando el alumno realmente exento no debe capturar examen final.

## Privacidad y Bloque 5.5

Durante el cierre del bloque tambien se reviso la privacidad de datos visibles al docente.

### Matricula oculta en vistas docentes

Se oculto la matricula del discente en pantallas docentes porque puede ser informacion institucional sensible.

La matricula se quito de:

- captura por corte
- resultado por corte
- resumen por discente
- detalle de asignacion docente

No se elimino del modelo ni del admin.

### Grado y empleo institucional

Se agrego un catalogo simple `GradoEmpleo` asociado a `Usuario`.

Se decidio ponerlo en `Usuario` y no solo en `Discente` porque tambien puede aplicar a:

- docentes militares
- docentes retirados
- jefaturas
- encargados de subseccion
- discentes

Se mantuvo como campo opcional para no afectar usuarios civiles o registros incompletos.

En vistas docentes se muestra:

- `Grado y empleo`
- `Nombre`

Si el usuario no tiene grado/empleo, se muestra `-` o solamente el nombre, segun la tabla.

## Archivos principales involucrados

### Evaluacion

- `backend/evaluacion/models.py`
- `backend/evaluacion/forms.py`
- `backend/evaluacion/services.py`
- `backend/evaluacion/views.py`
- `backend/evaluacion/urls.py`
- `backend/evaluacion/admin.py`
- `backend/evaluacion/tests.py`
- `backend/evaluacion/templates/evaluacion/captura_calificaciones.html`
- `backend/evaluacion/templates/evaluacion/resumen_calculo.html`
- `backend/evaluacion/migrations/0005_capturacalificacionpreliminar.py`
- `backend/evaluacion/migrations/0006_alter_esquemaevaluacion_umbral_exencion.py`

### Usuarios y vistas docentes

- `backend/usuarios/models.py`
- `backend/usuarios/admin.py`
- `backend/usuarios/forms.py`
- `backend/usuarios/tests.py`
- `backend/usuarios/templates/usuarios/validacion/docente_asignaciones.html`
- `backend/usuarios/templates/usuarios/validacion/docente_asignacion_detalle.html`
- `backend/usuarios/migrations/0014_gradoempleo_usuario_grado_empleo.py`

### Documentacion

- `README.md`
- `docs/resumen_bloque5_calificaciones_y_grado_empleo.md`
- `docs/resumen_cierre_bloque5_y_5_5_calculo_preliminar.md`

## Pruebas y validaciones realizadas

Se validaron los puntos principales del bloque:

- rechazo de calificaciones menores a 0
- rechazo de calificaciones mayores a 10
- guardado de calificaciones validas
- calculo ponderado por corte
- calculo de promedio de parciales
- exencion no permitida en materia de un parcial
- exencion permitida en materias de 2 o 3 parciales cuando cumple umbral
- uso de pesos configurados en el esquema
- restriccion para que un docente no capture asignaciones ajenas
- proteccion de campos oficiales de `InscripcionMateria`
- limpieza de capturas preliminares al dejar campos vacios
- visualizacion de exencion en evaluacion final
- visualizacion a un decimal

Comandos usados durante la validacion:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py showmigrations evaluacion
docker compose exec -T backend python manage.py test evaluacion usuarios
docker compose exec -T backend python manage.py test
```

Resultado de cierre:

- `manage.py check`: OK.
- `makemigrations --check`: OK.
- migracion `evaluacion.0006`: aplicada.
- `test evaluacion usuarios`: OK.
- suite completa: OK.

## Hallazgos de datos locales

Durante la revision se encontraron datos de prueba con inconsistencias operativas, por ejemplo asignaciones sin inscripciones o sin esquema activo.

Estos hallazgos no se corrigieron como cambio de backend porque corresponden a datos locales/de prueba.

El sistema debe bloquear o mostrar error claro cuando falten prerequisitos, pero no conviene que el backend invente inscripciones, esquemas o resultados oficiales automaticamente.

## Por que ya es posible pasar al siguiente bloque

Ya es posible avanzar porque el Bloque 5 cumple su objetivo: validar captura y calculo preliminar sin tocar actas oficiales.

El sistema ya tiene:

- modelo de captura preliminar separado
- servicio de calculo academico centralizado
- validacion de escala 0.0 a 10.0
- calculo por corte
- promedio de parciales
- evaluacion final
- exencion preliminar
- resultado final preliminar
- permisos basicos de captura docente
- privacidad en vistas docentes
- pruebas automatizadas de los escenarios principales

Lo mas importante es que no se escriben resultados oficiales en `InscripcionMateria`, por lo que el siguiente bloque puede construir actas encima de este calculo sin arrastrar cierres prematuros.

## Pendientes que no se realizaron y por que

### Actas oficiales

No se implementaron porque estaban fuera del alcance del Bloque 5.

Pendiente para el siguiente bloque:

- `Acta`
- detalle de acta
- cierre de acta
- validacion/firma
- consolidacion oficial

### Kardex e historial academico

No se implementaron porque dependen de actas cerradas y resultados oficiales.

Implementarlos antes de actas provocaria duplicidad o riesgo de inconsistencias.

### Reportes formales y exportaciones

No se implementaron PDF, Excel ni reportes oficiales.

Primero debe quedar definido el modelo formal de acta y el estado de cierre.

### Flujo de conformidad del discente

No se implemento porque pertenece al flujo formal posterior.

La captura preliminar no debe exigir conformidad del discente.

### Extraordinarios

No se implementaron porque requieren reglas posteriores sobre reprobacion, oportunidades, actas especiales y calendario.

### Estadistica como unidad organizacional

Estadistica ya existe como rol/grupo operativo para consulta y consolidacion.

No se agrego aun como subseccion de `UnidadOrganizacional` porque no participa como firmante o validador formal de actas. Puede agregarse despues como:

- `Subseccion de Estadistica`
- dependiente de `Seccion Pedagogica`
- sin carrera
- con rol operativo `ESTADISTICA` o `ENCARGADO_ESTADISTICA`

Esto conviene dejarlo separado del Bloque 5 para no mezclar calculo academico con estructura organizacional.

### Datos locales incompletos

No se corrigieron automaticamente porque son datos de prueba.

El siguiente bloque debe validar prerequisitos antes de generar actas:

- asignacion activa
- esquema activo
- componentes validos
- discentes inscritos
- capturas completas o exencion valida

## Recomendacion para el siguiente bloque

El Bloque 6 deberia enfocarse en el flujo formal de actas.

Recomendacion tecnica:

- Crear actas separadas de capturas preliminares.
- Congelar o guardar snapshot del esquema usado.
- Congelar pesos, componentes, umbral y resultados al cerrar el acta.
- No depender de que el esquema vivo siga igual despues del cierre.
- Actualizar campos oficiales de `InscripcionMateria` solo cuando el acta se cierre/consolide.
- Bloquear generacion de acta si faltan capturas requeridas o prerequisitos academicos.

Con esto el Bloque 5 queda como base de calculo y el Bloque 6 puede encargarse de oficializar.
