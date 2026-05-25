# Bloque 9G-H - Reportes de desempeño académico y cuadro de aprovechamiento

## Objetivo

Implementar reportes institucionales derivados de resultados oficiales consolidados para seguimiento académico, sin modificar actas, calificaciones, inscripciones, historial ni kárdex.

El bloque se centra en backend, APIs y exportaciones XLSX auditadas mediante `RegistroExportacion`. La integración visual completa queda para el Bloque 10C-3B.

## Alcance implementado

Se agregaron vistas previas JSON y descargas XLSX para:

- Aprobados y reprobados.
- Promedios académicos.
- Distribución de calificaciones.
- Exentos por asignatura.
- Desempeño por docente.
- Desempeño por carrera, antigüedad y año de formación.
- Reprobados nominal.
- Cuadro de aprovechamiento académico.

No se implementó PDF del cuadro en esta iteración. Queda marcado como pendiente para una fase posterior, para mantener el alcance estable y evitar abrir plantillas adicionales antes de validar el XLSX institucional.

## Archivos modificados

- `backend/reportes/models.py`
- `backend/reportes/migrations/0003_alter_registroexportacion_tipo_documento.py`
- `backend/reportes/catalogo.py`
- `backend/reportes/services.py`
- `backend/reportes/api_views.py`
- `backend/reportes/api_urls.py`
- `backend/reportes/reportes_desempeno.py`
- `backend/reportes/tests.py`
- `README.md`
- `docs/resumen_bloque9g_h_reportes_desempeno.md`

## Servicios creados

### `ServicioReportesDesempeno`

Ubicación: `backend/reportes/reportes_desempeno.py`.

Responsabilidades:

- Validar autenticación y permisos.
- Aplicar filtros seguros.
- Obtener resultados oficiales consolidados.
- Construir datasets de vista previa.
- Construir hojas XLSX mediante `ReporteSheet`.
- Registrar auditoría de exportación.
- Marcar exportaciones como `GENERADA` o `FALLIDA`.
- Calcular tamaño y hash SHA-256 del archivo.

## Fuente de datos

Los reportes usan como fuente principal:

- `InscripcionMateria.calificacion_final`.
- `InscripcionMateria.codigo_resultado_oficial`.
- `InscripcionMateria.codigo_marca`.
- `Acta` FINAL formalizada.
- `DetalleActa` asociado al acta FINAL formalizada.
- `CalificacionComponente` para exenciones del examen final.
- `AsignacionDocente`, `GrupoAcademico`, `PeriodoEscolar`, `ProgramaAsignatura`, `Materia`, `Carrera` y `Antiguedad` para contexto académico.

Regla importante: los reportes oficiales finales solo consideran inscripciones con calificación final y acta FINAL formalizada. No se usan capturas preliminares ni actas no formalizadas como fuente oficial.

## Endpoints JSON

- `GET /api/reportes/desempeno/aprobados-reprobados/`
- `GET /api/reportes/desempeno/promedios/`
- `GET /api/reportes/desempeno/distribucion/`
- `GET /api/reportes/desempeno/exentos/`
- `GET /api/reportes/desempeno/docentes/`
- `GET /api/reportes/desempeno/cohorte/`
- `GET /api/reportes/desempeno/reprobados-nominal/`
- `GET /api/reportes/desempeno/cuadro-aprovechamiento/`

Respuesta base:

```json
{
  "ok": true,
  "slug": "aprobados-reprobados",
  "nombre": "Reporte de aprobados y reprobados",
  "total": 1,
  "filtros": {},
  "columnas": [],
  "items": [],
  "resumen": {},
  "sheets": []
}
```

## Endpoints XLSX

- `GET /api/exportaciones/reportes/aprobados-reprobados/xlsx/`
- `GET /api/exportaciones/reportes/promedios/xlsx/`
- `GET /api/exportaciones/reportes/distribucion/xlsx/`
- `GET /api/exportaciones/reportes/exentos/xlsx/`
- `GET /api/exportaciones/reportes/desempeno-docente/xlsx/`
- `GET /api/exportaciones/reportes/desempeno-cohorte/xlsx/`
- `GET /api/exportaciones/reportes/reprobados-nominal/xlsx/`
- `GET /api/exportaciones/reportes/cuadro-aprovechamiento/xlsx/`

Cada descarga devuelve:

- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment`
- `X-Registro-Exportacion-Id`

## Catálogo actualizado

Se agregaron o marcaron como implementados en XLSX:

- `REPORTE_DESEMPENO`
- `REPORTE_APROBADOS_REPROBADOS`
- `REPORTE_PROMEDIOS_ACADEMICOS`
- `REPORTE_DISTRIBUCION_CALIFICACIONES`
- `REPORTE_EXENTOS`
- `REPORTE_DESEMPENO_DOCENTE`
- `REPORTE_DESEMPENO_COHORTE`
- `REPORTE_REPROBADOS_NOMINAL`
- `CUADRO_APROVECHAMIENTO`

PDF queda pendiente para estos reportes.

## Métricas

Se calculan, según reporte:

- Total evaluados.
- Aprobados.
- Reprobados.
- Porcentaje de aprobación.
- Porcentaje de reprobación.
- Promedio.
- Máxima.
- Mínima.
- Moda.
- Desviación estándar poblacional.
- Distribución por rangos.
- Total de exentos del examen final.

## Rangos de distribución

- `0.0 - 5.9`
- `6.0 - 6.9`
- `7.0 - 7.9`
- `8.0 - 8.9`
- `9.0 - 9.5`
- `9.6 - 10.0`

## Rangos de aprovechamiento

- Excelente aprovechamiento: `9.51` a `10.00`.
- Alto aprovechamiento académico: `9.01` a `9.50`.
- Buen aprovechamiento académico: `8.00` a `9.00`.

Por defecto, el cuadro excluye discentes con materias reprobadas. Puede incluirlos con el filtro `incluir_con_reprobadas=true`.

## Filtros soportados

- `periodo`
- `carrera`
- `grupo`
- `asignatura`
- `programa`
- `docente`
- `antiguedad`
- `generacion`
- `anio_formacion`
- `semestre`
- `fecha_desde`
- `fecha_hasta`
- `incluir_no_numericas`
- `incluir_extraordinarios`
- `incluir_con_reprobadas`
- `rango_aprovechamiento`

Los filtros vacíos se ignoran. Los filtros guardados en auditoría se sanitizan mediante el servicio común de exportaciones.

## Permisos

- Admin/superusuario puede consultar y exportar todos los reportes.
- Estadística puede consultar y exportar todos los reportes.
- Jefatura académica y jefatura pedagógica pueden consultar reportes institucionales autorizados.
- Jefatura de carrera puede consultar reportes filtrados a su ámbito/carrera.
- Docente no accede a reportes globales de desempeño en este bloque.
- Discente no accede a reportes de desempeño ni cuadro de aprovechamiento.

El backend sigue siendo la autoridad real de permisos.

## Privacidad

- No se muestra matrícula militar por defecto.
- Los reportes agregados no muestran nombres de discentes.
- `Reprobados nominal`, `Exentos` y `Cuadro de aprovechamiento` son nominales y quedan restringidos a perfiles institucionales autorizados.
- No se guarda el payload completo del reporte en `RegistroExportacion`.
- No se guardan listas completas de discentes en `parametros_json`.

## Auditoría

Cada exportación registra:

- usuario;
- tipo documental;
- formato `XLSX`;
- nombre de documento;
- nombre de archivo seguro;
- filtros sanitizados;
- rol/cargo de contexto;
- IP y user agent cuando están disponibles;
- estado `GENERADA` o `FALLIDA`;
- tamaño en bytes;
- hash SHA-256;
- fechas de creación y finalización.

## Limitaciones

- No se implementó PDF del cuadro de aprovechamiento.
- No se implementaron gráficas.
- No se implementó integración visual Next.js completa.
- No se implementó reporte de situación académica.
- No se implementó historial académico exportable.
- No se implementó kárdex Excel.
- No se implementó importación Excel.

## Pendientes para 10C-3B

- Crear páginas del portal para reportes de desempeño.
- Agregar filtros visuales.
- Mostrar vista previa JSON.
- Descargar XLSX desde el portal.
- Mostrar folio técnico de exportación.
- Mantener PDF del cuadro como pendiente o integrarlo cuando exista.

## Pendientes para 9I-M-E

- Reportes de situación académica.
- Movimientos académicos.
- Historial académico exportable.
- Bitácora transversal completa.
- Importación desde Excel y reporte de errores, si se autoriza en un bloque posterior.

## Validaciones ejecutadas

- `docker compose exec -T backend python manage.py makemigrations reportes`: OK, migración `0003`.
- `docker compose exec -T backend python manage.py migrate`: OK.
- `docker compose exec -T backend python manage.py check`: OK.
- `docker compose exec -T backend python manage.py makemigrations --check`: OK, sin cambios pendientes.
- `docker compose exec -T backend python manage.py test reportes`: OK, 65 tests.
- `docker compose exec -T backend python manage.py test evaluacion`: OK, 72 tests.
- `docker compose exec -T backend python manage.py test trayectoria`: OK, 25 tests.
- `docker compose exec -T backend python manage.py test`: OK, 365 tests.

Nota: `evaluacion` se volvió a ejecutar de forma secuencial porque una primera corrida en paralelo chocó con la creación de la misma base de pruebas; no fue un fallo del código.
