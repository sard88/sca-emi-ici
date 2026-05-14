import hashlib
from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from core.portal_services import portal_context
from evaluacion.models import Acta, ConformidadDiscente, ValidacionActa

from .exportadores.reportes_excel import ReporteSheet, XLSX_MIME, generar_reporte_xlsx
from .models import RegistroExportacion
from .services import ServicioExportacion, ServicioPermisosExportacion, construir_nombre_archivo


@dataclass(frozen=True)
class ReporteOperativoConfig:
    slug: str
    tipo_documento: str
    nombre: str


@dataclass(frozen=True)
class ReporteOperativoData:
    slug: str
    nombre: str
    columnas: list[dict]
    filas: list[dict]
    filtros: dict
    sheets: list[ReporteSheet]


@dataclass(frozen=True)
class ArchivoReporteGenerado:
    contenido: bytes
    nombre_archivo: str
    content_type: str
    registro: RegistroExportacion


REPORTES_OPERATIVOS = {
    "actas-estado": ReporteOperativoConfig("actas-estado", RegistroExportacion.TIPO_REPORTE_ACTAS_ESTADO, "Reporte de actas por estado"),
    "actas-pendientes": ReporteOperativoConfig("actas-pendientes", RegistroExportacion.TIPO_REPORTE_ACTAS_PENDIENTES, "Reporte de actas pendientes de validación"),
    "inconformidades": ReporteOperativoConfig("inconformidades", RegistroExportacion.TIPO_REPORTE_INCONFORMIDADES, "Reporte de actas con inconformidades"),
    "sin-conformidad": ReporteOperativoConfig("sin-conformidad", RegistroExportacion.TIPO_REPORTE_ACTAS_SIN_CONFORMIDAD, "Reporte de actas sin conformidad"),
    "actas-formalizadas": ReporteOperativoConfig("actas-formalizadas", RegistroExportacion.TIPO_REPORTE_ACTAS_FORMALIZADAS, "Reporte de actas formalizadas"),
    "validaciones-acta": ReporteOperativoConfig("validaciones-acta", RegistroExportacion.TIPO_REPORTE_VALIDACIONES_ACTA, "Historial de validaciones de acta"),
    "exportaciones-realizadas": ReporteOperativoConfig("exportaciones-realizadas", RegistroExportacion.TIPO_REPORTE_EXPORTACIONES, "Reporte de exportaciones realizadas"),
}


ACTAS_COLUMNS = [
    {"key": "acta_id", "label": "ID acta"},
    {"key": "periodo", "label": "Periodo académico"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "semestre", "label": "Semestre"},
    {"key": "programa", "label": "Programa de asignatura"},
    {"key": "materia", "label": "Unidad de aprendizaje"},
    {"key": "docente", "label": "Docente"},
    {"key": "corte", "label": "Corte"},
    {"key": "estado_acta", "label": "Estado del acta"},
    {"key": "creado_en", "label": "Fecha de creación"},
    {"key": "publicada_en", "label": "Fecha de publicación"},
    {"key": "remitida_en", "label": "Fecha de remisión"},
    {"key": "validada_carrera_en", "label": "Fecha validación carrera"},
    {"key": "formalizada_en", "label": "Fecha de formalización"},
    {"key": "total_discentes", "label": "Total discentes"},
    {"key": "total_conformes", "label": "Total conformes / acuses"},
    {"key": "total_inconformes", "label": "Total inconformes"},
    {"key": "total_sin_conformidad", "label": "Total sin conformidad"},
    {"key": "documento_oficial", "label": "Documento oficial"},
    {"key": "observaciones", "label": "Observaciones operativas"},
]

PENDIENTES_COLUMNS = [
    {"key": "acta_id", "label": "ID acta"},
    {"key": "tipo_pendiente", "label": "Tipo de pendiente"},
    {"key": "periodo", "label": "Periodo académico"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "docente", "label": "Docente"},
    {"key": "corte", "label": "Corte"},
    {"key": "estado_actual", "label": "Estado actual"},
    {"key": "fecha_remision", "label": "Fecha de remisión"},
    {"key": "fecha_validacion_carrera", "label": "Fecha validación carrera"},
    {"key": "dias_estado", "label": "Días en estado actual"},
    {"key": "jefatura_responsable", "label": "Jefatura responsable esperada"},
    {"key": "cargo_responsable", "label": "Cargo responsable"},
    {"key": "prioridad", "label": "Prioridad operativa"},
    {"key": "observaciones", "label": "Observaciones"},
]

INCONFORMIDADES_COLUMNS = [
    {"key": "acta_id", "label": "ID acta"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "corte", "label": "Corte"},
    {"key": "estado_acta", "label": "Estado del acta"},
    {"key": "grado_discente", "label": "Grado/empleo del discente"},
    {"key": "nombre_discente", "label": "Nombre del discente"},
    {"key": "fecha_inconformidad", "label": "Fecha de inconformidad"},
    {"key": "comentario", "label": "Comentario de inconformidad"},
    {"key": "docente", "label": "Docente"},
    {"key": "publicada_en", "label": "Fecha de publicación"},
    {"key": "remitida_en", "label": "Fecha de remisión"},
    {"key": "formalizada_en", "label": "Fecha de formalización"},
    {"key": "estado_atencion", "label": "Estado de atención"},
    {"key": "observaciones", "label": "Observaciones"},
]

SIN_CONFORMIDAD_COLUMNS = [
    {"key": "acta_id", "label": "ID acta"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "corte", "label": "Corte"},
    {"key": "estado_acta", "label": "Estado del acta"},
    {"key": "grado_discente", "label": "Grado/empleo del discente"},
    {"key": "nombre_discente", "label": "Nombre del discente"},
    {"key": "publicada_en", "label": "Fecha de publicación"},
    {"key": "dias_desde_publicacion", "label": "Días desde publicación"},
    {"key": "docente", "label": "Docente"},
    {"key": "observacion", "label": "Observación"},
]

FORMALIZADAS_COLUMNS = [
    {"key": "acta_id", "label": "ID acta"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "corte", "label": "Corte"},
    {"key": "docente", "label": "Docente"},
    {"key": "formalizada_en", "label": "Fecha de formalización"},
    {"key": "validado_por", "label": "Jefatura de carrera que validó"},
    {"key": "formalizado_por", "label": "Jefatura académica que formalizó"},
    {"key": "total_discentes", "label": "Total discentes"},
    {"key": "promedio_acta", "label": "Promedio del acta"},
    {"key": "reprobados", "label": "Reprobados"},
    {"key": "estado_final", "label": "Estado final"},
]

VALIDACIONES_COLUMNS = [
    {"key": "validacion_id", "label": "ID validación"},
    {"key": "acta_id", "label": "ID acta"},
    {"key": "periodo", "label": "Periodo"},
    {"key": "carrera", "label": "Carrera"},
    {"key": "grupo", "label": "Grupo"},
    {"key": "asignatura", "label": "Asignatura"},
    {"key": "corte", "label": "Corte"},
    {"key": "estado_acta", "label": "Estado actual del acta"},
    {"key": "etapa", "label": "Etapa de validación"},
    {"key": "accion", "label": "Acción"},
    {"key": "usuario", "label": "Usuario firmante"},
    {"key": "grado_usuario", "label": "Grado/empleo del firmante"},
    {"key": "cargo", "label": "Cargo institucional"},
    {"key": "tipo_designacion", "label": "Tipo de designación"},
    {"key": "unidad", "label": "Unidad organizacional"},
    {"key": "fecha_hora", "label": "Fecha/hora"},
    {"key": "ip_origen", "label": "IP origen"},
    {"key": "observacion", "label": "Observación"},
]

EXPORTACIONES_COLUMNS = [
    {"key": "registro_id", "label": "ID registro"},
    {"key": "creado_en", "label": "Fecha/hora creación"},
    {"key": "finalizado_en", "label": "Fecha/hora finalización"},
    {"key": "usuario", "label": "Usuario"},
    {"key": "rol_contexto", "label": "Rol contexto"},
    {"key": "cargo_contexto", "label": "Cargo contexto"},
    {"key": "tipo_documento", "label": "Tipo de documento"},
    {"key": "formato", "label": "Formato"},
    {"key": "nombre_documento", "label": "Nombre documento"},
    {"key": "nombre_archivo", "label": "Nombre archivo"},
    {"key": "objeto_tipo", "label": "Objeto tipo"},
    {"key": "objeto_id", "label": "Objeto ID"},
    {"key": "objeto_repr", "label": "Objeto representación"},
    {"key": "estado", "label": "Estado"},
    {"key": "tamano_bytes", "label": "Tamaño bytes"},
    {"key": "hash_archivo", "label": "Hash archivo"},
    {"key": "ip_origen", "label": "IP origen"},
    {"key": "user_agent", "label": "User agent resumido"},
    {"key": "mensaje_error", "label": "Mensaje error"},
]


class ServicioReportesOperativos:
    def __init__(self, user, request=None):
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Autenticación requerida.")
        self.user = user
        self.request = request
        self.ctx = portal_context(user)
        self.permisos = ServicioPermisosExportacion(user)
        self.servicio_exportacion = ServicioExportacion(user, request=request)

    def vista_previa(self, slug: str, params) -> ReporteOperativoData:
        config = self._config(slug)
        self._validar_permiso(config.tipo_documento)
        filtros = self._filtros(params)
        sheets = self._build_sheets(slug, filtros)
        filas = [row for sheet in sheets if not _is_summary_sheet(sheet) for row in sheet.filas]
        columnas = sheets[0].columnas if sheets else []
        return ReporteOperativoData(
            slug=slug,
            nombre=config.nombre,
            columnas=columnas,
            filas=filas,
            filtros=filtros,
            sheets=sheets,
        )

    def exportar_xlsx(self, slug: str, params) -> ArchivoReporteGenerado:
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
        return ArchivoReporteGenerado(
            contenido=contenido,
            nombre_archivo=nombre_archivo,
            content_type=XLSX_MIME,
            registro=registro,
        )

    def _config(self, slug):
        if slug not in REPORTES_OPERATIVOS:
            raise PermissionDenied("Reporte no reconocido.")
        return REPORTES_OPERATIVOS[slug]

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
            "corte",
            "estado_acta",
            "estado",
            "tipo_pendiente",
            "fecha_desde",
            "fecha_hasta",
            "usuario",
            "tipo_documento",
            "formato",
            "estado_exportacion",
            "etapa_validacion",
            "accion",
            "cargo",
        )
        return {key: str(params.get(key, "")).strip() for key in keys if str(params.get(key, "")).strip()}

    def _build_sheets(self, slug, filtros):
        if slug == "actas-estado":
            rows = [self._acta_estado_row(acta) for acta in self._actas_queryset(filtros)]
            return [ReporteSheet("Detalle", ACTAS_COLUMNS, rows), self._summary_sheet("Resumen por estado", rows, "estado_acta")]
        if slug == "actas-pendientes":
            rows_carrera, rows_academica = self._pendientes_rows(filtros)
            return [
                ReporteSheet("Pendientes carrera", PENDIENTES_COLUMNS, rows_carrera),
                ReporteSheet("Pendientes académica", PENDIENTES_COLUMNS, rows_academica),
                self._summary_sheet("Resumen", rows_carrera + rows_academica, "tipo_pendiente"),
            ]
        if slug == "inconformidades":
            return [ReporteSheet("Inconformidades", INCONFORMIDADES_COLUMNS, self._inconformidades_rows(filtros))]
        if slug == "sin-conformidad":
            return [ReporteSheet("Sin conformidad", SIN_CONFORMIDAD_COLUMNS, self._sin_conformidad_rows(filtros))]
        if slug == "actas-formalizadas":
            return [ReporteSheet("Formalizadas", FORMALIZADAS_COLUMNS, self._formalizadas_rows(filtros))]
        if slug == "validaciones-acta":
            return [ReporteSheet("Validaciones", VALIDACIONES_COLUMNS, self._validaciones_rows(filtros))]
        if slug == "exportaciones-realizadas":
            rows = self._exportaciones_rows(filtros)
            return [ReporteSheet("Exportaciones", EXPORTACIONES_COLUMNS, rows), self._summary_sheet("Resumen por estado", rows, "estado")]
        return []

    def _actas_queryset(self, filtros):
        qs = Acta.objects.select_related(
            "asignacion_docente__usuario_docente",
            "asignacion_docente__grupo_academico__periodo",
            "asignacion_docente__programa_asignatura__materia",
            "asignacion_docente__programa_asignatura__plan_estudios__carrera",
        ).prefetch_related("detalles__conformidades", "validaciones")

        if self.ctx.is_discente:
            return qs.none()
        if self.ctx.is_docente and not self.ctx.has_consulta_amplia:
            return qs.none()
        if self.ctx.is_jefatura_carrera and not self.ctx.has_consulta_amplia:
            if not self.ctx.carrera_ids:
                return qs.none()
            qs = qs.filter(asignacion_docente__programa_asignatura__plan_estudios__carrera_id__in=self.ctx.carrera_ids)

        qs = self._apply_acta_filters(qs, filtros)
        return qs.order_by("asignacion_docente__grupo_academico__periodo__clave", "asignacion_docente__grupo_academico__clave_grupo", "id")

    def _apply_acta_filters(self, qs, filtros):
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
        if filtros.get("corte"):
            qs = qs.filter(corte_codigo=filtros["corte"])
        if filtros.get("estado_acta") or filtros.get("estado"):
            qs = qs.filter(estado_acta=filtros.get("estado_acta") or filtros.get("estado"))
        desde = parse_date(filtros.get("fecha_desde") or "")
        hasta = parse_date(filtros.get("fecha_hasta") or "")
        if desde:
            qs = qs.filter(creado_en__date__gte=desde)
        if hasta:
            qs = qs.filter(creado_en__date__lte=hasta)
        return qs

    def _acta_estado_row(self, acta):
        info = self._acta_info(acta)
        total, conformes, inconformes, sin_conformidad = self._conformidad_counts(acta)
        validacion_carrera = self._ultima_validacion(acta, ValidacionActa.ETAPA_JEFATURA_CARRERA)
        info.update(
            {
                "creado_en": _dt(acta.creado_en),
                "publicada_en": _dt(acta.publicada_en),
                "remitida_en": _dt(acta.remitida_en),
                "validada_carrera_en": _dt(validacion_carrera.fecha_hora if validacion_carrera else None),
                "formalizada_en": _dt(acta.formalizada_en),
                "total_discentes": total,
                "total_conformes": conformes,
                "total_inconformes": inconformes,
                "total_sin_conformidad": sin_conformidad,
                "documento_oficial": "Sí" if acta.estado_acta == Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA else "No",
                "observaciones": "",
            }
        )
        return info

    def _pendientes_rows(self, filtros):
        rows_carrera = [
            self._pendiente_row(acta, "Pendiente de jefatura de carrera", "Jefatura de carrera", "Jefe de carrera")
            for acta in self._actas_queryset({**filtros, "estado_acta": Acta.ESTADO_REMITIDO_JEFATURA_CARRERA})
        ]
        rows_academica = [
            self._pendiente_row(acta, "Pendiente de jefatura académica", "Jefatura académica", "Jefe académico")
            for acta in self._actas_queryset({**filtros, "estado_acta": Acta.ESTADO_VALIDADO_JEFATURA_CARRERA})
        ]
        tipo = filtros.get("tipo_pendiente")
        if tipo == "carrera":
            rows_academica = []
        elif tipo == "academica":
            rows_carrera = []
        return rows_carrera, rows_academica

    def _pendiente_row(self, acta, tipo, jefatura, cargo):
        info = self._acta_info(acta)
        base_fecha = acta.remitida_en or acta.actualizado_en or acta.creado_en
        info.update(
            {
                "tipo_pendiente": tipo,
                "asignatura": info["materia"],
                "estado_actual": info["estado_acta"],
                "fecha_remision": _dt(acta.remitida_en),
                "fecha_validacion_carrera": _dt(self._fecha_validacion(acta, ValidacionActa.ETAPA_JEFATURA_CARRERA)),
                "dias_estado": _dias_desde(base_fecha),
                "jefatura_responsable": jefatura,
                "cargo_responsable": cargo,
                "prioridad": "Alta" if _dias_desde(base_fecha) >= 5 else "Normal",
                "observaciones": "",
            }
        )
        return info

    def _inconformidades_rows(self, filtros):
        qs = ConformidadDiscente.objects.filter(
            vigente=True,
            estado_conformidad=ConformidadDiscente.ESTADO_INCONFORME,
        ).select_related(
            "detalle__acta__asignacion_docente__usuario_docente",
            "detalle__acta__asignacion_docente__grupo_academico__periodo",
            "detalle__acta__asignacion_docente__programa_asignatura__materia",
            "detalle__acta__asignacion_docente__programa_asignatura__plan_estudios__carrera",
            "discente__usuario__grado_empleo",
        )
        acta_ids = self._actas_queryset(filtros).values_list("id", flat=True)
        rows = []
        for conf in qs.filter(detalle__acta_id__in=acta_ids).order_by("-registrado_en"):
            acta = conf.detalle.acta
            info = self._acta_info(acta)
            info.update(
                {
                    "asignatura": info["materia"],
                    "grado_discente": _grado(conf.discente.usuario),
                    "nombre_discente": conf.discente.usuario.nombre_visible,
                    "fecha_inconformidad": _dt(conf.registrado_en),
                    "comentario": conf.comentario,
                    "publicada_en": _dt(acta.publicada_en),
                    "remitida_en": _dt(acta.remitida_en),
                    "formalizada_en": _dt(acta.formalizada_en),
                    "estado_atencion": "Pendiente de definición",
                    "observaciones": "",
                }
            )
            rows.append(info)
        return rows

    def _sin_conformidad_rows(self, filtros):
        estados = [
            Acta.ESTADO_PUBLICADO_DISCENTE,
            Acta.ESTADO_REMITIDO_JEFATURA_CARRERA,
            Acta.ESTADO_VALIDADO_JEFATURA_CARRERA,
            Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
        ]
        rows = []
        for acta in self._actas_queryset(filtros).filter(estado_acta__in=estados):
            info = self._acta_info(acta)
            for detalle in acta.detalles.select_related("inscripcion_materia__discente__usuario__grado_empleo"):
                discente = detalle.inscripcion_materia.discente
                if detalle.conformidades.filter(vigente=True).exists():
                    continue
                row = dict(info)
                row.update(
                    {
                        "asignatura": info["materia"],
                        "grado_discente": _grado(discente.usuario),
                        "nombre_discente": discente.usuario.nombre_visible,
                        "publicada_en": _dt(acta.publicada_en),
                        "dias_desde_publicacion": _dias_desde(acta.publicada_en),
                        "observacion": "Sin conformidad vigente registrada",
                    }
                )
                rows.append(row)
        return rows

    def _formalizadas_rows(self, filtros):
        rows = []
        for acta in self._actas_queryset({**filtros, "estado_acta": Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA}):
            info = self._acta_info(acta)
            valores = [value for value in (_detalle_resultado(detalle) for detalle in acta.detalles.all()) if value is not None]
            promedio = _promedio(valores)
            reprobados = sum(1 for value in valores if Decimal(value) < Decimal("6.0"))
            info.update(
                {
                    "asignatura": info["materia"],
                    "formalizada_en": _dt(acta.formalizada_en),
                    "validado_por": _usuario_validacion(acta, ValidacionActa.ETAPA_JEFATURA_CARRERA),
                    "formalizado_por": _usuario_validacion(acta, ValidacionActa.ETAPA_JEFATURA_ACADEMICA),
                    "total_discentes": acta.detalles.count(),
                    "promedio_acta": f"{promedio:.1f}" if promedio is not None else "N/A",
                    "reprobados": reprobados,
                    "estado_final": acta.get_estado_acta_display(),
                }
            )
            rows.append(info)
        return rows

    def _validaciones_rows(self, filtros):
        qs = ValidacionActa.objects.select_related(
            "acta__asignacion_docente__grupo_academico__periodo",
            "acta__asignacion_docente__programa_asignatura__materia",
            "acta__asignacion_docente__programa_asignatura__plan_estudios__carrera",
            "usuario__grado_empleo",
            "asignacion_cargo__unidad_organizacional",
        )
        acta_ids = self._actas_queryset(filtros).values_list("id", flat=True)
        qs = qs.filter(acta_id__in=acta_ids)
        if filtros.get("etapa_validacion"):
            qs = qs.filter(etapa_validacion=filtros["etapa_validacion"])
        if filtros.get("accion"):
            qs = qs.filter(accion=filtros["accion"])
        if filtros.get("usuario"):
            value = filtros["usuario"]
            qs = qs.filter(Q(usuario__nombre_completo__icontains=value) | Q(usuario__username__icontains=value) | Q(usuario_id=_int_or_none(value)))
        if filtros.get("cargo"):
            qs = qs.filter(asignacion_cargo__cargo_codigo=filtros["cargo"])
        desde = parse_date(filtros.get("fecha_desde") or "")
        hasta = parse_date(filtros.get("fecha_hasta") or "")
        if desde:
            qs = qs.filter(fecha_hora__date__gte=desde)
        if hasta:
            qs = qs.filter(fecha_hora__date__lte=hasta)
        rows = []
        for validacion in qs.order_by("-fecha_hora"):
            acta = validacion.acta
            info = self._acta_info(acta)
            cargo = validacion.asignacion_cargo
            rows.append(
                {
                    "validacion_id": validacion.id,
                    "acta_id": acta.id,
                    "periodo": info["periodo"],
                    "carrera": info["carrera"],
                    "grupo": info["grupo"],
                    "asignatura": info["materia"],
                    "corte": info["corte"],
                    "estado_acta": info["estado_acta"],
                    "etapa": validacion.get_etapa_validacion_display(),
                    "accion": validacion.get_accion_display(),
                    "usuario": validacion.usuario.nombre_visible,
                    "grado_usuario": _grado(validacion.usuario),
                    "cargo": cargo.get_cargo_codigo_display() if cargo else "",
                    "tipo_designacion": cargo.get_tipo_designacion_display() if cargo else "",
                    "unidad": cargo.unidad_organizacional.nombre if cargo and cargo.unidad_organizacional_id else "",
                    "fecha_hora": _dt(validacion.fecha_hora),
                    "ip_origen": validacion.ip_origen or "",
                    "observacion": validacion.comentario,
                }
            )
        return rows

    def _exportaciones_rows(self, filtros):
        qs = RegistroExportacion.objects.select_related("usuario")
        if not self.permisos.puede_auditar_exportaciones:
            qs = qs.filter(usuario=self.user)
        qs = self._apply_exportacion_filters(qs, filtros)
        return [
            {
                "registro_id": item.id,
                "creado_en": _dt(item.creado_en),
                "finalizado_en": _dt(item.finalizado_en),
                "usuario": item.usuario.nombre_visible,
                "rol_contexto": item.rol_contexto,
                "cargo_contexto": item.cargo_contexto,
                "tipo_documento": item.get_tipo_documento_display(),
                "formato": item.formato,
                "nombre_documento": item.nombre_documento,
                "nombre_archivo": item.nombre_archivo,
                "objeto_tipo": item.objeto_tipo,
                "objeto_id": item.objeto_id,
                "objeto_repr": item.objeto_repr,
                "estado": item.get_estado_display(),
                "tamano_bytes": item.tamano_bytes or "",
                "hash_archivo": item.hash_archivo,
                "ip_origen": item.ip_origen or "",
                "user_agent": (item.user_agent or "")[:120],
                "mensaje_error": item.mensaje_error,
            }
            for item in qs.order_by("-creado_en")[:1000]
        ]

    def _apply_exportacion_filters(self, qs, filtros):
        desde = parse_date(filtros.get("fecha_desde") or "")
        hasta = parse_date(filtros.get("fecha_hasta") or "")
        if desde:
            qs = qs.filter(creado_en__date__gte=desde)
        if hasta:
            qs = qs.filter(creado_en__date__lte=hasta)
        if filtros.get("usuario"):
            value = filtros["usuario"]
            qs = qs.filter(Q(usuario__username__icontains=value) | Q(usuario__nombre_completo__icontains=value) | Q(usuario_id=_int_or_none(value)))
        if filtros.get("tipo_documento"):
            qs = qs.filter(tipo_documento=filtros["tipo_documento"])
        if filtros.get("formato"):
            qs = qs.filter(formato=filtros["formato"].upper())
        if filtros.get("estado_exportacion") or filtros.get("estado"):
            qs = qs.filter(estado=(filtros.get("estado_exportacion") or filtros.get("estado")).upper())
        return qs

    def _acta_info(self, acta):
        asignacion = acta.asignacion_docente
        grupo = asignacion.grupo_academico
        programa = asignacion.programa_asignatura
        materia = programa.materia
        carrera = programa.plan_estudios.carrera
        return {
            "acta_id": acta.id,
            "periodo": grupo.periodo.clave,
            "carrera": carrera.clave,
            "grupo": grupo.clave_grupo,
            "semestre": grupo.semestre_numero,
            "programa": str(programa),
            "materia": materia.nombre,
            "docente": asignacion.usuario_docente.nombre_visible,
            "corte": acta.get_corte_codigo_display(),
            "estado_acta": acta.get_estado_acta_display(),
        }

    def _conformidad_counts(self, acta):
        total = acta.detalles.count()
        conformidades = ConformidadDiscente.objects.filter(detalle__acta=acta, vigente=True)
        conformes = conformidades.filter(
            estado_conformidad__in=[ConformidadDiscente.ESTADO_ACUSE, ConformidadDiscente.ESTADO_CONFORME],
        ).count()
        inconformes = conformidades.filter(estado_conformidad=ConformidadDiscente.ESTADO_INCONFORME).count()
        con_registro = conformidades.values("detalle_id").distinct().count()
        return total, conformes, inconformes, max(total - con_registro, 0)

    def _ultima_validacion(self, acta, etapa):
        return acta.validaciones.filter(etapa_validacion=etapa).order_by("-fecha_hora").first()

    def _fecha_validacion(self, acta, etapa):
        validacion = self._ultima_validacion(acta, etapa)
        return validacion.fecha_hora if validacion else None

    def _summary_sheet(self, title, rows, key):
        counts = {}
        for row in rows:
            value = row.get(key) or "Sin dato"
            counts[value] = counts.get(value, 0) + 1
        summary_rows = [{"categoria": category, "total": total} for category, total in sorted(counts.items())]
        return ReporteSheet(title, [{"key": "categoria", "label": "Categoría"}, {"key": "total", "label": "Total"}], summary_rows)

    def _objeto_repr_filtros(self, filtros):
        parts = [filtros.get("periodo"), filtros.get("carrera"), filtros.get("grupo")]
        return "-".join(part for part in parts if part) or ""


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _dt(value):
    return timezone.localtime(value).strftime("%Y-%m-%d %H:%M") if value else ""


def _dias_desde(value):
    if not value:
        return ""
    value_date = timezone.localdate(value) if hasattr(value, "hour") else value
    return (timezone.localdate() - value_date).days


def _grado(user):
    return user.grado_empleo.abreviatura if getattr(user, "grado_empleo_id", None) else ""


def _promedio(values):
    if not values:
        return None
    decimals = [Decimal(value) for value in values]
    return sum(decimals, Decimal("0")) / Decimal(len(decimals))


def _usuario_validacion(acta, etapa):
    validacion = acta.validaciones.filter(etapa_validacion=etapa).order_by("-fecha_hora").first()
    return validacion.usuario.nombre_visible if validacion else "Pendiente"


def _detalle_resultado(detalle):
    for value in (
        detalle.resultado_corte_visible,
        detalle.resultado_final_preliminar_visible,
        detalle.resultado_corte,
    ):
        if value is not None:
            return value
    return None


def _is_summary_sheet(sheet):
    keys = {column["key"] for column in sheet.columnas}
    return keys == {"categoria", "total"}
