import json
from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from usuarios.api_views import serializar_usuario

from .models import AccesoRapidoUsuario, NotificacionUsuario
from .portal_services import (
    accesos_rapidos,
    actividad_reciente,
    busqueda,
    dashboard_resumen,
    eventos_mes,
    eventos_proximos,
    serialize_acceso_rapido,
    serialize_notificacion,
)


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


@require_GET
@api_login_required
def dashboard_resumen_view(request):
    return JsonResponse(dashboard_resumen(request.user))


@require_GET
@api_login_required
def actividad_reciente_view(request):
    return JsonResponse({"items": actividad_reciente(request.user)})


@require_GET
@api_login_required
def notificaciones_view(request):
    qs = NotificacionUsuario.objects.filter(usuario=request.user).order_by("-creada_en")
    limit = int(request.GET.get("limit") or 8)
    limit = max(1, min(limit, 30))
    return JsonResponse(
        {
            "unread_count": qs.filter(leida=False).count(),
            "items": [serialize_notificacion(item) for item in qs[:limit]],
        }
    )


@require_POST
@csrf_protect
@api_login_required
def notificacion_leer_view(request, pk):
    try:
        notificacion = NotificacionUsuario.objects.get(pk=pk, usuario=request.user)
    except NotificacionUsuario.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Notificación no encontrada."}, status=404)
    notificacion.marcar_leida()
    return JsonResponse({"ok": True, "item": serialize_notificacion(notificacion)})


@require_POST
@csrf_protect
@api_login_required
def notificaciones_leer_todas_view(request):
    ahora = timezone.now()
    NotificacionUsuario.objects.filter(usuario=request.user, leida=False).update(leida=True, leida_en=ahora)
    return JsonResponse({"ok": True, "unread_count": 0})


@require_GET
@api_login_required
def calendario_mes_view(request):
    today = date.today()
    try:
        year = int(request.GET.get("year") or today.year)
        month = int(request.GET.get("month") or today.month)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        return JsonResponse({"ok": False, "error": "Parámetros de calendario inválidos."}, status=400)
    return JsonResponse(eventos_mes(request.user, year, month))


@require_GET
@api_login_required
def calendario_proximos_view(request):
    return JsonResponse({"items": eventos_proximos(request.user)})


@require_GET
@api_login_required
def busqueda_view(request):
    return JsonResponse(busqueda(request.user, request.GET.get("q", "")))


@require_GET
@api_login_required
def perfil_me_view(request):
    data = serializar_usuario(request.user)
    data.update(
        {
            "estado_cuenta": request.user.estado_cuenta,
            "estado_cuenta_label": request.user.get_estado_cuenta_display(),
            "ultimo_acceso": request.user.ultimo_acceso.isoformat() if request.user.ultimo_acceso else None,
            "last_login": request.user.last_login.isoformat() if request.user.last_login else None,
            "date_joined": request.user.date_joined.isoformat() if request.user.date_joined else None,
        }
    )
    return JsonResponse(data)


@require_GET
@api_login_required
def accesos_rapidos_view(request):
    return JsonResponse(accesos_rapidos(request.user))


@require_POST
@csrf_protect
@api_login_required
def acceso_rapido_crear_view(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Solicitud inválida."}, status=400)

    acceso = AccesoRapidoUsuario(
        usuario=request.user,
        etiqueta=(data.get("etiqueta") or data.get("label") or "").strip(),
        url=(data.get("url") or "").strip(),
        icono=(data.get("icono") or "").strip(),
        orden=int(data.get("orden") or 0),
    )
    if not acceso.etiqueta or not acceso.url:
        return JsonResponse({"ok": False, "error": "Etiqueta y URL son obligatorias."}, status=400)

    try:
        acceso.full_clean()
        acceso.save()
    except (ValidationError, IntegrityError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return JsonResponse({"ok": True, "item": serialize_acceso_rapido(acceso)}, status=201)


@require_http_methods(["DELETE"])
@csrf_protect
@api_login_required
def acceso_rapido_eliminar_view(request, pk):
    try:
        acceso = AccesoRapidoUsuario.objects.get(pk=pk, usuario=request.user, activo=True)
    except AccesoRapidoUsuario.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Acceso rápido no encontrado."}, status=404)
    acceso.activo = False
    acceso.save(update_fields=["activo"])
    return JsonResponse({"ok": True})
