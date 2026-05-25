import logging
from contextlib import contextmanager
from decimal import Decimal

from django.conf import settings
from django.db import DatabaseError

from core.portal_services import portal_context

from .eventos import (
    MODULO_SISTEMA,
    RESULTADO_BLOQUEADO,
    RESULTADO_EXITOSO,
    RESULTADO_FALLIDO,
    SEVERIDAD_INFO,
    nombre_evento,
)
from .models import BitacoraEventoCritico

logger = logging.getLogger(__name__)

SENSITIVE_KEYS = {
    "password",
    "password1",
    "password2",
    "passwd",
    "token",
    "access",
    "refresh",
    "secret",
    "session",
    "cookie",
    "authorization",
    "csrf",
    "csrfmiddlewaretoken",
    "api_key",
    "credential",
    "firma",
    "private_key",
    "clave_privada",
}
MAX_STRING_LENGTH = 500
MAX_LIST_ITEMS = 20


def _is_sensitive_key(key):
    key_lower = str(key).lower().replace("-", "_")
    return any(sensitive in key_lower for sensitive in SENSITIVE_KEYS)


def _json_safe(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str) and len(value) > MAX_STRING_LENGTH:
            return value[:MAX_STRING_LENGTH] + "...[truncado]"
        return value
    return str(value)[:MAX_STRING_LENGTH]


def limpiar_payload_auditoria(value):
    if value is None:
        return {}
    if isinstance(value, dict):
        cleaned = {}
        for key, inner in value.items():
            if _is_sensitive_key(key):
                cleaned[str(key)] = "[REDACTADO]"
                continue
            cleaned[str(key)] = limpiar_payload_auditoria(inner)
        return cleaned
    if isinstance(value, (list, tuple, set)):
        items = list(value)
        cleaned = [limpiar_payload_auditoria(item) for item in items[:MAX_LIST_ITEMS]]
        if len(items) > MAX_LIST_ITEMS:
            cleaned.append({"total_elementos_no_incluidos": len(items) - MAX_LIST_ITEMS})
        return cleaned
    if hasattr(value, "read") or hasattr(value, "chunks"):
        return "[ARCHIVO_NO_ALMACENADO]"
    return _json_safe(value)


def obtener_ip_request(request):
    if not request:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def obtener_user_agent(request):
    if not request:
        return ""
    return (request.META.get("HTTP_USER_AGENT") or "")[:1000]


def extraer_contexto_request(request):
    if not request:
        return {}
    return {
        "request_id": request.META.get("HTTP_X_REQUEST_ID", "")[:120],
        "ip_origen": obtener_ip_request(request),
        "user_agent": obtener_user_agent(request),
        "ruta": request.path[:500],
        "metodo_http": request.method[:12],
    }


def construir_repr_objeto(objeto):
    if objeto is None:
        return "", "", ""
    return (
        f"{objeto.__class__.__module__}.{objeto.__class__.__name__}",
        str(getattr(objeto, "pk", ""))[:80],
        str(objeto)[:240],
    )


def _snapshot_usuario(usuario):
    if not usuario or not getattr(usuario, "is_authenticated", False):
        return None, "", ""
    nombre = getattr(usuario, "nombre_visible", "") or getattr(usuario, "nombre_completo", "") or ""
    return usuario, getattr(usuario, "username", "")[:150], nombre[:240]


def _contexto_portal(usuario):
    if not usuario or not getattr(usuario, "is_authenticated", False):
        return "", ""
    try:
        ctx = portal_context(usuario)
        cargo = ctx.cargos[0].cargo_codigo if ctx.cargos else ""
        return (ctx.perfil or "")[:80], cargo[:120]
    except Exception:
        logger.debug("No fue posible resolver contexto de portal para auditoria.", exc_info=True)
        return "", ""


class ServicioBitacoraEventos:
    @classmethod
    def registrar_evento_critico(
        cls,
        *,
        request=None,
        usuario=None,
        modulo=None,
        evento_codigo=None,
        evento_nombre=None,
        severidad=SEVERIDAD_INFO,
        resultado=RESULTADO_EXITOSO,
        objeto=None,
        objeto_tipo=None,
        objeto_id=None,
        objeto_repr=None,
        estado_anterior=None,
        estado_nuevo=None,
        resumen="",
        cambios=None,
        metadatos=None,
        correlacion_id=None,
        request_id=None,
        ip_origen=None,
        user_agent=None,
        ruta=None,
        metodo_http=None,
    ):
        try:
            usuario = usuario or getattr(request, "user", None)
            usuario, username_snapshot, nombre_usuario_snapshot = _snapshot_usuario(usuario)
            rol_contexto, cargo_contexto = _contexto_portal(usuario)
            tipo_obj, id_obj, repr_obj = construir_repr_objeto(objeto)
            contexto_request = extraer_contexto_request(request)

            evento = BitacoraEventoCritico.objects.create(
                usuario=usuario,
                username_snapshot=username_snapshot,
                nombre_usuario_snapshot=nombre_usuario_snapshot,
                rol_contexto=rol_contexto,
                cargo_contexto=cargo_contexto,
                modulo=modulo or MODULO_SISTEMA,
                evento_codigo=evento_codigo or "ACCESO_DENEGADO",
                evento_nombre=(evento_nombre or nombre_evento(evento_codigo))[:180],
                severidad=severidad,
                resultado=resultado,
                objeto_tipo=(objeto_tipo or tipo_obj)[:120],
                objeto_id=str(objeto_id or id_obj)[:80],
                objeto_repr=str(objeto_repr or repr_obj)[:240],
                estado_anterior=str(estado_anterior or "")[:120],
                estado_nuevo=str(estado_nuevo or "")[:120],
                resumen=resumen or evento_nombre or nombre_evento(evento_codigo),
                cambios_json=limpiar_payload_auditoria(cambios or {}),
                metadatos_json=limpiar_payload_auditoria(metadatos or {}),
                request_id=(request_id or contexto_request.get("request_id") or "")[:120],
                correlacion_id=str(correlacion_id or "")[:120],
                ip_origen=ip_origen or contexto_request.get("ip_origen"),
                user_agent=(user_agent or contexto_request.get("user_agent") or "")[:1000],
                ruta=(ruta or contexto_request.get("ruta") or "")[:500],
                metodo_http=(metodo_http or contexto_request.get("metodo_http") or "")[:12],
            )
            return evento
        except Exception:
            logger.exception("Fallo al registrar bitacora de evento critico.")
            if getattr(settings, "AUDITORIA_STRICT", False):
                raise
            return None

    @classmethod
    def registrar_evento_exitoso(cls, **kwargs):
        kwargs["resultado"] = RESULTADO_EXITOSO
        return cls.registrar_evento_critico(**kwargs)

    @classmethod
    def registrar_evento_fallido(cls, **kwargs):
        kwargs["resultado"] = RESULTADO_FALLIDO
        return cls.registrar_evento_critico(**kwargs)

    @classmethod
    def registrar_evento_bloqueado(cls, **kwargs):
        kwargs["resultado"] = RESULTADO_BLOQUEADO
        return cls.registrar_evento_critico(**kwargs)


registrar_evento_critico = ServicioBitacoraEventos.registrar_evento_critico
registrar_evento_exitoso = ServicioBitacoraEventos.registrar_evento_exitoso
registrar_evento_fallido = ServicioBitacoraEventos.registrar_evento_fallido
registrar_evento_bloqueado = ServicioBitacoraEventos.registrar_evento_bloqueado


def auditar_accion(**audit_kwargs):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                registrar_evento_fallido(
                    resumen=str(exc),
                    metadatos={"error": exc.__class__.__name__},
                    **audit_kwargs,
                )
                raise
            registrar_evento_exitoso(**audit_kwargs)
            return result

        return wrapper

    return decorator


@contextmanager
def contexto_auditoria(**audit_kwargs):
    try:
        yield
    except (DatabaseError, Exception) as exc:
        registrar_evento_fallido(
            resumen=str(exc),
            metadatos={"error": exc.__class__.__name__},
            **audit_kwargs,
        )
        raise
    else:
        registrar_evento_exitoso(**audit_kwargs)
