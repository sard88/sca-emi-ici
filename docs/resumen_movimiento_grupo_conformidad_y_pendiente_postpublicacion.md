# Resumen de ajustes: movimiento académico, conformidad y pendiente post-publicación

## Estado del trabajo

Este documento resume los ajustes realizados recientemente sobre:

- Movimiento académico de cambio de grupo.
- Sincronización de adscripciones e inscripciones a asignatura.
- Comentario obligatorio cuando un discente firma con inconformidad.
- Estado actual del flujo de actas frente a correcciones post-publicación.

Importante: al momento de generar este documento, estos cambios no tienen commit ni push. Están únicamente implementados y validados en la copia local de trabajo.

## 1. Problema detectado en cambio de grupo

Se detectó que el módulo de Movimiento Académico permitía registrar un movimiento de tipo Cambio de grupo con:

- Discente.
- Periodo.
- Grupo origen.
- Grupo destino.
- Fecha del movimiento.
- Observaciones.

Sin embargo, el movimiento solo quedaba como evidencia histórica. No aplicaba realmente el cambio operativo sobre la adscripción activa del discente.

Ejemplo observado:

- Discente: Christiany Montsserratt Clemente Dominguez.
- Movimiento registrado: ICI_A -> ICI-101.
- Fecha: 2026-05-11.
- Resultado antes del ajuste: el movimiento existía, pero la adscripción activa seguía en ICI_A.

Esto generaba una inconsistencia: el sistema decía que existía un movimiento académico, pero la relación activa del discente seguía apuntando al grupo anterior.

## 2. Ajuste realizado en MovimientoAcademico

Se ajustó el comportamiento del modelo `MovimientoAcademico` para que, cuando se cree un movimiento de tipo Cambio de grupo, el sistema haga dos cosas al mismo tiempo:

- Conservar la evidencia del movimiento.
- Aplicar realmente el cambio operativo.

El ajuste se hizo de forma transaccional. Esto significa que si una parte falla, no se guarda un movimiento incompleto o falso.

Ahora el flujo hace lo siguiente:

1. Valida que el movimiento tenga grupo origen y grupo destino.
2. Valida que origen y destino sean grupos distintos.
3. Valida que ambos grupos pertenezcan al periodo seleccionado.
4. Valida que ambos grupos correspondan a la antigüedad del discente.
5. Verifica que el grupo origen sea la adscripción activa del discente en ese periodo.
6. Cierra la adscripción activa del grupo origen.
7. Crea o conserva la adscripción activa del grupo destino.
8. Da de baja las inscripciones activas del grupo origen.
9. Crea inscripciones nuevas para el grupo destino si ya existen asignaciones docentes activas en ese grupo.

## 3. Conservación de evidencia

El movimiento académico sigue conservando:

- Grupo origen.
- Grupo destino.
- Fecha de movimiento.
- Observaciones.

La adscripción anterior no se borra. Queda como histórico:

- `activo = False`.
- `vigente_hasta = fecha_movimiento`.

La nueva adscripción queda como activa:

- `activo = True`.
- `vigente_desde = fecha_movimiento`.

Esto permite saber de dónde venía el discente, hacia dónde fue movido y en qué fecha ocurrió el cambio.

## 4. Inscripciones a asignatura

Además de mover la adscripción de grupo, se ajustó el impacto sobre `InscripcionMateria`.

Antes del ajuste, un discente podía quedar adscrito al nuevo grupo, pero conservar inscripciones activas en asignaciones docentes del grupo anterior. Eso podía provocar incongruencias en captura de calificaciones, actas y consultas académicas.

Ahora, al aplicar un cambio de grupo:

- Las inscripciones activas del grupo origen pasan a estado `baja`.
- No se eliminan inscripciones anteriores.
- No se borra evidencia.
- Se crean nuevas inscripciones para el grupo destino únicamente si el grupo destino ya tiene asignaciones docentes activas.

Si el grupo destino no tiene asignaciones docentes activas, no se crean inscripciones nuevas en ese momento.

Ejemplo real validado:

- Christiany quedó con adscripción activa en ICI-101.
- Su inscripción anterior de ICI_A / PROG1 quedó en estado `baja`.
- No se creó una inscripción nueva en ICI-101 porque ese grupo no tenía asignaciones docentes activas.

## 5. Protección frente a actas existentes

Se agregó una protección importante para no afectar evidencia formal.

Si las inscripciones del grupo origen ya están vinculadas a actas no archivadas, el cambio de grupo se bloquea.

Esto evita que el sistema:

- Dé de baja una inscripción que ya forma parte de un acta viva.
- Rompa la trazabilidad de una captura o acta.
- Deje un acta apuntando a una inscripción que fue movida automáticamente.

Estados considerados como actas vivas:

- BORRADOR_DOCENTE.
- PUBLICADO_DISCENTE.
- REMITIDO_JEFATURA_CARRERA.
- VALIDADO_JEFATURA_CARRERA.
- FORMALIZADO_JEFATURA_ACADEMICA.

El estado ARCHIVADO queda fuera de esta restricción porque representa una etapa posterior de cierre/consulta histórica.

## 6. Comentario obligatorio para inconformidad

También se ajustó la conformidad del discente.

Antes del ajuste, un discente podía registrar `INCONFORME` sin comentario.

Ahora, si el discente selecciona `INCONFORME`, el comentario es obligatorio.

Esta regla se implementó en tres capas:

- Formulario: el usuario ve el error en pantalla.
- Servicio/backend: no se puede omitir el comentario por llamada directa.
- Modelo: protege la creación desde ORM/admin u otros flujos internos.

La regla actual queda así:

- ACUSE: comentario opcional.
- CONFORME: comentario opcional.
- INCONFORME: comentario obligatorio.

## 7. Flujo actual de conformidad del discente

El discente puede registrar conformidad únicamente cuando el acta está en estado `PUBLICADO_DISCENTE`.

Mientras el acta está publicada a discentes:

- El discente puede registrar acuse.
- El discente puede registrar conformidad.
- El discente puede registrar inconformidad con comentario obligatorio.
- Si vuelve a registrar una conformidad, la anterior se invalida y queda una nueva como vigente.

Después de que el acta se remite a jefatura de carrera:

- La conformidad queda en solo lectura.
- El discente ya no puede modificar su firma, acuse, conformidad, inconformidad ni comentario.

## 8. Flujo actual de actas frente a correcciones

Hasta este punto, el sistema no tiene un flujo formal de corrección post-publicación.

El flujo implementado actualmente es:

1. El docente captura calificaciones preliminares.
2. El docente genera borrador de acta.
3. El docente puede regenerar el acta mientras esté en `BORRADOR_DOCENTE`.
4. El docente publica el acta a discentes.
5. El discente consulta y registra conformidad, acuse o inconformidad.
6. El docente remite el acta a jefatura de carrera.
7. Jefatura de carrera valida.
8. Jefatura académica formaliza.
9. Estadística consulta.

Mientras el acta está en `BORRADOR_DOCENTE`, el docente puede corregir capturas preliminares y regenerar el acta.

Después de publicar el acta:

- Ya no se permite regenerar el acta.
- Ya no se permite modificar captura preliminar asociada a esa acta/corte/asignación.
- El docente ya no puede cambiar calificaciones por ese flujo.

Después de remitir:

- El acta queda en solo lectura para docente y discente.
- La jefatura de carrera valida, pero no modifica calificaciones.
- La jefatura académica formaliza, pero no modifica calificaciones.

## 9. Qué no existe todavía

No existe todavía un flujo formal para:

- Devolver un acta publicada al docente para corrección.
- Reabrir un acta publicada.
- Rechazar un acta remitida con observaciones.
- Rectificar una calificación después de validación.
- Rectificar una calificación después de formalización.
- Sustituir una conformidad ya bloqueada después de remisión.
- Crear una bitácora específica de corrección post-publicación.

Esto significa que, actualmente, las jefaturas no modifican calificaciones. Su participación es de consulta, validación o formalización según el estado del acta.

## 10. Lo que falta definir para correcciones post-publicación

Para implementar correcciones post-publicación en un bloque posterior, todavía falta definir institucionalmente:

- Quién puede solicitar la corrección.
- Quién puede autorizarla.
- En qué estados se permite corregir.
- Si la corrección devuelve el acta a borrador o crea una versión/rectificación.
- Qué pasa con conformidades ya registradas.
- Si se invalidan firmas anteriores.
- Qué evidencia debe conservarse.
- Qué bitácora debe quedar.
- Si cambia el acta original o se genera un documento de rectificación.

## 11. Archivos modificados por este bloque de ajustes

Archivos funcionales:

- `backend/relaciones/models.py`
- `backend/evaluacion/forms.py`
- `backend/evaluacion/models.py`
- `backend/evaluacion/services.py`

Archivos de pruebas:

- `backend/relaciones/tests.py`
- `backend/evaluacion/tests.py`

Documento generado:

- `docs/resumen_movimiento_grupo_conformidad_y_pendiente_postpublicacion.md`

## 12. Pruebas ejecutadas

Se ejecutaron las siguientes validaciones:

- `docker compose exec -T backend python manage.py check`
- `docker compose exec -T backend python manage.py makemigrations --check`
- `docker compose exec -T backend python manage.py test relaciones`
- `docker compose exec -T backend python manage.py test evaluacion`
- `docker compose exec -T backend python manage.py test`

Resultados:

- Check de Django: OK.
- Revisión de migraciones: OK, sin migraciones nuevas.
- Pruebas de relaciones: OK.
- Pruebas de evaluación: OK.
- Suite completa: OK.

La última suite completa ejecutada reportó 248 pruebas correctas.

## 13. Nota final

Estos cambios están implementados y validados localmente, pero no se ha realizado commit ni push.

Antes de avanzar con otro bloque grande, conviene cerrar estos cambios en Git cuando el equipo confirme que el comportamiento descrito es el esperado.
