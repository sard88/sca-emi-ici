import json
from datetime import date

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from auditoria.eventos import MODULO_MOVIMIENTOS, SEVERIDAD_ADVERTENCIA, SEVERIDAD_INFO
from auditoria.services import registrar_evento_bloqueado, registrar_evento_exitoso
from core.api_views import api_login_required
from trayectoria.permisos import carreras_ambito_usuario

from .models import MovimientoAcademico
from .permisos import puede_consultar_relaciones, usuario_es_admin_soporte, usuario_es_estadistica


MAX_PAGE_SIZE = 100


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _date(value):
    return value.isoformat() if value else None


def _parse_date(value, field):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValidationError({field: "Usa formato de fecha AAAA-MM-DD."}) from exc


def _validation_errors(error):
    if hasattr(error, "message_dict"):
        return error.message_dict
    if hasattr(error, "messages"):
        return {"__all__": error.messages}
    return {"__all__": [str(error)]}


def _error_response(error, status=400, message="No fue posible completar la operación."):
    if isinstance(error, ValidationError):
        return JsonResponse({"ok": False, "message": message, "errors": _validation_errors(error)}, status=status)
    return JsonResponse({"ok": False, "message": message, "errors": {"__all__": [str(error)]}}, status=status)


def _deny(message="No tienes permiso para realizar esta acción."):
    return JsonResponse({"ok": False, "message": message}, status=403)


def _page_params(request):
    try:
        page = max(1, int(request.GET.get("page") or 1))
    except ValueError:
        page = 1
    try:
        page_size = max(1, min(int(request.GET.get("page_size") or 25), MAX_PAGE_SIZE))
    except ValueError:
        page_size = 25
    start = (page - 1) * page_size
    end = start + page_size
    return page, page_size, start, end


def _usuario_min(usuario):
    grado = getattr(usuario, "grado_empleo", None)
    return {
        "id": usuario.id,
        "username": usuario.username,
        "nombre": usuario.nombre_visible,
        "nombre_institucional": usuario.nombre_institucional,
        "grado_empleo": grado.abreviatura if grado else "",
        "label": usuario.nombre_institucional,
    }


def _carrera_min(carrera):
    if not carrera:
        return None
    return {"id": carrera.id, "clave": carrera.clave, "nombre": carrera.nombre, "label": str(carrera)}


def _periodo_min(periodo):
    if not periodo:
        return None
    return {"id": periodo.id, "clave": periodo.clave, "estado": periodo.estado, "estado_label": periodo.get_estado_display(), "label": str(periodo)}


def _grupo_min(grupo):
    if not grupo:
        return None
    return {
        "id": grupo.id,
        "clave": grupo.clave_grupo,
        "semestre": grupo.semestre_numero,
        "periodo": _periodo_min(grupo.periodo),
        "carrera": _carrera_min(grupo.antiguedad.plan_estudios.carrera),
        "label": str(grupo),
    }


def _discente_min(discente):
    return {
        "id": discente.id,
        "usuario": _usuario_min(discente.usuario),
        "nombre": discente.usuario.nombre_visible,
        "nombre_institucional": discente.usuario.nombre_institucional,
        "grado_empleo": discente.usuario.grado_empleo.abreviatura if discente.usuario.grado_empleo else "",
        "carrera": _carrera_min(discente.plan_estudios.carrera),
        "antiguedad": {"id": discente.antiguedad_id, "clave": discente.antiguedad.clave, "nombre": discente.antiguedad.nombre, "label": str(discente.antiguedad)},
        "situacion_actual": discente.situacion_actual,
        "situacion_actual_label": discente.get_situacion_actual_display(),
    }


def _impacto_movimiento(movimiento):
    if not movimiento.grupo_origen_id and not movimiento.grupo_destino_id:
        return {}
    return {
        "adscripcion_origen_activa": movimiento.discente.adscripciones_grupo.filter(grupo_academico=movimiento.grupo_origen, activo=True).exists() if movimiento.grupo_origen_id else None,
        "adscripcion_destino_activa": movimiento.discente.adscripciones_grupo.filter(grupo_academico=movimiento.grupo_destino, activo=True).exists() if movimiento.grupo_destino_id else None,
        "inscripciones_origen_activas": movimiento.discente.inscripciones_materia.filter(asignacion_docente__grupo_academico=movimiento.grupo_origen, estado_inscripcion="inscrita").count() if movimiento.grupo_origen_id else 0,
        "inscripciones_destino_activas": movimiento.discente.inscripciones_materia.filter(asignacion_docente__grupo_academico=movimiento.grupo_destino, estado_inscripcion="inscrita").count() if movimiento.grupo_destino_id else 0,
    }


def _movimiento_item(movimiento, include_impacto=False):
    item = {
        "id": movimiento.id,
        "discente": _discente_min(movimiento.discente),
        "periodo": _periodo_min(movimiento.periodo),
        "tipo_movimiento": movimiento.tipo_movimiento,
        "tipo_movimiento_label": movimiento.get_tipo_movimiento_display(),
        "grupo_origen": _grupo_min(movimiento.grupo_origen),
        "grupo_destino": _grupo_min(movimiento.grupo_destino),
        "fecha_movimiento": _date(movimiento.fecha_movimiento),
        "observaciones": movimiento.observaciones,
    }
    if include_impacto:
        item["impacto"] = _impacto_movimiento(movimiento)
    return item


def _movimientos_queryset(user):
    queryset = MovimientoAcademico.objects.select_related(
        "discente",
        "discente__usuario",
        "discente__usuario__grado_empleo",
        "discente__plan_estudios__carrera",
        "discente__antiguedad",
        "periodo",
        "grupo_origen",
        "grupo_origen__periodo",
        "grupo_origen__antiguedad__plan_estudios__carrera",
        "grupo_destino",
        "grupo_destino__periodo",
        "grupo_destino__antiguedad__plan_estudios__carrera",
    )
    if not (usuario_es_admin_soporte(user) or usuario_es_estadistica(user)):
        carrera_ids = carreras_ambito_usuario(user)
        queryset = queryset.filter(discente__plan_estudios__carrera_id__in=carrera_ids) if carrera_ids else queryset.none()
    return queryset


def _filter_movimientos(queryset, params):
    if params.get("periodo"):
        queryset = queryset.filter(periodo_id=params["periodo"])
    if params.get("carrera"):
        queryset = queryset.filter(discente__plan_estudios__carrera_id=params["carrera"])
    if params.get("grupo_origen"):
        queryset = queryset.filter(grupo_origen_id=params["grupo_origen"])
    if params.get("grupo_destino"):
        queryset = queryset.filter(grupo_destino_id=params["grupo_destino"])
    if params.get("discente"):
        queryset = queryset.filter(discente_id=params["discente"])
    if params.get("tipo_movimiento"):
        queryset = queryset.filter(tipo_movimiento=params["tipo_movimiento"])
    if params.get("fecha_desde"):
        queryset = queryset.filter(fecha_movimiento__gte=params["fecha_desde"])
    if params.get("fecha_hasta"):
        queryset = queryset.filter(fecha_movimiento__lte=params["fecha_hasta"])
    return queryset


def _crear_movimiento_desde_payload(request, force_tipo=None):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida."}, status=400)
    try:
        payload = {
            "discente_id": data.get("discente_id") or data.get("discente"),
            "periodo_id": data.get("periodo_id") or data.get("periodo"),
            "tipo_movimiento": force_tipo or data.get("tipo_movimiento"),
            "grupo_origen_id": data.get("grupo_origen_id") or data.get("grupo_origen") or None,
            "grupo_destino_id": data.get("grupo_destino_id") or data.get("grupo_destino") or None,
            "observaciones": (data.get("observaciones") or "").strip(),
        }
        fecha_movimiento = _parse_date(data.get("fecha_movimiento"), "fecha_movimiento")
        if fecha_movimiento:
            payload["fecha_movimiento"] = fecha_movimiento
        movimiento = MovimientoAcademico.objects.create(**payload)
    except Exception as exc:
        registrar_evento_bloqueado(
            request=request,
            modulo=MODULO_MOVIMIENTOS,
            evento_codigo="CAMBIO_GRUPO_BLOQUEADO" if force_tipo == MovimientoAcademico.CAMBIO_GRUPO else "MOVIMIENTO_ACADEMICO_REGISTRADO",
            severidad=SEVERIDAD_ADVERTENCIA,
            resumen="Movimiento academico bloqueado o rechazado.",
            metadatos={"tipo_movimiento": force_tipo or data.get("tipo_movimiento"), "motivo_bloqueo": str(exc)[:300]},
        )
        return _error_response(exc)
    impacto = _impacto_movimiento(movimiento)
    registrar_evento_exitoso(
        request=request,
        modulo=MODULO_MOVIMIENTOS,
        evento_codigo="CAMBIO_GRUPO_APLICADO" if movimiento.tipo_movimiento == MovimientoAcademico.CAMBIO_GRUPO else "MOVIMIENTO_ACADEMICO_REGISTRADO",
        severidad=SEVERIDAD_INFO,
        objeto=movimiento,
        resumen="Movimiento academico registrado.",
        metadatos={
            "movimiento_id": movimiento.id,
            "discente_id": movimiento.discente_id,
            "periodo_id": movimiento.periodo_id,
            "tipo_movimiento": movimiento.tipo_movimiento,
            "grupo_origen_id": movimiento.grupo_origen_id,
            "grupo_destino_id": movimiento.grupo_destino_id,
            "total_inscripciones_baja": impacto.get("inscripciones_origen_activas", 0),
            "total_inscripciones_creadas": impacto.get("inscripciones_destino_activas", 0),
        },
    )
    return JsonResponse({"ok": True, "item": _movimiento_item(movimiento, include_impacto=True)}, status=201)


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def movimientos_list_create_view(request):
    if request.method == "POST":
        if not (usuario_es_admin_soporte(request.user) or usuario_es_estadistica(request.user)):
            return _deny("No tienes permiso para registrar movimientos académicos.")
        return _crear_movimiento_desde_payload(request)
    if not puede_consultar_relaciones(request.user):
        return _deny("No tienes permiso para consultar movimientos académicos.")
    queryset = _filter_movimientos(_movimientos_queryset(request.user), request.GET).order_by("-fecha_movimiento", "-id")
    page, page_size, start, end = _page_params(request)
    total = queryset.count()
    return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [_movimiento_item(item) for item in queryset[start:end]]})


@require_GET
@api_login_required
def movimiento_detail_view(request, pk):
    if not puede_consultar_relaciones(request.user):
        return _deny("No tienes permiso para consultar movimientos académicos.")
    item = _movimientos_queryset(request.user).filter(pk=pk).first()
    if not item:
        return JsonResponse({"ok": False, "message": "Movimiento académico no encontrado."}, status=404)
    return JsonResponse({"ok": True, "item": _movimiento_item(item, include_impacto=True)})


@require_POST
@csrf_protect
@api_login_required
def cambio_grupo_create_view(request):
    if not (usuario_es_admin_soporte(request.user) or usuario_es_estadistica(request.user)):
        return _deny("No tienes permiso para registrar cambios de grupo.")
    return _crear_movimiento_desde_payload(request, force_tipo=MovimientoAcademico.CAMBIO_GRUPO)
