from dataclasses import dataclass
from datetime import datetime
import re
import unicodedata

from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from core.portal_services import portal_context

from .catalogo import CATALOGO_EXPORTACIONES, CATALOGO_POR_CODIGO
from .models import RegistroExportacion

SENSITIVE_KEYWORDS = (
    "password",
    "passwd",
    "token",
    "secret",
    "session",
    "cookie",
    "authorization",
    "csrf",
    "credential",
    "contrasena",
    "contraseña",
    "clave_privada",
)


@dataclass(frozen=True)
class ExportacionResultado:
    registro: RegistroExportacion
    contenido: bytes | None = None
    content_type: str = "application/octet-stream"


class CatalogoExportaciones:
    @classmethod
    def todos(cls):
        return CATALOGO_EXPORTACIONES

    @classmethod
    def obtener(cls, codigo: str):
        return CATALOGO_POR_CODIGO.get(codigo)

    @classmethod
    def filtrado_para_usuario(cls, user):
        permisos = ServicioPermisosExportacion(user)
        items = []
        for item in cls.todos():
            if not permisos.puede_ver_tipo(item.codigo):
                continue
            disponible, motivo = permisos.estado_disponibilidad(item)
            data = item.as_dict()
            data.update({"disponible": disponible, "motivo_no_disponible": motivo})
            items.append(data)
        return items


class ServicioPermisosExportacion:
    def __init__(self, user):
        self.user = user
        self.ctx = portal_context(user) if getattr(user, "is_authenticated", False) else None

    @property
    def roles(self):
        return self.ctx.roles if self.ctx else set()

    @property
    def is_admin(self):
        return bool(self.ctx and self.ctx.is_admin)

    @property
    def is_estadistica(self):
        return bool(self.ctx and self.ctx.is_estadistica)

    @property
    def is_docente(self):
        return bool(self.ctx and self.ctx.is_docente)

    @property
    def is_discente(self):
        return bool(self.ctx and self.ctx.is_discente)

    @property
    def is_jefatura_carrera(self):
        return bool(self.ctx and self.ctx.is_jefatura_carrera)

    @property
    def is_jefatura_academica(self):
        return bool(self.ctx and self.ctx.is_jefatura_academica)

    @property
    def is_jefatura_pedagogica(self):
        return bool(self.ctx and self.ctx.is_jefatura_pedagogica)

    @property
    def puede_auditar_exportaciones(self):
        return self.is_admin or self.is_estadistica or self.is_jefatura_academica

    def puede_ver_tipo(self, tipo_documento: str) -> bool:
        if not self.ctx:
            return False
        if self.is_admin:
            return True
        if tipo_documento == RegistroExportacion.TIPO_OTRO:
            return self.is_admin or self.is_estadistica
        item = CatalogoExportaciones.obtener(tipo_documento)
        if not item:
            return False
        if self.is_discente:
            return False
        if self.is_docente:
            return tipo_documento in {
                RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL,
                RegistroExportacion.TIPO_ACTA_EVALUACION_FINAL,
                RegistroExportacion.TIPO_ACTA_CALIFICACION_FINAL,
            }
        if self.is_estadistica:
            return True
        if self.is_jefatura_carrera:
            return tipo_documento in {
                RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL,
                RegistroExportacion.TIPO_ACTA_EVALUACION_FINAL,
                RegistroExportacion.TIPO_ACTA_CALIFICACION_FINAL,
                RegistroExportacion.TIPO_KARDEX_OFICIAL,
                RegistroExportacion.TIPO_HISTORIAL_ACADEMICO,
                RegistroExportacion.TIPO_REPORTE_ACTAS_ESTADO,
                RegistroExportacion.TIPO_REPORTE_ACTAS_PENDIENTES,
                RegistroExportacion.TIPO_REPORTE_INCONFORMIDADES,
                RegistroExportacion.TIPO_REPORTE_ACTAS_SIN_CONFORMIDAD,
                RegistroExportacion.TIPO_REPORTE_ACTAS_FORMALIZADAS,
                RegistroExportacion.TIPO_REPORTE_DESEMPENO,
                RegistroExportacion.TIPO_REPORTE_APROBADOS_REPROBADOS,
                RegistroExportacion.TIPO_REPORTE_PROMEDIOS_ACADEMICOS,
                RegistroExportacion.TIPO_REPORTE_DISTRIBUCION_CALIFICACIONES,
                RegistroExportacion.TIPO_REPORTE_EXENTOS,
                RegistroExportacion.TIPO_REPORTE_DESEMPENO_DOCENTE,
                RegistroExportacion.TIPO_REPORTE_DESEMPENO_COHORTE,
                RegistroExportacion.TIPO_REPORTE_REPROBADOS_NOMINAL,
                RegistroExportacion.TIPO_CUADRO_APROVECHAMIENTO,
                RegistroExportacion.TIPO_REPORTE_SITUACION_ACADEMICA,
                RegistroExportacion.TIPO_REPORTE_EXTRAORDINARIOS,
                RegistroExportacion.TIPO_REPORTE_BAJAS_TEMPORALES,
                RegistroExportacion.TIPO_REPORTE_BAJAS_DEFINITIVAS,
                RegistroExportacion.TIPO_REPORTE_REINGRESOS,
                RegistroExportacion.TIPO_REPORTE_EGRESADOS_EGRESABLES,
                RegistroExportacion.TIPO_REPORTE_SITUACION_ACADEMICA_AGREGADO,
                RegistroExportacion.TIPO_REPORTE_VALIDACIONES_ACTA,
                RegistroExportacion.TIPO_REPORTE_MOVIMIENTOS_ACADEMICOS,
                RegistroExportacion.TIPO_REPORTE_CAMBIOS_GRUPO,
                RegistroExportacion.TIPO_REPORTE_HISTORIAL_ACADEMICO_INTERNO,
            }
        if self.is_jefatura_academica or self.is_jefatura_pedagogica:
            return tipo_documento in {
                RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL,
                RegistroExportacion.TIPO_ACTA_EVALUACION_FINAL,
                RegistroExportacion.TIPO_ACTA_CALIFICACION_FINAL,
                RegistroExportacion.TIPO_KARDEX_OFICIAL,
                RegistroExportacion.TIPO_HISTORIAL_ACADEMICO,
                RegistroExportacion.TIPO_REPORTE_ACTAS_ESTADO,
                RegistroExportacion.TIPO_REPORTE_ACTAS_PENDIENTES,
                RegistroExportacion.TIPO_REPORTE_INCONFORMIDADES,
                RegistroExportacion.TIPO_REPORTE_ACTAS_SIN_CONFORMIDAD,
                RegistroExportacion.TIPO_REPORTE_ACTAS_FORMALIZADAS,
                RegistroExportacion.TIPO_REPORTE_DESEMPENO,
                RegistroExportacion.TIPO_REPORTE_APROBADOS_REPROBADOS,
                RegistroExportacion.TIPO_REPORTE_PROMEDIOS_ACADEMICOS,
                RegistroExportacion.TIPO_REPORTE_DISTRIBUCION_CALIFICACIONES,
                RegistroExportacion.TIPO_REPORTE_EXENTOS,
                RegistroExportacion.TIPO_REPORTE_DESEMPENO_DOCENTE,
                RegistroExportacion.TIPO_REPORTE_DESEMPENO_COHORTE,
                RegistroExportacion.TIPO_REPORTE_REPROBADOS_NOMINAL,
                RegistroExportacion.TIPO_CUADRO_APROVECHAMIENTO,
                RegistroExportacion.TIPO_REPORTE_SITUACION_ACADEMICA,
                RegistroExportacion.TIPO_REPORTE_EXTRAORDINARIOS,
                RegistroExportacion.TIPO_REPORTE_BAJAS_TEMPORALES,
                RegistroExportacion.TIPO_REPORTE_BAJAS_DEFINITIVAS,
                RegistroExportacion.TIPO_REPORTE_REINGRESOS,
                RegistroExportacion.TIPO_REPORTE_EGRESADOS_EGRESABLES,
                RegistroExportacion.TIPO_REPORTE_SITUACION_ACADEMICA_AGREGADO,
                RegistroExportacion.TIPO_REPORTE_VALIDACIONES_ACTA,
                RegistroExportacion.TIPO_REPORTE_EXPORTACIONES,
                RegistroExportacion.TIPO_REPORTE_MOVIMIENTOS_ACADEMICOS,
                RegistroExportacion.TIPO_REPORTE_CAMBIOS_GRUPO,
                RegistroExportacion.TIPO_HISTORIAL_ACADEMICO,
                RegistroExportacion.TIPO_REPORTE_HISTORIAL_ACADEMICO_INTERNO,
            }
        return False

    def puede_exportar(self, tipo_documento: str, formato: str, objeto=None) -> bool:
        if not self.puede_ver_tipo(tipo_documento):
            return False
        if tipo_documento == RegistroExportacion.TIPO_OTRO:
            return self.is_admin or self.is_estadistica
        item = CatalogoExportaciones.obtener(tipo_documento)
        if not item or formato not in item.formatos_soportados:
            return False
        # 9A no genera documentos finales. Solo la auditoría metadata queda operable.
        return item.implementado

    def estado_disponibilidad(self, item):
        if not self.puede_ver_tipo(item.codigo):
            return False, "No autorizado para tu perfil."
        if not item.implementado:
            return False, "Generación documental pendiente para un subbloque posterior."
        return True, ""


def normalizar_fragmento_archivo(value: str, *, fallback="documento") -> str:
    value = value or fallback
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or fallback


def construir_nombre_archivo(tipo_documento: str, formato: str, objeto_repr="", *, timestamp=None) -> str:
    item = CatalogoExportaciones.obtener(tipo_documento)
    base = normalizar_fragmento_archivo(item.nombre if item else tipo_documento)
    partes = [base]
    if objeto_repr:
        partes.append(normalizar_fragmento_archivo(objeto_repr, fallback="objeto")[:80])
    marca = timestamp or timezone.now()
    if isinstance(marca, datetime):
        partes.append(marca.strftime("%Y%m%d-%H%M%S"))
    else:
        partes.append(str(marca))
    extension = normalizar_fragmento_archivo(formato, fallback="dat")
    return f"{'_'.join(partes)}.{extension}"


def limpiar_json_seguro(value):
    if not isinstance(value, dict):
        return {}

    def clean(obj):
        if isinstance(obj, dict):
            cleaned = {}
            for key, inner_value in obj.items():
                key_str = str(key)
                key_lower = normalizar_fragmento_archivo(key_str, fallback="campo")
                if any(sensitive in key_lower for sensitive in SENSITIVE_KEYWORDS):
                    continue
                cleaned[key_str] = clean(inner_value)
            return cleaned
        if isinstance(obj, list):
            return [clean(item) for item in obj]
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        return str(obj)

    return clean(value)


def obtener_ip_request(request):
    if not request:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def obtener_user_agent(request):
    if not request:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")[:300]


class ServicioExportacion:
    def __init__(self, user, request=None):
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Usuario autenticado requerido para exportar.")
        self.user = user
        self.request = request
        self.ctx = portal_context(user)
        self.permisos = ServicioPermisosExportacion(user)

    def registrar_solicitud(
        self,
        *,
        tipo_documento: str,
        formato: str,
        nombre_documento: str = "",
        nombre_archivo: str = "",
        objeto=None,
        objeto_tipo: str = "",
        objeto_id: str = "",
        objeto_repr: str = "",
        filtros=None,
        parametros=None,
        validar_disponible: bool = True,
    ) -> RegistroExportacion:
        formato = (formato or "").upper()
        if formato not in dict(RegistroExportacion.FORMATO_CHOICES):
            raise ValidationError({"formato": "Formato de exportación no soportado."})

        item = CatalogoExportaciones.obtener(tipo_documento)
        if tipo_documento != RegistroExportacion.TIPO_OTRO and not item:
            raise ValidationError({"tipo_documento": "Tipo de documento no reconocido."})

        if validar_disponible and not self.permisos.puede_exportar(tipo_documento, formato, objeto=objeto):
            raise PermissionDenied("No tienes permiso para exportar este documento o todavía no está implementado.")
        if not validar_disponible and not self.permisos.puede_ver_tipo(tipo_documento):
            raise PermissionDenied("No tienes permiso para registrar este tipo de exportación.")

        objeto_tipo_final = objeto_tipo
        objeto_id_final = str(objeto_id or "")
        objeto_repr_final = str(objeto_repr or "")[:240]
        if objeto is not None:
            objeto_tipo_final = objeto_tipo_final or f"{objeto.__class__.__module__}.{objeto.__class__.__name__}"
            objeto_id_final = objeto_id_final or str(getattr(objeto, "pk", ""))
            objeto_repr_final = objeto_repr_final or str(objeto)[:240]

        nombre_documento_final = nombre_documento or (item.nombre if item else "Evento de exportación")
        nombre_archivo_final = nombre_archivo or construir_nombre_archivo(
            tipo_documento,
            formato,
            objeto_repr=objeto_repr_final or nombre_documento_final,
        )

        cargo_contexto = self.ctx.cargos[0].cargo_codigo if self.ctx.cargos else ""
        registro = RegistroExportacion.objects.create(
            usuario=self.user,
            tipo_documento=tipo_documento,
            formato=formato,
            nombre_documento=nombre_documento_final[:180],
            nombre_archivo=nombre_archivo_final[:220],
            objeto_tipo=objeto_tipo_final[:120],
            objeto_id=objeto_id_final[:80],
            objeto_repr=objeto_repr_final,
            filtros_json=limpiar_json_seguro(filtros or {}),
            parametros_json=limpiar_json_seguro(parametros or {}),
            rol_contexto=self.ctx.perfil or "",
            cargo_contexto=cargo_contexto,
            ip_origen=obtener_ip_request(self.request),
            user_agent=obtener_user_agent(self.request),
            estado=RegistroExportacion.ESTADO_SOLICITADA,
        )
        return registro

    def marcar_generada(self, registro: RegistroExportacion, *, tamano_bytes=None, hash_archivo=""):
        self._validar_dueno_o_auditor(registro)
        registro.marcar_generada(tamano_bytes=tamano_bytes, hash_archivo=hash_archivo)
        return registro

    def marcar_fallida(self, registro: RegistroExportacion, mensaje_error):
        self._validar_dueno_o_auditor(registro)
        registro.marcar_fallida(mensaje_error)
        return registro

    def registrar_evento_prueba(self, *, formato=RegistroExportacion.FORMATO_PDF, filtros=None, parametros=None):
        if not (self.permisos.is_admin or self.permisos.is_estadistica):
            raise PermissionDenied("Solo Admin o Estadística pueden registrar eventos técnicos de prueba.")
        registro = self.registrar_solicitud(
            tipo_documento=RegistroExportacion.TIPO_OTRO,
            formato=formato,
            nombre_documento="Evento técnico de prueba de exportación",
            objeto_tipo="reportes.validacion_tecnica",
            objeto_repr="Bloque 9A",
            filtros=filtros or {},
            parametros=parametros or {},
            validar_disponible=False,
        )
        registro.marcar_generada(tamano_bytes=0, hash_archivo="")
        return ExportacionResultado(registro=registro, contenido=b"")

    def _validar_dueno_o_auditor(self, registro):
        if registro.usuario_id == self.user.id or self.permisos.puede_auditar_exportaciones:
            return
        raise PermissionDenied("No tienes permiso para modificar este registro de exportación.")
