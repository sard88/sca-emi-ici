# Resumen Bloque 9F-J-L - Reportes operativos de actas, validaciones y exportaciones

## Objetivo

Implementar una primera base backend de reportes operativos en formato XLSX para:

- Bloque 9F: reportes operativos de actas.
- Bloque 9J: historial de validaciones de acta.
- Bloque 9L: reporte de exportaciones realizadas.

El bloque conserva a Django como fuente de verdad, no modifica datos académicos y registra auditoría en cada descarga mediante `RegistroExportacion`.

## Alcance Implementado

Se implementaron siete reportes:

- Actas por estado.
- Actas pendientes de validación.
- Actas con inconformidades.
- Actas sin conformidad de discentes.
- Actas formalizadas.
- Historial de validaciones de acta.
- Exportaciones realizadas.

El formato implementado es XLSX. PDF queda marcado como pendiente.

## Archivos Principales

- `backend/reportes/models.py`
- `backend/reportes/catalogo.py`
- `backend/reportes/services.py`
- `backend/reportes/reportes_operativos.py`
- `backend/reportes/exportadores/reportes_excel.py`
- `backend/reportes/api_views.py`
- `backend/reportes/api_urls.py`
- `backend/reportes/tests.py`
- `backend/reportes/migrations/0002_alter_registroexportacion_tipo_documento.py`
- `README.md`
- `docs/resumen_bloque9f_j_l_reportes_operativos.md`

## Modelo y Catálogo

Se agregaron tipos documentales para separar reportes que antes no existían como choice explícito:

- `REPORTE_ACTAS_SIN_CONFORMIDAD`
- `REPORTE_ACTAS_FORMALIZADAS`

El catálogo de exportaciones marca como implementados en XLSX:

- `REPORTE_ACTAS_ESTADO`
- `REPORTE_ACTAS_PENDIENTES`
- `REPORTE_INCONFORMIDADES`
- `REPORTE_ACTAS_SIN_CONFORMIDAD`
- `REPORTE_ACTAS_FORMALIZADAS`
- `REPORTE_VALIDACIONES_ACTA`
- `REPORTE_EXPORTACIONES`

Los demás reportes de desempeño, situación académica, movimientos y auditoría transversal permanecen pendientes.

## Servicios Creados

### `ServicioReportesOperativos`

Construye datasets de vista previa y exportación para cada reporte operativo.

Responsabilidades:

- validar autenticación;
- validar permiso por tipo de reporte;
- aplicar filtros seguros;
- filtrar actas por ámbito institucional;
- construir hojas de detalle y resumen;
- generar registro de exportación;
- marcar exportación como `GENERADA` o `FALLIDA`;
- calcular tamaño y hash SHA-256 del XLSX.

### Exportador Tabular XLSX

Archivo:

- `backend/reportes/exportadores/reportes_excel.py`

Funciones:

- generar workbook con `openpyxl`;
- agregar encabezado institucional simple;
- agregar filtros aplicados;
- agregar tabla con estilos;
- congelar encabezados;
- ajustar anchos de columnas;
- activar autofiltros;
- crear hojas de resumen cuando aplica.

No usa pandas, CSV ni fórmulas.

## Endpoints JSON

Se agregaron endpoints de vista previa:

- `GET /api/reportes/operativos/actas-estado/`
- `GET /api/reportes/operativos/actas-pendientes/`
- `GET /api/reportes/operativos/inconformidades/`
- `GET /api/reportes/operativos/sin-conformidad/`
- `GET /api/reportes/operativos/actas-formalizadas/`
- `GET /api/reportes/operativos/validaciones-acta/`
- `GET /api/reportes/operativos/exportaciones-realizadas/`

Respuesta general:

- `ok`
- `slug`
- `nombre`
- `total`
- `filtros`
- `columnas`
- `items`
- `sheets`

La vista previa JSON devuelve filas operativas de detalle. Las hojas de resumen se reservan para el XLSX y se informan en metadatos.

## Endpoints XLSX

Se agregaron endpoints de descarga:

- `GET /api/exportaciones/reportes/actas-estado/xlsx/`
- `GET /api/exportaciones/reportes/actas-pendientes/xlsx/`
- `GET /api/exportaciones/reportes/inconformidades/xlsx/`
- `GET /api/exportaciones/reportes/sin-conformidad/xlsx/`
- `GET /api/exportaciones/reportes/actas-formalizadas/xlsx/`
- `GET /api/exportaciones/reportes/validaciones-acta/xlsx/`
- `GET /api/exportaciones/reportes/exportaciones-realizadas/xlsx/`

Cada respuesta incluye:

- `Content-Disposition: attachment`
- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `X-Registro-Exportacion-Id`

## Columnas Principales

### Actas Por Estado

Incluye periodo, carrera, grupo, semestre, programa, unidad de aprendizaje, docente, corte, estado, fechas de creación/publicación/remisión/validación/formalización, totales de conformidad e indicador de documento oficial.

### Actas Pendientes

Separa pendientes de jefatura de carrera y pendientes de jefatura académica. Incluye estado actual, fechas, días en estado, jefatura responsable esperada y prioridad operativa.

### Inconformidades

Incluye acta, periodo, carrera, grupo, asignatura, corte, estado del acta, grado/empleo, nombre del discente, fecha y comentario de inconformidad.

### Sin Conformidad

Lista discentes incluidos en actas publicadas o superiores sin conformidad vigente registrada.

### Formalizadas

Incluye actas formalizadas, fecha de formalización, jefatura que validó, jefatura académica que formalizó, total de discentes, promedio y reprobados cuando se pueden derivar sin modificar datos.

### Validaciones de Acta

Incluye etapa, acción, usuario firmante, grado/empleo, cargo, tipo de designación, unidad organizacional, fecha/hora, IP y observación.

### Exportaciones Realizadas

Incluye usuario, rol/cargo de contexto, tipo documental, formato, nombre de archivo, objeto, estado, tamaño, hash, IP, user agent resumido y mensaje de error si aplica.

## Filtros Soportados

Los servicios aceptan filtros seguros como:

- `periodo`
- `carrera`
- `grupo`
- `asignatura`
- `programa`
- `docente`
- `corte`
- `estado_acta`
- `estado`
- `tipo_pendiente`
- `fecha_desde`
- `fecha_hasta`
- `usuario`
- `tipo_documento`
- `formato`
- `estado_exportacion`
- `etapa_validacion`
- `accion`
- `cargo`

Solo se guardan filtros reconocidos en `RegistroExportacion`.

## Permisos

Reglas aplicadas:

- Admin/superusuario puede consultar y exportar todos los reportes.
- Estadística puede consultar y exportar reportes institucionales.
- Jefatura académica y pedagógica pueden consultar reportes institucionales autorizados.
- Jefatura de carrera queda filtrada a su carrera/ámbito cuando se puede inferir.
- Docente no accede a reportes globales en este bloque.
- Discente no accede.

El frontend puede ocultar opciones, pero la validación real queda en backend.

## Privacidad

Reglas aplicadas:

- No se muestra matrícula militar por defecto.
- Los reportes nominales muestran grado/empleo y nombre solo para perfiles autorizados.
- Comentarios de inconformidad se incluyen únicamente en el reporte específico de inconformidades.
- No se guardan payloads completos de reportes en auditoría.
- No se guardan listados completos de discentes en `parametros_json`.
- Los filtros se sanitizan y no conservan claves como password, token, session, cookie o authorization.

## Auditoría

Cada descarga XLSX:

- crea un `RegistroExportacion` en estado `SOLICITADA`;
- genera el XLSX;
- marca el registro como `GENERADA`;
- registra tamaño y hash SHA-256;
- registra `FALLIDA` si ocurre error durante la generación.

## Validaciones Ejecutadas

Durante la implementación se ejecutó:

- `python3 -m compileall backend/reportes`
- `docker compose ps`
- `docker compose exec -T backend python manage.py check`
- `docker compose exec -T backend python manage.py makemigrations reportes`
- `docker compose exec -T backend python manage.py migrate reportes`
- `docker compose exec -T backend python manage.py makemigrations --check`
- `docker compose exec -T backend python manage.py test reportes`
- `docker compose exec -T backend python manage.py test evaluacion`
- `docker compose exec -T backend python manage.py test`

Resultados confirmados:

- `python manage.py check`: OK.
- `python manage.py makemigrations --check`: OK, sin cambios pendientes.
- `python manage.py test reportes`: 57 pruebas OK.
- `python manage.py test evaluacion`: 72 pruebas OK.
- `python manage.py test`: 357 pruebas OK.

No se ejecutó lint/build de frontend porque el bloque no modifica código de Next.js.

## Limitaciones

- El XLSX usa un formato institucional tabular simple, no una plantilla oficial final.
- No se implementa PDF para estos reportes.
- La integración visual completa en Next.js queda pendiente.
- Los reportes de desempeño, situación académica y cuadro de aprovechamiento siguen fuera de alcance.

## Pendientes Para 10C-3A

- Crear pantallas del portal para reportes operativos.
- Agregar filtros visuales para cada reporte.
- Mostrar previsualización en tablas React.
- Descargar XLSX desde el portal usando los endpoints de este bloque.
- Integrar resultados con historial de exportaciones.

## Pendientes Para 9G-H y 9I-M-E

- Reportes de desempeño académico.
- Cuadro de aprovechamiento.
- Reportes de situación académica.
- Reportes de movimientos académicos si se decide separarlos.
- Reportes PDF posteriores.
- Indicadores y visualizaciones.
