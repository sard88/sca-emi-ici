from io import BytesIO

from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET
from openpyxl import Workbook

from core.api_views import api_login_required
from core.portal_services import portal_context
from reportes.models import RegistroExportacion
from reportes.services import ServicioExportacion

from .eventos import MODULO_REPORTES, SEVERIDAD_INFO
from .models import BitacoraEventoCritico
from .services import limpiar_payload_auditoria, registrar_evento_exitoso


MAX_PAGE_SIZE = 100


def _puede_consultar(user):
    if not user.is_authenticated:
        return False
    ctx = portal_context(user)
    return ctx.is_admin or ctx.is_estadistica or ctx.is_jefatura_academica or ctx.is_jefatura_pedagogica


def _deny():
    return JsonResponse({"ok": False, "error": "No autorizado para consultar bitacora de eventos criticos."}, status=403)


def _page_params(request):
    try:
        page = max(1, int(request.GET.get("page") or 1))
    except ValueError:
        page = 1
    try:
        page_size = max(1, min(int(request.GET.get("page_size") or request.GET.get("limit") or 25), MAX_PAGE_SIZE))
    except ValueError:
        page_size = 25
    start = (page - 1) * page_size
    end = start + page_size
    return page, page_size, start, end


def aplicar_filtros_eventos(qs, params):
    fecha_desde = parse_date(params.get("fecha_desde") or "")
    fecha_hasta = parse_date(params.get("fecha_hasta") or "")
    if fecha_desde:
        qs = qs.filter(creado_en__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(creado_en__date__lte=fecha_hasta)
    filtros_exactos = (
        "modulo",
        "evento_codigo",
        "severidad",
        "resultado",
        "objeto_tipo",
        "objeto_id",
        "ip_origen",
        "request_id",
        "correlacion_id",
    )
    for field in filtros_exactos:
        value = (params.get(field) or "").strip()
        if value:
            qs = qs.filter(**{field: value})
    usuario = (params.get("usuario") or "").strip()
    if usuario:
        if usuario.isdigit():
            qs = qs.filter(Q(usuario_id=int(usuario)) | Q(username_snapshot__icontains=usuario))
        else:
            qs = qs.filter(Q(username_snapshot__icontains=usuario) | Q(nombre_usuario_snapshot__icontains=usuario))
    return qs.order_by("-creado_en", "-id")


def serializar_evento(evento, detalle=False):
    item = {
        "id": evento.id,
        "creado_en": evento.creado_en.isoformat() if evento.creado_en else None,
        "usuario": {
            "id": evento.usuario_id,
            "username": evento.username_snapshot,
            "nombre": evento.nombre_usuario_snapshot,
        },
        "rol_contexto": evento.rol_contexto,
        "cargo_contexto": evento.cargo_contexto,
        "modulo": evento.modulo,
        "modulo_label": evento.get_modulo_display(),
        "evento_codigo": evento.evento_codigo,
        "evento_nombre": evento.evento_nombre,
        "severidad": evento.severidad,
        "severidad_label": evento.get_severidad_display(),
        "resultado": evento.resultado,
        "resultado_label": evento.get_resultado_display(),
        "objeto_tipo": evento.objeto_tipo,
        "objeto_id": evento.objeto_id,
        "objeto_repr": evento.objeto_repr,
        "estado_anterior": evento.estado_anterior,
        "estado_nuevo": evento.estado_nuevo,
        "resumen": evento.resumen,
        "ip_origen": evento.ip_origen,
        "ruta": evento.ruta,
        "metodo_http": evento.metodo_http,
        "request_id": evento.request_id,
        "correlacion_id": evento.correlacion_id,
    }
    if detalle:
        item["cambios_json"] = limpiar_payload_auditoria(evento.cambios_json)
        item["metadatos_json"] = limpiar_payload_auditoria(evento.metadatos_json)
        item["user_agent"] = evento.user_agent
    return item


@require_GET
@api_login_required
def eventos_list_view(request):
    if not _puede_consultar(request.user):
        return _deny()
    qs = aplicar_filtros_eventos(BitacoraEventoCritico.objects.select_related("usuario"), request.GET)
    page, page_size, start, end = _page_params(request)
    total = qs.count()
    return JsonResponse(
        {
            "ok": True,
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [serializar_evento(item) for item in qs[start:end]],
        }
    )


@require_GET
@api_login_required
def eventos_detail_view(request, pk):
    if not _puede_consultar(request.user):
        return _deny()
    evento = BitacoraEventoCritico.objects.select_related("usuario").filter(pk=pk).first()
    if not evento:
        return JsonResponse({"ok": False, "error": "Evento no encontrado."}, status=404)
    return JsonResponse({"ok": True, "item": serializar_evento(evento, detalle=True)})


@require_GET
@api_login_required
def eventos_resumen_view(request):
    if not _puede_consultar(request.user):
        return _deny()
    qs = aplicar_filtros_eventos(BitacoraEventoCritico.objects.all(), request.GET)
    return JsonResponse(
        {
            "ok": True,
            "resumen": {
                "por_modulo": list(qs.values("modulo").annotate(total=Count("id")).order_by("modulo")),
                "por_evento": list(qs.values("evento_codigo", "evento_nombre").annotate(total=Count("id")).order_by("evento_codigo")),
                "por_resultado": list(qs.values("resultado").annotate(total=Count("id")).order_by("resultado")),
                "por_severidad": list(qs.values("severidad").annotate(total=Count("id")).order_by("severidad")),
            },
        }
    )


def _crear_xlsx_eventos(qs):
    wb = Workbook()
    ws = wb.active
    ws.title = "Eventos criticos"
    headers = [
        "ID evento",
        "Fecha/hora",
        "Usuario",
        "Rol contexto",
        "Cargo contexto",
        "Modulo",
        "Evento",
        "Severidad",
        "Resultado",
        "Objeto tipo",
        "Objeto ID",
        "Objeto representacion",
        "Estado anterior",
        "Estado nuevo",
        "Resumen",
        "IP",
        "Ruta",
        "Metodo",
        "Request ID",
        "Correlacion ID",
    ]
    ws.append(headers)
    for evento in qs[:5000]:
        ws.append(
            [
                evento.id,
                evento.creado_en.isoformat() if evento.creado_en else "",
                evento.username_snapshot,
                evento.rol_contexto,
                evento.cargo_contexto,
                evento.modulo,
                evento.evento_codigo,
                evento.severidad,
                evento.resultado,
                evento.objeto_tipo,
                evento.objeto_id,
                evento.objeto_repr,
                evento.estado_anterior,
                evento.estado_nuevo,
                evento.resumen,
                evento.ip_origen or "",
                evento.ruta,
                evento.metodo_http,
                evento.request_id,
                evento.correlacion_id,
            ]
        )
    for column_cells in ws.columns:
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(len(str(cell.value or "")) for cell in column_cells) + 2, 45)
    output = BytesIO()
    wb.save(output)
    return output.getvalue()


@require_GET
@api_login_required
def exportar_eventos_xlsx_view(request):
    if not _puede_consultar(request.user):
        return _deny()
    servicio = ServicioExportacion(request.user, request=request)
    qs = aplicar_filtros_eventos(BitacoraEventoCritico.objects.select_related("usuario"), request.GET)
    registro = servicio.registrar_solicitud(
        tipo_documento=RegistroExportacion.TIPO_AUDITORIA_EVENTOS,
        formato=RegistroExportacion.FORMATO_XLSX,
        nombre_documento="Auditoria de eventos criticos",
        objeto_tipo="auditoria.BitacoraEventoCritico",
        objeto_repr="Bitacora transversal filtrada",
        filtros=dict(request.GET.items()),
        validar_disponible=False,
    )
    try:
        contenido = _crear_xlsx_eventos(qs)
        servicio.marcar_generada(registro, tamano_bytes=len(contenido))
    except Exception as exc:
        servicio.marcar_fallida(registro, str(exc))
        raise
    registrar_evento_exitoso(
        request=request,
        modulo=MODULO_REPORTES,
        evento_codigo="AUDITORIA_EVENTOS_EXPORTADA",
        severidad=SEVERIDAD_INFO,
        objeto=registro,
        resumen="Exportacion XLSX de bitacora de eventos criticos.",
        metadatos={
            "registro_exportacion_id": registro.id,
            "tipo_documento": registro.tipo_documento,
            "formato": registro.formato,
            "nombre_archivo": registro.nombre_archivo,
            "estado": registro.estado,
            "tamano_bytes": registro.tamano_bytes,
        },
    )
    response = HttpResponse(contenido, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{registro.nombre_archivo}"'
    response["X-Registro-Exportacion-Id"] = str(registro.id)
    return response
