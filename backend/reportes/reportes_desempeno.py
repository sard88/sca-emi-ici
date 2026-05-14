import hashlib
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from statistics import StatisticsError, mode

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from core.portal_services import portal_context
from evaluacion.models import Acta, CalificacionComponente, ComponenteEvaluacion, DetalleActa
from relaciones.models import InscripcionMateria
from trayectoria.models import CatalogoResultadoAcademico

from .exportadores.reportes_excel import ReporteSheet, XLSX_MIME, generar_reporte_xlsx
from .models import RegistroExportacion
from .services import ServicioExportacion, ServicioPermisosExportacion, construir_nombre_archivo


APROBATORIA = Decimal("6.0")
RANGOS_DISTRIBUCION = (
    ("0.0 - 5.9", Decimal("0.0"), Decimal("5.9")),
    ("6.0 - 6.9", Decimal("6.0"), Decimal("6.9")),
    ("7.0 - 7.9", Decimal("7.0"), Decimal("7.9")),
    ("8.0 - 8.9", Decimal("8.0"), Decimal("8.9")),
    ("9.0 - 9.5", Decimal("9.0"), Decimal("9.5")),
    ("9.6 - 10.0", Decimal("9.6"), Decimal("10.0")),
)
RANGOS_APROVECHAMIENTO = (
    ("Excelente aprovechamiento", Decimal("9.51"), Decimal("10.00")),
    ("Alto aprovechamiento academico", Decimal("9.01"), Decimal("9.50")),
    ("Buen aprovechamiento academico", Decimal("8.00"), Decimal("9.00")),
)


@dataclass(frozen=True)
class ReporteDesempenoConfig:
    slug: str
    tipo_documento: str
    nombre: str


@dataclass(frozen=True)
class ReporteDesempenoData:
    slug: str
    nombre: str
    columnas: list[dict]
    filas: list[dict]
    filtros: dict
    sheets: list[ReporteSheet]
    resumen: dict


@dataclass(frozen=True)
class ArchivoReporteDesempeno:
    contenido: bytes
    nombre_archivo: str
    content_type: str
    registro: RegistroExportacion


REPORTES_DESEMPENO = {
    "aprobados-reprobados": ReporteDesempenoConfig(
        "aprobados-reprobados",
        RegistroExportacion.TIPO_REPORTE_APROBADOS_REPROBADOS,
        "Reporte de aprobados y reprobados",
    ),
    "promedios": ReporteDesempenoConfig(
        "promedios",
        RegistroExportacion.TIPO_REPORTE_PROMEDIOS_ACADEMICOS,
        "Reporte de promedios academicos",
    ),
    "distribucion": ReporteDesempenoConfig(
        "distribucion",
        RegistroExportacion.TIPO_REPORTE_DISTRIBUCION_CALIFICACIONES,
        "Reporte de distribucion de calificaciones",
    ),
    "exentos": ReporteDesempenoConfig(
        "exentos",
        RegistroExportacion.TIPO_REPORTE_EXENTOS,
        "Reporte de exentos por asignatura",
    ),
    "docentes": ReporteDesempenoConfig(
        "docentes",
        RegistroExportacion.TIPO_REPORTE_DESEMPENO_DOCENTE,
        "Reporte de desempeno por docente",
    ),
    "cohorte": ReporteDesempenoConfig(
        "cohorte",
        RegistroExportacion.TIPO_REPORTE_DESEMPENO_COHORTE,
        "Reporte de desempeno por carrera y antiguedad",
    ),
    "reprobados-nominal": ReporteDesempenoConfig(
        "reprobados-nominal",
        RegistroExportacion.TIPO_REPORTE_REPROBADOS_NOMINAL,
        "Reporte nominal de reprobados",
    ),
    "cuadro-aprovechamiento": ReporteDesempenoConfig(
        "cuadro-aprovechamiento",
        RegistroExportacion.TIPO_CUADRO_APROVECHAMIENTO,
        "Cuadro de aprovechamiento academico",
    ),
}


AGREGADO_COLUMNS = [
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "anio_formacion", "label": "Anio de formacion"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "semestre", "label": "Semestre"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "docente", "label": "Docente"},
    {"key": "total_evaluados", "label": "Total evaluados"},
    {"key": "aprobados", "label": "Aprobados"},
    {"key": "reprobados", "label": "Reprobados"},
    {"key": "porcentaje_aprobados", "label": "% aprobados"},
    {"key": "porcentaje_reprobados", "label": "% reprobados"},
    {"key": "promedio", "label": "Promedio"},
    {"key": "maxima", "label": "Maxima"},
    {"key": "minima", "label": "Minima"},
    {"key": "moda", "label": "Moda"},
    {"key": "desviacion_estandar", "label": "Desviacion estandar"},
]

PROMEDIOS_COLUMNS = [
    {"key": "dimension", "label": "Dimension"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "anio_formacion", "label": "Anio de formacion"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "semestre", "label": "Semestre"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "docente", "label": "Docente"},
    {"key": "total_evaluados", "label": "Total evaluados"},
    {"key": "promedio", "label": "Promedio"},
    {"key": "maxima", "label": "Maxima"},
    {"key": "minima", "label": "Minima"},
    {"key": "moda", "label": "Moda"},
    {"key": "desviacion_estandar", "label": "Desviacion estandar"},
]

DISTRIBUCION_COLUMNS = [
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "docente", "label": "Docente"},
    {"key": "rango", "label": "Rango"},
    {"key": "total_discentes", "label": "Total discentes"},
    {"key": "porcentaje", "label": "Porcentaje"},
]

EXENTOS_COLUMNS = [
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "docente", "label": "Docente"},
    {"key": "corte", "label": "Corte"},
    {"key": "grado_discente", "label": "Grado/empleo del discente"},
    {"key": "nombre_discente", "label": "Nombre del discente"},
    {"key": "promedio_parciales", "label": "Promedio de parciales"},
    {"key": "componente_exento", "label": "Componente exento"},
    {"key": "valor_aplicado", "label": "Valor aplicado"},
    {"key": "resultado_final", "label": "Resultado final"},
    {"key": "estado_acta", "label": "Estado del acta"},
    {"key": "formalizada_en", "label": "Fecha de formalizacion"},
]

DOCENTE_COLUMNS = [
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "docente", "label": "Docente"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "total_evaluados", "label": "Total evaluados"},
    {"key": "aprobados", "label": "Aprobados"},
    {"key": "reprobados", "label": "Reprobados"},
    {"key": "exentos", "label": "Exentos"},
    {"key": "promedio", "label": "Promedio"},
    {"key": "maxima", "label": "Maxima"},
    {"key": "minima", "label": "Minima"},
    {"key": "moda", "label": "Moda"},
    {"key": "desviacion_estandar", "label": "Desviacion estandar"},
    {"key": "actas_formalizadas", "label": "Actas formalizadas"},
    {"key": "actas_pendientes", "label": "Actas pendientes"},
]

COHORTE_COLUMNS = [
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "anio_formacion", "label": "Anio de formacion"},
    {"key": "semestre", "label": "Semestre"},
    {"key": "total_evaluados", "label": "Total evaluados"},
    {"key": "aprobados", "label": "Aprobados"},
    {"key": "reprobados", "label": "Reprobados"},
    {"key": "exentos", "label": "Exentos"},
    {"key": "promedio", "label": "Promedio"},
    {"key": "maxima", "label": "Maxima"},
    {"key": "minima", "label": "Minima"},
    {"key": "dist_0_5_9", "label": "Distribucion 0-5.9"},
    {"key": "dist_6_6_9", "label": "Distribucion 6-6.9"},
    {"key": "dist_7_7_9", "label": "Distribucion 7-7.9"},
    {"key": "dist_8_8_9", "label": "Distribucion 8-8.9"},
    {"key": "dist_9_10", "label": "Distribucion 9-10"},
]

REPROBADOS_COLUMNS = [
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "docente", "label": "Docente"},
    {"key": "grado", "label": "Grado/empleo"},
    {"key": "nombre_discente", "label": "Nombre del discente"},
    {"key": "calificacion_ordinaria", "label": "Calificacion ordinaria"},
    {"key": "resultado_oficial", "label": "Resultado oficial"},
    {"key": "extraordinario_pendiente", "label": "Extraordinario pendiente"},
    {"key": "extraordinario_aprobado", "label": "Extraordinario aprobado"},
    {"key": "marca", "label": "Marca EE"},
    {"key": "situacion_academica", "label": "Situacion academica actual"},
    {"key": "acta_final", "label": "Acta FINAL"},
    {"key": "formalizada_en", "label": "Fecha de formalizacion"},
]

CUADRO_COLUMNS = [
    {"key": "rango_aprovechamiento", "label": "Rango de aprovechamiento"},
    {"key": "lugar", "label": "Lugar"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "anio_formacion", "label": "Anio de formacion"},
    {"key": "grado", "label": "Grado/empleo"},
    {"key": "nombre_discente", "label": "Nombre del discente"},
    {"key": "promedio", "label": "Promedio"},
    {"key": "total_materias", "label": "Total materias consideradas"},
    {"key": "observaciones", "label": "Observaciones"},
]


class ServicioReportesDesempeno:
    def __init__(self, user, request=None):
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Autenticacion requerida.")
        self.user = user
        self.request = request
        self.ctx = portal_context(user)
        self.permisos = ServicioPermisosExportacion(user)
        self.servicio_exportacion = ServicioExportacion(user, request=request)

    def vista_previa(self, slug: str, params) -> ReporteDesempenoData:
        config = self._config(slug)
        self._validar_permiso(config.tipo_documento)
        filtros = self._filtros(params)
        sheets = self._build_sheets(slug, filtros)
        filas = [row for sheet in sheets for row in sheet.filas if not _is_summary_sheet(sheet)]
        columnas = sheets[0].columnas if sheets else []
        return ReporteDesempenoData(
            slug=slug,
            nombre=config.nombre,
            columnas=columnas,
            filas=filas,
            filtros=filtros,
            sheets=sheets,
            resumen=self._resumen_general(filas),
        )

    def exportar_xlsx(self, slug: str, params) -> ArchivoReporteDesempeno:
        config = self._config(slug)
        self._validar_permiso(config.tipo_documento)
        filtros = self._filtros(params)
        nombre_archivo = construir_nombre_archivo(
            config.tipo_documento,
            RegistroExportacion.FORMATO_XLSX,
            objeto_repr=self._objeto_repr_filtros(filtros),
        )
        registro = self.servicio_exportacion.registrar_solicitud(
            tipo_documento=config.tipo_documento,
            formato=RegistroExportacion.FORMATO_XLSX,
            nombre_documento=config.nombre,
            nombre_archivo=nombre_archivo,
            filtros=filtros,
            parametros={"slug": slug},
        )
        try:
            data = self.vista_previa(slug, params)
            contenido = generar_reporte_xlsx(titulo=config.nombre, filtros=filtros, sheets=data.sheets)
        except Exception as exc:
            self.servicio_exportacion.marcar_fallida(registro, exc)
            raise
        self.servicio_exportacion.marcar_generada(
            registro,
            tamano_bytes=len(contenido),
            hash_archivo=hashlib.sha256(contenido).hexdigest(),
        )
        return ArchivoReporteDesempeno(
            contenido=contenido,
            nombre_archivo=nombre_archivo,
            content_type=XLSX_MIME,
            registro=registro,
        )

    def _config(self, slug):
        if slug not in REPORTES_DESEMPENO:
            raise PermissionDenied("Reporte no reconocido.")
        return REPORTES_DESEMPENO[slug]

    def _validar_permiso(self, tipo_documento):
        if not self.permisos.puede_ver_tipo(tipo_documento):
            raise PermissionDenied("No tienes permiso para consultar este reporte.")

    def _filtros(self, params):
        keys = (
            "periodo",
            "carrera",
            "grupo",
            "asignatura",
            "programa",
            "docente",
            "antiguedad",
            "generacion",
            "anio_formacion",
            "semestre",
            "fecha_desde",
            "fecha_hasta",
            "incluir_no_numericas",
            "incluir_extraordinarios",
            "incluir_con_reprobadas",
            "rango_aprovechamiento",
        )
        return {key: str(params.get(key, "")).strip() for key in keys if str(params.get(key, "")).strip()}

    def _build_sheets(self, slug, filtros):
        records = self._official_records(filtros)
        if slug == "aprobados-reprobados":
            rows = self._agregado_rows(records, self._key_asignatura)
            return [ReporteSheet("Resumen", AGREGADO_COLUMNS, rows)]
        if slug == "promedios":
            return self._promedios_sheets(records)
        if slug == "distribucion":
            rows = self._distribucion_rows(records)
            return [ReporteSheet("Distribucion", DISTRIBUCION_COLUMNS, rows)]
        if slug == "exentos":
            rows = self._exentos_rows(filtros)
            return [
                ReporteSheet("Exentos", EXENTOS_COLUMNS, rows),
                self._summary_sheet("Resumen por asignatura", rows, "asignatura"),
            ]
        if slug == "docentes":
            rows = self._docente_rows(records)
            return [ReporteSheet("Resumen docente", DOCENTE_COLUMNS, rows)]
        if slug == "cohorte":
            rows = self._cohorte_rows(records)
            return [ReporteSheet("Carrera antiguedad", COHORTE_COLUMNS, rows)]
        if slug == "reprobados-nominal":
            rows = self._reprobados_rows(records)
            return [ReporteSheet("Reprobados", REPROBADOS_COLUMNS, rows)]
        if slug == "cuadro-aprovechamiento":
            rows = self._cuadro_aprovechamiento_rows(records, filtros)
            return [
                ReporteSheet("Cuadro", CUADRO_COLUMNS, rows),
                self._summary_sheet("Resumen por rango", rows, "rango_aprovechamiento"),
            ]
        return []

    def _official_queryset(self, filtros):
        qs = (
            InscripcionMateria.objects.select_related(
                "discente__usuario__grado_empleo",
                "discente__plan_estudios__carrera",
                "discente__antiguedad",
                "asignacion_docente__usuario_docente",
                "asignacion_docente__grupo_academico__periodo",
                "asignacion_docente__programa_asignatura__materia",
                "asignacion_docente__programa_asignatura__plan_estudios__carrera",
            )
            .filter(
                calificacion_final__isnull=False,
                detalles_acta__acta__corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
                detalles_acta__acta__estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            )
            .distinct()
        )
        if self.ctx.is_discente or self.ctx.is_docente:
            return qs.none()
        if self.ctx.is_jefatura_carrera and not self.ctx.has_consulta_amplia:
            if not self.ctx.carrera_ids:
                return qs.none()
            qs = qs.filter(asignacion_docente__programa_asignatura__plan_estudios__carrera_id__in=self.ctx.carrera_ids)
        qs = self._apply_common_filters(qs, filtros)
        return qs.order_by(
            "asignacion_docente__grupo_academico__periodo__clave",
            "asignacion_docente__programa_asignatura__plan_estudios__carrera__clave",
            "asignacion_docente__grupo_academico__clave_grupo",
            "asignacion_docente__programa_asignatura__materia__clave",
            "discente__matricula",
        )

    def _apply_common_filters(self, qs, filtros):
        if filtros.get("periodo"):
            value = filtros["periodo"]
            qs = qs.filter(Q(asignacion_docente__grupo_academico__periodo__clave__iexact=value) | Q(asignacion_docente__grupo_academico__periodo_id=_int_or_none(value)))
        if filtros.get("carrera"):
            value = filtros["carrera"]
            qs = qs.filter(Q(asignacion_docente__programa_asignatura__plan_estudios__carrera__clave__iexact=value) | Q(asignacion_docente__programa_asignatura__plan_estudios__carrera_id=_int_or_none(value)))
        if filtros.get("grupo"):
            value = filtros["grupo"]
            qs = qs.filter(Q(asignacion_docente__grupo_academico__clave_grupo__icontains=value) | Q(asignacion_docente__grupo_academico_id=_int_or_none(value)))
        if filtros.get("asignatura") or filtros.get("programa"):
            value = filtros.get("asignatura") or filtros.get("programa")
            qs = qs.filter(Q(asignacion_docente__programa_asignatura__materia__nombre__icontains=value) | Q(asignacion_docente__programa_asignatura__materia__clave__icontains=value) | Q(asignacion_docente__programa_asignatura_id=_int_or_none(value)))
        if filtros.get("docente"):
            value = filtros["docente"]
            qs = qs.filter(Q(asignacion_docente__usuario_docente__nombre_completo__icontains=value) | Q(asignacion_docente__usuario_docente__username__icontains=value) | Q(asignacion_docente__usuario_docente_id=_int_or_none(value)))
        if filtros.get("antiguedad") or filtros.get("generacion"):
            value = filtros.get("antiguedad") or filtros.get("generacion")
            qs = qs.filter(Q(discente__antiguedad__clave__icontains=value) | Q(discente__antiguedad_id=_int_or_none(value)))
        if filtros.get("anio_formacion"):
            qs = qs.filter(asignacion_docente__programa_asignatura__anio_formacion=_int_or_none(filtros["anio_formacion"]))
        if filtros.get("semestre"):
            qs = qs.filter(asignacion_docente__grupo_academico__semestre_numero=_int_or_none(filtros["semestre"]))
        desde = parse_date(filtros.get("fecha_desde") or "")
        hasta = parse_date(filtros.get("fecha_hasta") or "")
        if desde:
            qs = qs.filter(cerrado_en__date__gte=desde)
        if hasta:
            qs = qs.filter(cerrado_en__date__lte=hasta)
        return qs

    def _official_records(self, filtros):
        return [self._record(inscripcion) for inscripcion in self._official_queryset(filtros)]

    def _record(self, inscripcion):
        asignacion = inscripcion.asignacion_docente
        grupo = asignacion.grupo_academico
        programa = asignacion.programa_asignatura
        materia = programa.materia
        carrera = programa.plan_estudios.carrera
        discente = inscripcion.discente
        final_acta = self._final_acta(inscripcion)
        extraordinario = getattr(inscripcion, "extraordinario", None)
        calificacion = Decimal(inscripcion.calificacion_final).quantize(Decimal("0.01"))
        return {
            "inscripcion_id": inscripcion.id,
            "periodo": grupo.periodo.clave,
            "carrera": carrera.clave,
            "carrera_nombre": carrera.nombre,
            "grupo": grupo.clave_grupo,
            "antiguedad": discente.antiguedad.clave,
            "anio_formacion": programa.anio_formacion,
            "semestre": grupo.semestre_numero,
            "asignatura": materia.nombre,
            "asignatura_clave": materia.clave,
            "docente": asignacion.usuario_docente.nombre_visible,
            "docente_id": asignacion.usuario_docente_id,
            "discente_id": discente.id,
            "grado": _grado(discente.usuario),
            "nombre_discente": discente.usuario.nombre_visible,
            "situacion_academica": discente.get_situacion_actual_display(),
            "calificacion": calificacion,
            "calificacion_ordinaria": getattr(extraordinario, "calificacion_ordinaria", None) or calificacion,
            "resultado_oficial": inscripcion.codigo_resultado_oficial or _resultado_por_calificacion(calificacion),
            "marca": inscripcion.codigo_marca or "",
            "extraordinario_aprobado": bool(extraordinario and extraordinario.aprobado),
            "extraordinario_pendiente": calificacion < APROBATORIA and not (extraordinario and extraordinario.aprobado),
            "final_acta_id": final_acta.id if final_acta else "",
            "formalizada_en": _dt(final_acta.formalizada_en if final_acta else None),
            "asignacion_id": asignacion.id,
        }

    def _final_acta(self, inscripcion):
        detalle = (
            DetalleActa.objects.select_related("acta")
            .filter(
                inscripcion_materia=inscripcion,
                acta__corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
                acta__estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            )
            .order_by("-acta__formalizada_en", "-acta_id")
            .first()
        )
        return detalle.acta if detalle else None

    def _agregado_rows(self, records, key_func):
        grouped = {}
        for record in records:
            grouped.setdefault(key_func(record), []).append(record)
        rows = []
        for key in sorted(grouped):
            values = grouped[key]
            sample = values[0]
            stats = _metricas([item["calificacion"] for item in values])
            rows.append(
                {
                    "periodo": sample.get("periodo", ""),
                    "carrera": sample.get("carrera", ""),
                    "antiguedad": sample.get("antiguedad", ""),
                    "anio_formacion": sample.get("anio_formacion", ""),
                    "grupo": sample.get("grupo", ""),
                    "semestre": sample.get("semestre", ""),
                    "asignatura": sample.get("asignatura", ""),
                    "docente": sample.get("docente", ""),
                    **stats,
                }
            )
        return rows

    def _promedios_sheets(self, records):
        return [
            ReporteSheet("Por grupo", PROMEDIOS_COLUMNS, self._promedio_dimension_rows(records, "Grupo", lambda r: (r["periodo"], r["carrera"], r["grupo"]))),
            ReporteSheet("Por asignatura", PROMEDIOS_COLUMNS, self._promedio_dimension_rows(records, "Asignatura", self._key_asignatura)),
            ReporteSheet("Por docente", PROMEDIOS_COLUMNS, self._promedio_dimension_rows(records, "Docente", lambda r: (r["periodo"], r["carrera"], r["docente"]))),
            ReporteSheet("Por carrera anio", PROMEDIOS_COLUMNS, self._promedio_dimension_rows(records, "Carrera/anio", lambda r: (r["periodo"], r["carrera"], r["antiguedad"], r["anio_formacion"]))),
        ]

    def _promedio_dimension_rows(self, records, dimension, key_func):
        rows = self._agregado_rows(records, key_func)
        return [{"dimension": dimension, **row} for row in rows]

    def _distribucion_rows(self, records):
        grouped = {}
        for record in records:
            grouped.setdefault(self._key_asignatura(record), []).append(record)
        rows = []
        for values in grouped.values():
            sample = values[0]
            total = len(values)
            for label, minimum, maximum in RANGOS_DISTRIBUCION:
                count = sum(1 for item in values if minimum <= item["calificacion"] <= maximum)
                rows.append(
                    {
                        "periodo": sample["periodo"],
                        "carrera": sample["carrera"],
                        "grupo": sample["grupo"],
                        "asignatura": sample["asignatura"],
                        "docente": sample["docente"],
                        "rango": label,
                        "total_discentes": count,
                        "porcentaje": _percent(count, total),
                    }
                )
        return rows

    def _exentos_rows(self, filtros):
        actas = self._final_actas_queryset(filtros).values_list("id", flat=True)
        qs = CalificacionComponente.objects.select_related(
            "detalle__acta__asignacion_docente__usuario_docente",
            "detalle__acta__asignacion_docente__grupo_academico__periodo",
            "detalle__acta__asignacion_docente__programa_asignatura__materia",
            "detalle__acta__asignacion_docente__programa_asignatura__plan_estudios__carrera",
            "detalle__inscripcion_materia__discente__usuario__grado_empleo",
        ).filter(
            detalle__acta_id__in=actas,
            componente_es_examen_snapshot=True,
            sustituido_por_exencion=True,
        )
        rows = []
        for componente in qs.order_by("detalle__acta_id", "detalle__inscripcion_materia__discente__matricula"):
            detalle = componente.detalle
            acta = detalle.acta
            asignacion = acta.asignacion_docente
            grupo = asignacion.grupo_academico
            programa = asignacion.programa_asignatura
            discente = detalle.inscripcion_materia.discente
            rows.append(
                {
                    "periodo": grupo.periodo.clave,
                    "carrera": programa.plan_estudios.carrera.clave,
                    "grupo": grupo.clave_grupo,
                    "asignatura": programa.materia.nombre,
                    "docente": asignacion.usuario_docente.nombre_visible,
                    "corte": acta.get_corte_codigo_display(),
                    "grado_discente": _grado(discente.usuario),
                    "nombre_discente": discente.usuario.nombre_visible,
                    "promedio_parciales": _fmt_decimal(detalle.promedio_parciales_visible or detalle.promedio_parciales),
                    "componente_exento": componente.componente_nombre_snapshot,
                    "valor_aplicado": _fmt_decimal(componente.valor_calculado),
                    "resultado_final": _fmt_decimal(detalle.resultado_final_preliminar_visible or detalle.resultado_corte_visible),
                    "estado_acta": acta.get_estado_acta_display(),
                    "formalizada_en": _dt(acta.formalizada_en),
                }
            )
        return rows

    def _final_actas_queryset(self, filtros):
        qs = Acta.objects.select_related(
            "asignacion_docente__usuario_docente",
            "asignacion_docente__grupo_academico__periodo",
            "asignacion_docente__programa_asignatura__materia",
            "asignacion_docente__programa_asignatura__plan_estudios__carrera",
        ).filter(corte_codigo=ComponenteEvaluacion.CORTE_FINAL, estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA)
        if self.ctx.is_jefatura_carrera and not self.ctx.has_consulta_amplia:
            if not self.ctx.carrera_ids:
                return qs.none()
            qs = qs.filter(asignacion_docente__programa_asignatura__plan_estudios__carrera_id__in=self.ctx.carrera_ids)
        dummy_qs = InscripcionMateria.objects.filter(id__in=[])
        inscripciones = self._apply_common_filters(
            InscripcionMateria.objects.filter(asignacion_docente_id__in=qs.values_list("asignacion_docente_id", flat=True)),
            filtros,
        )
        if dummy_qs is not None:
            qs = qs.filter(asignacion_docente_id__in=inscripciones.values_list("asignacion_docente_id", flat=True))
        return qs

    def _docente_rows(self, records):
        rows = self._agregado_rows(records, lambda r: (r["periodo"], r["carrera"], r["docente"], r["grupo"], r["asignatura"]))
        exentos_por_asignacion = self._exentos_count_by_asignacion()
        for row in rows:
            matching = [r for r in records if r["periodo"] == row["periodo"] and r["carrera"] == row["carrera"] and r["docente"] == row["docente"] and r["grupo"] == row["grupo"] and r["asignatura"] == row["asignatura"]]
            asignacion_ids = {item["asignacion_id"] for item in matching}
            row["exentos"] = sum(exentos_por_asignacion.get(asignacion_id, 0) for asignacion_id in asignacion_ids)
            row["actas_formalizadas"] = self._actas_formalizadas_count(asignacion_ids)
            row["actas_pendientes"] = self._actas_pendientes_count(asignacion_ids)
        return rows

    def _cohorte_rows(self, records):
        rows = self._agregado_rows(records, lambda r: (r["periodo"], r["carrera"], r["antiguedad"], r["anio_formacion"], r["semestre"]))
        exentos_por_key = {}
        for row in self._exentos_rows({}):
            key = (row["periodo"], row["carrera"], row["grupo"])
            exentos_por_key[key] = exentos_por_key.get(key, 0) + 1
        for row in rows:
            values = [
                item["calificacion"]
                for item in records
                if item["periodo"] == row["periodo"]
                and item["carrera"] == row["carrera"]
                and item["antiguedad"] == row["antiguedad"]
                and item["anio_formacion"] == row["anio_formacion"]
                and item["semestre"] == row["semestre"]
            ]
            row["exentos"] = sum(count for (periodo, carrera, _grupo), count in exentos_por_key.items() if periodo == row["periodo"] and carrera == row["carrera"])
            row.update(_distribucion_compacta(values))
        return rows

    def _reprobados_rows(self, records):
        rows = []
        for record in records:
            if record["calificacion"] >= APROBATORIA:
                continue
            rows.append(
                {
                    "periodo": record["periodo"],
                    "carrera": record["carrera"],
                    "grupo": record["grupo"],
                    "antiguedad": record["antiguedad"],
                    "asignatura": record["asignatura"],
                    "docente": record["docente"],
                    "grado": record["grado"],
                    "nombre_discente": record["nombre_discente"],
                    "calificacion_ordinaria": _fmt_decimal(record["calificacion_ordinaria"]),
                    "resultado_oficial": record["resultado_oficial"],
                    "extraordinario_pendiente": "Si" if record["extraordinario_pendiente"] else "No",
                    "extraordinario_aprobado": "Si" if record["extraordinario_aprobado"] else "No",
                    "marca": "EE" if record["marca"] == CatalogoResultadoAcademico.CLAVE_EE else record["marca"],
                    "situacion_academica": record["situacion_academica"],
                    "acta_final": record["final_acta_id"],
                    "formalizada_en": record["formalizada_en"],
                }
            )
        return rows

    def _cuadro_aprovechamiento_rows(self, records, filtros):
        incluir_con_reprobadas = _is_truthy(filtros.get("incluir_con_reprobadas"))
        por_discente = {}
        for record in records:
            por_discente.setdefault(record["discente_id"], []).append(record)
        candidatos = []
        for values in por_discente.values():
            calificaciones = [item["calificacion"] for item in values]
            if not incluir_con_reprobadas and any(value < APROBATORIA for value in calificaciones):
                continue
            promedio = _mean(calificaciones)
            rango = _rango_aprovechamiento(promedio)
            if not rango:
                continue
            sample = values[0]
            if filtros.get("rango_aprovechamiento") and filtros["rango_aprovechamiento"].lower() not in rango.lower():
                continue
            candidatos.append((promedio, sample, len(calificaciones), rango))
        candidatos.sort(key=lambda item: (-item[0], item[1]["nombre_discente"]))
        rows = []
        for index, (promedio, sample, total, rango) in enumerate(candidatos, start=1):
            rows.append(
                {
                    "rango_aprovechamiento": rango,
                    "lugar": index,
                    "periodo": sample["periodo"],
                    "carrera": sample["carrera"],
                    "grupo": sample["grupo"],
                    "antiguedad": sample["antiguedad"],
                    "anio_formacion": sample["anio_formacion"],
                    "grado": sample["grado"],
                    "nombre_discente": sample["nombre_discente"],
                    "promedio": _fmt_decimal(promedio),
                    "total_materias": total,
                    "observaciones": "Sin materias reprobadas" if not incluir_con_reprobadas else "Incluye filtro con reprobadas",
                }
            )
        return rows

    def _exentos_count_by_asignacion(self):
        rows = {}
        qs = CalificacionComponente.objects.filter(
            detalle__acta__corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
            detalle__acta__estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            componente_es_examen_snapshot=True,
            sustituido_por_exencion=True,
        ).values_list("detalle__acta__asignacion_docente_id", flat=True)
        for asignacion_id in qs:
            rows[asignacion_id] = rows.get(asignacion_id, 0) + 1
        return rows

    def _actas_formalizadas_count(self, asignacion_ids):
        return Acta.objects.filter(
            asignacion_docente_id__in=asignacion_ids,
            estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
        ).count()

    def _actas_pendientes_count(self, asignacion_ids):
        return Acta.objects.filter(asignacion_docente_id__in=asignacion_ids).exclude(
            estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
        ).count()

    def _key_asignatura(self, record):
        return (
            record["periodo"],
            record["carrera"],
            record["antiguedad"],
            record["anio_formacion"],
            record["grupo"],
            record["semestre"],
            record["asignatura"],
            record["docente"],
        )

    def _summary_sheet(self, title, rows, key):
        counts = {}
        for row in rows:
            value = row.get(key) or "Sin dato"
            counts[value] = counts.get(value, 0) + 1
        summary_rows = [{"categoria": category, "total": total} for category, total in sorted(counts.items())]
        return ReporteSheet(title, [{"key": "categoria", "label": "Categoria"}, {"key": "total", "label": "Total"}], summary_rows)

    def _resumen_general(self, filas):
        return {"total_filas": len(filas)}

    def _objeto_repr_filtros(self, filtros):
        parts = [filtros.get("periodo"), filtros.get("carrera"), filtros.get("grupo")]
        return "-".join(part for part in parts if part) or ""


def _metricas(values):
    values = [Decimal(value) for value in values if value is not None]
    total = len(values)
    aprobados = sum(1 for value in values if value >= APROBATORIA)
    reprobados = sum(1 for value in values if value < APROBATORIA)
    return {
        "total_evaluados": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "porcentaje_aprobados": _percent(aprobados, total),
        "porcentaje_reprobados": _percent(reprobados, total),
        "promedio": _fmt_decimal(_mean(values)),
        "maxima": _fmt_decimal(max(values) if values else None),
        "minima": _fmt_decimal(min(values) if values else None),
        "moda": _fmt_decimal(_mode(values)),
        "desviacion_estandar": _fmt_decimal(_std_population(values)),
    }


def _mean(values):
    values = [Decimal(value) for value in values if value is not None]
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))


def _mode(values):
    if not values:
        return None
    rounded = [_round_decimal(value) for value in values]
    try:
        return mode(rounded)
    except StatisticsError:
        counts = {}
        for value in rounded:
            counts[value] = counts.get(value, 0) + 1
        max_count = max(counts.values())
        return min(value for value, count in counts.items() if count == max_count)


def _std_population(values):
    values = [Decimal(value) for value in values if value is not None]
    if not values:
        return None
    mean = _mean(values)
    variance = sum((value - mean) ** 2 for value in values) / Decimal(len(values))
    return variance.sqrt()


def _distribucion_compacta(values):
    values = [Decimal(value) for value in values]
    return {
        "dist_0_5_9": sum(1 for value in values if Decimal("0.0") <= value <= Decimal("5.9")),
        "dist_6_6_9": sum(1 for value in values if Decimal("6.0") <= value <= Decimal("6.9")),
        "dist_7_7_9": sum(1 for value in values if Decimal("7.0") <= value <= Decimal("7.9")),
        "dist_8_8_9": sum(1 for value in values if Decimal("8.0") <= value <= Decimal("8.9")),
        "dist_9_10": sum(1 for value in values if Decimal("9.0") <= value <= Decimal("10.0")),
    }


def _rango_aprovechamiento(promedio):
    if promedio is None:
        return ""
    for label, minimum, maximum in RANGOS_APROVECHAMIENTO:
        if minimum <= promedio <= maximum:
            return label
    return ""


def _percent(value, total):
    if not total:
        return "0.0"
    return _fmt_decimal(Decimal(value) * Decimal("100") / Decimal(total))


def _fmt_decimal(value):
    if value is None or value == "":
        return "N/A"
    return f"{_round_decimal(Decimal(value)):.1f}"


def _round_decimal(value):
    return Decimal(value).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def _resultado_por_calificacion(value):
    return "APROBADO" if value >= APROBATORIA else "REPROBADO"


def _grado(user):
    return user.grado_empleo.abreviatura if getattr(user, "grado_empleo_id", None) else ""


def _dt(value):
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M") if value else ""


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _is_truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "si", "sí", "yes", "on"}


def _is_summary_sheet(sheet):
    keys = {column["key"] for column in sheet.columnas}
    return keys == {"categoria", "total"}
