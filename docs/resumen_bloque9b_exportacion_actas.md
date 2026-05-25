# Resumen Bloque 9B - Exportación de actas PDF/Excel

## Objetivo

El Bloque 9B implementa la exportación real de actas en PDF y Excel para el Sistema de Control Académico EMI - ICI, usando como base el núcleo común de exportaciones y auditoría del Bloque 9A.

La estrategia corregida usa XLSX como fuente maestra del formato documental. El sistema ya no dibuja actas a mano para producción: carga plantillas XLSX institucionales anonimizadas, rellena celdas específicas con datos del sistema y conserva formato, merges, bordes, anchos, alturas, orientación, márgenes y área de impresión. El PDF se obtiene convirtiendo ese XLSX final con LibreOffice headless.

El bloque genera documentos reales, pero no modifica reglas académicas, no altera actas formalizadas, no cambia resultados oficiales y no implementa kárdex ni reportes generales.

## Alcance implementado

Se implementaron tres variantes documentales:

- Acta de evaluación parcial PDF/XLSX para cortes `P1`, `P2` y `P3`.
- Acta de Evaluación Final PDF/XLSX para corte `FINAL`.
- Acta de Calificación Final PDF/XLSX como consolidado por asignación docente.

Todas las exportaciones:

- requieren autenticación;
- validan permisos en backend;
- usan datos reales del sistema;
- generan nombre de archivo seguro;
- registran auditoría en `RegistroExportacion`;
- calculan tamaño y hash SHA-256;
- no modifican datos académicos.

## Archivos modificados o creados

### Backend

- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/evaluacion/models.py`
- `backend/evaluacion/migrations/0009_acta_probables_causas_reprobacion_and_more.py`
- `backend/usuarios/models.py`
- `backend/usuarios/admin.py`
- `backend/usuarios/forms.py`
- `backend/usuarios/migrations/0017_usuario_cedula_profesional_and_more.py`
- `backend/reportes/catalogo.py`
- `backend/reportes/api_views.py`
- `backend/reportes/api_urls.py`
- `backend/reportes/tests.py`
- `backend/reportes/constantes.py`
- `backend/reportes/actas_context.py`
- `backend/reportes/actas_services.py`
- `backend/reportes/exportadores/__init__.py`
- `backend/reportes/exportadores/actas_pdf.py`
- `backend/reportes/exportadores/actas_excel.py`
- `backend/reportes/templates_xlsx/actas/acta_evaluacion_parcial_template.xlsx`
- `backend/reportes/templates_xlsx/actas/acta_evaluacion_final_template.xlsx`
- `backend/reportes/templates_xlsx/actas/acta_calificacion_final_template.xlsx`

### Documentación y control de archivos

- `README.md`
- `docs/resumen_bloque9b_exportacion_actas.md`
- `.gitignore`

## Referencias privadas

Los ejemplos reales entregados por el equipo se copiaron para referencia visual local en:

- `docs/referencias_privadas/actas_bloque9/`

Esta carpeta queda ignorada por Git mediante:

- `docs/referencias_privadas/`

Los archivos reales no deben subirse al repositorio porque pueden contener datos académicos o personales.

## Plantillas productivas anonimizadas

Se crearon plantillas productivas en:

- `backend/reportes/templates_xlsx/actas/acta_evaluacion_parcial_template.xlsx`
- `backend/reportes/templates_xlsx/actas/acta_evaluacion_final_template.xlsx`
- `backend/reportes/templates_xlsx/actas/acta_calificacion_final_template.xlsx`

Estas plantillas se derivan visualmente de los XLSX de referencia, pero se limpiaron para no contener nombres, calificaciones, matrículas ni datos reales. Son las plantillas que usa el sistema en producción para generar las actas.

## Dependencias agregadas

Se agregaron o ajustaron dependencias del backend:

- `openpyxl>=3.1,<3.2` para generación XLSX.
- `LibreOffice Calc` en `backend/Dockerfile` para conversión XLSX a PDF.

El PDF ya no se genera con ReportLab ni HTML como fuente principal; se genera convirtiendo el XLSX final con `soffice`/`libreoffice` en modo headless. El binario puede configurarse con `LIBREOFFICE_BINARY`.

## Cambios de modelo

Se agregaron dos campos opcionales al modelo `Acta`:

- `probables_causas_reprobacion`
- `sugerencias_academicas`

Ambos son opcionales. Si no tienen contenido, las exportaciones muestran `N/A`.

Migración creada:

- `evaluacion.0009_acta_probables_causas_reprobacion_and_more`

Se agregaron dos campos opcionales al modelo `Usuario` para alimentar firmas docentes:

- `titulo_profesional`
- `cedula_profesional`

Estos campos permiten que el bloque `Evaluó` muestre el grado/título académico del docente y su cédula profesional sin usar la leyenda genérica `Docente`.

Migración creada:

- `usuarios.0017_usuario_cedula_profesional_and_more`

## Servicios creados

### Contexto documental

Archivo:

- `backend/reportes/actas_context.py`

Responsabilidades:

- construir contexto común para actas por corte;
- construir contexto consolidado para calificación final;
- resolver encabezados institucionales;
- obtener carrera, materia, docente, grupo, ciclo escolar y semestre;
- armar filas de discentes;
- calcular componentes ponderados;
- calcular estadísticos;
- preparar leyendas, causas, sugerencias y firmas;
- marcar documentos no oficiales cuando corresponda.

### Servicio de exportación de actas

Archivo:

- `backend/reportes/actas_services.py`

Responsabilidades:

- validar permisos por usuario y objeto;
- registrar solicitud en `RegistroExportacion`;
- generar PDF o XLSX;
- marcar exportación como `GENERADA` o `FALLIDA`;
- calcular tamaño y hash SHA-256;
- devolver bytes, MIME type y nombre de archivo.

### Exportador PDF

Archivo:

- `backend/reportes/exportadores/actas_pdf.py`

Genera primero el XLSX final desde la plantilla institucional y luego lo convierte a PDF con LibreOffice headless. Así el PDF respeta la orientación, área de impresión y distribución visual definida por la plantilla XLSX.

### Exportador Excel

Archivo:

- `backend/reportes/exportadores/actas_excel.py`

Genera XLSX con:

- carga de plantilla XLSX institucional;
- conservación de encabezados combinados, bordes, anchos, alturas, márgenes y área de impresión;
- valores cerrados, sin fórmulas;
- población de metadatos, tabla principal, resumen estadístico, causas, sugerencias, firmas y leyendas;
- ocultamiento de filas sobrantes del roster para mostrar únicamente los discentes reales del curso;
- formato compacto propio para Evaluación Final.

Las filas sobrantes no se imprimen ni se muestran visualmente en el XLSX/PDF generado. Se ocultan en lugar de eliminarse físicamente para preservar celdas combinadas, bordes, altura, orientación, área de impresión y la geometría institucional de las plantillas.

## Endpoints creados

### Acta por corte PDF

`GET /api/exportaciones/actas/<acta_id>/pdf/`

### Acta por corte Excel

`GET /api/exportaciones/actas/<acta_id>/xlsx/`

### Acta de Calificación Final PDF

`GET /api/exportaciones/asignaciones/<asignacion_docente_id>/calificacion-final/pdf/`

### Acta de Calificación Final Excel

`GET /api/exportaciones/asignaciones/<asignacion_docente_id>/calificacion-final/xlsx/`

Todos los endpoints devuelven `Content-Disposition: attachment` y agregan el encabezado `X-Registro-Exportacion-Id` para facilitar trazabilidad técnica.

## Reglas de permisos

### Admin/superusuario

Puede exportar actas por soporte técnico.

### Estadística

Puede exportar actas institucionales autorizadas.

### Docente

Puede exportar únicamente sus propias actas y calificación final de sus asignaciones.

### Jefatura de carrera

Puede exportar actas de su ámbito/carrera cuando el sistema puede inferir la carrera.

### Jefatura académica y pedagógica

Conservan consulta institucional autorizada.

### Discente

No puede exportar actas completas de grupo, reportes globales ni kárdex oficial.

## Reglas documentales

### Acta de evaluación parcial

Muestra componentes ponderados del corte, calificación final del corte y firma de conformidad.

### Acta de Evaluación Final

Muestra componentes propios del corte `FINAL`, incluyendo examen final cuando exista.

### Acta de Calificación Final

Muestra columnas consolidadas:

- Parcial 1;
- Parcial 2;
- Parcial 3;
- Evaluación Final;
- Calificación final.

No muestra componentes por corte.

### Firmas institucionales

El bloque de firmas se resuelve con datos reales cuando están disponibles:

- `Evaluó`: docente asociado a la asignación docente, con `titulo_profesional` y `cedula_profesional`.
- `Revisó`: cargo vigente de jefatura de carrera/subsección asociado a la carrera del grupo.
- `Vo. Bo.`: cargo vigente de jefatura académica.

Si no existe una jefatura o validación vigente, se conserva el espacio de firma como pendiente sin inventar nombres.

### Documentos no formalizados

Si el acta no está formalizada, el documento incluye marca visible:

- `BORRADOR / DOCUMENTO NO OFICIAL`
- `DOCUMENTO NO OFICIAL / PARA REVISION O FIRMA FISICA`

La exportación no modifica el estado del acta.

## Cálculo visual de componentes

Para actas por corte, cada componente muestra la aportación ponderada:

`valor_capturado * porcentaje / 100`

Si existe `valor_calculado`, se usa ese valor persistido.

La salida se muestra a un decimal, manteniendo el cálculo interno con `Decimal`.

## Exención

Cuando un componente de examen final está sustituido por exención:

- la celda muestra `EXENTO`;
- el documento incluye nota: `Valor aplicado por regla de exención conforme al promedio de parciales.`

No se simula captura manual y no se modifican calificaciones persistidas.

## Estadísticos

Se calculan al momento de exportar:

- alumnos reprobados;
- media;
- moda;
- desviación estándar.

Reglas:

- escala 0.0 a 10.0;
- reprobado menor a 6.0;
- visualización a un decimal;
- si no hay datos suficientes, se muestra `N/A`.

## Auditoría

Cada descarga crea un `RegistroExportacion` con:

- usuario;
- tipo de documento;
- formato;
- nombre del documento;
- nombre seguro del archivo;
- objeto asociado;
- parámetros no sensibles;
- rol/cargo de contexto;
- IP de origen;
- user agent;
- estado;
- tamaño en bytes;
- hash SHA-256;
- fecha de finalización.

Si falla la generación:

- se marca `FALLIDA`;
- se guarda mensaje de error;
- se devuelve respuesta controlada;
- no se crea archivo parcial.

## Catálogo actualizado

Se actualizaron como implementados:

- `ACTA_EVALUACION_PARCIAL`
- `ACTA_EVALUACION_FINAL`
- `ACTA_CALIFICACION_FINAL`

Los demás documentos permanecen pendientes para subbloques posteriores.

## Pruebas automatizadas agregadas

Se agregaron pruebas para:

- exportar acta parcial PDF;
- exportar acta parcial XLSX;
- exportar evaluación final PDF/XLSX;
- exportar calificación final PDF/XLSX;
- generar XLSX desde plantilla parcial;
- generar XLSX desde plantilla de Evaluación Final;
- generar XLSX desde plantilla de Calificación Final;
- aislar la conversión PDF para validar uso de LibreOffice headless sin depender del binario en tests unitarios;
- impedir exportación de acta ajena por docente;
- impedir exportación completa a discente;
- permitir exportación a Estadística;
- crear `RegistroExportacion` en exportación exitosa;
- registrar `FALLIDA` ante error de generación;
- validar nombre de archivo sin datos sensibles;
- marcar documento no oficial cuando no está formalizado;
- no marcar borrador en acta formalizada;
- mostrar componentes ponderados;
- calcular estadísticos;
- mostrar `N/A` en causas/sugerencias vacías;
- no modificar `Acta` ni `InscripcionMateria` al exportar.

## Validaciones ejecutadas

```bash
docker compose build backend
docker compose up -d backend
docker compose exec -T backend python manage.py makemigrations evaluacion
docker compose exec -T backend python manage.py makemigrations usuarios
docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test reportes
docker compose exec -T backend python manage.py test
```

Resultados:

- `build backend`: OK. Imagen backend reconstruida con LibreOffice Calc.
- `up -d backend`: OK.
- `makemigrations evaluacion`: OK, creó `0009`.
- `makemigrations usuarios`: OK, creó `0017`.
- `migrate`: OK.
- `check`: OK.
- `makemigrations --check`: OK.
- `test reportes`: 27 pruebas OK.
- `test`: 327 pruebas OK.
- Validación PDF real: OK. `/api/exportaciones/actas/5/pdf/` respondió `200 application/pdf`, generó contenido `%PDF-` y registró la exportación.

## Limitaciones actuales

- El PDF depende de LibreOffice disponible en el contenedor o entorno backend.
- El XLSX replica la estructura principal de los ejemplos mediante plantillas productivas anonimizadas.
- No se insertan escudos/logos dentro del PDF porque los ejemplos de acta proporcionados no los incluyen en el documento.
- No se almacena archivo histórico permanente; solo se entrega la descarga y se registra auditoría.
- No se implementa pantalla React de reportes.
- La firma electrónica, QR y sello digital quedan fuera.

## Pendientes para 9C y reportes posteriores

### Bloque 9C

- Kárdex oficial PDF.
- Reglas de visibilidad del kárdex institucional sin exposición al discente.
- Auditoría de descarga de kárdex.

### Reportes posteriores

- Historial académico exportable.
- Reportes de desempeño.
- Reportes de situación académica.
- Actas por estado.
- Inconformidades y conformidades pendientes.
- Movimientos académicos.
- Cuadro de aprovechamiento.

### Integración posterior con frontend

- Pantalla React de catálogo de reportes.
- Historial visual de exportaciones.
- Botones de descarga por acta/asignación.
- Estados de disponibilidad por rol/cargo.
