# Resumen técnico del Bloque 8 - Kárdex oficial

## 1. Resultado general

El Bloque 8 implementa el kárdex oficial como una vista institucional derivada del historial académico y de los resultados oficiales consolidados.

Resultado del bloque: **APROBADO CON OBSERVACIONES**.

Con el estado actual sí es posible pasar al siguiente bloque, porque:

- No existen errores técnicos bloqueantes.
- Las pruebas automáticas principales pasan correctamente.
- El kárdex se construye desde fuentes oficiales consolidadas.
- No se crearon tablas transaccionales innecesarias.
- No se implementaron exportaciones PDF/Excel antes de definir el formato oficial.
- El kárdex quedó restringido como consulta institucional y ya no es visible para discentes.

## 2. Contexto previo

Antes del Bloque 8 ya existían:

- Bloque 5: captura preliminar y cálculo académico.
- Bloque 6: actas formales, publicación, conformidad, remisión, validación y formalización.
- Bloque 7: historial académico, trayectoria, extraordinarios, baja temporal, baja definitiva y reingreso.

El historial académico ya podía consultar resultados oficiales desde actas `FINAL` formalizadas y campos oficiales de `InscripcionMateria`.

El kárdex se implementó sobre esa base, sin convertirlo en una tabla oficial independiente.

## 3. Objetivo del Bloque 8

Construir una vista de kárdex académico oficial por discente, usando únicamente información ya consolidada:

- Actas `FINAL` formalizadas.
- Campos oficiales de `InscripcionMateria`.
- Resultados ordinarios.
- Extraordinarios aprobados o reprobados.
- Marca `EE` cuando aplique.
- Situación académica actual del discente.

El kárdex no debe modificar datos del dominio. Solo consulta, organiza y presenta información.

## 4. Qué se implementó

Se implementó el servicio de kárdex en `backend/trayectoria/services.py`.

Elementos principales:

- `ServicioKardex`.
- Función `construir_kardex_discente`.
- DTOs internos en memoria:
  - `KardexOficial`.
  - `KardexAnio`.
  - `KardexAsignatura`.

Estos DTOs no son modelos de base de datos. Solo sirven para armar la vista en memoria.

También se implementaron vistas y plantillas:

- Búsqueda institucional de kárdex.
- Detalle del kárdex por discente.
- Plantilla visual de kárdex oficial.
- Plantilla visual de historial académico con apariencia institucional.
- Estilos reutilizables para documentos académicos.

## 5. Qué se ajustó durante el bloque

### Restricción de acceso para discentes

Inicialmente el diseño contemplaba una vista "Mi kárdex" para discentes. Se corrigió porque institucionalmente se decidió que el kárdex no debe ser visible para los discentes.

Ajustes realizados:

- Se eliminó la ruta `/trayectoria/mi-kardex/`.
- Se quitó el enlace "Mi kárdex" del dashboard del discente.
- Se crearon o conectaron permisos específicos para kárdex.
- El detalle `/trayectoria/kardex/<discente_id>/` ya no reutiliza permisos de historial propio.
- Si un discente intenta consultar su propio kárdex o el de otro discente por URL directa, recibe acceso denegado.

El discente conserva acceso a:

- Sus actas publicadas, según el flujo del Bloque 6.
- Su historial académico, según el Bloque 7.
- Su carga académica.

Pero no ve kárdex.

### Ajuste visual institucional

Se ajustaron las plantillas para que historial académico y kárdex se parezcan más a documentos institucionales, sin implementar todavía PDF ni Excel.

Cambios visuales:

- Encabezado formal.
- Sección de datos generales del discente.
- Tabla principal compacta.
- Sección de resultados oficiales.
- Sección de eventos de trayectoria en historial.
- Sección de leyendas en kárdex.
- Nota institucional al final.
- CSS básico para impresión con `@media print`.

El objetivo fue preparar una base visual reutilizable para el Bloque 9, sin fijar todavía un formato oficial definitivo.

## 6. Qué se mantuvo igual

Se conservaron las reglas importantes del diseño anterior:

- El kárdex no es una tabla transaccional principal.
- No existe modelo `KardexOficial`.
- No se duplican resultados oficiales.
- No se modifican actas formalizadas.
- No se modifican resultados oficiales desde el kárdex.
- No se actualiza `InscripcionMateria` desde el kárdex.
- No se usan capturas preliminares.
- No se usan actas no formalizadas.
- No se implementan PDF ni Excel.
- No se implementan reportes estadísticos.
- No se implementan cuadros de aprovechamiento.

## 7. Reglas principales implementadas

### Fuente oficial del kárdex

El kárdex se construye desde:

- Inscripciones con acta `FINAL` formalizada.
- Campos oficiales de `InscripcionMateria`.
- Extraordinarios registrados cuando existen.

No aparecen:

- Capturas preliminares.
- Actas en borrador.
- Actas publicadas pero no formalizadas.
- Actas remitidas o validadas que todavía no estén formalizadas.

### Extraordinario y marca EE

Cuando una materia fue aprobada por extraordinario:

- El kárdex muestra la calificación aprobatoria del extraordinario.
- Se muestra la marca `EE`.
- La evidencia ordinaria se conserva en historial académico.
- No se borra ni se oculta la evidencia ordinaria del sistema.

### Resultados no numéricos

El kárdex permite mostrar resultados no numéricos como:

- `ACREDITADA`.
- `APROBADO`.
- `APROBADO_NO_NUMERICO`.
- `EXCEPTUADO`.

Estos resultados no se incluyen en el promedio anual.

### Promedio anual

El promedio anual:

- Solo considera asignaturas con calificación numérica.
- Excluye resultados no numéricos.
- Usa `Decimal`.
- Se muestra visualmente redondeado a un decimal.
- No modifica datos persistidos.

## 8. Permisos y perfiles

### Discente

- No puede ver kárdex.
- No tiene enlace visible al kárdex.
- No puede consultar kárdex propio por URL directa.
- No puede consultar kárdex ajeno por URL directa.
- Sí conserva su vista de historial académico.

### Estadística/Admin

- Puede buscar y consultar kárdex de discentes.
- Puede consultar la vista institucional.
- No se le otorgaron acciones de modificación desde el kárdex.

### Jefatura de carrera / Jefe de subsección de Ejecución y Control

- Puede consultar kárdex de discentes dentro de su ámbito.
- No obtiene consulta general fuera de su carrera/unidad.

### Jefatura académica / pedagógica

- Puede consultar según los permisos institucionales ya existentes.

La validación se realiza en backend, no solamente ocultando enlaces.

## 9. Rutas principales

Rutas conservadas:

- `GET /trayectoria/kardex/`
- `GET /trayectoria/kardex/<discente_id>/`

Ruta eliminada:

- `GET /trayectoria/mi-kardex/`

La ruta propia del discente se eliminó porque el kárdex no debe ser visible para discentes.

## 10. Cambios visuales de historial académico

La vista de historial académico se ajustó para mostrar:

- Nombre del discente.
- Grado y empleo, si existe.
- Carrera.
- Plan de estudios.
- Antigüedad.
- Situación actual.
- Resultados oficiales.
- Periodo académico.
- Año de formación.
- Semestre.
- Programa de asignatura.
- Grupo.
- Tipo de resultado.
- Calificación.
- Resultado.
- Marca.
- Evidencia ordinaria.
- Eventos de trayectoria.

El historial mantiene una tabla única ordenada. No se forzó agrupación formal porque el historial mezcla resultados ordinarios, extraordinarios y eventos de trayectoria. Agruparlo demasiado ahora podría aparentar un formato oficial que todavía no está definido.

## 11. Cambios visuales de kárdex oficial

La vista de kárdex oficial se ajustó para mostrar:

- Encabezado formal.
- Datos generales del discente.
- Resultados agrupados por año de formación.
- Periodo académico.
- Semestre.
- Clave de materia.
- Programa de asignatura.
- Grupo.
- Calificación.
- Calificación con letra.
- Resultado.
- Marca.
- Promedio anual.
- Leyendas de escala y marca `EE`.

El kárdex ya tiene agrupación por año de formación porque el servicio lo construye de forma segura.

## 12. Archivos modificados o creados

### Servicios, permisos y vistas

- `backend/trayectoria/services.py`
- `backend/trayectoria/permisos.py`
- `backend/trayectoria/views.py`
- `backend/trayectoria/urls.py`
- `backend/usuarios/views.py`

### Plantillas

- `backend/trayectoria/templates/trayectoria/kardex_busqueda.html`
- `backend/trayectoria/templates/trayectoria/kardex_detalle.html`
- `backend/trayectoria/templates/trayectoria/historial_detalle.html`
- `backend/trayectoria/templates/trayectoria/_documento_academico_styles.html`

### Pruebas

- `backend/trayectoria/tests.py`
- `backend/usuarios/tests.py`

### Documentación

- `README.md`
- `docs/resumen_bloque8_kardex_oficial.md`

## 13. Pruebas y validaciones ejecutadas

Validaciones ejecutadas:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test trayectoria
docker compose exec -T backend python manage.py test usuarios trayectoria
docker compose exec -T backend python manage.py test trayectoria evaluacion usuarios relaciones
docker compose exec -T backend python manage.py test
```

Resultados:

- `manage.py check`: OK.
- `makemigrations --check`: OK, sin migraciones pendientes.
- `test trayectoria`: OK, 25 pruebas.
- `test usuarios trayectoria`: OK, 103 pruebas.
- `test trayectoria evaluacion usuarios relaciones`: OK, 212 pruebas.
- `test`: OK, 274 pruebas.

También se realizó revisión visual en navegador:

- La búsqueda de kárdex carga correctamente.
- El detalle de kárdex muestra la nueva estructura institucional.
- El historial académico muestra la nueva estructura institucional.
- No aparecen opciones de PDF/Excel.
- El kárdex no queda disponible para discentes.

## 14. Pendientes intencionales

Quedan pendientes para bloques posteriores:

- Definir formato oficial de PDF.
- Definir formato oficial de Excel.
- Agregar folio o identificador documental oficial, si la institución lo requiere.
- Incorporar logos, sellos o membretes oficiales si se proporcionan.
- Definir firmas o responsables de emisión documental.
- Definir si el historial también tendrá una versión exportable separada del kárdex.
- Definir criterios de impresión oficial: márgenes, encabezados, pies, paginación y leyendas obligatorias.
- Reportes estadísticos y cuadros de aprovechamiento.

Estos pendientes no bloquean el cierre del Bloque 8 porque pertenecen al Bloque 9 o a definición documental institucional.

## 15. Riesgos no bloqueantes

- El diseño visual actual es una aproximación institucional, no un formato oficial definitivo.
- La impresión desde navegador ya tiene una base razonable, pero no sustituye una exportación PDF formal.
- Si se requiere documento oficial con folio, firmas o sellos, será necesario definir esos datos antes de exportar.
- Si la institución decide que el discente pueda ver una versión parcial del kárdex en el futuro, habría que crear una vista separada con permisos distintos.

## 16. Conclusión

El Bloque 8 queda listo para cierre técnico y se puede pasar al siguiente bloque.

La implementación cumple el objetivo principal:

- Kárdex oficial como vista derivada.
- Sin tabla transaccional principal.
- Sin duplicar resultados oficiales.
- Sin usar capturas preliminares.
- Sin mostrar actas no formalizadas.
- Sin permitir acceso a discentes.
- Con consulta institucional para perfiles autorizados.
- Con base visual más formal para exportación futura.

Recomendación final:

- Se puede pasar al siguiente bloque.
- Antes de iniciar exportaciones formales, conviene que el equipo defina el formato oficial esperado.
- Conviene hacer commit y push de este bloque antes de continuar con cambios grandes.

