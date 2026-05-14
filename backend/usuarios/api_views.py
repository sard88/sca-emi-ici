import json

from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from auditoria.eventos import MODULO_AUTENTICACION, SEVERIDAD_ADVERTENCIA, SEVERIDAD_INFO
from auditoria.services import registrar_evento_exitoso, registrar_evento_fallido

from .models import AsignacionCargo, Usuario


PERFIL_PRIORIDAD = (
    "ADMIN",
    "ADMIN_SISTEMA",
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "DOCENTE",
    "DISCENTE",
)


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _cargos_vigentes(user):
    hoy = timezone.localdate()
    return (
        AsignacionCargo.objects.filter(
            Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
            Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
            usuario=user,
            activo=True,
        )
        .select_related("carrera", "unidad_organizacional", "unidad_organizacional__carrera")
        .distinct()
    )


def _serializar_cargo(cargo):
    unidad = cargo.unidad_organizacional
    carrera = cargo.carrera or (unidad.carrera if unidad and unidad.carrera_id else None)
    return {
        "cargo_codigo": cargo.cargo_codigo,
        "cargo": cargo.get_cargo_codigo_display(),
        "tipo_designacion": cargo.tipo_designacion,
        "vigente_desde": cargo.vigente_desde.isoformat() if cargo.vigente_desde else None,
        "vigente_hasta": cargo.vigente_hasta.isoformat() if cargo.vigente_hasta else None,
        "unidad_organizacional": {
            "clave": unidad.clave,
            "nombre": unidad.nombre,
        }
        if unidad
        else None,
        "carrera": {
            "clave": carrera.clave,
            "nombre": carrera.nombre,
        }
        if carrera
        else None,
    }


def _carreras_usuario(user, cargos):
    carreras = {}
    for cargo in cargos:
        carrera = cargo.carrera
        if not carrera and cargo.unidad_organizacional_id:
            carrera = cargo.unidad_organizacional.carrera
        if carrera:
            carreras[carrera.clave] = {"clave": carrera.clave, "nombre": carrera.nombre}

    try:
        perfiles_discente = user.perfiles_discente.select_related("plan_estudios__carrera").all()
        for discente in perfiles_discente:
            carrera = discente.plan_estudios.carrera
            carreras[carrera.clave] = {"clave": carrera.clave, "nombre": carrera.nombre}
    except Exception:
        pass

    return list(carreras.values())


def _perfil_principal(user, roles, cargos):
    if user.is_superuser:
        return "ADMIN"

    codigos = {cargo.cargo_codigo for cargo in cargos}
    disponibles = set(roles) | codigos
    for perfil in PERFIL_PRIORIDAD:
        if perfil in disponibles:
            return perfil
    return roles[0] if roles else None


def _enlaces_frontend(perfil, roles):
    enlaces = []

    if perfil in {"ADMIN", "ADMIN_SISTEMA"} or "ADMIN" in roles or "ADMIN_SISTEMA" in roles:
        enlaces.append({"label": "Django Admin", "href": "/admin/", "backend": True, "perfil": "ADMIN"})

    if perfil in {"DOCENTE"} or "DOCENTE" in roles:
        enlaces.extend(
            [
                {"label": "Mis asignaciones", "href": "/validacion/docente/asignaciones/", "backend": True},
                {"label": "Actas docente", "href": "/evaluacion/actas/docente/", "backend": True},
            ]
        )
    if perfil in {"DISCENTE"} or "DISCENTE" in roles:
        enlaces.extend(
            [
                {"label": "Mi carga académica", "href": "/validacion/discente/carga/", "backend": True},
                {"label": "Mis actas publicadas", "href": "/evaluacion/actas/discente/", "backend": True},
                {"label": "Mi historial académico", "href": "/trayectoria/mi-historial/", "backend": True},
            ]
        )
    if perfil in {"JEFE_CARRERA", "JEFATURA_CARRERA", "JEFE_SUB_EJEC_CTR"}:
        enlaces.extend(
            [
                {"label": "Asignaciones docentes", "href": "/validacion/jefatura/asignaciones-docentes/", "backend": True},
                {"label": "Actas pendientes", "href": "/evaluacion/actas/jefatura-carrera/pendientes/", "backend": True},
                {"label": "Pendientes de asignación docente", "href": "/actas/pendientes-asignacion-docente/", "backend": True},
            ]
        )
    if perfil in {"JEFE_ACADEMICO", "JEFATURA_ACADEMICA"}:
        enlaces.append(
            {"label": "Actas por formalizar", "href": "/evaluacion/actas/jefatura-academica/pendientes/", "backend": True}
        )
    if perfil in {"JEFE_PEDAGOGICA", "JEFE_SUB_PLAN_EVAL"}:
        enlaces.append(
            {"label": "Consulta de actas", "href": "/evaluacion/actas/planeacion-evaluacion/consulta/", "backend": True}
        )
    if perfil in {"ENCARGADO_ESTADISTICA", "ESTADISTICA", "ADMIN", "ADMIN_SISTEMA"}:
        enlaces.extend(
            [
                {"label": "Carga académica", "href": "/validacion/estadistica/carga/", "backend": True},
                {"label": "Cierre y apertura de periodo", "href": "/actas/periodos/", "backend": True},
                {"label": "Kárdex institucional", "href": "/trayectoria/kardex/", "backend": True},
            ]
        )

    return enlaces


def serializar_usuario(user):
    roles = list(user.groups.order_by("name").values_list("name", flat=True))
    cargos = list(_cargos_vigentes(user))
    perfil = _perfil_principal(user, roles, cargos)
    grado = user.grado_empleo

    return {
        "authenticated": True,
        "id": user.id,
        "username": user.username,
        "nombre_completo": user.nombre_completo,
        "nombre_visible": user.nombre_visible,
        "nombre_institucional": user.nombre_institucional,
        "email": user.email,
        "correo": user.correo,
        "grado_empleo": {
            "clave": grado.clave,
            "abreviatura": grado.abreviatura,
            "nombre": grado.nombre,
            "tipo": grado.tipo,
        }
        if grado
        else None,
        "roles": roles,
        "cargos_vigentes": [_serializar_cargo(cargo) for cargo in cargos],
        "perfil_principal": perfil,
        "carreras": _carreras_usuario(user, cargos),
        "enlaces": _enlaces_frontend(perfil, roles),
    }


@require_GET
@ensure_csrf_cookie
def csrf_view(request):
    return JsonResponse({"csrfToken": get_token(request)})


@require_POST
@csrf_protect
def login_view(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Solicitud inválida."}, status=400)

    username = data.get("username", "")
    password = data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if not user or not user.is_active or user.estado_cuenta != Usuario.ESTADO_ACTIVO:
        registrar_evento_fallido(
            request=request,
            usuario=None,
            modulo=MODULO_AUTENTICACION,
            evento_codigo="LOGIN_FALLIDO",
            severidad=SEVERIDAD_ADVERTENCIA,
            resumen="Intento de login fallido.",
            metadatos={"username_intentado": str(username)[:150]},
        )
        return JsonResponse({"ok": False, "error": "Usuario o contraseña incorrectos."}, status=400)

    login(request, user)
    registrar_evento_exitoso(
        request=request,
        usuario=user,
        modulo=MODULO_AUTENTICACION,
        evento_codigo="LOGIN_EXITOSO",
        severidad=SEVERIDAD_INFO,
        resumen="Login exitoso.",
    )
    return JsonResponse({"ok": True, "csrfToken": get_token(request), "user": serializar_usuario(user)})


@require_POST
@csrf_protect
def logout_view(request):
    usuario = request.user if request.user.is_authenticated else None
    logout(request)
    registrar_evento_exitoso(
        request=request,
        usuario=usuario,
        modulo=MODULO_AUTENTICACION,
        evento_codigo="LOGOUT",
        severidad=SEVERIDAD_INFO,
        resumen="Logout exitoso.",
    )
    return JsonResponse({"ok": True})


@require_GET
def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False})
    return JsonResponse(serializar_usuario(request.user))
