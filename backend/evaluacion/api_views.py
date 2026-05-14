import json
from decimal import Decimal, InvalidOperation

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from auditoria.eventos import MODULO_EVALUACION, SEVERIDAD_ADVERTENCIA, SEVERIDAD_INFO
from auditoria.services import registrar_evento_bloqueado, registrar_evento_exitoso
from core.api_views import api_login_required
from relaciones.models import AsignacionDocente, Discente, InscripcionMateria
from relaciones.permisos import usuario_es_admin_soporte, usuario_es_docente, usuario_es_estadistica

from .models import (
    Acta,
    CalificacionComponente,
    CapturaCalificacionPreliminar,
    ComponenteEvaluacion,
    ConformidadDiscente,
    DetalleActa,
    ValidacionActa,
)
from .services import (
    ServicioCalculoAcademico,
    crear_o_regenerar_borrador_acta,
    formalizar_acta_jefatura_academica,
    publicar_acta,
    registrar_conformidad_discente,
    remitir_acta,
    validar_acta_jefatura_carrera,
)
from .views import (
    ip_origen_request,
    obtener_acta_bloqueante_captura,
    obtener_cargo_jefatura_carrera_para_acta,
    puede_capturar_calificaciones,
    puede_consultar_acta,
    puede_consultar_calificaciones,
    puede_consultar_estados_actas,
    puede_formalizar_acta_academica,
    puede_operar_acta_docente,
    puede_validar_acta_carrera,
    puede_ver_actas_por_validar,
)


MAX_LIST_LIMIT = 200


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


def _choice_label(choices, value):
    return dict(choices).get(value, value)


def _messages(error):
    if hasattr(error, "message_dict"):
        messages = []
        for field, values in error.message_dict.items():
            messages.extend([f"{field}: {value}" for value in values])
        return messages
    if hasattr(error, "messages"):
        return error.messages
    return [str(error)]


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


def _bad_request(message="Solicitud inválida."):
    return JsonResponse({"ok": False, "message": message}, status=400)


def _limit(request, default=100):
    try:
        return max(1, min(int(request.GET.get("limit") or default), MAX_LIST_LIMIT))
    except ValueError:
        return default


def _usuario_min(usuario):
    if not usuario:
        return None
    grado = usuario.grado_empleo
    return {
        "id": usuario.id,
        "username": usuario.username,
        "nombre": usuario.nombre_visible,
        "nombre_institucional": usuario.nombre_institucional,
        "grado_empleo": grado.abreviatura if grado else "",
        "label": usuario.nombre_institucional,
    }


def _discente_min(discente):
    usuario = discente.usuario
    grado = usuario.grado_empleo
    return {
        "id": discente.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre_visible,
        "nombre_institucional": usuario.nombre_institucional,
        "grado_empleo": grado.abreviatura if grado else "",
        "situacion_actual": discente.situacion_actual,
        "situacion_actual_label": discente.get_situacion_actual_display(),
    }


def _carrera_min(carrera):
    if not carrera:
        return None
    return {"id": carrera.id, "clave": carrera.clave, "nombre": carrera.nombre, "label": str(carrera)}


def _periodo_min(periodo):
    if not periodo:
        return None
    return {
        "id": periodo.id,
        "clave": periodo.clave,
        "anio_escolar": periodo.anio_escolar,
        "periodo_academico": periodo.periodo_academico,
        "label": str(periodo),
    }


def _grupo_min(grupo):
    if not grupo:
        return None
    return {
        "id": grupo.id,
        "clave": grupo.clave_grupo,
        "nombre": grupo.clave_grupo,
        "semestre": grupo.semestre_numero,
        "periodo": _periodo_min(grupo.periodo),
        "label": str(grupo),
    }


def _programa_min(programa):
    if not programa:
        return None
    materia = programa.materia
    plan = programa.plan_estudios
    return {
        "id": programa.id,
        "materia_id": materia.id,
        "clave": materia.clave,
        "nombre": materia.nombre,
        "label": str(programa),
        "semestre": programa.semestre_numero,
        "anio_formacion": programa.anio_formacion,
        "plan": {"id": plan.id, "clave": plan.clave, "nombre": plan.nombre, "label": str(plan)},
        "carrera": _carrera_min(plan.carrera),
    }


def _asignaciones_queryset():
    return (
        AsignacionDocente.objects.select_related(
            "usuario_docente",
            "usuario_docente__grado_empleo",
            "grupo_academico",
            "grupo_academico__periodo",
            "grupo_academico__antiguedad",
            "grupo_academico__antiguedad__plan_estudios",
            "grupo_academico__antiguedad__plan_estudios__carrera",
            "programa_asignatura",
            "programa_asignatura__materia",
            "programa_asignatura__plan_estudios",
            "programa_asignatura__plan_estudios__carrera",
        )
        .annotate(num_discentes=Count("inscripciones_materia", filter=Q(inscripciones_materia__estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA)))
        .order_by("-activo", "grupo_academico__periodo__clave", "grupo_academico__clave_grupo", "programa_asignatura__materia__clave")
    )


def _actas_queryset():
    return (
        Acta.objects.select_related(
            "asignacion_docente",
            "asignacion_docente__usuario_docente",
            "asignacion_docente__usuario_docente__grado_empleo",
            "asignacion_docente__grupo_academico",
            "asignacion_docente__grupo_academico__periodo",
            "asignacion_docente__grupo_academico__antiguedad",
            "asignacion_docente__programa_asignatura",
            "asignacion_docente__programa_asignatura__materia",
            "asignacion_docente__programa_asignatura__plan_estudios",
            "asignacion_docente__programa_asignatura__plan_estudios__carrera",
            "esquema",
            "creado_por",
            "creado_por__grado_empleo",
        )
        .prefetch_related(
            "detalles",
            "detalles__inscripcion_materia",
            "detalles__inscripcion_materia__discente",
            "detalles__inscripcion_materia__discente__usuario",
            "detalles__inscripcion_materia__discente__usuario__grado_empleo",
            "detalles__calificaciones_componentes",
            "detalles__calificaciones_componentes__componente",
            "detalles__conformidades",
            "validaciones",
            "validaciones__usuario",
            "validaciones__usuario__grado_empleo",
            "validaciones__asignacion_cargo",
            "validaciones__asignacion_cargo__unidad_organizacional",
            "validaciones__asignacion_cargo__carrera",
        )
        .order_by("-creado_en")
    )


def _serialize_esquema(esquema):
    return {
        "id": esquema.id,
        "version": esquema.version,
        "num_parciales": esquema.num_parciales,
        "cortes": esquema.cortes_esperados(),
        "permite_exencion": esquema.permite_exencion,
        "peso_parciales": _decimal(esquema.peso_parciales),
        "peso_final": _decimal(esquema.peso_final),
        "umbral_exencion": _decimal(esquema.umbral_exencion),
    }


def _serialize_componente(componente):
    return {
        "id": componente.id,
        "corte_codigo": componente.corte_codigo,
        "corte_label": componente.get_corte_codigo_display(),
        "nombre": componente.nombre,
        "porcentaje": _decimal(componente.porcentaje),
        "es_examen": componente.es_examen,
        "orden": componente.orden,
    }


def _serialize_asignacion(asignacion, include_urls=True):
    grupo = asignacion.grupo_academico
    programa = asignacion.programa_asignatura
    actas = list(asignacion.actas.exclude(estado_acta=Acta.ESTADO_ARCHIVADO).order_by("corte_codigo"))
    estado_operativo = "Sin acta"
    if actas:
        estado_operativo = ", ".join([f"{acta.corte_codigo}: {acta.get_estado_acta_display()}" for acta in actas])

    item = {
        "asignacion_id": asignacion.id,
        "id": asignacion.id,
        "docente": _usuario_min(asignacion.usuario_docente),
        "periodo": _periodo_min(grupo.periodo),
        "carrera": _carrera_min(programa.plan_estudios.carrera),
        "grupo": _grupo_min(grupo),
        "semestre": grupo.semestre_numero,
        "programa_asignatura": _programa_min(programa),
        "materia": {"id": programa.materia_id, "clave": programa.materia.clave, "nombre": programa.materia.nombre},
        "num_discentes": getattr(asignacion, "num_discentes", None),
        "activo": asignacion.activo,
        "estado_operativo": estado_operativo,
    }
    if include_urls:
        item["urls"] = {
            "detalle": f"/api/docente/asignaciones/{asignacion.id}/",
            "captura_base": f"/api/docente/asignaciones/{asignacion.id}/captura/",
            "resumen": f"/api/docente/asignaciones/{asignacion.id}/resumen/",
            "actas": f"/api/docente/actas/?asignacion={asignacion.id}",
        }
    return item


def _acta_actions(acta, user):
    return {
        "puede_regenerar": acta.estado_acta == Acta.ESTADO_BORRADOR_DOCENTE and puede_operar_acta_docente(user, acta),
        "puede_publicar": acta.estado_acta == Acta.ESTADO_BORRADOR_DOCENTE and puede_operar_acta_docente(user, acta),
        "puede_remitir": acta.estado_acta == Acta.ESTADO_PUBLICADO_DISCENTE and puede_operar_acta_docente(user, acta),
        "puede_validar_carrera": acta.estado_acta == Acta.ESTADO_REMITIDO_JEFATURA_CARRERA and bool(puede_validar_acta_carrera(user, acta)),
        "puede_formalizar": acta.estado_acta == Acta.ESTADO_VALIDADO_JEFATURA_CARRERA and bool(puede_formalizar_acta_academica(user)),
        "solo_lectura": acta.solo_lectura,
    }


def _serialize_acta_resumen(acta, user=None):
    asignacion = acta.asignacion_docente
    grupo = asignacion.grupo_academico
    programa = asignacion.programa_asignatura
    item = {
        "acta_id": acta.id,
        "id": acta.id,
        "asignacion_docente_id": asignacion.id,
        "periodo": _periodo_min(grupo.periodo),
        "carrera": _carrera_min(programa.plan_estudios.carrera),
        "grupo": _grupo_min(grupo),
        "semestre": grupo.semestre_numero,
        "programa_asignatura": _programa_min(programa),
        "materia": {"id": programa.materia_id, "clave": programa.materia.clave, "nombre": programa.materia.nombre},
        "docente": _usuario_min(asignacion.usuario_docente),
        "corte_codigo": acta.corte_codigo,
        "corte_label": _choice_label(ComponenteEvaluacion.CORTE_CHOICES, acta.corte_codigo),
        "estado_acta": acta.estado_acta,
        "estado_acta_label": acta.get_estado_acta_display(),
        "es_final": acta.es_final,
        "solo_lectura": acta.solo_lectura,
        "es_documento_oficial": acta.estado_acta == Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
        "publicada_en": _datetime(acta.publicada_en),
        "remitida_en": _datetime(acta.remitida_en),
        "formalizada_en": _datetime(acta.formalizada_en),
        "creado_en": _datetime(acta.creado_en),
        "actualizado_en": _datetime(acta.actualizado_en),
        "total_discentes": acta.detalles.count() if hasattr(acta, "detalles") else None,
        "url_pdf": f"/api/exportaciones/actas/{acta.id}/pdf/",
        "url_xlsx": f"/api/exportaciones/actas/{acta.id}/xlsx/",
    }
    if user is not None:
        item["acciones"] = _acta_actions(acta, user)
    return item


def _serialize_calificacion(calificacion):
    return {
        "id": calificacion.id,
        "componente_id": calificacion.componente_id,
        "nombre": calificacion.componente_nombre_snapshot,
        "porcentaje": _decimal(calificacion.componente_porcentaje_snapshot),
        "es_examen": calificacion.componente_es_examen_snapshot,
        "valor_capturado": _decimal(calificacion.valor_capturado),
        "valor_calculado": _decimal(calificacion.valor_calculado),
        "sustituido_por_exencion": calificacion.sustituido_por_exencion,
    }


def _serialize_conformidad(conformidad, include_comment=True):
    if not conformidad:
        return None
    item = {
        "id": conformidad.id,
        "estado_conformidad": conformidad.estado_conformidad,
        "estado_conformidad_label": conformidad.get_estado_conformidad_display(),
        "vigente": conformidad.vigente,
        "registrado_en": _datetime(conformidad.registrado_en),
        "invalidado_en": _datetime(conformidad.invalidado_en),
    }
    if include_comment:
        item["comentario"] = conformidad.comentario
    return item


def _serialize_detalle_acta(detalle, include_discente=True, include_comment=True):
    conformidad = detalle.conformidades.filter(vigente=True).first()
    item = {
        "detalle_id": detalle.id,
        "id": detalle.id,
        "resultado_corte": _decimal(detalle.resultado_corte_visible),
        "promedio_parciales": _decimal(detalle.promedio_parciales_visible),
        "resultado_final_preliminar": _decimal(detalle.resultado_final_preliminar_visible),
        "resultado_preliminar": detalle.resultado_preliminar,
        "exencion_aplica": detalle.exencion_aplica,
        "completo": detalle.completo,
        "calificaciones": [_serialize_calificacion(calificacion) for calificacion in detalle.calificaciones_componentes.all()],
        "conformidad_vigente": _serialize_conformidad(conformidad, include_comment=include_comment),
    }
    if include_discente:
        item["discente"] = _discente_min(detalle.inscripcion_materia.discente)
    return item


def _serialize_validacion(validacion):
    cargo = validacion.asignacion_cargo
    return {
        "id": validacion.id,
        "etapa_validacion": validacion.etapa_validacion,
        "etapa_validacion_label": validacion.get_etapa_validacion_display(),
        "accion": validacion.accion,
        "accion_label": validacion.get_accion_display(),
        "usuario": _usuario_min(validacion.usuario),
        "cargo": cargo.get_cargo_codigo_display() if cargo else "",
        "cargo_codigo": cargo.cargo_codigo if cargo else "",
        "unidad_organizacional": str(cargo.unidad_organizacional) if cargo and cargo.unidad_organizacional_id else "",
        "carrera": str(cargo.carrera) if cargo and cargo.carrera_id else "",
        "fecha_hora": _datetime(validacion.fecha_hora),
        "ip_origen": validacion.ip_origen,
        "comentario": validacion.comentario,
    }


def _serialize_acta_detalle(acta, user, include_all_rows=True):
    detalles = list(acta.detalles.all())
    componentes = []
    seen = set()
    for detalle in detalles:
        for calificacion in detalle.calificaciones_componentes.all():
            if calificacion.componente_id in seen:
                continue
            seen.add(calificacion.componente_id)
            componentes.append(
                {
                    "id": calificacion.componente_id,
                    "nombre": calificacion.componente_nombre_snapshot,
                    "porcentaje": _decimal(calificacion.componente_porcentaje_snapshot),
                    "es_examen": calificacion.componente_es_examen_snapshot,
                }
            )

    return {
        "ok": True,
        "acta": _serialize_acta_resumen(acta, user=user),
        "componentes": componentes,
        "filas": [_serialize_detalle_acta(detalle, include_discente=include_all_rows) for detalle in detalles],
        "validaciones": [_serialize_validacion(validacion) for validacion in acta.validaciones.all()],
        "acciones": _acta_actions(acta, user),
        "exportaciones": {
            "pdf": f"/api/exportaciones/actas/{acta.id}/pdf/",
            "xlsx": f"/api/exportaciones/actas/{acta.id}/xlsx/",
        },
        "avisos": {
            "solo_lectura": acta.solo_lectura,
            "documento_oficial": acta.estado_acta == Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            "no_oficial": acta.estado_acta != Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
        },
    }


def _filter_actas(qs, params):
    periodo = (params.get("periodo") or "").strip()
    carrera = (params.get("carrera") or "").strip()
    grupo = (params.get("grupo") or "").strip()
    docente = (params.get("docente") or "").strip()
    corte = (params.get("corte") or "").strip().upper()
    estado = (params.get("estado") or params.get("estado_acta") or "").strip().upper()
    asignacion = (params.get("asignacion") or "").strip()

    if periodo:
        qs = qs.filter(Q(asignacion_docente__grupo_academico__periodo_id=periodo) if periodo.isdigit() else Q(asignacion_docente__grupo_academico__periodo__clave__icontains=periodo))
    if carrera:
        qs = qs.filter(Q(asignacion_docente__programa_asignatura__plan_estudios__carrera_id=carrera) if carrera.isdigit() else Q(asignacion_docente__programa_asignatura__plan_estudios__carrera__clave__icontains=carrera))
    if grupo:
        qs = qs.filter(Q(asignacion_docente__grupo_academico_id=grupo) if grupo.isdigit() else Q(asignacion_docente__grupo_academico__clave_grupo__icontains=grupo))
    if docente:
        qs = qs.filter(Q(asignacion_docente__usuario_docente_id=docente) if docente.isdigit() else (Q(asignacion_docente__usuario_docente__username__icontains=docente) | Q(asignacion_docente__usuario_docente__nombre_completo__icontains=docente)))
    if corte:
        qs = qs.filter(corte_codigo=corte)
    if estado:
        qs = qs.filter(estado_acta=estado)
    if asignacion and asignacion.isdigit():
        qs = qs.filter(asignacion_docente_id=asignacion)
    return qs


def _actas_list_response(request, qs, user):
    qs = _filter_actas(qs, request.GET)
    total = qs.count() if hasattr(qs, "count") else len(qs)
    items = [_serialize_acta_resumen(acta, user=user) for acta in list(qs)[: _limit(request)]]
    return JsonResponse({"ok": True, "total": total, "items": items})


def _get_asignacion_or_404(pk):
    return _asignaciones_queryset().get(pk=pk)


def _get_acta_or_404(acta_id):
    return _actas_queryset().get(pk=acta_id)


def _capture_components(asignacion, corte_codigo):
    esquema = ServicioCalculoAcademico.obtener_esquema_activo(asignacion.programa_asignatura)
    corte = corte_codigo.upper()
    if corte not in esquema.cortes_esperados():
        raise ValidationError("El corte solicitado no aplica al esquema activo.")
    componentes = list(esquema.componentes.filter(corte_codigo=corte).order_by("orden", "pk"))
    return esquema, corte, componentes


def _serialize_calculo_resultado(resultado):
    cortes = {}
    for corte, data in resultado["cortes"].items():
        cortes[corte] = {
            "corte": corte,
            "completo": data["completo"],
            "resultado": _decimal(data["resultado_visual"]),
            "componentes": [
                {
                    "componente_id": item["componente"].id,
                    "nombre": item["componente"].nombre,
                    "valor": _decimal(item["valor"]),
                    "valor_capturado": _decimal(item["valor_capturado"]),
                    "porcentaje": _decimal(item["porcentaje"]),
                    "ponderado": _decimal(item["ponderado"]),
                    "sustituido_por_exencion": item["sustituido_por_exencion"],
                }
                for item in data["componentes"]
            ],
        }

    inscripcion = resultado["inscripcion"]
    return {
        "inscripcion_id": inscripcion.id,
        "discente": _discente_min(inscripcion.discente),
        "cortes": cortes,
        "promedio_parciales": _decimal(resultado["promedio_parciales_visual"]),
        "exencion_aplica": resultado["exencion_aplica"],
        "resultado_final": _decimal(resultado["resultado_final_visual"]),
        "calificacion_final_preliminar": _decimal(resultado["calificacion_final_preliminar_visual"]),
        "resultado_preliminar": resultado["resultado_preliminar"],
    }


@require_GET
@api_login_required
def docente_asignaciones_view(request):
    if not (usuario_es_docente(request.user) or usuario_es_admin_soporte(request.user)):
        return _deny("No tienes permiso para consultar asignaciones docentes.")
    qs = _asignaciones_queryset().filter(activo=True)
    if not usuario_es_admin_soporte(request.user):
        qs = qs.filter(usuario_docente=request.user)
    query = (request.GET.get("q") or request.GET.get("search") or "").strip()
    if query:
        qs = qs.filter(Q(grupo_academico__clave_grupo__icontains=query) | Q(programa_asignatura__materia__clave__icontains=query) | Q(programa_asignatura__materia__nombre__icontains=query))
    items = [_serialize_asignacion(asignacion) for asignacion in qs[: _limit(request)]]
    return JsonResponse({"ok": True, "total": qs.count(), "items": items})


@require_GET
@api_login_required
def docente_asignacion_detalle_view(request, pk):
    try:
        asignacion = _get_asignacion_or_404(pk)
    except AsignacionDocente.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Asignación no encontrada."}, status=404)
    if not puede_consultar_calificaciones(request.user, asignacion):
        return _deny("No tienes permiso para consultar esta asignación.")
    inscripciones = asignacion.inscripciones_materia.select_related("discente", "discente__usuario", "discente__usuario__grado_empleo").filter(estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA).order_by("discente__usuario__nombre_completo", "discente__usuario__username")
    try:
        esquema = ServicioCalculoAcademico.obtener_esquema_activo(asignacion.programa_asignatura)
        componentes = [_serialize_componente(componente) for componente in esquema.componentes.all().order_by("corte_codigo", "orden", "pk")]
        cortes = esquema.cortes_esperados()
    except ValidationError:
        esquema = None
        componentes = []
        cortes = []
    actas = asignacion.actas.exclude(estado_acta=Acta.ESTADO_ARCHIVADO).all()
    return JsonResponse(
        {
            "ok": True,
            "item": _serialize_asignacion(asignacion),
            "esquema": _serialize_esquema(esquema) if esquema else None,
            "componentes": componentes,
            "cortes": cortes,
            "discentes": [{"inscripcion_id": item.id, "discente": _discente_min(item.discente)} for item in inscripciones],
            "actas": [_serialize_acta_resumen(acta, user=request.user) for acta in actas],
        }
    )


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def docente_captura_corte_view(request, pk, corte_codigo):
    try:
        asignacion = _get_asignacion_or_404(pk)
    except AsignacionDocente.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Asignación no encontrada."}, status=404)
    if not puede_capturar_calificaciones(request.user, asignacion):
        return _deny("No tienes permiso para capturar esta asignación.")
    try:
        esquema, corte, componentes = _capture_components(asignacion, corte_codigo)
    except ValidationError as exc:
        return _error_response(exc)

    acta_bloqueante = obtener_acta_bloqueante_captura(asignacion, corte)
    if request.method == "POST":
        if acta_bloqueante:
            registrar_evento_bloqueado(
                request=request,
                modulo=MODULO_EVALUACION,
                evento_codigo="CAPTURA_PRELIMINAR_BLOQUEADA",
                severidad=SEVERIDAD_ADVERTENCIA,
                objeto=asignacion,
                resumen="Captura preliminar bloqueada por acta avanzada.",
                metadatos={
                    "asignacion_docente_id": asignacion.id,
                    "corte_codigo": corte,
                    "acta_bloqueante_id": acta_bloqueante.id,
                    "estado_acta": acta_bloqueante.estado_acta,
                },
            )
            return _bad_request("Este corte ya tiene un acta publicada, remitida, validada o formalizada. La captura preliminar quedó bloqueada.")
        data = _json_body(request)
        if data is None:
            return _bad_request()
        try:
            saved, deleted = _guardar_captura_payload(asignacion, componentes, data, request.user)
        except ValidationError as exc:
            return _error_response(exc, message="No fue posible guardar la captura preliminar.")
        except (InvalidOperation, ValueError) as exc:
            return _error_response(ValidationError(str(exc)), message="No fue posible guardar la captura preliminar.")
        total_recibidos = len(data.get("valores") or data.get("capturas") or []) if isinstance(data, dict) else 0
        registrar_evento_exitoso(
            request=request,
            modulo=MODULO_EVALUACION,
            evento_codigo="CAPTURA_PRELIMINAR_GUARDADA",
            severidad=SEVERIDAD_INFO,
            objeto=asignacion,
            resumen="Captura preliminar guardada con resumen de valores.",
            metadatos={
                "asignacion_docente_id": asignacion.id,
                "corte_codigo": corte,
                "total_discentes": asignacion.inscripciones_materia.filter(estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA).count(),
                "total_componentes": len(componentes),
                "total_valores_recibidos": total_recibidos,
                "total_valores_guardados": saved,
                "total_valores_borrados": deleted,
            },
        )
        if deleted:
            registrar_evento_exitoso(
                request=request,
                modulo=MODULO_EVALUACION,
                evento_codigo="CAPTURA_PRELIMINAR_ELIMINADA",
                severidad=SEVERIDAD_INFO,
                objeto=asignacion,
                resumen="Valores de captura preliminar eliminados por campo vacio.",
                metadatos={
                    "asignacion_docente_id": asignacion.id,
                    "corte_codigo": corte,
                    "total_valores_borrados": deleted,
                },
            )
    else:
        saved = deleted = 0

    return _captura_response(asignacion, esquema, corte, componentes, request.user, bool(acta_bloqueante), acta_bloqueante, saved, deleted)


def _guardar_captura_payload(asignacion, componentes, data, usuario):
    entries = data.get("valores") or data.get("capturas") or []
    if not isinstance(entries, list):
        raise ValidationError("El payload debe incluir una lista de valores.")
    componentes_por_id = {componente.id: componente for componente in componentes}
    inscripciones = {
        item.id: item
        for item in asignacion.inscripciones_materia.filter(estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA)
    }
    saved = 0
    deleted = 0
    with transaction.atomic():
        for entry in entries:
            try:
                inscripcion_id = int(entry.get("inscripcion_id"))
                componente_id = int(entry.get("componente_id"))
            except (TypeError, ValueError):
                raise ValidationError("Cada valor debe incluir inscripcion_id y componente_id válidos.")
            if inscripcion_id not in inscripciones:
                raise ValidationError("Una inscripción no pertenece a la asignación docente.")
            if componente_id not in componentes_por_id:
                raise ValidationError("Un componente no corresponde al corte solicitado.")
            value = entry.get("valor")
            existing = CapturaCalificacionPreliminar.objects.filter(
                inscripcion_materia_id=inscripcion_id,
                componente_id=componente_id,
            ).first()
            if value in ("", None):
                if existing:
                    existing.delete()
                    deleted += 1
                continue
            valor = Decimal(str(value))
            if existing:
                existing.valor = valor
                existing.capturado_por = usuario
                existing.save()
            else:
                CapturaCalificacionPreliminar.objects.create(
                    inscripcion_materia=inscripciones[inscripcion_id],
                    componente=componentes_por_id[componente_id],
                    valor=valor,
                    capturado_por=usuario,
                )
            saved += 1
    return saved, deleted


def _captura_response(asignacion, esquema, corte, componentes, user, bloqueada, acta_bloqueante, saved=0, deleted=0):
    inscripciones = list(
        asignacion.inscripciones_materia.select_related("discente", "discente__usuario", "discente__usuario__grado_empleo")
        .filter(estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA)
        .order_by("discente__usuario__nombre_completo", "discente__usuario__username")
    )
    capturas = {
        (captura.inscripcion_materia_id, captura.componente_id): captura
        for captura in CapturaCalificacionPreliminar.objects.filter(
            inscripcion_materia__in=inscripciones,
            componente__in=componentes,
        )
    }
    filas = []
    resultados = []
    errores = []
    for inscripcion in inscripciones:
        filas.append(
            {
                "inscripcion_id": inscripcion.id,
                "discente": _discente_min(inscripcion.discente),
                "valores": [
                    {
                        "componente_id": componente.id,
                        "valor": _decimal(capturas[(inscripcion.id, componente.id)].valor) if (inscripcion.id, componente.id) in capturas else None,
                    }
                    for componente in componentes
                ],
            }
        )
        try:
            resultado = ServicioCalculoAcademico(inscripcion).calcular()
            corte_resultado = resultado["cortes"].get(corte)
            resultados.append(
                {
                    "inscripcion_id": inscripcion.id,
                    "resultado_corte": _decimal(corte_resultado["resultado_visual"]) if corte_resultado else None,
                    "completo": bool(corte_resultado["completo"]) if corte_resultado else False,
                    "exencion_aplica": resultado["exencion_aplica"],
                }
            )
        except ValidationError as exc:
            errores.extend(_messages(exc))

    return JsonResponse(
        {
            "ok": True,
            "asignacion": _serialize_asignacion(asignacion),
            "esquema": _serialize_esquema(esquema),
            "corte": corte,
            "componentes": [_serialize_componente(componente) for componente in componentes],
            "filas": filas,
            "resultados_corte": resultados,
            "captura_bloqueada": bloqueada,
            "acta_bloqueante": _serialize_acta_resumen(acta_bloqueante, user=user) if acta_bloqueante else None,
            "guardados": saved,
            "limpiados": deleted,
            "errores_calculo": errores,
        }
    )


@require_GET
@api_login_required
def docente_resumen_asignacion_view(request, pk):
    try:
        asignacion = _get_asignacion_or_404(pk)
    except AsignacionDocente.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Asignación no encontrada."}, status=404)
    if not puede_consultar_calificaciones(request.user, asignacion):
        return _deny("No tienes permiso para consultar el resumen de esta asignación.")
    resultados = []
    errores = []
    for inscripcion in asignacion.inscripciones_materia.select_related("discente", "discente__usuario", "discente__usuario__grado_empleo").filter(estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA):
        try:
            resultados.append(_serialize_calculo_resultado(ServicioCalculoAcademico(inscripcion).calcular()))
        except ValidationError as exc:
            errores.extend(_messages(exc))
    return JsonResponse({"ok": True, "asignacion": _serialize_asignacion(asignacion), "items": resultados, "total": len(resultados), "errores_calculo": errores})


@require_GET
@api_login_required
def docente_actas_view(request):
    if not (usuario_es_docente(request.user) or usuario_es_admin_soporte(request.user)):
        return _deny("No tienes permiso para consultar actas docentes.")
    qs = _actas_queryset()
    if not usuario_es_admin_soporte(request.user):
        qs = qs.filter(asignacion_docente__usuario_docente=request.user)
    return _actas_list_response(request, qs, request.user)


@require_GET
@api_login_required
def docente_acta_detalle_view(request, acta_id):
    try:
        acta = _get_acta_or_404(acta_id)
    except Acta.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Acta no encontrada."}, status=404)
    if not puede_operar_acta_docente(request.user, acta):
        return _deny("No tienes permiso para consultar esta acta docente.")
    return JsonResponse(_serialize_acta_detalle(acta, request.user))


@require_POST
@csrf_protect
@api_login_required
def docente_generar_acta_view(request, pk):
    try:
        asignacion = _get_asignacion_or_404(pk)
    except AsignacionDocente.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Asignación no encontrada."}, status=404)
    if not puede_capturar_calificaciones(request.user, asignacion):
        return _deny("No tienes permiso para generar actas de esta asignación.")
    data = _json_body(request)
    if data is None:
        return _bad_request()
    try:
        acta = crear_o_regenerar_borrador_acta(asignacion, (data.get("corte_codigo") or data.get("corte") or "").upper(), request.user)
    except ValidationError as exc:
        return _error_response(exc, message="No fue posible generar el borrador de acta.")
    return JsonResponse({"ok": True, "item": _serialize_acta_resumen(acta, user=request.user), "detalle": _serialize_acta_detalle(_get_acta_or_404(acta.id), request.user)})


@require_POST
@csrf_protect
@api_login_required
def docente_regenerar_acta_view(request, acta_id):
    try:
        acta = _get_acta_or_404(acta_id)
    except Acta.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Acta no encontrada."}, status=404)
    if not puede_operar_acta_docente(request.user, acta):
        return _deny("No tienes permiso para regenerar esta acta.")
    try:
        acta = crear_o_regenerar_borrador_acta(acta.asignacion_docente, acta.corte_codigo, request.user)
    except ValidationError as exc:
        return _error_response(exc, message="No fue posible regenerar el acta.")
    return JsonResponse({"ok": True, "item": _serialize_acta_resumen(acta, user=request.user)})


@require_POST
@csrf_protect
@api_login_required
def docente_publicar_acta_view(request, acta_id):
    return _docente_action(request, acta_id, publicar_acta, "No fue posible publicar el acta.")


@require_POST
@csrf_protect
@api_login_required
def docente_remitir_acta_view(request, acta_id):
    return _docente_action(request, acta_id, remitir_acta, "No fue posible remitir el acta.")


def _docente_action(request, acta_id, service_func, error_message):
    try:
        acta = _get_acta_or_404(acta_id)
    except Acta.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Acta no encontrada."}, status=404)
    if not puede_operar_acta_docente(request.user, acta):
        return _deny("No tienes permiso para operar esta acta.")
    try:
        acta = service_func(acta, request.user, ip_origen=ip_origen_request(request))
    except ValidationError as exc:
        return _error_response(exc, message=error_message)
    return JsonResponse({"ok": True, "item": _serialize_acta_resumen(acta, user=request.user), "detalle": _serialize_acta_detalle(_get_acta_or_404(acta.id), request.user)})


@require_GET
@api_login_required
def discente_actas_view(request):
    discente = Discente.objects.filter(usuario=request.user, activo=True).first()
    if not discente:
        return JsonResponse({"ok": True, "total": 0, "items": []})
    detalles = (
        DetalleActa.objects.select_related(
            "acta",
            "acta__asignacion_docente",
            "acta__asignacion_docente__usuario_docente",
            "acta__asignacion_docente__usuario_docente__grado_empleo",
            "acta__asignacion_docente__grupo_academico",
            "acta__asignacion_docente__grupo_academico__periodo",
            "acta__asignacion_docente__programa_asignatura",
            "acta__asignacion_docente__programa_asignatura__materia",
            "acta__asignacion_docente__programa_asignatura__plan_estudios",
            "acta__asignacion_docente__programa_asignatura__plan_estudios__carrera",
        )
        .prefetch_related("conformidades")
        .filter(
            inscripcion_materia__discente=discente,
            acta__estado_acta__in=[
                Acta.ESTADO_PUBLICADO_DISCENTE,
                Acta.ESTADO_REMITIDO_JEFATURA_CARRERA,
                Acta.ESTADO_VALIDADO_JEFATURA_CARRERA,
                Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            ],
        )
        .order_by("-acta__publicada_en", "-acta__creado_en")
    )
    items = []
    for detalle in detalles[: _limit(request)]:
        acta = detalle.acta
        conformidad = detalle.conformidades.filter(vigente=True).first()
        items.append(
            {
                "acta_id": acta.id,
                "detalle_id": detalle.id,
                "asignatura": acta.asignacion_docente.programa_asignatura.materia.nombre,
                "docente": _usuario_min(acta.asignacion_docente.usuario_docente),
                "grupo": _grupo_min(acta.asignacion_docente.grupo_academico),
                "periodo": _periodo_min(acta.asignacion_docente.grupo_academico.periodo),
                "corte_codigo": acta.corte_codigo,
                "corte_label": _choice_label(ComponenteEvaluacion.CORTE_CHOICES, acta.corte_codigo),
                "estado_acta": acta.estado_acta,
                "estado_acta_label": acta.get_estado_acta_display(),
                "resultado_visible": _decimal(detalle.resultado_corte_visible if not acta.es_final else detalle.resultado_final_preliminar_visible),
                "conformidad_vigente": _serialize_conformidad(conformidad, include_comment=False),
                "puede_registrar_conformidad": acta.estado_acta == Acta.ESTADO_PUBLICADO_DISCENTE,
                "fecha_publicacion": _datetime(acta.publicada_en),
            }
        )
    return JsonResponse({"ok": True, "total": detalles.count(), "items": items})


@require_GET
@api_login_required
def discente_acta_detalle_view(request, detalle_id):
    try:
        detalle = (
            DetalleActa.objects.select_related(
                "acta",
                "acta__asignacion_docente",
                "acta__asignacion_docente__usuario_docente",
                "acta__asignacion_docente__grupo_academico",
                "acta__asignacion_docente__grupo_academico__periodo",
                "acta__asignacion_docente__programa_asignatura",
                "acta__asignacion_docente__programa_asignatura__materia",
                "acta__asignacion_docente__programa_asignatura__plan_estudios",
                "acta__asignacion_docente__programa_asignatura__plan_estudios__carrera",
                "inscripcion_materia",
                "inscripcion_materia__discente",
                "inscripcion_materia__discente__usuario",
                "inscripcion_materia__discente__usuario__grado_empleo",
            )
            .prefetch_related("calificaciones_componentes", "conformidades")
            .get(pk=detalle_id)
        )
    except DetalleActa.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Detalle de acta no encontrado."}, status=404)
    if detalle.inscripcion_materia.discente.usuario_id != request.user.id:
        return _deny("No tienes permiso para consultar este detalle.")
    if detalle.acta.estado_acta == Acta.ESTADO_BORRADOR_DOCENTE:
        return _deny("El acta aún no está publicada.")
    return JsonResponse(
        {
            "ok": True,
            "acta": _serialize_acta_resumen(detalle.acta, user=request.user),
            "detalle": _serialize_detalle_acta(detalle, include_discente=False, include_comment=True),
            "puede_registrar_conformidad": detalle.acta.estado_acta == Acta.ESTADO_PUBLICADO_DISCENTE,
            "historial_conformidad": [_serialize_conformidad(item, include_comment=True) for item in detalle.conformidades.all()],
        }
    )


@require_POST
@csrf_protect
@api_login_required
def discente_conformidad_view(request, detalle_id):
    data = _json_body(request)
    if data is None:
        return _bad_request()
    try:
        detalle = DetalleActa.objects.select_related("acta", "inscripcion_materia", "inscripcion_materia__discente").get(pk=detalle_id)
    except DetalleActa.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Detalle de acta no encontrado."}, status=404)
    try:
        conformidad = registrar_conformidad_discente(
            detalle,
            request.user,
            (data.get("tipo_conformidad") or data.get("estado_conformidad") or "").upper(),
            data.get("comentario") or "",
        )
    except ValidationError as exc:
        return _error_response(exc, message="No fue posible registrar la conformidad.")
    return JsonResponse({"ok": True, "item": _serialize_conformidad(conformidad, include_comment=True)})


@require_GET
@api_login_required
def jefatura_carrera_actas_pendientes_view(request):
    if not puede_ver_actas_por_validar(request.user):
        return _deny("No tienes permiso para consultar actas por validar.")
    qs = _filter_actas(_actas_queryset().filter(estado_acta=Acta.ESTADO_REMITIDO_JEFATURA_CARRERA), request.GET)
    if usuario_es_admin_soporte(request.user):
        return _actas_list_response(request, qs, request.user)
    actas = [acta for acta in qs if obtener_cargo_jefatura_carrera_para_acta(request.user, acta)]
    return JsonResponse({"ok": True, "total": len(actas), "items": [_serialize_acta_resumen(acta, user=request.user) for acta in actas[: _limit(request)]]})


@require_GET
@api_login_required
def jefatura_carrera_acta_detalle_view(request, acta_id):
    try:
        acta = _get_acta_or_404(acta_id)
    except Acta.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Acta no encontrada."}, status=404)
    if not puede_validar_acta_carrera(request.user, acta):
        return _deny("No tienes permiso para consultar esta acta.")
    return JsonResponse(_serialize_acta_detalle(acta, request.user))


@require_POST
@csrf_protect
@api_login_required
def jefatura_carrera_validar_acta_view(request, acta_id):
    try:
        acta = _get_acta_or_404(acta_id)
    except Acta.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Acta no encontrada."}, status=404)
    if not puede_validar_acta_carrera(request.user, acta):
        return _deny("No tienes permiso para validar esta acta.")
    try:
        acta = validar_acta_jefatura_carrera(acta, request.user, ip_origen=ip_origen_request(request))
    except ValidationError as exc:
        return _error_response(exc, message="No fue posible validar el acta.")
    return JsonResponse({"ok": True, "item": _serialize_acta_resumen(acta, user=request.user), "detalle": _serialize_acta_detalle(_get_acta_or_404(acta.id), request.user)})


@require_GET
@api_login_required
def jefatura_academica_actas_pendientes_view(request):
    if not puede_formalizar_acta_academica(request.user):
        return _deny("No tienes permiso para consultar actas por formalizar.")
    qs = _actas_queryset().filter(estado_acta=Acta.ESTADO_VALIDADO_JEFATURA_CARRERA)
    return _actas_list_response(request, qs, request.user)


@require_GET
@api_login_required
def jefatura_academica_acta_detalle_view(request, acta_id):
    try:
        acta = _get_acta_or_404(acta_id)
    except Acta.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Acta no encontrada."}, status=404)
    if not puede_formalizar_acta_academica(request.user):
        return _deny("No tienes permiso para consultar esta acta.")
    return JsonResponse(_serialize_acta_detalle(acta, request.user))


@require_POST
@csrf_protect
@api_login_required
def jefatura_academica_formalizar_acta_view(request, acta_id):
    try:
        acta = _get_acta_or_404(acta_id)
    except Acta.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Acta no encontrada."}, status=404)
    if not puede_formalizar_acta_academica(request.user):
        return _deny("No tienes permiso para formalizar esta acta.")
    try:
        acta = formalizar_acta_jefatura_academica(acta, request.user, ip_origen=ip_origen_request(request))
    except ValidationError as exc:
        return _error_response(exc, message="No fue posible formalizar el acta.")
    return JsonResponse({"ok": True, "item": _serialize_acta_resumen(acta, user=request.user), "detalle": _serialize_acta_detalle(_get_acta_or_404(acta.id), request.user)})


@require_GET
@api_login_required
def estadistica_actas_view(request):
    if not puede_consultar_estados_actas(request.user):
        return _deny("No tienes permiso para consultar actas operativas.")
    return _actas_list_response(request, _actas_queryset(), request.user)


@require_GET
@api_login_required
def estadistica_acta_detalle_view(request, acta_id):
    try:
        acta = _get_acta_or_404(acta_id)
    except Acta.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Acta no encontrada."}, status=404)
    if not puede_consultar_acta(request.user, acta) or not (usuario_es_estadistica(request.user) or usuario_es_admin_soporte(request.user)):
        return _deny("No tienes permiso para consultar esta acta.")
    detalle = _serialize_acta_detalle(acta, request.user)
    detalle["acciones"] = {**detalle["acciones"], "puede_validar_carrera": False, "puede_formalizar": False}
    return JsonResponse(detalle)
