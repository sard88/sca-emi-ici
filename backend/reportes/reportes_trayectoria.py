import hashlib
from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from catalogos.models import ProgramaAsignatura
from core.portal_services import portal_context
from evaluacion.models import Acta, ComponenteEvaluacion, DetalleActa
from relaciones.models import AdscripcionGrupo, Discente, InscripcionMateria, MovimientoAcademico
from trayectoria.models import CatalogoResultadoAcademico, CatalogoSituacionAcademica, EventoSituacionAcademica, Extraordinario
from trayectoria.services import construir_historial_discente

from .exportadores.reportes_excel import ReporteSheet, XLSX_MIME, generar_reporte_xlsx
from .models import RegistroExportacion
from .services import ServicioExportacion, ServicioPermisosExportacion, construir_nombre_archivo


@dataclass(frozen=True)
class ReporteTrayectoriaConfig:
    slug: str
    tipo_documento: str
    nombre: str


@dataclass(frozen=True)
class ReporteTrayectoriaData:
    slug: str
    nombre: str
    columnas: list[dict]
    filas: list[dict]
    filtros: dict
    sheets: list[ReporteSheet]
    resumen: dict


@dataclass(frozen=True)
class ArchivoReporteTrayectoria:
    contenido: bytes
    nombre_archivo: str
    content_type: str
    registro: RegistroExportacion


REPORTES_TRAYECTORIA = {
    "extraordinarios": ReporteTrayectoriaConfig("extraordinarios", RegistroExportacion.TIPO_REPORTE_EXTRAORDINARIOS, "Reporte de extraordinarios registrados"),
    "situacion-actual": ReporteTrayectoriaConfig("situacion-actual", RegistroExportacion.TIPO_REPORTE_SITUACION_ACADEMICA, "Reporte de situacion academica actual"),
    "bajas-temporales": ReporteTrayectoriaConfig("bajas-temporales", RegistroExportacion.TIPO_REPORTE_BAJAS_TEMPORALES, "Reporte de bajas temporales"),
    "bajas-definitivas": ReporteTrayectoriaConfig("bajas-definitivas", RegistroExportacion.TIPO_REPORTE_BAJAS_DEFINITIVAS, "Reporte de bajas definitivas"),
    "reingresos": ReporteTrayectoriaConfig("reingresos", RegistroExportacion.TIPO_REPORTE_REINGRESOS, "Reporte de reingresos"),
    "egresables": ReporteTrayectoriaConfig("egresables", RegistroExportacion.TIPO_REPORTE_EGRESADOS_EGRESABLES, "Reporte de egresables y egresados"),
    "situacion-agregado": ReporteTrayectoriaConfig("situacion-agregado", RegistroExportacion.TIPO_REPORTE_SITUACION_ACADEMICA_AGREGADO, "Reporte agregado de situacion academica"),
    "movimientos-academicos": ReporteTrayectoriaConfig("movimientos-academicos", RegistroExportacion.TIPO_REPORTE_MOVIMIENTOS_ACADEMICOS, "Reporte de movimientos academicos"),
    "cambios-grupo": ReporteTrayectoriaConfig("cambios-grupo", RegistroExportacion.TIPO_REPORTE_CAMBIOS_GRUPO, "Reporte de cambios de grupo"),
    "historial-interno": ReporteTrayectoriaConfig("historial-interno", RegistroExportacion.TIPO_REPORTE_HISTORIAL_ACADEMICO_INTERNO, "Reporte de historial academico interno"),
    "historial-interno-discente": ReporteTrayectoriaConfig("historial-interno-discente", RegistroExportacion.TIPO_HISTORIAL_ACADEMICO, "Historial academico interno por discente"),
}

EXTRAORDINARIOS_COLUMNS = [
    {"key": "extraordinario_id", "label": "ID extraordinario"},
    {"key": "periodo", "label": "Periodo academico"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "anio_formacion", "label": "Anio de formacion"},
    {"key": "semestre", "label": "Semestre"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "docente", "label": "Docente"},
    {"key": "grado_discente", "label": "Grado/empleo del discente"},
    {"key": "nombre_discente", "label": "Nombre del discente"},
    {"key": "calificacion_ordinaria_previa", "label": "Calificacion ordinaria previa"},
    {"key": "calificacion_extraordinaria", "label": "Calificacion extraordinaria"},
    {"key": "aprobado_extraordinario", "label": "Aprobado extraordinario"},
    {"key": "resultado_oficial", "label": "Resultado oficial"},
    {"key": "marca", "label": "Marca"},
    {"key": "fecha_aplicacion", "label": "Fecha de aplicacion"},
    {"key": "fecha_registro", "label": "Fecha de registro"},
    {"key": "acta_asociada", "label": "Acta asociada"},
    {"key": "situacion_posterior", "label": "Situacion academica posterior"},
    {"key": "observaciones", "label": "Observaciones"},
]

SITUACION_COLUMNS = [
    {"key": "discente_id", "label": "ID discente"},
    {"key": "grado", "label": "Grado/empleo"},
    {"key": "nombre", "label": "Nombre"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "plan_estudios", "label": "Plan de estudios"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "grupo_actual", "label": "Grupo actual"},
    {"key": "periodo_actual", "label": "Periodo actual"},
    {"key": "situacion_actual", "label": "Situacion academica actual"},
    {"key": "fecha_ultima_situacion", "label": "Fecha de ultima situacion"},
    {"key": "motivo_ultima_situacion", "label": "Motivo de ultima situacion"},
    {"key": "usuario_registro", "label": "Usuario que registro"},
    {"key": "observaciones", "label": "Observaciones"},
    {"key": "extraordinario_pendiente", "label": "Tiene extraordinario pendiente"},
    {"key": "baja_abierta", "label": "Tiene baja abierta"},
    {"key": "egresable", "label": "Egresable"},
]

EVENTOS_COLUMNS = [
    {"key": "evento_id", "label": "ID evento"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "grado", "label": "Grado/empleo"},
    {"key": "nombre", "label": "Nombre"},
    {"key": "situacion", "label": "Situacion"},
    {"key": "fecha_inicio", "label": "Fecha inicio"},
    {"key": "fecha_fin", "label": "Fecha fin"},
    {"key": "baja_abierta", "label": "Baja abierta"},
    {"key": "motivo", "label": "Motivo"},
    {"key": "materia_detonante", "label": "Materia detonante"},
    {"key": "calificacion_ordinaria", "label": "Calificacion ordinaria"},
    {"key": "calificacion_extraordinaria", "label": "Calificacion extraordinaria"},
    {"key": "usuario_registro", "label": "Usuario que registro"},
    {"key": "observaciones", "label": "Observaciones"},
    {"key": "reingreso_asociado", "label": "Reingreso asociado"},
]

EGRESABLES_COLUMNS = [
    {"key": "discente_id", "label": "ID discente"},
    {"key": "grado", "label": "Grado/empleo"},
    {"key": "nombre", "label": "Nombre"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "plan", "label": "Plan"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "ultimo_grupo", "label": "Ultimo grupo"},
    {"key": "situacion", "label": "Situacion"},
    {"key": "egresable", "label": "Egresable"},
    {"key": "egresado", "label": "Egresado"},
    {"key": "fecha_egreso", "label": "Fecha de egreso"},
    {"key": "periodo_asociado", "label": "Periodo asociado"},
    {"key": "observaciones", "label": "Observaciones"},
]

SITUACION_AGREGADO_COLUMNS = [
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "situacion_academica", "label": "Situacion academica"},
    {"key": "total_discentes", "label": "Total discentes"},
    {"key": "porcentaje", "label": "Porcentaje"},
]

MOVIMIENTOS_COLUMNS = [
    {"key": "movimiento_id", "label": "ID movimiento"},
    {"key": "tipo_movimiento", "label": "Tipo de movimiento"},
    {"key": "fecha_movimiento", "label": "Fecha del movimiento"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "grado", "label": "Grado/empleo"},
    {"key": "nombre_discente", "label": "Nombre del discente"},
    {"key": "grupo_origen", "label": "Grupo origen"},
    {"key": "grupo_destino", "label": "Grupo destino"},
    {"key": "aplicado", "label": "Estado operativo aplicado"},
    {"key": "observaciones", "label": "Observaciones"},
    {"key": "usuario_registro", "label": "Usuario que registro"},
    {"key": "fecha_creacion", "label": "Fecha de creacion"},
    {"key": "afecto_adscripcion", "label": "Afecto adscripcion"},
    {"key": "afecto_inscripciones", "label": "Afecto inscripciones"},
]

CAMBIOS_GRUPO_COLUMNS = [
    {"key": "movimiento_id", "label": "ID movimiento"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "fecha", "label": "Fecha"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "antiguedad", "label": "Antiguedad"},
    {"key": "grado", "label": "Grado/empleo"},
    {"key": "nombre", "label": "Nombre"},
    {"key": "grupo_origen", "label": "Grupo origen"},
    {"key": "grupo_destino", "label": "Grupo destino"},
    {"key": "adscripcion_origen_cerrada", "label": "Adscripcion origen cerrada"},
    {"key": "adscripcion_destino_activa", "label": "Adscripcion destino activa"},
    {"key": "inscripciones_origen_baja", "label": "Inscripciones origen dadas de baja"},
    {"key": "inscripciones_destino", "label": "Nuevas inscripciones destino"},
    {"key": "bloqueado_por_actas_vivas", "label": "Bloqueado por actas vivas"},
    {"key": "observaciones", "label": "Observaciones"},
]

HISTORIAL_RESULTADOS_COLUMNS = [
    {"key": "discente_id", "label": "ID discente"},
    {"key": "grado", "label": "Grado/empleo"},
    {"key": "nombre", "label": "Nombre"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "anio_formacion", "label": "Anio de formacion"},
    {"key": "semestre", "label": "Semestre"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "tipo_resultado", "label": "Tipo de resultado"},
    {"key": "calificacion_ordinaria", "label": "Calificacion ordinaria"},
    {"key": "calificacion_extraordinaria", "label": "Calificacion extraordinaria"},
    {"key": "resultado_oficial", "label": "Resultado oficial"},
    {"key": "marca", "label": "Marca"},
    {"key": "acta_asociada", "label": "Acta asociada"},
    {"key": "fecha_formalizacion", "label": "Fecha de formalizacion"},
    {"key": "observaciones", "label": "Observaciones"},
]

HISTORIAL_EVENTOS_COLUMNS = [
    {"key": "discente_id", "label": "ID discente"},
    {"key": "nombre", "label": "Nombre"},
    {"key": "situacion", "label": "Situacion"},
    {"key": "fecha_inicio", "label": "Fecha inicio"},
    {"key": "fecha_fin", "label": "Fecha fin"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "motivo", "label": "Motivo"},
    {"key": "usuario_registro", "label": "Usuario que registro"},
    {"key": "observaciones", "label": "Observaciones"},
]

RESUMEN_COLUMNS = [
    {"key": "categoria", "label": "Categoria"},
    {"key": "total", "label": "Total"},
]


class ServicioReportesTrayectoria:
    def __init__(self, user, request=None):
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Autenticacion requerida.")
        self.user = user
        self.request = request
        self.ctx = portal_context(user)
        self.permisos = ServicioPermisosExportacion(user)
        self.servicio_exportacion = ServicioExportacion(user, request=request)

    def vista_previa(self, slug: str, params, discente_id=None) -> ReporteTrayectoriaData:
        config = self._config(slug)
        self._validar_permiso(config.tipo_documento)
        filtros = self._filtros(params)
        if discente_id:
            filtros["discente_id"] = str(discente_id)
        sheets = self._build_sheets(slug, filtros, discente_id=discente_id)
        filas = [row for sheet in sheets if not _is_summary_sheet(sheet) for row in sheet.filas]
        columnas = sheets[0].columnas if sheets else []
        return ReporteTrayectoriaData(
            slug=slug,
            nombre=config.nombre,
            columnas=columnas,
            filas=filas,
            filtros=filtros,
            sheets=sheets,
            resumen={"total_filas": len(filas)},
        )

    def exportar_xlsx(self, slug: str, params, discente_id=None) -> ArchivoReporteTrayectoria:
        config = self._config(slug)
        self._validar_permiso(config.tipo_documento)
        filtros = self._filtros(params)
        if discente_id:
            filtros["discente_id"] = str(discente_id)
        objeto = None
        objeto_tipo = ""
        objeto_id = ""
        objeto_repr = self._objeto_repr_filtros(filtros)
        if discente_id:
            objeto = self._get_visible_discente(discente_id)
            objeto_tipo = "relaciones.Discente"
            objeto_id = str(objeto.id)
            objeto_repr = f"discente-{objeto.id}"
        nombre_archivo = construir_nombre_archivo(config.tipo_documento, RegistroExportacion.FORMATO_XLSX, objeto_repr=objeto_repr)
        registro = self.servicio_exportacion.registrar_solicitud(
            tipo_documento=config.tipo_documento,
            formato=RegistroExportacion.FORMATO_XLSX,
            nombre_documento=config.nombre,
            nombre_archivo=nombre_archivo,
            objeto=objeto,
            objeto_tipo=objeto_tipo,
            objeto_id=objeto_id,
            objeto_repr=objeto_repr,
            filtros=filtros,
            parametros={"slug": slug},
        )
        try:
            data = self.vista_previa(slug, params, discente_id=discente_id)
            contenido = generar_reporte_xlsx(titulo=config.nombre, filtros=filtros, sheets=data.sheets)
        except Exception as exc:
            self.servicio_exportacion.marcar_fallida(registro, exc)
            raise
        self.servicio_exportacion.marcar_generada(
            registro,
            tamano_bytes=len(contenido),
            hash_archivo=hashlib.sha256(contenido).hexdigest(),
        )
        return ArchivoReporteTrayectoria(contenido=contenido, nombre_archivo=nombre_archivo, content_type=XLSX_MIME, registro=registro)

    def _config(self, slug):
        if slug not in REPORTES_TRAYECTORIA:
            raise PermissionDenied("Reporte no reconocido.")
        return REPORTES_TRAYECTORIA[slug]

    def _validar_permiso(self, tipo_documento):
        if self.ctx.is_discente or self.ctx.is_docente:
            raise PermissionDenied("No tienes permiso para consultar este reporte.")
        if not self.permisos.puede_ver_tipo(tipo_documento):
            raise PermissionDenied("No tienes permiso para consultar este reporte.")

    def _filtros(self, params):
        keys = (
            "periodo", "carrera", "grupo", "plan", "antiguedad", "generacion", "anio_formacion", "semestre",
            "asignatura", "docente", "discente", "situacion", "tipo_movimiento", "grupo_origen", "grupo_destino",
            "aprobado", "baja_abierta", "fecha_desde", "fecha_hasta", "incluir_extraordinarios", "incluir_eventos",
            "incluir_movimientos",
        )
        return {key: str(params.get(key, "")).strip() for key in keys if str(params.get(key, "")).strip()}

    def _build_sheets(self, slug, filtros, discente_id=None):
        if slug == "extraordinarios":
            rows = self._extraordinarios_rows(filtros)
            return [ReporteSheet("Detalle", EXTRAORDINARIOS_COLUMNS, rows), self._summary_sheet("Resumen por resultado", rows, "resultado_oficial")]
        if slug == "situacion-actual":
            rows = self._situacion_actual_rows(filtros)
            return [ReporteSheet("Nominal", SITUACION_COLUMNS, rows), self._summary_sheet("Resumen por situacion", rows, "situacion_actual")]
        if slug == "bajas-temporales":
            rows = self._eventos_rows(CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL, filtros)
            return [ReporteSheet("Detalle", EVENTOS_COLUMNS, rows), self._summary_sheet("Resumen", rows, "baja_abierta")]
        if slug == "bajas-definitivas":
            rows = self._eventos_rows(CatalogoSituacionAcademica.CLAVE_BAJA_DEFINITIVA, filtros)
            return [ReporteSheet("Detalle", EVENTOS_COLUMNS, rows), self._summary_sheet("Resumen", rows, "situacion")]
        if slug == "reingresos":
            rows = self._eventos_rows(CatalogoSituacionAcademica.CLAVE_REINGRESO, filtros)
            return [ReporteSheet("Detalle", EVENTOS_COLUMNS, rows)]
        if slug == "egresables":
            rows = self._egresables_rows(filtros)
            return [ReporteSheet("Egresables", EGRESABLES_COLUMNS, rows), self._summary_sheet("Resumen", rows, "situacion")]
        if slug == "situacion-agregado":
            rows = self._situacion_agregado_rows(filtros)
            return [ReporteSheet("Agregado", SITUACION_AGREGADO_COLUMNS, rows)]
        if slug == "movimientos-academicos":
            rows = self._movimientos_rows(filtros)
            return [ReporteSheet("Movimientos", MOVIMIENTOS_COLUMNS, rows), self._summary_sheet("Resumen por tipo", rows, "tipo_movimiento")]
        if slug == "cambios-grupo":
            rows = self._cambios_grupo_rows(filtros)
            return [ReporteSheet("Cambios de grupo", CAMBIOS_GRUPO_COLUMNS, rows)]
        if slug == "historial-interno":
            return self._historial_institucional_sheets(filtros)
        if slug == "historial-interno-discente":
            if not discente_id:
                raise ValidationError("Se requiere discente_id para historial interno por discente.")
            return self._historial_discente_sheets(self._get_visible_discente(discente_id))
        return []

    def _visible_discentes_queryset(self):
        qs = Discente.objects.select_related("usuario__grado_empleo", "plan_estudios__carrera", "antiguedad")
        if self.ctx.is_jefatura_carrera and not self.ctx.has_consulta_amplia:
            if not self.ctx.carrera_ids:
                return qs.none()
            qs = qs.filter(plan_estudios__carrera_id__in=self.ctx.carrera_ids)
        elif not (self.ctx.is_admin or self.ctx.is_estadistica or self.ctx.is_jefatura_academica or self.ctx.is_jefatura_pedagogica or self.ctx.is_jefatura_carrera):
            return qs.none()
        return qs

    def _apply_discente_filters(self, qs, filtros):
        if filtros.get("carrera"):
            value = filtros["carrera"]
            qs = qs.filter(Q(plan_estudios__carrera__clave__iexact=value) | Q(plan_estudios__carrera_id=_int_or_none(value)))
        if filtros.get("plan"):
            value = filtros["plan"]
            qs = qs.filter(Q(plan_estudios__clave__icontains=value) | Q(plan_estudios_id=_int_or_none(value)))
        if filtros.get("antiguedad") or filtros.get("generacion"):
            value = filtros.get("antiguedad") or filtros.get("generacion")
            qs = qs.filter(Q(antiguedad__clave__icontains=value) | Q(antiguedad_id=_int_or_none(value)))
        if filtros.get("situacion"):
            qs = qs.filter(situacion_actual__icontains=filtros["situacion"])
        if filtros.get("discente"):
            value = filtros["discente"]
            qs = qs.filter(Q(usuario__nombre_completo__icontains=value) | Q(usuario__username__icontains=value) | Q(id=_int_or_none(value)))
        if filtros.get("grupo") or filtros.get("periodo"):
            ads = AdscripcionGrupo.objects.filter(activo=True)
            if filtros.get("grupo"):
                value = filtros["grupo"]
                ads = ads.filter(Q(grupo_academico__clave_grupo__icontains=value) | Q(grupo_academico_id=_int_or_none(value)))
            if filtros.get("periodo"):
                value = filtros["periodo"]
                ads = ads.filter(Q(grupo_academico__periodo__clave__iexact=value) | Q(grupo_academico__periodo_id=_int_or_none(value)))
            qs = qs.filter(id__in=ads.values_list("discente_id", flat=True))
        return qs

    def _get_visible_discente(self, discente_id):
        try:
            return self._visible_discentes_queryset().get(pk=discente_id)
        except Discente.DoesNotExist:
            raise PermissionDenied("No tienes permiso para consultar este discente o no existe.")

    def _extraordinarios_queryset(self, filtros):
        qs = Extraordinario.objects.select_related(
            "inscripcion_materia__discente__usuario__grado_empleo",
            "inscripcion_materia__discente__plan_estudios__carrera",
            "inscripcion_materia__discente__antiguedad",
            "inscripcion_materia__asignacion_docente__usuario_docente",
            "inscripcion_materia__asignacion_docente__grupo_academico__periodo",
            "inscripcion_materia__asignacion_docente__programa_asignatura__materia",
            "inscripcion_materia__asignacion_docente__programa_asignatura__plan_estudios__carrera",
        )
        qs = qs.filter(inscripcion_materia__discente_id__in=self._apply_discente_filters(self._visible_discentes_queryset(), filtros).values_list("id", flat=True))
        qs = self._apply_inscripcion_filters(qs, filtros, prefix="inscripcion_materia__")
        if filtros.get("aprobado"):
            qs = qs.filter(aprobado=_is_truthy(filtros["aprobado"]))
        desde = parse_date(filtros.get("fecha_desde") or "")
        hasta = parse_date(filtros.get("fecha_hasta") or "")
        if desde:
            qs = qs.filter(fecha_aplicacion__gte=desde)
        if hasta:
            qs = qs.filter(fecha_aplicacion__lte=hasta)
        return qs.order_by("-fecha_aplicacion", "inscripcion_materia__discente__matricula")

    def _apply_inscripcion_filters(self, qs, filtros, prefix=""):
        base = prefix
        if filtros.get("periodo"):
            value = filtros["periodo"]
            qs = qs.filter(Q(**{f"{base}asignacion_docente__grupo_academico__periodo__clave__iexact": value}) | Q(**{f"{base}asignacion_docente__grupo_academico__periodo_id": _int_or_none(value)}))
        if filtros.get("carrera"):
            value = filtros["carrera"]
            qs = qs.filter(Q(**{f"{base}asignacion_docente__programa_asignatura__plan_estudios__carrera__clave__iexact": value}) | Q(**{f"{base}asignacion_docente__programa_asignatura__plan_estudios__carrera_id": _int_or_none(value)}))
        if filtros.get("grupo"):
            value = filtros["grupo"]
            qs = qs.filter(Q(**{f"{base}asignacion_docente__grupo_academico__clave_grupo__icontains": value}) | Q(**{f"{base}asignacion_docente__grupo_academico_id": _int_or_none(value)}))
        if filtros.get("asignatura"):
            value = filtros["asignatura"]
            qs = qs.filter(Q(**{f"{base}asignacion_docente__programa_asignatura__materia__nombre__icontains": value}) | Q(**{f"{base}asignacion_docente__programa_asignatura__materia__clave__icontains": value}) | Q(**{f"{base}asignacion_docente__programa_asignatura_id": _int_or_none(value)}))
        if filtros.get("docente"):
            value = filtros["docente"]
            qs = qs.filter(Q(**{f"{base}asignacion_docente__usuario_docente__nombre_completo__icontains": value}) | Q(**{f"{base}asignacion_docente__usuario_docente__username__icontains": value}) | Q(**{f"{base}asignacion_docente__usuario_docente_id": _int_or_none(value)}))
        if filtros.get("anio_formacion"):
            qs = qs.filter(**{f"{base}asignacion_docente__programa_asignatura__anio_formacion": _int_or_none(filtros["anio_formacion"])})
        if filtros.get("semestre"):
            qs = qs.filter(**{f"{base}asignacion_docente__grupo_academico__semestre_numero": _int_or_none(filtros["semestre"])})
        return qs

    def _extraordinarios_rows(self, filtros):
        rows = []
        for extra in self._extraordinarios_queryset(filtros):
            inscripcion = extra.inscripcion_materia
            base = _inscripcion_base(inscripcion)
            rows.append(
                {
                    "extraordinario_id": extra.id,
                    **base,
                    "grado_discente": _grado(inscripcion.discente.usuario),
                    "nombre_discente": inscripcion.discente.usuario.nombre_visible,
                    "calificacion_ordinaria_previa": _fmt_decimal(extra.calificacion_ordinaria),
                    "calificacion_extraordinaria": _fmt_decimal(extra.calificacion),
                    "aprobado_extraordinario": _si_no(extra.aprobado),
                    "resultado_oficial": extra.codigo_resultado_oficial or inscripcion.codigo_resultado_oficial or "",
                    "marca": "EE" if extra.codigo_marca == CatalogoResultadoAcademico.CLAVE_EE else extra.codigo_marca or "",
                    "fecha_aplicacion": _date(extra.fecha_aplicacion),
                    "fecha_registro": _dt(extra.creado_en),
                    "acta_asociada": _acta_final_id(inscripcion),
                    "situacion_posterior": inscripcion.discente.get_situacion_actual_display(),
                    "observaciones": "Extraordinario aprobado" if extra.aprobado else "Extraordinario no aprobado",
                }
            )
        return rows

    def _situacion_actual_rows(self, filtros):
        rows = []
        qs = self._apply_discente_filters(self._visible_discentes_queryset(), filtros).order_by("plan_estudios__carrera__clave", "antiguedad__clave", "usuario__nombre_completo")
        for discente in qs:
            grupo = _grupo_actual(discente)
            ultimo = _ultimo_evento(discente)
            rows.append(
                {
                    "discente_id": discente.id,
                    "grado": _grado(discente.usuario),
                    "nombre": discente.usuario.nombre_visible,
                    "carrera": discente.plan_estudios.carrera.clave,
                    "plan_estudios": discente.plan_estudios.clave,
                    "antiguedad": discente.antiguedad.clave,
                    "grupo_actual": grupo.clave_grupo if grupo else "",
                    "periodo_actual": grupo.periodo.clave if grupo else "",
                    "situacion_actual": discente.get_situacion_actual_display(),
                    "fecha_ultima_situacion": _date(ultimo.fecha_inicio if ultimo else None),
                    "motivo_ultima_situacion": ultimo.motivo if ultimo else "",
                    "usuario_registro": ultimo.registrado_por.nombre_visible if ultimo and ultimo.registrado_por_id else "",
                    "observaciones": "",
                    "extraordinario_pendiente": _si_no(_tiene_extraordinario_pendiente(discente)),
                    "baja_abierta": _si_no(_tiene_baja_abierta(discente)),
                    "egresable": _si_no(_es_egresable(discente)),
                }
            )
        return rows

    def _eventos_queryset(self, situacion_clave, filtros):
        qs = EventoSituacionAcademica.objects.select_related(
            "discente__usuario__grado_empleo",
            "discente__plan_estudios__carrera",
            "discente__antiguedad",
            "situacion",
            "periodo",
            "registrado_por",
            "inscripcion_materia__asignacion_docente__programa_asignatura__materia",
        ).filter(situacion__clave=situacion_clave)
        qs = qs.filter(discente_id__in=self._apply_discente_filters(self._visible_discentes_queryset(), filtros).values_list("id", flat=True))
        desde = parse_date(filtros.get("fecha_desde") or "")
        hasta = parse_date(filtros.get("fecha_hasta") or "")
        if desde:
            qs = qs.filter(fecha_inicio__gte=desde)
        if hasta:
            qs = qs.filter(fecha_inicio__lte=hasta)
        if filtros.get("periodo"):
            value = filtros["periodo"]
            qs = qs.filter(Q(periodo__clave__iexact=value) | Q(periodo_id=_int_or_none(value)))
        if filtros.get("baja_abierta"):
            qs = qs.filter(fecha_fin__isnull=_is_truthy(filtros["baja_abierta"]))
        return qs.order_by("-fecha_inicio", "discente__usuario__nombre_completo")

    def _eventos_rows(self, situacion_clave, filtros):
        rows = []
        for evento in self._eventos_queryset(situacion_clave, filtros):
            discente = evento.discente
            grupo = _grupo_actual(discente)
            inscripcion = evento.inscripcion_materia
            extra = getattr(inscripcion, "extraordinario", None) if inscripcion else None
            rows.append(
                {
                    "evento_id": evento.id,
                    "periodo": evento.periodo.clave if evento.periodo_id else (grupo.periodo.clave if grupo else ""),
                    "carrera": discente.plan_estudios.carrera.clave,
                    "grupo": grupo.clave_grupo if grupo else "",
                    "antiguedad": discente.antiguedad.clave,
                    "grado": _grado(discente.usuario),
                    "nombre": discente.usuario.nombre_visible,
                    "situacion": evento.situacion.nombre,
                    "fecha_inicio": _date(evento.fecha_inicio),
                    "fecha_fin": _date(evento.fecha_fin),
                    "baja_abierta": _si_no(situacion_clave == CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL and not evento.fecha_fin),
                    "motivo": evento.motivo,
                    "materia_detonante": inscripcion.asignacion_docente.programa_asignatura.materia.nombre if inscripcion else "",
                    "calificacion_ordinaria": _fmt_decimal(getattr(extra, "calificacion_ordinaria", None) or getattr(inscripcion, "calificacion_final", None)),
                    "calificacion_extraordinaria": _fmt_decimal(getattr(extra, "calificacion", None)),
                    "usuario_registro": evento.registrado_por.nombre_visible if evento.registrado_por_id else "",
                    "observaciones": evento.motivo,
                    "reingreso_asociado": _si_no(_tiene_reingreso_posterior(evento)),
                }
            )
        return rows

    def _egresables_rows(self, filtros):
        rows = []
        for discente in self._apply_discente_filters(self._visible_discentes_queryset(), filtros):
            if not (_es_egresable(discente) or discente.situacion_actual == Discente.SITUACION_EGRESADO):
                continue
            grupo = _grupo_actual(discente)
            egreso = discente.eventos_situacion.filter(situacion__clave=CatalogoSituacionAcademica.CLAVE_EGRESADO).order_by("-fecha_inicio").first()
            rows.append(
                {
                    "discente_id": discente.id,
                    "grado": _grado(discente.usuario),
                    "nombre": discente.usuario.nombre_visible,
                    "carrera": discente.plan_estudios.carrera.clave,
                    "plan": discente.plan_estudios.clave,
                    "antiguedad": discente.antiguedad.clave,
                    "ultimo_grupo": grupo.clave_grupo if grupo else "",
                    "situacion": discente.get_situacion_actual_display(),
                    "egresable": _si_no(_es_egresable(discente)),
                    "egresado": _si_no(discente.situacion_actual == Discente.SITUACION_EGRESADO),
                    "fecha_egreso": _date(egreso.fecha_inicio if egreso else None),
                    "periodo_asociado": egreso.periodo.clave if egreso and egreso.periodo_id else "",
                    "observaciones": "Derivado de situación actual y resultados oficiales disponibles",
                }
            )
        return rows

    def _situacion_agregado_rows(self, filtros):
        base_rows = self._situacion_actual_rows(filtros)
        grouped = {}
        for row in base_rows:
            key = (row["periodo_actual"], row["carrera"], row["antiguedad"], row["grupo_actual"], row["situacion_actual"])
            grouped[key] = grouped.get(key, 0) + 1
        totals = {}
        for periodo, carrera, antiguedad, grupo, _situacion in grouped:
            totals[(periodo, carrera, antiguedad, grupo)] = totals.get((periodo, carrera, antiguedad, grupo), 0) + grouped[(periodo, carrera, antiguedad, grupo, _situacion)]
        rows = []
        for key, total in sorted(grouped.items()):
            periodo, carrera, antiguedad, grupo, situacion = key
            denominator = totals.get((periodo, carrera, antiguedad, grupo), 0)
            rows.append({"periodo": periodo, "carrera": carrera, "antiguedad": antiguedad, "grupo": grupo, "situacion_academica": situacion, "total_discentes": total, "porcentaje": _percent(total, denominator)})
        return rows

    def _movimientos_queryset(self, filtros):
        qs = MovimientoAcademico.objects.select_related(
            "discente__usuario__grado_empleo",
            "discente__plan_estudios__carrera",
            "discente__antiguedad",
            "periodo",
            "grupo_origen",
            "grupo_destino",
        )
        qs = qs.filter(discente_id__in=self._apply_discente_filters(self._visible_discentes_queryset(), filtros).values_list("id", flat=True))
        if filtros.get("tipo_movimiento"):
            qs = qs.filter(tipo_movimiento=filtros["tipo_movimiento"])
        if filtros.get("periodo"):
            value = filtros["periodo"]
            qs = qs.filter(Q(periodo__clave__iexact=value) | Q(periodo_id=_int_or_none(value)))
        if filtros.get("grupo_origen"):
            value = filtros["grupo_origen"]
            qs = qs.filter(Q(grupo_origen__clave_grupo__icontains=value) | Q(grupo_origen_id=_int_or_none(value)))
        if filtros.get("grupo_destino"):
            value = filtros["grupo_destino"]
            qs = qs.filter(Q(grupo_destino__clave_grupo__icontains=value) | Q(grupo_destino_id=_int_or_none(value)))
        desde = parse_date(filtros.get("fecha_desde") or "")
        hasta = parse_date(filtros.get("fecha_hasta") or "")
        if desde:
            qs = qs.filter(fecha_movimiento__gte=desde)
        if hasta:
            qs = qs.filter(fecha_movimiento__lte=hasta)
        return qs.order_by("-fecha_movimiento", "discente__usuario__nombre_completo")

    def _movimientos_rows(self, filtros):
        rows = []
        for mov in self._movimientos_queryset(filtros):
            discente = mov.discente
            rows.append(
                {
                    "movimiento_id": mov.id,
                    "tipo_movimiento": mov.get_tipo_movimiento_display(),
                    "fecha_movimiento": _date(mov.fecha_movimiento),
                    "periodo": mov.periodo.clave,
                    "carrera": discente.plan_estudios.carrera.clave,
                    "antiguedad": discente.antiguedad.clave,
                    "grado": _grado(discente.usuario),
                    "nombre_discente": discente.usuario.nombre_visible,
                    "grupo_origen": mov.grupo_origen.clave_grupo if mov.grupo_origen_id else "",
                    "grupo_destino": mov.grupo_destino.clave_grupo if mov.grupo_destino_id else "",
                    "aplicado": _si_no(_movimiento_aplicado(mov)),
                    "observaciones": mov.observaciones,
                    "usuario_registro": "No registrado en modelo",
                    "fecha_creacion": "No registrado en modelo",
                    "afecto_adscripcion": _si_no(_movimiento_afecto_adscripcion(mov)),
                    "afecto_inscripciones": _si_no(_movimiento_afecto_inscripciones(mov)),
                }
            )
        return rows

    def _cambios_grupo_rows(self, filtros):
        rows = []
        filtros = {**filtros, "tipo_movimiento": MovimientoAcademico.CAMBIO_GRUPO}
        for mov in self._movimientos_queryset(filtros):
            discente = mov.discente
            rows.append(
                {
                    "movimiento_id": mov.id,
                    "periodo": mov.periodo.clave,
                    "fecha": _date(mov.fecha_movimiento),
                    "carrera": discente.plan_estudios.carrera.clave,
                    "antiguedad": discente.antiguedad.clave,
                    "grado": _grado(discente.usuario),
                    "nombre": discente.usuario.nombre_visible,
                    "grupo_origen": mov.grupo_origen.clave_grupo if mov.grupo_origen_id else "",
                    "grupo_destino": mov.grupo_destino.clave_grupo if mov.grupo_destino_id else "",
                    "adscripcion_origen_cerrada": _si_no(_adscripcion_origen_cerrada(mov)),
                    "adscripcion_destino_activa": _si_no(_adscripcion_destino_activa(mov)),
                    "inscripciones_origen_baja": _si_no(_inscripciones_origen_baja(mov)),
                    "inscripciones_destino": _si_no(_inscripciones_destino(mov)),
                    "bloqueado_por_actas_vivas": "No registrado en modelo",
                    "observaciones": mov.observaciones,
                }
            )
        return rows

    def _historial_institucional_sheets(self, filtros):
        discentes = self._apply_discente_filters(self._visible_discentes_queryset(), filtros).order_by("plan_estudios__carrera__clave", "usuario__nombre_completo")
        resultados = []
        eventos = []
        movimientos = []
        for discente in discentes:
            resultados.extend(self._historial_resultados_rows(discente, filtros))
            if _is_truthy(filtros.get("incluir_eventos", "true")):
                eventos.extend(self._historial_eventos_rows(discente))
            if _is_truthy(filtros.get("incluir_movimientos", "true")):
                movimientos.extend(self._historial_movimientos_rows(discente))
        return [
            ReporteSheet("Resultados", HISTORIAL_RESULTADOS_COLUMNS, resultados),
            ReporteSheet("Eventos", HISTORIAL_EVENTOS_COLUMNS, eventos),
            ReporteSheet("Movimientos", MOVIMIENTOS_COLUMNS, movimientos),
            ReporteSheet("Resumen", RESUMEN_COLUMNS, [
                {"categoria": "Discentes", "total": discentes.count()},
                {"categoria": "Resultados", "total": len(resultados)},
                {"categoria": "Eventos", "total": len(eventos)},
                {"categoria": "Movimientos", "total": len(movimientos)},
            ]),
        ]

    def _historial_discente_sheets(self, discente):
        resultados = self._historial_resultados_rows(discente, {})
        eventos = self._historial_eventos_rows(discente)
        movimientos = self._historial_movimientos_rows(discente)
        extra_rows = [row for row in self._extraordinarios_rows({"discente": str(discente.id)}) if row.get("nombre_discente") == discente.usuario.nombre_visible]
        return [
            ReporteSheet("Resultados", HISTORIAL_RESULTADOS_COLUMNS, resultados),
            ReporteSheet("Extraordinarios", EXTRAORDINARIOS_COLUMNS, extra_rows),
            ReporteSheet("Eventos", HISTORIAL_EVENTOS_COLUMNS, eventos),
            ReporteSheet("Movimientos", MOVIMIENTOS_COLUMNS, movimientos),
            ReporteSheet("Resumen", RESUMEN_COLUMNS, [
                {"categoria": "Resultados", "total": len(resultados)},
                {"categoria": "Extraordinarios", "total": len(extra_rows)},
                {"categoria": "Eventos", "total": len(eventos)},
                {"categoria": "Movimientos", "total": len(movimientos)},
            ]),
        ]

    def _historial_resultados_rows(self, discente, filtros):
        rows = []
        historial = construir_historial_discente(discente)
        for resultado in historial["resultados"]:
            inscripcion = resultado.inscripcion
            base = _inscripcion_base(inscripcion)
            if filtros and not _row_matches_basic_filters(base, filtros):
                continue
            rows.append(
                {
                    "discente_id": discente.id,
                    "grado": _grado(discente.usuario),
                    "nombre": discente.usuario.nombre_visible,
                    **base,
                    "tipo_resultado": resultado.tipo_resultado,
                    "calificacion_ordinaria": _fmt_decimal_exact(resultado.calificacion_ordinaria if resultado.extraordinario else resultado.calificacion),
                    "calificacion_extraordinaria": _fmt_decimal(resultado.extraordinario.calificacion if resultado.extraordinario else None),
                    "resultado_oficial": resultado.codigo_resultado,
                    "marca": resultado.codigo_marca,
                    "acta_asociada": _acta_final_id(inscripcion),
                    "fecha_formalizacion": _acta_final_fecha(inscripcion),
                    "observaciones": "Conserva evidencia ordinaria previa a EE" if resultado.extraordinario else "Resultado ordinario formalizado",
                }
            )
        return rows

    def _historial_eventos_rows(self, discente):
        rows = []
        for evento in discente.eventos_situacion.select_related("situacion", "periodo", "registrado_por").order_by("-fecha_inicio", "-creado_en"):
            rows.append(
                {
                    "discente_id": discente.id,
                    "nombre": discente.usuario.nombre_visible,
                    "situacion": evento.situacion.nombre,
                    "fecha_inicio": _date(evento.fecha_inicio),
                    "fecha_fin": _date(evento.fecha_fin),
                    "periodo": evento.periodo.clave if evento.periodo_id else "",
                    "motivo": evento.motivo,
                    "usuario_registro": evento.registrado_por.nombre_visible if evento.registrado_por_id else "",
                    "observaciones": evento.motivo,
                }
            )
        return rows

    def _historial_movimientos_rows(self, discente):
        return [row for row in self._movimientos_rows({"discente": str(discente.id)}) if row.get("nombre_discente") == discente.usuario.nombre_visible]

    def _summary_sheet(self, title, rows, key):
        counts = {}
        for row in rows:
            value = row.get(key) or "Sin dato"
            counts[value] = counts.get(value, 0) + 1
        return ReporteSheet(title, RESUMEN_COLUMNS, [{"categoria": category, "total": total} for category, total in sorted(counts.items())])

    def _objeto_repr_filtros(self, filtros):
        parts = [filtros.get("periodo"), filtros.get("carrera"), filtros.get("grupo"), filtros.get("situacion")]
        return "-".join(part for part in parts if part) or ""


def _inscripcion_base(inscripcion):
    asignacion = inscripcion.asignacion_docente
    grupo = asignacion.grupo_academico
    programa = asignacion.programa_asignatura
    materia = programa.materia
    semestre = grupo.semestre_numero or programa.semestre_numero
    return {
        "periodo": grupo.periodo.clave,
        "carrera": programa.plan_estudios.carrera.clave,
        "antiguedad": inscripcion.discente.antiguedad.clave,
        "grupo": grupo.clave_grupo,
        "anio_formacion": ProgramaAsignatura.calculate_anio_formacion(semestre),
        "semestre": semestre,
        "asignatura": materia.nombre,
        "docente": asignacion.usuario_docente.nombre_visible,
    }


def _row_matches_basic_filters(row, filtros):
    for key in ("periodo", "carrera", "grupo", "asignatura", "antiguedad"):
        if filtros.get(key) and str(filtros[key]).lower() not in str(row.get(key, "")).lower():
            return False
    return True


def _grupo_actual(discente):
    adscripcion = discente.adscripciones_grupo.select_related("grupo_academico__periodo").filter(activo=True).order_by("-vigente_desde", "-id").first()
    return adscripcion.grupo_academico if adscripcion else None


def _ultimo_evento(discente):
    return discente.eventos_situacion.select_related("situacion", "registrado_por").order_by("-fecha_inicio", "-creado_en").first()


def _tiene_extraordinario_pendiente(discente):
    return InscripcionMateria.objects.filter(discente=discente, calificacion_final__lt=Decimal("6.0")).exclude(extraordinario__aprobado=True).exists()


def _tiene_baja_abierta(discente):
    return discente.eventos_situacion.filter(situacion__clave=CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL, fecha_fin__isnull=True).exists()


def _es_egresable(discente):
    grupo = _grupo_actual(discente)
    if grupo and grupo.semestre_numero >= 12 and discente.situacion_actual != Discente.SITUACION_BAJA_DEFINITIVA:
        return True
    return False


def _tiene_reingreso_posterior(evento):
    return EventoSituacionAcademica.objects.filter(
        discente=evento.discente,
        situacion__clave=CatalogoSituacionAcademica.CLAVE_REINGRESO,
        fecha_inicio__gte=evento.fecha_inicio,
    ).exists()


def _movimiento_aplicado(mov):
    if mov.tipo_movimiento == MovimientoAcademico.CAMBIO_GRUPO:
        return _adscripcion_destino_activa(mov)
    return True


def _movimiento_afecto_adscripcion(mov):
    return bool(mov.grupo_destino_id and AdscripcionGrupo.objects.filter(discente=mov.discente, grupo_academico=mov.grupo_destino).exists())


def _movimiento_afecto_inscripciones(mov):
    if not mov.grupo_destino_id:
        return False
    return InscripcionMateria.objects.filter(discente=mov.discente, asignacion_docente__grupo_academico=mov.grupo_destino).exists()


def _adscripcion_origen_cerrada(mov):
    if not mov.grupo_origen_id:
        return False
    return AdscripcionGrupo.objects.filter(discente=mov.discente, grupo_academico=mov.grupo_origen, activo=False).exists()


def _adscripcion_destino_activa(mov):
    if not mov.grupo_destino_id:
        return False
    return AdscripcionGrupo.objects.filter(discente=mov.discente, grupo_academico=mov.grupo_destino, activo=True).exists()


def _inscripciones_origen_baja(mov):
    if not mov.grupo_origen_id:
        return False
    return InscripcionMateria.objects.filter(discente=mov.discente, asignacion_docente__grupo_academico=mov.grupo_origen, estado_inscripcion=InscripcionMateria.ESTADO_BAJA).exists()


def _inscripciones_destino(mov):
    if not mov.grupo_destino_id:
        return False
    return InscripcionMateria.objects.filter(discente=mov.discente, asignacion_docente__grupo_academico=mov.grupo_destino).exists()


def _acta_final_id(inscripcion):
    detalle = _detalle_final(inscripcion)
    return detalle.acta_id if detalle else ""


def _acta_final_fecha(inscripcion):
    detalle = _detalle_final(inscripcion)
    return _dt(detalle.acta.formalizada_en) if detalle else ""


def _detalle_final(inscripcion):
    return DetalleActa.objects.select_related("acta").filter(
        inscripcion_materia=inscripcion,
        acta__corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
        acta__estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
    ).order_by("-acta__formalizada_en", "-acta_id").first()


def _si_no(value):
    return "Si" if value else "No"


def _percent(value, total):
    if not total:
        return "0.0"
    return _fmt_decimal(Decimal(value) * Decimal("100") / Decimal(total))


def _fmt_decimal(value):
    if value is None or value == "":
        return "N/A"
    return f"{Decimal(value).quantize(Decimal('0.1')):.1f}"


def _fmt_decimal_exact(value):
    if value is None or value == "":
        return "N/A"
    return str(Decimal(value).normalize())


def _grado(user):
    return user.grado_empleo.abreviatura if getattr(user, "grado_empleo_id", None) else ""


def _date(value):
    return value.strftime("%Y-%m-%d") if value else ""


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
