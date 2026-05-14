# Bloque 9I-M-E - Reportes de situación académica, movimientos e historial interno

## Objetivo

Implementar reportes institucionales XLSX para seguimiento de trayectoria académica, extraordinarios, eventos de situación, movimientos académicos e historial interno exportable.

El bloque es backend/API. No modifica actas, calificaciones, inscripciones, kárdex, historial persistente ni movimientos académicos. Cada exportación queda auditada mediante `RegistroExportacion`.

## Alcance implementado

Se agregaron vistas previas JSON y descargas XLSX para:

- Extraordinarios registrados.
- Situación académica actual.
- Bajas temporales.
- Bajas definitivas.
- Reingresos.
- Egresables / egresados.
- Situación académica agregada.
- Movimientos académicos.
- Cambios de grupo.
- Historial académico interno institucional.
- Historial académico interno por discente.

No se implementaron PDF, kárdex Excel, importación Excel, gráficas ni pantallas Next.js completas.

## Archivos modificados

- `backend/reportes/models.py`
- `backend/reportes/migrations/0004_alter_registroexportacion_tipo_documento.py`
- `backend/reportes/catalogo.py`
- `backend/reportes/services.py`
- `backend/reportes/api_views.py`
- `backend/reportes/api_urls.py`
- `backend/reportes/reportes_trayectoria.py`
- `backend/reportes/tests.py`
- `README.md`
- `docs/resumen_bloque9i_m_e_reportes_situacion_historial.md`

## Servicios creados

### `ServicioReportesTrayectoria`

Ubicación: `backend/reportes/reportes_trayectoria.py`.

Responsabilidades:

- Validar autenticación y permisos por tipo documental.
- Bloquear discentes y docentes para estos reportes institucionales.
- Aplicar filtros seguros.
- Filtrar jefatura de carrera por ámbito cuando existe carrera asociada.
- Construir datasets de situación académica.
- Construir datasets de movimientos académicos.
- Construir historial interno institucional y por discente.
- Generar XLSX mediante el exportador tabular común.
- Registrar exportaciones como `GENERADA` o `FALLIDA`.
- Calcular tamaño y hash SHA-256.

## Catálogo actualizado

Se agregaron o marcaron como implementados en XLSX:

- `REPORTE_SITUACION_ACADEMICA`
- `REPORTE_EXTRAORDINARIOS`
- `REPORTE_BAJAS_TEMPORALES`
- `REPORTE_BAJAS_DEFINITIVAS`
- `REPORTE_REINGRESOS`
- `REPORTE_EGRESADOS_EGRESABLES`
- `REPORTE_SITUACION_ACADEMICA_AGREGADO`
- `REPORTE_MOVIMIENTOS_ACADEMICOS`
- `REPORTE_CAMBIOS_GRUPO`
- `HISTORIAL_ACADEMICO`
- `REPORTE_HISTORIAL_ACADEMICO_INTERNO`

PDF queda pendiente para estos reportes.

## Endpoints JSON

- `GET /api/reportes/situacion/extraordinarios/`
- `GET /api/reportes/situacion/actual/`
- `GET /api/reportes/situacion/bajas-temporales/`
- `GET /api/reportes/situacion/bajas-definitivas/`
- `GET /api/reportes/situacion/reingresos/`
- `GET /api/reportes/situacion/egresables/`
- `GET /api/reportes/situacion/agregado/`
- `GET /api/reportes/movimientos/`
- `GET /api/reportes/movimientos/cambios-grupo/`
- `GET /api/reportes/historial-interno/`
- `GET /api/reportes/historial-interno/<discente_id>/`

Respuesta base:

```json
{
  "ok": true,
  "slug": "situacion-actual",
  "nombre": "Reporte de situacion academica actual",
  "total": 10,
  "filtros": {},
  "columnas": [],
  "items": [],
  "resumen": {},
  "sheets": []
}
```

## Endpoints XLSX

- `GET /api/exportaciones/reportes/extraordinarios/xlsx/`
- `GET /api/exportaciones/reportes/situacion-actual/xlsx/`
- `GET /api/exportaciones/reportes/bajas-temporales/xlsx/`
- `GET /api/exportaciones/reportes/bajas-definitivas/xlsx/`
- `GET /api/exportaciones/reportes/reingresos/xlsx/`
- `GET /api/exportaciones/reportes/egresables/xlsx/`
- `GET /api/exportaciones/reportes/situacion-agregado/xlsx/`
- `GET /api/exportaciones/reportes/movimientos-academicos/xlsx/`
- `GET /api/exportaciones/reportes/cambios-grupo/xlsx/`
- `GET /api/exportaciones/reportes/historial-interno/xlsx/`
- `GET /api/exportaciones/reportes/historial-interno/<discente_id>/xlsx/`

Cada descarga devuelve:

- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment`
- `X-Registro-Exportacion-Id`

## Filtros soportados

- `periodo`
- `carrera`
- `grupo`
- `plan`
- `antiguedad`
- `generacion`
- `anio_formacion`
- `semestre`
- `asignatura`
- `docente`
- `discente`
- `situacion`
- `tipo_movimiento`
- `grupo_origen`
- `grupo_destino`
- `aprobado`
- `baja_abierta`
- `fecha_desde`
- `fecha_hasta`
- `incluir_extraordinarios`
- `incluir_eventos`
- `incluir_movimientos`

Los filtros vacíos se ignoran. En auditoría solo se guardan filtros reconocidos y sanitizados.

## Reglas de permisos

- Admin/superusuario puede consultar y exportar todo.
- Estadística puede consultar y exportar todo.
- Jefatura académica puede consultar reportes institucionales autorizados.
- Jefatura pedagógica puede consultar reportes institucionales autorizados.
- Jefatura de carrera queda filtrada a su carrera/ámbito cuando el sistema puede inferirlo.
- Docente no accede a reportes globales de situación, movimientos ni historial interno.
- Discente no accede a reportes institucionales ni exporta historial interno XLSX.

El frontend puede ocultar opciones, pero el backend mantiene la decisión real.

## Reglas de privacidad

- No se muestra matrícula militar por defecto.
- Los reportes agregados no muestran nombres.
- Los reportes nominales muestran grado/empleo y nombre solo para perfiles autorizados.
- El historial interno es sensible y no se expone a discentes como exportación XLSX.
- No se guarda el payload completo del reporte en `RegistroExportacion`.
- No se guardan listados completos de discentes en `parametros_json`.

## Reglas de historial interno

- El historial interno no es kárdex oficial.
- Conserva evidencia ordinaria aunque exista extraordinario aprobado.
- Se separan resultados, extraordinarios, eventos y movimientos en hojas XLSX.
- El historial por discente usa nombre de archivo seguro con ID interno, sin nombre completo ni matrícula.

## Reglas de extraordinarios

- El reporte de extraordinarios muestra calificación ordinaria previa cuando existe.
- Si el extraordinario está aprobado, se muestra marca `EE`.
- Si está reprobado, se reporta como evidencia sin modificar resultado persistido.
- Las exportaciones no crean ni modifican extraordinarios.

## Reglas de bajas y reingresos

- Las bajas temporales se reportan desde `EventoSituacionAcademica`.
- Se identifica baja abierta cuando no existe fecha de fin.
- El reingreso se vincula con baja temporal previa cuando hay evidencia disponible.
- No se crean, cierran ni alteran eventos al exportar.

## Reglas de movimientos académicos

- Los reportes solo muestran evidencia registrada.
- Cambios de grupo se reportan como subtipo específico.
- No se aplican movimientos, no se recalculan inscripciones y no se modifican adscripciones.
- Si no existe evidencia de intentos fallidos, no se inventa bloqueo por actas vivas.

## Auditoría

Cada exportación registra:

- usuario;
- tipo documental;
- formato `XLSX`;
- nombre de documento;
- nombre de archivo seguro;
- objeto cuando aplica, por ejemplo `discente_id`;
- filtros sanitizados;
- rol/cargo de contexto;
- IP y user agent cuando están disponibles;
- estado `GENERADA` o `FALLIDA`;
- tamaño en bytes;
- hash SHA-256;
- fecha de creación y finalización;
- mensaje de error si falla.

## Validaciones ejecutadas

- `docker compose exec -T backend python manage.py check`: OK.
- `docker compose exec -T backend python manage.py makemigrations`: OK, sin cambios pendientes después de crear `0004`.
- `docker compose exec -T backend python manage.py migrate`: OK, aplicada `reportes.0004_alter_registroexportacion_tipo_documento`.
- `docker compose exec -T backend python manage.py makemigrations --check`: OK, sin cambios pendientes.
- `docker compose exec -T backend python manage.py test reportes`: OK, 74 tests.
- `docker compose exec -T backend python manage.py test trayectoria`: OK, 25 tests.
- `docker compose exec -T backend python manage.py test relaciones`: OK, 37 tests.
- `docker compose exec -T backend python manage.py test`: OK, 374 tests.

No se ejecutó lint/build frontend porque este bloque no modificó archivos Next.js.

## Limitaciones

- No hay integración visual completa en portal; queda para Bloque 10C-3C.
- No hay PDF de reportes de situación, movimientos ni historial interno.
- No hay kárdex Excel.
- No hay importación Excel ni reporte de errores de importación.
- No hay bitácora transversal completa.
- No hay gráficas ni dashboard BI.

## Pendientes para 10C-3C

- Crear vistas del portal para situación académica, movimientos e historial interno.
- Consumir endpoints JSON.
- Aplicar filtros visuales.
- Descargar XLSX auditados desde el portal.
- Mostrar folio técnico `X-Registro-Exportacion-Id`.
- Mantener restricciones visuales para discentes y docentes.

## Pendientes futuros

- Bitácora transversal completa de eventos críticos.
- Importación Excel y reporte de errores, si se autoriza.
- Reportes PDF institucionales solo si se aprueban plantillas.
