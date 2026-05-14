import json

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from core.portal_services import portal_context
from evaluacion.models import Acta, ComponenteEvaluacion
from relaciones.models import Discente

from .actas_services import ServicioExportacionActa
from .kardex_services import ServicioExportacionKardex
from .models import RegistroExportacion
from .reportes_operativos import ServicioReportesOperativos
from .services import CatalogoExportaciones, ServicioExportacion, ServicioPermisosExportacion
from trayectoria.permisos import filtrar_discentes_por_ambito, puede_consultar_kardex

Usuario = get_user_model()


def api_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "error": "Autenticación requerida."}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _error_response(exc, status=400):
    if isinstance(exc, PermissionDenied):
        return JsonResponse({"ok": False, "error": str(exc) or "Permiso denegado."}, status=403)
    if isinstance(exc, ValidationError):
        return JsonResponse({"ok": False, "error": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=status)
    return JsonResponse({"ok": False, "error": str(exc)}, status=status)


def _archivo_response(resultado):
    response = HttpResponse(resultado.contenido, content_type=resultado.content_type)
    response["Content-Disposition"] = f'attachment; filename="{resultado.nombre_archivo}"'
    response["X-Registro-Exportacion-Id"] = str(resultado.registro.id)
    return response


@require_GET
@api_login_required
def catalogo_reportes_view(request):
    return JsonResponse({"items": CatalogoExportaciones.filtrado_para_usuario(request.user)})


@require_GET
@api_login_required
def exportaciones_usuario_view(request):
    permisos = ServicioPermisosExportacion(request.user)
    qs = RegistroExportacion.objects.select_related("usuario")
    if not (permisos.is_admin or permisos.is_estadistica):
        qs = qs.filter(usuario=request.user)
    qs = aplicar_filtros_exportaciones(qs, request.GET)
    limit = normalizar_limit(request.GET.get("limit"), default=30, maximum=100)
    return JsonResponse({"items": [serializar_registro_exportacion(item) for item in qs[:limit]]})


@require_GET
@api_login_required
def actas_disponibles_view(request):
    ctx = portal_context(request.user)
    qs = actas_exportables_queryset(ctx)
    limit = normalizar_limit(request.GET.get("limit"), default=100, maximum=300)
    return JsonResponse({"items": [serializar_acta_exportable(acta) for acta in qs[:limit]]})


@require_GET
@api_login_required
def kardex_disponibles_view(request):
    if not puede_consultar_kardex(request.user):
        return JsonResponse({"items": []})

    qs = kardex_exportables_queryset(request.user, request.GET)
    limit = normalizar_limit(request.GET.get("page_size") or request.GET.get("limit"), default=40, maximum=100)
    return JsonResponse({"items": [serializar_kardex_exportable(discente) for discente in qs[:limit]]})


@require_GET
@api_login_required
def auditoria_exportaciones_view(request):
    permisos = ServicioPermisosExportacion(request.user)
    if not permisos.puede_auditar_exportaciones:
        return JsonResponse({"ok": False, "error": "No autorizado para consultar auditoría de exportaciones."}, status=403)
    qs = aplicar_filtros_exportaciones(RegistroExportacion.objects.select_related("usuario"), request.GET)
    limit = normalizar_limit(request.GET.get("limit"), default=50, maximum=200)
    return JsonResponse({"items": [serializar_registro_exportacion(item) for item in qs[:limit]]})


@require_POST
@csrf_protect
@api_login_required
def registrar_evento_prueba_view(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Solicitud inválida."}, status=400)
    try:
        resultado = ServicioExportacion(request.user, request=request).registrar_evento_prueba(
            formato=(data.get("formato") or RegistroExportacion.FORMATO_PDF).upper(),
            filtros=data.get("filtros") or {},
            parametros=data.get("parametros") or {},
        )
    except (PermissionDenied, ValidationError) as exc:
        return _error_response(exc)
    return JsonResponse({"ok": True, "item": serializar_registro_exportacion(resultado.registro)}, status=201)


@require_GET
@api_login_required
def exportar_acta_pdf_view(request, acta_id):
    return _exportar_acta_corte(request, acta_id, RegistroExportacion.FORMATO_PDF)


@require_GET
@api_login_required
def exportar_acta_xlsx_view(request, acta_id):
    return _exportar_acta_corte(request, acta_id, RegistroExportacion.FORMATO_XLSX)


@require_GET
@api_login_required
def exportar_calificacion_final_pdf_view(request, asignacion_docente_id):
    return _exportar_calificacion_final(request, asignacion_docente_id, RegistroExportacion.FORMATO_PDF)


@require_GET
@api_login_required
def exportar_calificacion_final_xlsx_view(request, asignacion_docente_id):
    return _exportar_calificacion_final(request, asignacion_docente_id, RegistroExportacion.FORMATO_XLSX)


@require_GET
@api_login_required
def exportar_kardex_pdf_view(request, discente_id):
    try:
        resultado = ServicioExportacionKardex(request.user, request=request).exportar_kardex_pdf(discente_id)
    except Http404:
        raise
    except (PermissionDenied, ValidationError) as exc:
        return _error_response(exc)
    except Exception:
        return JsonResponse({"ok": False, "error": "No fue posible generar el archivo de kárdex."}, status=500)
    return _archivo_response(resultado)


@require_GET
@api_login_required
def reporte_actas_estado_view(request):
    return _reporte_operativo_json(request, "actas-estado")


@require_GET
@api_login_required
def reporte_actas_pendientes_view(request):
    return _reporte_operativo_json(request, "actas-pendientes")


@require_GET
@api_login_required
def reporte_inconformidades_view(request):
    return _reporte_operativo_json(request, "inconformidades")


@require_GET
@api_login_required
def reporte_sin_conformidad_view(request):
    return _reporte_operativo_json(request, "sin-conformidad")


@require_GET
@api_login_required
def reporte_actas_formalizadas_view(request):
    return _reporte_operativo_json(request, "actas-formalizadas")


@require_GET
@api_login_required
def reporte_validaciones_acta_view(request):
    return _reporte_operativo_json(request, "validaciones-acta")


@require_GET
@api_login_required
def reporte_exportaciones_realizadas_view(request):
    return _reporte_operativo_json(request, "exportaciones-realizadas")


@require_GET
@api_login_required
def exportar_reporte_actas_estado_xlsx_view(request):
    return _exportar_reporte_operativo_xlsx(request, "actas-estado")


@require_GET
@api_login_required
def exportar_reporte_actas_pendientes_xlsx_view(request):
    return _exportar_reporte_operativo_xlsx(request, "actas-pendientes")


@require_GET
@api_login_required
def exportar_reporte_inconformidades_xlsx_view(request):
    return _exportar_reporte_operativo_xlsx(request, "inconformidades")


@require_GET
@api_login_required
def exportar_reporte_sin_conformidad_xlsx_view(request):
    return _exportar_reporte_operativo_xlsx(request, "sin-conformidad")


@require_GET
@api_login_required
def exportar_reporte_actas_formalizadas_xlsx_view(request):
    return _exportar_reporte_operativo_xlsx(request, "actas-formalizadas")


@require_GET
@api_login_required
def exportar_reporte_validaciones_acta_xlsx_view(request):
    return _exportar_reporte_operativo_xlsx(request, "validaciones-acta")


@require_GET
@api_login_required
def exportar_reporte_exportaciones_realizadas_xlsx_view(request):
    return _exportar_reporte_operativo_xlsx(request, "exportaciones-realizadas")


def _reporte_operativo_json(request, slug):
    try:
        data = ServicioReportesOperativos(request.user, request=request).vista_previa(slug, request.GET)
    except (PermissionDenied, ValidationError) as exc:
        return _error_response(exc)
    except Exception:
        return JsonResponse({"ok": False, "error": "No fue posible consultar el reporte operativo."}, status=500)

    limit = normalizar_limit(request.GET.get("limit"), default=100, maximum=500)
    return JsonResponse(
        {
            "ok": True,
            "slug": data.slug,
            "nombre": data.nombre,
            "total": len(data.filas),
            "filtros": data.filtros,
            "columnas": data.columnas,
            "items": data.filas[:limit],
            "sheets": [
                {
                    "titulo": sheet.titulo,
                    "total": len(sheet.filas),
                    "columnas": sheet.columnas,
                }
                for sheet in data.sheets
            ],
        }
    )


def _exportar_reporte_operativo_xlsx(request, slug):
    try:
        resultado = ServicioReportesOperativos(request.user, request=request).exportar_xlsx(slug, request.GET)
    except (PermissionDenied, ValidationError) as exc:
        return _error_response(exc)
    except Exception:
        return JsonResponse({"ok": False, "error": "No fue posible generar el reporte operativo."}, status=500)
    return _archivo_response(resultado)


def _exportar_acta_corte(request, acta_id, formato):
    try:
        resultado = ServicioExportacionActa(request.user, request=request).exportar_acta_corte(acta_id, formato)
    except Http404:
        raise
    except (PermissionDenied, ValidationError) as exc:
        return _error_response(exc)
    except Exception:
        return JsonResponse({"ok": False, "error": "No fue posible generar el archivo de acta."}, status=500)
    return _archivo_response(resultado)


def _exportar_calificacion_final(request, asignacion_docente_id, formato):
    try:
        resultado = ServicioExportacionActa(request.user, request=request).exportar_calificacion_final(
            asignacion_docente_id,
            formato,
        )
    except Http404:
        raise
    except (PermissionDenied, ValidationError) as exc:
        return _error_response(exc)
    except Exception:
        return JsonResponse({"ok": False, "error": "No fue posible generar el archivo de calificación final."}, status=500)
    return _archivo_response(resultado)


def aplicar_filtros_exportaciones(qs, params):
    fecha_desde = parse_date(params.get("fecha_desde") or "")
    fecha_hasta = parse_date(params.get("fecha_hasta") or "")
    if fecha_desde:
        qs = qs.filter(creado_en__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(creado_en__date__lte=fecha_hasta)

    usuario = (params.get("usuario") or "").strip()
    if usuario:
        if usuario.isdigit():
            qs = qs.filter(Q(usuario_id=int(usuario)) | Q(usuario__username__icontains=usuario))
        else:
            qs = qs.filter(Q(usuario__username__icontains=usuario) | Q(usuario__nombre_completo__icontains=usuario))

    tipo_documento = (params.get("tipo_documento") or "").strip().upper()
    if tipo_documento:
        qs = qs.filter(tipo_documento=tipo_documento)

    formato = (params.get("formato") or "").strip().upper()
    if formato:
        qs = qs.filter(formato=formato)

    estado = (params.get("estado") or "").strip().upper()
    if estado:
        qs = qs.filter(estado=estado)

    return qs.order_by("-creado_en")


def actas_exportables_queryset(ctx):
    qs = (
        Acta.objects.select_related(
            "asignacion_docente__usuario_docente",
            "asignacion_docente__grupo_academico__periodo",
            "asignacion_docente__programa_asignatura__materia",
            "asignacion_docente__programa_asignatura__plan_estudios__carrera",
        )
        .exclude(estado_acta=Acta.ESTADO_ARCHIVADO)
        .order_by(
            "asignacion_docente__grupo_academico__clave_grupo",
            "asignacion_docente__programa_asignatura__materia__nombre",
            "corte_codigo",
        )
    )

    if ctx.is_discente and not ctx.is_admin:
        return qs.none()
    if ctx.has_consulta_amplia:
        return qs
    if ctx.is_docente:
        return qs.filter(asignacion_docente__usuario_docente=ctx.user)
    if ctx.is_jefatura_carrera:
        if ctx.carrera_ids:
            return qs.filter(asignacion_docente__programa_asignatura__plan_estudios__carrera_id__in=ctx.carrera_ids)
        return qs
    return qs.none()


def kardex_exportables_queryset(user, params):
    qs = Discente.objects.filter(activo=True).select_related(
        "usuario",
        "usuario__grado_empleo",
        "plan_estudios",
        "plan_estudios__carrera",
        "antiguedad",
    )
    qs = filtrar_discentes_por_ambito(user, qs)

    query = (params.get("q") or "").strip()
    if query:
        filters = (
            Q(usuario__nombre_completo__icontains=query)
            | Q(usuario__first_name__icontains=query)
            | Q(usuario__last_name__icontains=query)
            | Q(usuario__grado_empleo__nombre__icontains=query)
            | Q(usuario__grado_empleo__abreviatura__icontains=query)
            | Q(plan_estudios__carrera__clave__icontains=query)
            | Q(plan_estudios__carrera__nombre__icontains=query)
            | Q(plan_estudios__nombre__icontains=query)
            | Q(antiguedad__nombre__icontains=query)
            | Q(adscripciones_grupo__grupo_academico__clave_grupo__icontains=query)
        )
        if query.isdigit():
            filters |= Q(pk=int(query))
        qs = qs.filter(filters)

    carrera = (params.get("carrera") or "").strip()
    if carrera:
        carrera_filter = Q(plan_estudios__carrera__clave__iexact=carrera)
        if carrera.isdigit():
            carrera_filter |= Q(plan_estudios__carrera_id=int(carrera))
        qs = qs.filter(carrera_filter)

    situacion = (params.get("situacion") or "").strip()
    if situacion:
        qs = qs.filter(situacion_actual=situacion)

    return qs.distinct().order_by("usuario__nombre_completo", "id")


def normalizar_limit(value, *, default, maximum):
    try:
        limit = int(value or default)
    except (TypeError, ValueError):
        limit = default
    return max(1, min(limit, maximum))


def serializar_registro_exportacion(registro: RegistroExportacion):
    return {
        "id": registro.id,
        "usuario": {
            "id": registro.usuario_id,
            "username": registro.usuario.username,
            "nombre": registro.usuario.nombre_visible,
        },
        "tipo_documento": registro.tipo_documento,
        "tipo_documento_label": registro.get_tipo_documento_display(),
        "formato": registro.formato,
        "nombre_documento": registro.nombre_documento,
        "nombre_archivo": registro.nombre_archivo,
        "objeto_tipo": registro.objeto_tipo,
        "objeto_id": registro.objeto_id,
        "objeto_repr": registro.objeto_repr,
        "rol_contexto": registro.rol_contexto,
        "cargo_contexto": registro.cargo_contexto,
        "ip_origen": registro.ip_origen,
        "estado": registro.estado,
        "estado_label": registro.get_estado_display(),
        "mensaje_error": registro.mensaje_error,
        "tamano_bytes": registro.tamano_bytes,
        "hash_archivo": registro.hash_archivo,
        "creado_en": registro.creado_en.isoformat() if registro.creado_en else None,
        "finalizado_en": registro.finalizado_en.isoformat() if registro.finalizado_en else None,
    }


def serializar_acta_exportable(acta: Acta):
    asignacion = acta.asignacion_docente
    programa = asignacion.programa_asignatura
    materia = programa.materia
    carrera = programa.plan_estudios.carrera
    grupo = asignacion.grupo_academico
    periodo = grupo.periodo
    es_oficial = acta.estado_acta == Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA
    tipo_acta = (
        RegistroExportacion.TIPO_ACTA_EVALUACION_FINAL
        if acta.corte_codigo == ComponenteEvaluacion.CORTE_FINAL
        else RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL
    )

    return {
        "acta_id": acta.id,
        "asignacion_docente_id": asignacion.id,
        "tipo_acta": tipo_acta,
        "corte_codigo": acta.corte_codigo,
        "corte_nombre": acta.get_corte_codigo_display(),
        "estado_acta": acta.estado_acta,
        "estado_acta_label": acta.get_estado_acta_display(),
        "estado_documental": "Documento oficial" if es_oficial else "Documento no oficial",
        "periodo": periodo.clave,
        "carrera": carrera.nombre,
        "carrera_clave": carrera.clave,
        "grupo": grupo.clave_grupo,
        "programa_asignatura": materia.nombre,
        "docente": asignacion.usuario_docente.nombre_visible,
        "fecha_publicacion": acta.publicada_en.isoformat() if acta.publicada_en else None,
        "fecha_remision": acta.remitida_en.isoformat() if acta.remitida_en else None,
        "fecha_formalizacion": acta.formalizada_en.isoformat() if acta.formalizada_en else None,
        "puede_exportar_pdf": True,
        "puede_exportar_xlsx": True,
        "url_pdf": f"/api/exportaciones/actas/{acta.id}/pdf/",
        "url_xlsx": f"/api/exportaciones/actas/{acta.id}/xlsx/",
        "es_documento_oficial": es_oficial,
        "motivo_no_disponible": "",
        "calificacion_final_disponible": True,
        "url_calificacion_final_pdf": f"/api/exportaciones/asignaciones/{asignacion.id}/calificacion-final/pdf/",
        "url_calificacion_final_xlsx": f"/api/exportaciones/asignaciones/{asignacion.id}/calificacion-final/xlsx/",
    }


def serializar_kardex_exportable(discente: Discente):
    carrera = discente.plan_estudios.carrera
    adscripcion = (
        discente.adscripciones_grupo.filter(activo=True)
        .select_related("grupo_academico", "grupo_academico__periodo")
        .order_by("-vigente_desde", "-id")
        .first()
    )
    grupo = adscripcion.grupo_academico if adscripcion else None
    grado = discente.usuario.grado_empleo
    return {
        "discente_id": discente.id,
        "nombre_completo": discente.usuario.nombre_visible,
        "grado_empleo": grado.abreviatura if grado else "",
        "carrera": {"clave": carrera.clave, "nombre": carrera.nombre},
        "plan_estudios": discente.plan_estudios.nombre,
        "antiguedad": discente.antiguedad.nombre,
        "grupo_actual": grupo.clave_grupo if grupo else "",
        "periodo_actual": grupo.periodo.clave if grupo and grupo.periodo_id else "",
        "situacion_actual": discente.get_situacion_actual_display(),
        "puede_exportar_pdf": True,
        "url_kardex_pdf": f"/api/exportaciones/kardex/{discente.id}/pdf/",
        "motivo_no_disponible": "",
    }
