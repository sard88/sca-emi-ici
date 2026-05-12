# Resumen técnico de cierre - Bloque 6: Gestión formal de actas

## 1. Resultado general del bloque

**Resultado: APROBADO CON OBSERVACIONES**

El Bloque 6, correspondiente a la gestión formal de actas, quedó suficientemente estable para avanzar al siguiente bloque. No se detectaron bloqueantes técnicos en el flujo principal y las pruebas completas pasaron correctamente.

Se puede continuar con el siguiente bloque siempre que el equipo acepte las observaciones no bloqueantes documentadas, principalmente la decisión pendiente sobre si el comentario de inconformidad del discente debe ser obligatorio u opcional.

## 2. Contexto previo

Antes del Bloque 6, el sistema ya contaba con captura preliminar de calificaciones y con el servicio `ServicioCalculoAcademico`.

La captura preliminar permitía registrar calificaciones por componente, calcular resultados por corte, promedio de parciales, evaluación final, exención preliminar y resultado final preliminar. Sin embargo, esa captura no tenía carácter oficial.

Los campos oficiales de `InscripcionMateria`, como `calificacion_final`, `codigo_resultado_oficial`, `codigo_marca` y `cerrado_en`, no se actualizaban todavía desde la captura preliminar.

Antes de este bloque no existía el flujo formal completo de actas con estados, publicación, conformidad, remisión, validación y formalización.

## 3. Qué se mantuvo original

Se conservó la separación entre captura preliminar y acta oficial.

- `CapturaCalificacionPreliminar` sigue siendo preliminar y no representa un resultado oficial.
- `ServicioCalculoAcademico` sigue siendo la base para calcular resultados académicos.
- No se convirtió la captura preliminar en acta oficial.
- No se implementó historial académico.
- No se implementó kárdex.
- No se implementaron extraordinarios.
- No se implementaron reportes PDF/Excel.
- No se implementó consolidación final estadística.
- No se actualizan campos oficiales antes de formalizar el acta final.
- No se tocó el flujo de matrícula ni reportes formales.

## 4. Qué se agregó

Se agregaron modelos formales para la gestión de actas:

- `Acta`.
- `DetalleActa`.
- `CalificacionComponente`.
- `ConformidadDiscente`.
- `ValidacionActa`.

También se agregó:

- Servicio formal de actas para generar, publicar, remitir, validar y formalizar.
- Vistas y rutas para docente, discente, jefatura de carrera, jefatura académica y Estadística.
- Templates para el flujo de actas.
- Administración técnica en Django Admin para revisión de actas, detalles, componentes, conformidades y validaciones.
- Actualización del README técnico con la sección del Bloque 6.
- Vista tipo acta de calificaciones por corte.
- Consulta general de actas para Estadística.
- Consulta limitada para jefatura de carrera según ámbito, carrera o unidad.
- Conformidad informativa del discente.

## 5. Qué se modificó respecto al comportamiento original

Se separó formalmente la captura preliminar del acta oficial.

- Se agregó el flujo formal de estados del acta.
- Se agregó generación de borrador desde captura preliminar.
- Se agregó regeneración únicamente cuando el acta está en `BORRADOR_DOCENTE`.
- Se agregó publicación del acta a discentes.
- Se agregó remisión del acta a jefatura de carrera.
- Se agregó validación por jefatura de carrera.
- Se agregó formalización por jefatura académica.
- Se agregó bloqueo de captura preliminar cuando existe acta avanzada del mismo corte y asignación.
- Se agregó control para que el docente pierda edición directa después de remitir.
- Se corrigió la vista del acta para parecerse más a un acta de calificaciones por corte.
- Se separó visualmente grado/empleo y nombre del discente.
- Se ocultó la matrícula en vistas docentes.
- Se corrigieron textos visibles en español.

## 6. Qué solo se ajustó

Se realizaron ajustes puntuales para cerrar observaciones funcionales y de presentación:

- Precisión decimal interna del cálculo.
- Redondeo visual a 1 decimal.
- Corrección para que `valor_capturado` represente únicamente lo capturado realmente por el docente.
- Uso de `valor_calculado` para guardar el valor usado en el cálculo cuando aplica exención.
- Corrección de exención para no simular una captura real del examen final.
- Botones y enlaces según perfil para evitar enlaces que conduzcan a 403 esperados.
- Correcciones de ortografía y tildes.
- Corrección del acceso diferenciado de Estadística y Jefatura de Carrera.
- Visualización de conformidad del discente sin colocar comentarios completos en la tabla principal del acta.

## 7. Justificación de los cambios

Se separó captura preliminar y acta formal para evitar oficializar datos antes de tiempo.

Se usaron snapshots básicos para que el acta no dependa completamente del esquema vivo.

Se controlaron estados para asegurar trazabilidad académica.

Se bloqueó la edición después de publicar o remitir para proteger la integridad del proceso.

Se permitió la conformidad del discente como registro informativo no bloqueante.

Se dio a Estadística acceso de consulta sin permitir validación ni firma.

Se limitó a jefatura de carrera a su ámbito para evitar consulta o validación de actas ajenas.

Se ocultó matrícula militar en vistas docentes por privacidad.

Se mantuvo precisión interna y redondeo solo visual para evitar errores de cálculo.

## 8. Flujo final implementado

1. El docente captura calificaciones preliminares.
2. El docente genera un borrador de acta.
3. El docente puede regenerar el acta mientras esté en `BORRADOR_DOCENTE`.
4. El docente publica el acta a discentes.
5. El discente consulta y registra acuse, conformidad o inconformidad.
6. El docente remite el acta a jefatura de carrera.
7. La jefatura de carrera valida el acta.
8. La jefatura académica formaliza el acta.
9. Estadística consulta estados y actas en modo solo lectura.

## 9. Reglas principales implementadas

- No se permite duplicidad de acta activa por asignación docente y corte.
- La publicación se bloquea si faltan capturas requeridas.
- La exención válida permite omitir el examen final.
- La regeneración solo se permite en `BORRADOR_DOCENTE`.
- La captura preliminar se bloquea si existe acta avanzada del mismo corte.
- El discente solo consulta su propio detalle.
- Estadística solo consulta.
- Jefatura de carrera valida solo actas de su ámbito.
- Jefatura académica formaliza solo actas previamente validadas.
- Solo el acta `FINAL` formalizada actualiza campos oficiales de `InscripcionMateria`.
- Las actas parciales formalizadas no actualizan calificación final oficial.

## 10. Permisos y perfiles

| Perfil | Permisos implementados |
|---|---|
| Docente | Captura preliminares, genera borrador, regenera en borrador, publica y remite sus propias actas. |
| Discente | Consulta sus actas publicadas y registra conformidad informativa. |
| Jefatura de carrera / Jefe de Subsección de Ejecución y Control | Consulta y valida actas remitidas dentro de su ámbito, carrera o unidad. |
| Jefatura académica | Consulta pendientes, formaliza actas validadas y consulta actas ya formalizadas. |
| Estadística | Consulta actas y estados en modo solo lectura, sin validar ni formalizar. |
| Admin/superusuario | Puede operar como soporte técnico según reglas existentes. |

## 11. Archivos modificados

### Documentación

- `README.md`

### Evaluación

- `backend/evaluacion/admin.py`
- `backend/evaluacion/forms.py`
- `backend/evaluacion/models.py`
- `backend/evaluacion/services.py`
- `backend/evaluacion/tests.py`
- `backend/evaluacion/urls.py`
- `backend/evaluacion/views.py`

### Templates de evaluación agregados

- `backend/evaluacion/templates/evaluacion/acta_detalle.html`
- `backend/evaluacion/templates/evaluacion/consulta_actas.html`
- `backend/evaluacion/templates/evaluacion/discente_acta_detalle.html`
- `backend/evaluacion/templates/evaluacion/discente_actas.html`
- `backend/evaluacion/templates/evaluacion/docente_actas.html`
- `backend/evaluacion/templates/evaluacion/estadistica_actas.html`
- `backend/evaluacion/templates/evaluacion/jefatura_academica_actas.html`
- `backend/evaluacion/templates/evaluacion/jefatura_carrera_actas.html`

### Migraciones generadas

- `backend/evaluacion/migrations/0007_acta_detalleacta_conformidaddiscente_and_more.py`
- `backend/evaluacion/migrations/0008_alter_calificacioncomponente_options_and_more.py`

### Relaciones

- `backend/relaciones/forms.py`
- `backend/relaciones/permisos.py`
- `backend/relaciones/tests.py`

### Usuarios y front temporal

- `backend/usuarios/views.py`
- `backend/usuarios/tests.py`
- `backend/usuarios/templates/usuarios/validacion/docente_asignacion_detalle.html`
- `backend/usuarios/templates/usuarios/validacion/docente_asignaciones.html`

## 12. Pruebas ejecutadas

| Comando | Resultado |
|---|---|
| `docker compose exec -T backend python manage.py check` | OK |
| `docker compose exec -T backend python manage.py makemigrations --check` | OK, sin cambios pendientes |
| `docker compose exec -T backend python manage.py test evaluacion` | OK, 69 tests |
| `docker compose exec -T backend python manage.py test usuarios relaciones` | OK, 103 tests |
| `docker compose exec -T backend python manage.py test` | OK, 234 tests |

## 13. Observaciones no bloqueantes

- El comentario para `INCONFORME` actualmente quedó opcional. Si se desea obligatorio, es un ajuste menor.
- El estado `ARCHIVADO` existe, pero la transición operativa queda pendiente.
- Los snapshots actuales son suficientes para el prototipo, pero a futuro conviene congelar también nombre, grado, grupo, materia y docente.
- Hay cambios pendientes sin commit/push que conviene cerrar antes del siguiente bloque.

## 14. Pendientes intencionales y por qué

- Historial académico queda fuera porque depende de actas formalizadas y consolidación estable.
- Kárdex queda fuera porque requiere historial académico estable.
- Extraordinarios quedan fuera porque representan un flujo académico posterior.
- Reportes PDF/Excel quedan fuera porque primero se estabiliza el flujo funcional.
- Consolidación estadística queda fuera porque Estadística por ahora solo consulta.
- Archivado/consolidación queda fuera para un bloque posterior.
- Rectificaciones posteriores al cierre quedan fuera porque requieren reglas institucionales adicionales.
- Snapshots avanzados quedan fuera porque probablemente requieren migración y mayor definición documental.
- Catálogo oficial completo de resultados/marcas queda pendiente si aún no está definido institucionalmente.

## 15. Recomendación final

El Bloque 6 está listo para commit y push si el equipo acepta las observaciones documentadas.

Se puede pasar al siguiente bloque.

Antes de iniciar un bloque grande nuevo, conviene decidir si el comentario de inconformidad debe ser obligatorio o mantenerse opcional.

Se recomienda cerrar este bloque en Git antes de continuar, para que el siguiente desarrollo parta de una base estable y compartida.
