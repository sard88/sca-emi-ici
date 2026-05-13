import json

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from .actas_services import ServicioExportacionActa
from .models import RegistroExportacion
from .services import CatalogoExportaciones, ServicioExportacion, ServicioPermisosExportacion

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
