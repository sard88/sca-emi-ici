import copy
import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from auditoria.eventos import MODULO_PERIODOS, SEVERIDAD_ADVERTENCIA, SEVERIDAD_INFO
from auditoria.services import registrar_evento_bloqueado, registrar_evento_exitoso
from catalogos.models import ESTADO_ACTIVO, ESTADO_CERRADO, ESTADO_PLANIFICADO, PeriodoEscolar
from core.api_views import api_login_required

from .models import DetalleCierrePeriodoDiscente, ProcesoAperturaPeriodo, ProcesoCierrePeriodo
from .permisos import puede_consultar_cierre_periodo, puede_consultar_pendientes_docente, puede_operar_cierre_apertura
from .services import ServicioAperturaPeriodo, ServicioCierrePeriodo, ServicioDiagnosticoCierrePeriodo, listar_pendientes_asignacion_docente


MAX_PAGE_SIZE = 100


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _date(value):
    return value.isoformat() if value else None


def _datetime(value):
    return value.isoformat() if value else None


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


def _periodo_item(periodo, user=None):
    puede_operar = puede_operar_cierre_apertura(user) if user else False
    puede_consultar = puede_consultar_cierre_periodo(user) if user else False
    return {
        "id": periodo.id,
        "clave": periodo.clave,
        "anio_escolar": periodo.anio_escolar,
        "periodo_academico": periodo.periodo_academico,
        "fecha_inicio": _date(periodo.fecha_inicio),
        "fecha_fin": _date(periodo.fecha_fin),
        "estado": periodo.estado,
        "estado_label": periodo.get_estado_display(),
        "label": str(periodo),
        "acciones": {
            "puede_diagnosticar": puede_consultar and periodo.estado == ESTADO_ACTIVO,
            "puede_cerrar": puede_operar and periodo.estado == ESTADO_ACTIVO,
            "puede_usarse_como_origen_apertura": puede_operar and periodo.estado == ESTADO_CERRADO,
            "puede_usarse_como_destino_apertura": puede_operar and periodo.estado in {ESTADO_PLANIFICADO, ESTADO_ACTIVO},
        },
    }


def _sanitize_json(value, parent_key=""):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if key.lower() == "matricula":
                continue
            if key.lower() in {"discente", "discentes"} and isinstance(item, str):
                cleaned[key] = "Dato protegido"
                continue
            cleaned[key] = _sanitize_json(item, key)
        return cleaned
    if isinstance(value, list):
        if parent_key in {"egresables"} and all(isinstance(item, str) for item in value):
            return [{"discente": "Dato protegido"} for _ in value]
        return [_sanitize_json(item, parent_key) for item in value]
    return value


def _diagnostico_payload(periodo, diagnostico):
    limpio = _sanitize_json(copy.deepcopy(diagnostico))
    resumen = limpio.get("resumen_por_grupo", {})
    return {
        "ok": True,
        "periodo": _periodo_item(periodo),
        "puede_cerrar": not bool(limpio.get("bloqueantes")),
        "bloqueantes": limpio.get("bloqueantes", []),
        "advertencias": limpio.get("advertencias", []),
        "resumen_por_grupo": resumen,
        "discentes_promovibles": limpio.get("discentes_promovibles", []),
        "discentes_pendientes_extraordinario": limpio.get("discentes_pendientes_extraordinario", []),
        "discentes_baja_temporal": limpio.get("discentes_baja_temporal", []),
        "discentes_baja_definitiva": limpio.get("discentes_baja_definitiva", []),
        "discentes_egresables": limpio.get("discentes_egresables", []),
        "resumen": {
            "bloqueantes": len(limpio.get("bloqueantes", [])),
            "advertencias": len(limpio.get("advertencias", [])),
            "promovibles": len(limpio.get("discentes_promovibles", [])),
            "pendientes_extraordinario": len(limpio.get("discentes_pendientes_extraordinario", [])),
            "bajas_temporales": len(limpio.get("discentes_baja_temporal", [])),
            "bajas_definitivas": len(limpio.get("discentes_baja_definitiva", [])),
            "egresables": len(limpio.get("discentes_egresables", [])),
        },
    }


def _detalle_cierre_item(detalle):
    discente = detalle.discente
    usuario = discente.usuario
    return {
        "id": detalle.id,
        "discente": {
            "id": discente.id,
            "nombre": usuario.nombre_visible,
            "nombre_institucional": usuario.nombre_institucional,
            "grado_empleo": usuario.grado_empleo.abreviatura if usuario.grado_empleo else "",
            "situacion_actual": discente.situacion_actual,
            "situacion_actual_label": discente.get_situacion_actual_display(),
        },
        "grupo_origen": detalle.grupo_origen.clave_grupo if detalle.grupo_origen_id else "",
        "clasificacion": detalle.clasificacion,
        "clasificacion_label": detalle.get_clasificacion_display(),
        "motivo": detalle.motivo,
        "promovible": detalle.promovible,
        "requiere_extraordinario": detalle.requiere_extraordinario,
        "situacion_detectada": detalle.situacion_detectada,
    }


def _cierre_item(proceso, include_detalles=False):
    item = {
        "id": proceso.id,
        "periodo": _periodo_item(proceso.periodo),
        "estado": proceso.estado,
        "estado_label": proceso.get_estado_display(),
        "ejecutado_por": _usuario_min(proceso.ejecutado_por),
        "ejecutado_en": _datetime(proceso.ejecutado_en),
        "resumen": _sanitize_json(proceso.resumen_json),
        "observaciones": proceso.observaciones,
    }
    if include_detalles:
        item["detalles"] = [_detalle_cierre_item(detalle) for detalle in proceso.detalles_discente.select_related("discente", "discente__usuario", "discente__usuario__grado_empleo", "grupo_origen")]
    return item


def _apertura_item(proceso):
    return {
        "id": proceso.id,
        "periodo_origen": _periodo_item(proceso.periodo_origen),
        "periodo_destino": _periodo_item(proceso.periodo_destino),
        "estado": proceso.estado,
        "estado_label": proceso.get_estado_display(),
        "ejecutado_por": _usuario_min(proceso.ejecutado_por),
        "ejecutado_en": _datetime(proceso.ejecutado_en),
        "resumen": _sanitize_json(proceso.resumen_json),
        "observaciones": proceso.observaciones,
    }


def _pendiente_item(item):
    grupo = item["grupo"]
    programa = item["programa"]
    plan = grupo.antiguedad.plan_estudios
    return {
        "grupo": {"id": grupo.id, "clave": grupo.clave_grupo, "semestre": grupo.semestre_numero, "label": str(grupo)},
        "periodo": _periodo_item(grupo.periodo),
        "carrera": {"id": plan.carrera.id, "clave": plan.carrera.clave, "nombre": plan.carrera.nombre, "label": str(plan.carrera)},
        "plan": {"id": plan.id, "clave": plan.clave, "nombre": plan.nombre, "label": str(plan)},
        "programa_asignatura": {"id": programa.id, "semestre": programa.semestre_numero, "anio_formacion": programa.anio_formacion, "label": str(programa)},
        "materia": {"id": programa.materia.id, "clave": programa.materia.clave, "nombre": programa.materia.nombre, "label": str(programa.materia)},
        "estado": "pendiente",
        "accion_sugerida": "Asignar docente desde módulo de administración/catálogos o Django Admin según disponibilidad.",
    }


@require_GET
@api_login_required
def periodos_list_view(request):
    if not (puede_consultar_cierre_periodo(request.user) or puede_consultar_pendientes_docente(request.user)):
        return _deny("No tienes permiso para consultar periodos operativos.")
    queryset = PeriodoEscolar.objects.order_by("-anio_escolar", "-periodo_academico", "clave")
    if request.GET.get("estado"):
        queryset = queryset.filter(estado=request.GET["estado"])
    page, page_size, start, end = _page_params(request)
    total = queryset.count()
    return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [_periodo_item(periodo, request.user) for periodo in queryset[start:end]]})


@require_GET
@api_login_required
def diagnostico_cierre_view(request, periodo_id):
    if not puede_consultar_cierre_periodo(request.user):
        return _deny("No tienes permiso para consultar diagnósticos de cierre.")
    periodo = PeriodoEscolar.objects.filter(pk=periodo_id).first()
    if not periodo:
        return JsonResponse({"ok": False, "message": "Periodo no encontrado."}, status=404)
    diagnostico = ServicioDiagnosticoCierrePeriodo(periodo).diagnosticar()
    registrar_evento_exitoso(
        request=request,
        modulo=MODULO_PERIODOS,
        evento_codigo="DIAGNOSTICO_CIERRE_EJECUTADO",
        severidad=SEVERIDAD_INFO,
        objeto=periodo,
        resumen="Diagnostico de cierre ejecutado.",
        metadatos={
            "periodo_id": periodo.id,
            "total_bloqueantes": len(diagnostico.get("bloqueantes", [])),
            "total_advertencias": len(diagnostico.get("advertencias", [])),
            "puede_cerrar": not bool(diagnostico.get("bloqueantes")),
        },
    )
    return JsonResponse(_diagnostico_payload(periodo, diagnostico))


@require_POST
@csrf_protect
@api_login_required
def cerrar_periodo_view(request, periodo_id):
    if not puede_operar_cierre_apertura(request.user):
        return _deny("No tienes permiso para cerrar periodos académicos.")
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida."}, status=400)
    periodo = PeriodoEscolar.objects.filter(pk=periodo_id).first()
    if not periodo:
        return JsonResponse({"ok": False, "message": "Periodo no encontrado."}, status=404)
    try:
        proceso = ServicioCierrePeriodo(periodo, request.user, observaciones=(data.get("observaciones") or "").strip()).cerrar()
    except Exception as exc:
        registrar_evento_bloqueado(
            request=request,
            modulo=MODULO_PERIODOS,
            evento_codigo="CIERRE_PERIODO_BLOQUEADO",
            severidad=SEVERIDAD_ADVERTENCIA,
            objeto=periodo,
            resumen="Cierre de periodo bloqueado.",
            metadatos={"periodo_id": periodo.id, "motivo_bloqueo": str(exc)[:300]},
        )
        return _error_response(exc)
    resumen = proceso.resumen_json or {}
    registrar_evento_exitoso(
        request=request,
        modulo=MODULO_PERIODOS,
        evento_codigo="CIERRE_PERIODO_EJECUTADO",
        severidad=SEVERIDAD_INFO,
        objeto=proceso,
        resumen="Cierre de periodo ejecutado.",
        metadatos={
            "periodo_id": periodo.id,
            "proceso_cierre_id": proceso.id,
            "total_promovibles": len(resumen.get("discentes_promovibles", [])),
            "total_extraordinario_pendiente": len(resumen.get("discentes_pendientes_extraordinario", [])),
            "total_baja_temporal": len(resumen.get("discentes_baja_temporal", [])),
            "total_baja_definitiva": len(resumen.get("discentes_baja_definitiva", [])),
            "total_egresables": len(resumen.get("discentes_egresables", [])),
        },
    )
    return JsonResponse({"ok": True, "item": _cierre_item(proceso, include_detalles=True)}, status=201)


@require_GET
@api_login_required
def cierres_list_view(request):
    if not puede_consultar_cierre_periodo(request.user):
        return _deny("No tienes permiso para consultar procesos de cierre.")
    queryset = ProcesoCierrePeriodo.objects.select_related("periodo", "ejecutado_por", "ejecutado_por__grado_empleo").order_by("-ejecutado_en")
    if request.GET.get("periodo"):
        queryset = queryset.filter(periodo_id=request.GET["periodo"])
    page, page_size, start, end = _page_params(request)
    total = queryset.count()
    return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [_cierre_item(item) for item in queryset[start:end]]})


@require_GET
@api_login_required
def cierre_detail_view(request, pk):
    if not puede_consultar_cierre_periodo(request.user):
        return _deny("No tienes permiso para consultar procesos de cierre.")
    item = ProcesoCierrePeriodo.objects.select_related("periodo", "ejecutado_por", "ejecutado_por__grado_empleo").filter(pk=pk).first()
    if not item:
        return JsonResponse({"ok": False, "message": "Proceso de cierre no encontrado."}, status=404)
    return JsonResponse({"ok": True, "item": _cierre_item(item, include_detalles=True)})


@require_POST
@csrf_protect
@api_login_required
def apertura_create_view(request):
    if not puede_operar_cierre_apertura(request.user):
        return _deny("No tienes permiso para abrir periodos académicos.")
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida."}, status=400)
    try:
        origen = PeriodoEscolar.objects.get(pk=data.get("periodo_origen_id") or data.get("periodo_origen"))
        destino = PeriodoEscolar.objects.get(pk=data.get("periodo_destino_id") or data.get("periodo_destino"))
        proceso = ServicioAperturaPeriodo(origen, destino, request.user, observaciones=(data.get("observaciones") or "").strip()).abrir()
    except PeriodoEscolar.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Periodo origen o destino no encontrado."}, status=404)
    except Exception as exc:
        registrar_evento_bloqueado(
            request=request,
            modulo=MODULO_PERIODOS,
            evento_codigo="APERTURA_PERIODO_BLOQUEADA",
            severidad=SEVERIDAD_ADVERTENCIA,
            resumen="Apertura de periodo bloqueada.",
            metadatos={
                "periodo_origen_id": data.get("periodo_origen_id") or data.get("periodo_origen"),
                "periodo_destino_id": data.get("periodo_destino_id") or data.get("periodo_destino"),
                "motivo_bloqueo": str(exc)[:300],
            },
        )
        return _error_response(exc)
    resumen = proceso.resumen_json or {}
    registrar_evento_exitoso(
        request=request,
        modulo=MODULO_PERIODOS,
        evento_codigo="APERTURA_PERIODO_EJECUTADA",
        severidad=SEVERIDAD_INFO,
        objeto=proceso,
        resumen="Apertura de periodo ejecutada.",
        metadatos={
            "periodo_origen_id": proceso.periodo_origen_id,
            "periodo_destino_id": proceso.periodo_destino_id,
            "proceso_apertura_id": proceso.id,
            "total_promovidos": resumen.get("adscripciones_creadas", 0),
            "total_egresables": len(resumen.get("egresables", [])),
            "total_grupos_creados": len(resumen.get("grupos_creados", [])),
            "total_grupos_reutilizados": len(resumen.get("grupos_existentes", [])),
        },
    )
    return JsonResponse({"ok": True, "item": _apertura_item(proceso)}, status=201)


@require_GET
@api_login_required
def aperturas_list_view(request):
    if not puede_consultar_cierre_periodo(request.user):
        return _deny("No tienes permiso para consultar procesos de apertura.")
    queryset = ProcesoAperturaPeriodo.objects.select_related("periodo_origen", "periodo_destino", "ejecutado_por", "ejecutado_por__grado_empleo").order_by("-ejecutado_en")
    if request.GET.get("periodo_origen"):
        queryset = queryset.filter(periodo_origen_id=request.GET["periodo_origen"])
    if request.GET.get("periodo_destino"):
        queryset = queryset.filter(periodo_destino_id=request.GET["periodo_destino"])
    page, page_size, start, end = _page_params(request)
    total = queryset.count()
    return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [_apertura_item(item) for item in queryset[start:end]]})


@require_GET
@api_login_required
def apertura_detail_view(request, pk):
    if not puede_consultar_cierre_periodo(request.user):
        return _deny("No tienes permiso para consultar procesos de apertura.")
    item = ProcesoAperturaPeriodo.objects.select_related("periodo_origen", "periodo_destino", "ejecutado_por", "ejecutado_por__grado_empleo").filter(pk=pk).first()
    if not item:
        return JsonResponse({"ok": False, "message": "Proceso de apertura no encontrado."}, status=404)
    return JsonResponse({"ok": True, "item": _apertura_item(item)})


@require_GET
@api_login_required
def pendientes_asignacion_docente_view(request):
    if not puede_consultar_pendientes_docente(request.user):
        return _deny("No tienes permiso para consultar pendientes de asignación docente.")
    periodo = None
    if request.GET.get("periodo"):
        periodo = PeriodoEscolar.objects.filter(pk=request.GET["periodo"]).first()
    if not periodo:
        periodo = PeriodoEscolar.objects.order_by("-anio_escolar", "-periodo_academico").first()
    if not periodo:
        return JsonResponse({"ok": True, "total": 0, "items": []})
    pendientes = [_pendiente_item(item) for item in listar_pendientes_asignacion_docente(periodo, request.user)]
    if request.GET.get("carrera"):
        pendientes = [item for item in pendientes if str(item["carrera"]["id"]) == str(request.GET["carrera"])]
    if request.GET.get("grupo"):
        pendientes = [item for item in pendientes if str(item["grupo"]["id"]) == str(request.GET["grupo"])]
    if request.GET.get("semestre"):
        pendientes = [item for item in pendientes if str(item["grupo"]["semestre"]) == str(request.GET["semestre"])]
    return JsonResponse({"ok": True, "periodo": _periodo_item(periodo), "total": len(pendientes), "items": pendientes})
