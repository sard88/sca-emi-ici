from dataclasses import dataclass

from .models import RegistroExportacion


ROL_ADMIN = "ADMIN"
ROL_ADMIN_SISTEMA = "ADMIN_SISTEMA"
ROL_ESTADISTICA = "ENCARGADO_ESTADISTICA"
ROL_ESTADISTICA_ALT = "ESTADISTICA"
ROL_DOCENTE = "DOCENTE"
ROL_DISCENTE = "DISCENTE"
ROL_JEFE_CARRERA = "JEFE_CARRERA"
ROL_JEFATURA_CARRERA = "JEFATURA_CARRERA"
ROL_JEFE_SUB_EJEC_CTR = "JEFE_SUB_EJEC_CTR"
ROL_JEFE_ACADEMICO = "JEFE_ACADEMICO"
ROL_JEFATURA_ACADEMICA = "JEFATURA_ACADEMICA"
ROL_JEFE_PEDAGOGICA = "JEFE_PEDAGOGICA"
ROL_JEFE_SUB_PLAN_EVAL = "JEFE_SUB_PLAN_EVAL"

ROLES_ADMIN = {ROL_ADMIN, ROL_ADMIN_SISTEMA}
ROLES_ESTADISTICA = {ROL_ESTADISTICA, ROL_ESTADISTICA_ALT}
ROLES_JEFATURA_CARRERA = {ROL_JEFE_CARRERA, ROL_JEFATURA_CARRERA, ROL_JEFE_SUB_EJEC_CTR}
ROLES_JEFATURA_ACADEMICA = {ROL_JEFE_ACADEMICO, ROL_JEFATURA_ACADEMICA}
ROLES_JEFATURA_PEDAGOGICA = {ROL_JEFE_PEDAGOGICA, ROL_JEFE_SUB_PLAN_EVAL}
ROLES_AUTORIDAD = ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA


@dataclass(frozen=True)
class ExportacionCatalogoItem:
    codigo: str
    nombre: str
    descripcion: str
    formatos_soportados: tuple[str, ...]
    implementado: bool
    requiere_objeto: bool
    roles_sugeridos: tuple[str, ...]
    bloque_origen: str
    nota: str

    def as_dict(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "formatos_soportados": list(self.formatos_soportados),
            "implementado": self.implementado,
            "requiere_objeto": self.requiere_objeto,
            "roles_sugeridos": list(self.roles_sugeridos),
            "bloque_origen": self.bloque_origen,
            "nota": self.nota,
        }


CATALOGO_EXPORTACIONES = (
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL,
        nombre="Acta de evaluación parcial",
        descripcion="Documento formal de corte parcial asociado a una asignación docente.",
        formatos_soportados=(RegistroExportacion.FORMATO_PDF, RegistroExportacion.FORMATO_XLSX),
        implementado=True,
        requiere_objeto=True,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA | {ROL_DOCENTE})),
        bloque_origen="9B",
        nota="Implementado en Bloque 9B con auditoría de exportación.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_ACTA_EVALUACION_FINAL,
        nombre="Acta de evaluación final",
        descripcion="Documento formal del corte de evaluación final.",
        formatos_soportados=(RegistroExportacion.FORMATO_PDF, RegistroExportacion.FORMATO_XLSX),
        implementado=True,
        requiere_objeto=True,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA | {ROL_DOCENTE})),
        bloque_origen="9B",
        nota="Implementado en Bloque 9B con componentes de evaluación final.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_ACTA_CALIFICACION_FINAL,
        nombre="Acta de calificación final",
        descripcion="Documento consolidado de calificación final por asignatura/grupo.",
        formatos_soportados=(RegistroExportacion.FORMATO_PDF, RegistroExportacion.FORMATO_XLSX),
        implementado=True,
        requiere_objeto=True,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA | {ROL_DOCENTE})),
        bloque_origen="9B",
        nota="Implementado en Bloque 9B como documento consolidado derivado.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_KARDEX_OFICIAL,
        nombre="Kárdex oficial",
        descripcion="Vista oficial derivada del historial académico consolidado.",
        formatos_soportados=(RegistroExportacion.FORMATO_PDF,),
        implementado=True,
        requiere_objeto=True,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA)),
        bloque_origen="9C",
        nota="PDF implementado en Bloque 9C desde ServicioKardex; no visible ni exportable para discentes. XLSX queda pendiente.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_HISTORIAL_ACADEMICO,
        nombre="Historial académico interno",
        descripcion="Trayectoria académica interna para consulta autorizada.",
        formatos_soportados=(RegistroExportacion.FORMATO_PDF,),
        implementado=False,
        requiere_objeto=True,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA)),
        bloque_origen="9C",
        nota="Documento interno; no sustituye kárdex oficial.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_ACTAS_ESTADO,
        nombre="Actas por estado",
        descripcion="Reporte operativo de actas agrupadas por estado de flujo.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX,),
        implementado=True,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA)),
        bloque_origen="9F",
        nota="XLSX implementado en Bloque 9F-J-L. PDF queda pendiente.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_ACTAS_PENDIENTES,
        nombre="Actas pendientes de validación",
        descripcion="Reporte de actas pendientes por etapa de validación.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX,),
        implementado=True,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA)),
        bloque_origen="9F",
        nota="XLSX implementado en Bloque 9F-J-L. PDF queda pendiente.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_INCONFORMIDADES,
        nombre="Actas con inconformidades",
        descripcion="Reporte operativo de inconformidades registradas por discentes.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX,),
        implementado=True,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA)),
        bloque_origen="9F",
        nota="XLSX implementado en Bloque 9F-J-L. La conformidad del discente sigue siendo informativa y no bloqueante.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_ACTAS_SIN_CONFORMIDAD,
        nombre="Actas sin conformidad de discentes",
        descripcion="Reporte de discentes incluidos en actas publicadas o superiores sin conformidad vigente.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX,),
        implementado=True,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA)),
        bloque_origen="9F",
        nota="XLSX implementado en Bloque 9F-J-L. No bloquea el avance del acta.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_ACTAS_FORMALIZADAS,
        nombre="Actas formalizadas",
        descripcion="Reporte operativo de actas formalizadas por periodo, carrera y grupo.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX,),
        implementado=True,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA)),
        bloque_origen="9F",
        nota="XLSX implementado en Bloque 9F-J-L. PDF queda pendiente.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_DESEMPENO,
        nombre="Reporte de desempeño académico",
        descripcion="Aprobados, reprobados, promedios, exentos y extraordinarios.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX, RegistroExportacion.FORMATO_PDF),
        implementado=False,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA)),
        bloque_origen="9G",
        nota="Pendiente de indicadores institucionales.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_SITUACION_ACADEMICA,
        nombre="Reporte de situación académica",
        descripcion="Bajas, reingresos, situación vigente y trayectoria institucional.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX, RegistroExportacion.FORMATO_PDF),
        implementado=False,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA)),
        bloque_origen="9I",
        nota="Pendiente de reportes de situación académica.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_VALIDACIONES_ACTA,
        nombre="Historial de validaciones de acta",
        descripcion="Reporte de trazabilidad de validaciones y remisiones de actas.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX,),
        implementado=True,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA)),
        bloque_origen="9J",
        nota="XLSX implementado en Bloque 9F-J-L. PDF queda pendiente.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_EXPORTACIONES,
        nombre="Exportaciones realizadas",
        descripcion="Consulta institucional de salidas documentales registradas.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX,),
        implementado=True,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_ACADEMICA)),
        bloque_origen="9L",
        nota="XLSX implementado en Bloque 9F-J-L con filtros sanitizados. CSV/PDF quedan pendientes.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_REPORTE_MOVIMIENTOS_ACADEMICOS,
        nombre="Movimientos académicos",
        descripcion="Altas, bajas y cambios de grupo con trazabilidad operativa.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX, RegistroExportacion.FORMATO_PDF),
        implementado=False,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA | ROLES_JEFATURA_CARRERA | ROLES_JEFATURA_ACADEMICA)),
        bloque_origen="9F",
        nota="Pendiente de reporte operativo.",
    ),
    ExportacionCatalogoItem(
        codigo=RegistroExportacion.TIPO_AUDITORIA_EVENTOS,
        nombre="Auditoría de eventos",
        descripcion="Reporte futuro de eventos críticos del sistema.",
        formatos_soportados=(RegistroExportacion.FORMATO_XLSX, RegistroExportacion.FORMATO_CSV),
        implementado=False,
        requiere_objeto=False,
        roles_sugeridos=tuple(sorted(ROLES_ADMIN | ROLES_ESTADISTICA)),
        bloque_origen="9I",
        nota="Pendiente de bitácora transversal formal.",
    ),
)

CATALOGO_POR_CODIGO = {item.codigo: item for item in CATALOGO_EXPORTACIONES}
