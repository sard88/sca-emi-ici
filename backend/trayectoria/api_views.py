import json
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from auditoria.eventos import MODULO_TRAYECTORIA, SEVERIDAD_ADVERTENCIA, SEVERIDAD_INFO
from auditoria.services import registrar_evento_exitoso, registrar_evento_fallido
from catalogos.models import GrupoAcademico, PeriodoEscolar
from core.api_views import api_login_required
from relaciones.models import AdscripcionGrupo, Discente, InscripcionMateria, MovimientoAcademico

from .models import CatalogoSituacionAcademica, EventoSituacionAcademica, Extraordinario
from .permisos import (
    carreras_ambito_usuario,
    filtrar_discentes_por_ambito,
    puede_consultar_historial_discente,
    puede_consultar_historiales,
    puede_operar_trayectoria,
)
from .services import construir_historial_discente, registrar_evento_situacion, registrar_extraordinario


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


def _decimal(value):
    if value is None:
        return None
    return float(value)


def _parse_date(value, field):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValidationError({field: "Usa formato de fecha AAAA-MM-DD."}) from exc


def _parse_decimal(value, field):
    if value in (None, ""):
        raise ValidationError({field: "Este campo es obligatorio."})
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError({field: "Debe ser un número válido."}) from exc


def _validation_errors(error):
    if hasattr(error, "message_dict"):
        return error.message_dict
    if hasattr(error, "messages"):
        return {"__all__": error.messages}
    return {"__all__": [str(error)]}


def _error_response(error, status=400, message="No fue posible completar la operación."):
    if isinstance(error, PermissionDenied):
        return JsonResponse({"ok": False, "message": str(error) or "No tienes permiso para realizar esta acción."}, status=403)
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


def _plan_min(plan):
    if not plan:
        return None
    return {"id": plan.id, "clave": plan.clave, "nombre": plan.nombre, "label": str(plan), "carrera": _carrera_min(plan.carrera)}


def _antiguedad_min(antiguedad):
    if not antiguedad:
        return None
    return {"id": antiguedad.id, "clave": antiguedad.clave, "nombre": antiguedad.nombre, "label": str(antiguedad)}


def _periodo_min(periodo):
    if not periodo:
        return None
    return {
        "id": periodo.id,
        "clave": periodo.clave,
        "anio_escolar": periodo.anio_escolar,
        "periodo_academico": periodo.periodo_academico,
        "estado": periodo.estado,
        "estado_label": periodo.get_estado_display(),
        "label": str(periodo),
    }


def _grupo_min(grupo):
    if not grupo:
        return None
    return {
        "id": grupo.id,
        "clave": grupo.clave_grupo,
        "semestre": grupo.semestre_numero,
        "periodo": _periodo_min(grupo.periodo),
        "label": str(grupo),
    }


def _discente_min(discente):
    adscripcion = _adscripcion_actual(discente)
    return {
        "id": discente.id,
        "usuario": _usuario_min(discente.usuario),
        "nombre": discente.usuario.nombre_visible,
        "nombre_institucional": discente.usuario.nombre_institucional,
        "grado_empleo": discente.usuario.grado_empleo.abreviatura if discente.usuario.grado_empleo else "",
        "plan_estudios": _plan_min(discente.plan_estudios),
        "carrera": _carrera_min(discente.plan_estudios.carrera),
        "antiguedad": _antiguedad_min(discente.antiguedad),
        "grupo_actual": _grupo_min(adscripcion.grupo_academico) if adscripcion else None,
        "situacion_actual": discente.situacion_actual,
        "situacion_actual_label": discente.get_situacion_actual_display(),
        "activo": discente.activo,
    }


def _adscripcion_actual(discente):
    return (
        AdscripcionGrupo.objects.filter(discente=discente, activo=True)
        .select_related("grupo_academico", "grupo_academico__periodo")
        .order_by("-vigente_desde", "-id")
        .first()
    )


def _materia_min(programa):
    materia = programa.materia
    return {
        "id": materia.id,
        "clave": materia.clave,
        "nombre": materia.nombre,
        "label": str(materia),
        "semestre": programa.semestre_numero,
        "anio_formacion": programa.anio_formacion,
    }


def _inscripcion_contexto(inscripcion):
    asignacion = inscripcion.asignacion_docente
    grupo = asignacion.grupo_academico
    programa = asignacion.programa_asignatura
    return {
        "inscripcion_id": inscripcion.id,
        "periodo": _periodo_min(grupo.periodo),
        "carrera": _carrera_min(programa.plan_estudios.carrera),
        "grupo": _grupo_min(grupo),
        "materia": _materia_min(programa),
        "docente": _usuario_min(asignacion.usuario_docente),
    }


def _resultado_item(resultado):
    inscripcion = resultado.inscripcion
    data = _inscripcion_contexto(inscripcion)
    data.update(
        {
            "tipo_resultado": resultado.tipo_resultado,
            "calificacion": _decimal(resultado.calificacion),
            "calificacion_ordinaria": _decimal(resultado.calificacion_ordinaria),
            "codigo_resultado": resultado.codigo_resultado,
            "codigo_marca": resultado.codigo_marca,
            "codigo_resultado_ordinario": resultado.codigo_resultado_ordinario,
            "extraordinario_id": resultado.extraordinario.id if resultado.extraordinario else None,
        }
    )
    return data


def _evento_item(evento):
    return {
        "id": evento.id,
        "discente": _discente_min(evento.discente),
        "situacion": {
            "id": evento.situacion_id,
            "clave": evento.situacion.clave,
            "nombre": evento.situacion.nombre,
            "label": evento.situacion.nombre,
        },
        "periodo": _periodo_min(evento.periodo),
        "fecha_inicio": _date(evento.fecha_inicio),
        "fecha_fin": _date(evento.fecha_fin),
        "motivo": evento.motivo,
        "registrado_por": _usuario_min(evento.registrado_por) if evento.registrado_por_id else None,
        "creado_en": _datetime(evento.creado_en),
    }


def _extraordinario_item(extraordinario):
    inscripcion = extraordinario.inscripcion_materia
    data = _inscripcion_contexto(inscripcion)
    data.update(
        {
            "id": extraordinario.id,
            "discente": _discente_min(inscripcion.discente),
            "fecha_aplicacion": _date(extraordinario.fecha_aplicacion),
            "calificacion": _decimal(extraordinario.calificacion),
            "aprobado": extraordinario.aprobado,
            "codigo_resultado_oficial": extraordinario.codigo_resultado_oficial,
            "codigo_marca": extraordinario.codigo_marca,
            "calificacion_ordinaria": _decimal(extraordinario.calificacion_ordinaria),
            "codigo_resultado_ordinario": extraordinario.codigo_resultado_ordinario,
            "registrado_por": _usuario_min(extraordinario.registrado_por),
            "creado_en": _datetime(extraordinario.creado_en),
        }
    )
    return data


def _movimiento_item(movimiento):
    return {
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


def _historial_payload(discente, vista_propia=False):
    historial = construir_historial_discente(discente)
    extraordinarios = Extraordinario.objects.filter(inscripcion_materia__discente=discente).select_related(
        "inscripcion_materia",
        "inscripcion_materia__discente",
        "inscripcion_materia__discente__usuario",
        "inscripcion_materia__discente__usuario__grado_empleo",
        "inscripcion_materia__discente__plan_estudios",
        "inscripcion_materia__discente__plan_estudios__carrera",
        "inscripcion_materia__discente__antiguedad",
        "inscripcion_materia__asignacion_docente",
        "inscripcion_materia__asignacion_docente__usuario_docente",
        "inscripcion_materia__asignacion_docente__grupo_academico",
        "inscripcion_materia__asignacion_docente__grupo_academico__periodo",
        "inscripcion_materia__asignacion_docente__programa_asignatura",
        "inscripcion_materia__asignacion_docente__programa_asignatura__materia",
        "inscripcion_materia__asignacion_docente__programa_asignatura__plan_estudios__carrera",
        "registrado_por",
    )
    movimientos = MovimientoAcademico.objects.filter(discente=discente).select_related(
        "discente",
        "discente__usuario",
        "discente__usuario__grado_empleo",
        "discente__plan_estudios__carrera",
        "discente__antiguedad",
        "periodo",
        "grupo_origen",
        "grupo_origen__periodo",
        "grupo_destino",
        "grupo_destino__periodo",
    )
    return {
        "ok": True,
        "discente": _discente_min(discente),
        "resultados": [_resultado_item(resultado) for resultado in historial["resultados"]],
        "extraordinarios": [_extraordinario_item(extraordinario) for extraordinario in extraordinarios],
        "eventos": [_evento_item(evento) for evento in historial["eventos"]],
        "movimientos": [_movimiento_item(movimiento) for movimiento in movimientos],
        "vista_propia": vista_propia,
        "es_kardex_oficial": False,
        "aviso_privacidad": "Historial académico interno. No sustituye al kárdex oficial.",
    }


def _discentes_queryset(user):
    queryset = Discente.objects.select_related(
        "usuario",
        "usuario__grado_empleo",
        "plan_estudios",
        "plan_estudios__carrera",
        "antiguedad",
    ).order_by("usuario__nombre_completo", "id")
    return filtrar_discentes_por_ambito(user, queryset)


def _filter_discentes(queryset, params):
    q = (params.get("q") or "").strip()
    if q:
        queryset = queryset.filter(usuario__nombre_completo__icontains=q)
    if params.get("carrera"):
        queryset = queryset.filter(plan_estudios__carrera_id=params["carrera"])
    if params.get("plan"):
        queryset = queryset.filter(plan_estudios_id=params["plan"])
    if params.get("antiguedad"):
        queryset = queryset.filter(antiguedad_id=params["antiguedad"])
    if params.get("situacion"):
        queryset = queryset.filter(situacion_actual=params["situacion"])
    if params.get("grupo"):
        queryset = queryset.filter(adscripciones_grupo__grupo_academico_id=params["grupo"], adscripciones_grupo__activo=True)
    return queryset.distinct()


def _filter_extraordinarios(queryset, params, user):
    if not puede_operar_trayectoria(user):
        carrera_ids = carreras_ambito_usuario(user)
        if carrera_ids:
            queryset = queryset.filter(inscripcion_materia__discente__plan_estudios__carrera_id__in=carrera_ids)
        else:
            queryset = queryset.none()
    if params.get("periodo"):
        queryset = queryset.filter(inscripcion_materia__asignacion_docente__grupo_academico__periodo_id=params["periodo"])
    if params.get("carrera"):
        queryset = queryset.filter(inscripcion_materia__discente__plan_estudios__carrera_id=params["carrera"])
    if params.get("grupo"):
        queryset = queryset.filter(inscripcion_materia__asignacion_docente__grupo_academico_id=params["grupo"])
    if params.get("discente"):
        queryset = queryset.filter(inscripcion_materia__discente_id=params["discente"])
    if params.get("asignatura"):
        queryset = queryset.filter(inscripcion_materia__asignacion_docente__programa_asignatura__materia_id=params["asignatura"])
    if params.get("aprobado") in {"true", "false"}:
        queryset = queryset.filter(aprobado=params["aprobado"] == "true")
    if params.get("fecha_desde"):
        queryset = queryset.filter(fecha_aplicacion__gte=params["fecha_desde"])
    if params.get("fecha_hasta"):
        queryset = queryset.filter(fecha_aplicacion__lte=params["fecha_hasta"])
    return queryset


def _filter_eventos(queryset, params, user):
    if not puede_operar_trayectoria(user):
        queryset = queryset.filter(discente__in=_discentes_queryset(user))
    if params.get("discente"):
        queryset = queryset.filter(discente_id=params["discente"])
    if params.get("situacion"):
        queryset = queryset.filter(situacion__clave=params["situacion"])
    if params.get("periodo"):
        queryset = queryset.filter(periodo_id=params["periodo"])
    if params.get("carrera"):
        queryset = queryset.filter(discente__plan_estudios__carrera_id=params["carrera"])
    if params.get("fecha_desde"):
        queryset = queryset.filter(fecha_inicio__gte=params["fecha_desde"])
    if params.get("fecha_hasta"):
        queryset = queryset.filter(fecha_inicio__lte=params["fecha_hasta"])
    return queryset


@require_GET
@api_login_required
def mi_historial_view(request):
    try:
        discente = Discente.objects.select_related(
            "usuario",
            "usuario__grado_empleo",
            "plan_estudios",
            "plan_estudios__carrera",
            "antiguedad",
        ).get(usuario=request.user, activo=True)
    except Discente.DoesNotExist:
        return JsonResponse({"ok": False, "message": "No existe un perfil de discente activo para este usuario."}, status=404)
    return JsonResponse(_historial_payload(discente, vista_propia=True))


@require_GET
@api_login_required
def historial_list_view(request):
    if not puede_consultar_historiales(request.user):
        return _deny("No tienes permiso para consultar historiales académicos.")
    queryset = _filter_discentes(_discentes_queryset(request.user), request.GET)
    page, page_size, start, end = _page_params(request)
    total = queryset.count()
    items = []
    for discente in queryset[start:end]:
        item = _discente_min(discente)
        item["url_detalle"] = f"/trayectoria/historial/{discente.id}"
        items.append(item)
    return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": items})


@require_GET
@api_login_required
def historial_detail_view(request, discente_id):
    discente = Discente.objects.select_related(
        "usuario",
        "usuario__grado_empleo",
        "plan_estudios",
        "plan_estudios__carrera",
        "antiguedad",
    ).filter(pk=discente_id).first()
    if not discente:
        return JsonResponse({"ok": False, "message": "Discente no encontrado."}, status=404)
    if not puede_consultar_historial_discente(request.user, discente):
        return _deny("No tienes permiso para consultar este historial académico.")
    return JsonResponse(_historial_payload(discente, vista_propia=discente.usuario_id == request.user.id))


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def extraordinarios_list_view(request):
    if request.method == "POST":
        return extraordinario_create_view(request)
    if not puede_consultar_historiales(request.user):
        return _deny("No tienes permiso para consultar extraordinarios.")
    queryset = Extraordinario.objects.select_related(
        "inscripcion_materia",
        "inscripcion_materia__discente",
        "inscripcion_materia__discente__usuario",
        "inscripcion_materia__discente__usuario__grado_empleo",
        "inscripcion_materia__discente__plan_estudios__carrera",
        "inscripcion_materia__discente__antiguedad",
        "inscripcion_materia__asignacion_docente__usuario_docente",
        "inscripcion_materia__asignacion_docente__grupo_academico__periodo",
        "inscripcion_materia__asignacion_docente__programa_asignatura__materia",
        "inscripcion_materia__asignacion_docente__programa_asignatura__plan_estudios__carrera",
        "registrado_por",
    )
    queryset = _filter_extraordinarios(queryset, request.GET, request.user).order_by("-fecha_aplicacion", "-id")
    page, page_size, start, end = _page_params(request)
    total = queryset.count()
    return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [_extraordinario_item(item) for item in queryset[start:end]]})


@require_http_methods(["GET"])
@api_login_required
def extraordinario_detail_view(request, pk):
    if not puede_consultar_historiales(request.user):
        return _deny("No tienes permiso para consultar extraordinarios.")
    queryset = _filter_extraordinarios(Extraordinario.objects.select_related(
        "inscripcion_materia",
        "inscripcion_materia__discente",
        "inscripcion_materia__discente__usuario",
        "inscripcion_materia__discente__usuario__grado_empleo",
        "inscripcion_materia__discente__plan_estudios__carrera",
        "inscripcion_materia__discente__antiguedad",
        "inscripcion_materia__asignacion_docente__usuario_docente",
        "inscripcion_materia__asignacion_docente__grupo_academico__periodo",
        "inscripcion_materia__asignacion_docente__programa_asignatura__materia",
        "inscripcion_materia__asignacion_docente__programa_asignatura__plan_estudios__carrera",
        "registrado_por",
    ), request.GET, request.user)
    item = queryset.filter(pk=pk).first()
    if not item:
        return JsonResponse({"ok": False, "message": "Extraordinario no encontrado."}, status=404)
    return JsonResponse({"ok": True, "item": _extraordinario_item(item)})


@require_POST
@csrf_protect
@api_login_required
def extraordinario_create_view(request):
    if not puede_operar_trayectoria(request.user):
        return _deny("No tienes permiso para registrar extraordinarios.")
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida."}, status=400)
    try:
        inscripcion = InscripcionMateria.objects.get(pk=data.get("inscripcion_materia_id") or data.get("inscripcion_materia"))
        extraordinario = registrar_extraordinario(
            inscripcion_materia=inscripcion,
            calificacion=_parse_decimal(data.get("calificacion"), "calificacion"),
            fecha_aplicacion=_parse_date(data.get("fecha_aplicacion"), "fecha_aplicacion"),
            registrado_por=request.user,
        )
    except InscripcionMateria.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Inscripción a materia no encontrada.", "errors": {"inscripcion_materia_id": ["No existe."]}}, status=404)
    except Exception as exc:
        registrar_evento_fallido(
            request=request,
            modulo=MODULO_TRAYECTORIA,
            evento_codigo="EXTRAORDINARIO_RECHAZADO",
            severidad=SEVERIDAD_ADVERTENCIA,
            resumen="Registro de extraordinario rechazado.",
            metadatos={"inscripcion_materia_id": data.get("inscripcion_materia_id") or data.get("inscripcion_materia"), "error": str(exc)[:300]},
        )
        return _error_response(exc)
    registrar_evento_exitoso(
        request=request,
        modulo=MODULO_TRAYECTORIA,
        evento_codigo="EXTRAORDINARIO_REGISTRADO",
        severidad=SEVERIDAD_INFO,
        objeto=extraordinario,
        resumen="Extraordinario registrado.",
        metadatos={
            "extraordinario_id": extraordinario.id,
            "discente_id": extraordinario.inscripcion_materia.discente_id,
            "inscripcion_materia_id": extraordinario.inscripcion_materia_id,
            "periodo_id": extraordinario.inscripcion_materia.asignacion_docente.grupo_academico.periodo_id,
            "aprobado": extraordinario.aprobado,
            "marca_generada": extraordinario.codigo_marca,
            "fecha_aplicacion": _date(extraordinario.fecha_aplicacion),
        },
    )
    return JsonResponse({"ok": True, "item": _extraordinario_item(extraordinario)}, status=201)


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def situaciones_list_view(request):
    if request.method == "POST":
        return situacion_create_view(request)
    if not puede_consultar_historiales(request.user):
        return _deny("No tienes permiso para consultar situaciones académicas.")
    queryset = EventoSituacionAcademica.objects.select_related(
        "discente",
        "discente__usuario",
        "discente__usuario__grado_empleo",
        "discente__plan_estudios__carrera",
        "discente__antiguedad",
        "situacion",
        "periodo",
        "registrado_por",
    )
    queryset = _filter_eventos(queryset, request.GET, request.user).order_by("-fecha_inicio", "-id")
    page, page_size, start, end = _page_params(request)
    total = queryset.count()
    return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [_evento_item(item) for item in queryset[start:end]]})


@require_GET
@api_login_required
def situacion_detail_view(request, pk):
    if not puede_consultar_historiales(request.user):
        return _deny("No tienes permiso para consultar situaciones académicas.")
    queryset = _filter_eventos(EventoSituacionAcademica.objects.select_related(
        "discente",
        "discente__usuario",
        "discente__usuario__grado_empleo",
        "discente__plan_estudios__carrera",
        "discente__antiguedad",
        "situacion",
        "periodo",
        "registrado_por",
    ), request.GET, request.user)
    item = queryset.filter(pk=pk).first()
    if not item:
        return JsonResponse({"ok": False, "message": "Situación académica no encontrada."}, status=404)
    return JsonResponse({"ok": True, "item": _evento_item(item)})


@require_POST
@csrf_protect
@api_login_required
def situacion_create_view(request):
    if not puede_operar_trayectoria(request.user):
        return _deny("No tienes permiso para registrar situaciones académicas.")
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida."}, status=400)
    try:
        discente = Discente.objects.get(pk=data.get("discente_id") or data.get("discente"))
        if data.get("situacion_id"):
            situacion = CatalogoSituacionAcademica.objects.get(pk=data.get("situacion_id"), activo=True)
        else:
            situacion = CatalogoSituacionAcademica.objects.get(clave=data.get("situacion_codigo") or data.get("situacion"), activo=True)
        periodo = None
        periodo_id = data.get("periodo_id") or data.get("periodo")
        if periodo_id:
            periodo = PeriodoEscolar.objects.get(pk=periodo_id)
        motivo = (data.get("motivo") or "").strip()
        observaciones = (data.get("observaciones") or "").strip()
        if observaciones and observaciones not in motivo:
            motivo = f"{motivo}\nObservaciones: {observaciones}".strip()
        evento = registrar_evento_situacion(
            discente=discente,
            situacion=situacion,
            fecha_inicio=_parse_date(data.get("fecha_inicio"), "fecha_inicio"),
            fecha_fin=_parse_date(data.get("fecha_fin"), "fecha_fin"),
            periodo=periodo,
            motivo=motivo,
            registrado_por=request.user,
        )
    except Discente.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Discente no encontrado.", "errors": {"discente_id": ["No existe."]}}, status=404)
    except CatalogoSituacionAcademica.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Situación académica no encontrada.", "errors": {"situacion": ["No existe o está inactiva."]}}, status=404)
    except PeriodoEscolar.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Periodo no encontrado.", "errors": {"periodo_id": ["No existe."]}}, status=404)
    except Exception as exc:
        return _error_response(exc)
    situacion_clave = evento.situacion.clave.upper()
    evento_codigo = "SITUACION_ACADEMICA_REGISTRADA"
    if "BAJA_TEMPORAL" in situacion_clave:
        evento_codigo = "BAJA_TEMPORAL_REGISTRADA"
    elif "BAJA_DEFINITIVA" in situacion_clave:
        evento_codigo = "BAJA_DEFINITIVA_REGISTRADA"
    elif "REINGRESO" in situacion_clave:
        evento_codigo = "REINGRESO_REGISTRADO"
    registrar_evento_exitoso(
        request=request,
        modulo=MODULO_TRAYECTORIA,
        evento_codigo=evento_codigo,
        severidad=SEVERIDAD_INFO,
        objeto=evento,
        resumen="Situacion academica registrada.",
        metadatos={
            "evento_situacion_id": evento.id,
            "discente_id": evento.discente_id,
            "periodo_id": evento.periodo_id,
            "situacion_codigo": evento.situacion.clave,
            "fecha_aplicacion": _date(evento.fecha_inicio),
        },
    )
    return JsonResponse({"ok": True, "item": _evento_item(evento)}, status=201)
