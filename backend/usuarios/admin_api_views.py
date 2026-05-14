import json

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from catalogos.models import Carrera
from core.api_views import api_login_required

from .models import AsignacionCargo, GradoEmpleo, UnidadOrganizacional, Usuario


ADMIN_ROLES = {"ADMIN", "ADMIN_SISTEMA"}
INSTITUTIONAL_ROLES = {
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
}


def _roles(user):
    return set(user.groups.values_list("name", flat=True))


def _is_admin(user):
    return user.is_superuser or user.is_staff or bool(_roles(user) & ADMIN_ROLES)


def _can_read_admin(user):
    return _is_admin(user) or bool(_roles(user) & INSTITUTIONAL_ROLES)


def _can_write_admin(user):
    return _is_admin(user)


def _deny(message="No tienes permiso para realizar esta acción."):
    return JsonResponse({"ok": False, "message": message}, status=403)


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _validation_errors(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"__all__": exc.messages}
    return {"__all__": [str(exc)]}


def _error_response(exc, message="No fue posible guardar el registro."):
    if isinstance(exc, ValidationError):
        return JsonResponse({"ok": False, "message": message, "errors": _validation_errors(exc)}, status=400)
    return JsonResponse({"ok": False, "message": message, "errors": {"__all__": [str(exc)]}}, status=400)


def _pagination(request):
    try:
        page = max(1, int(request.GET.get("page") or 1))
        page_size = max(1, min(int(request.GET.get("page_size") or request.GET.get("limit") or 25), 100))
    except ValueError:
        page, page_size = 1, 25
    return page, page_size


def _paginate(request, qs):
    page, page_size = _pagination(request)
    total = qs.count()
    start = (page - 1) * page_size
    return total, page, page_size, qs[start:start + page_size]


def _choice_label(choices, value):
    return dict(choices).get(value, value)


def _date(value):
    return value.isoformat() if value else None


def _datetime(value):
    return value.isoformat() if value else None


def _grado_label(grado):
    if not grado:
        return ""
    return f"{grado.abreviatura} - {grado.nombre}"


def _carrera_min(carrera):
    if not carrera:
        return None
    return {"id": carrera.id, "clave": carrera.clave, "nombre": carrera.nombre, "label": str(carrera)}


def _unidad_min(unidad):
    if not unidad:
        return None
    return {"id": unidad.id, "clave": unidad.clave, "nombre": unidad.nombre, "label": str(unidad)}


def _usuario_min(user):
    if not user:
        return None
    return {"id": user.id, "username": user.username, "nombre": user.nombre_visible, "label": f"{user.username} - {user.nombre_visible}"}


def _serialize_grado(item):
    return {
        "id": item.id,
        "clave": item.clave,
        "abreviatura": item.abreviatura,
        "nombre": item.nombre,
        "tipo": item.tipo,
        "tipo_label": item.get_tipo_display(),
        "activo": item.activo,
        "label": _grado_label(item),
    }


def _serialize_unidad(item):
    return {
        "id": item.id,
        "clave": item.clave,
        "nombre": item.nombre,
        "tipo_unidad": item.tipo_unidad,
        "tipo_unidad_label": item.get_tipo_unidad_display(),
        "padre": _unidad_min(item.padre),
        "padre_id": item.padre_id,
        "carrera": _carrera_min(item.carrera),
        "carrera_id": item.carrera_id,
        "activo": item.activo,
        "orden": item.orden,
        "label": str(item),
    }


def _serialize_usuario(item):
    roles = list(item.groups.order_by("name").values_list("name", flat=True))
    cargos = [
        {
            "id": cargo.id,
            "cargo_codigo": cargo.cargo_codigo,
            "cargo": cargo.get_cargo_codigo_display(),
            "tipo_designacion": cargo.tipo_designacion,
            "unidad": _unidad_min(cargo.unidad_organizacional),
            "carrera": _carrera_min(cargo.carrera),
            "vigente_desde": _date(cargo.vigente_desde),
            "vigente_hasta": _date(cargo.vigente_hasta),
            "activo": cargo.activo,
        }
        for cargo in item.asignaciones_cargo.select_related("unidad_organizacional", "carrera").order_by("-activo", "-vigente_desde")[:5]
    ]
    return {
        "id": item.id,
        "username": item.username,
        "nombre_completo": item.nombre_completo,
        "nombre_visible": item.nombre_visible,
        "email": item.email,
        "correo": item.correo,
        "telefono": item.telefono,
        "titulo_profesional": item.titulo_profesional,
        "cedula_profesional": item.cedula_profesional,
        "estado_cuenta": item.estado_cuenta,
        "estado_cuenta_label": item.get_estado_cuenta_display(),
        "is_active": item.is_active,
        "grado_empleo": _serialize_grado(item.grado_empleo) if item.grado_empleo else None,
        "grado_empleo_id": item.grado_empleo_id,
        "roles": roles,
        "rol": roles[0] if roles else "",
        "cargos_vigentes": cargos,
        "last_login": _datetime(item.last_login),
        "date_joined": _datetime(item.date_joined),
        "ultimo_acceso": _datetime(item.ultimo_acceso),
        "label": f"{item.username} - {item.nombre_visible}",
    }


def _serialize_cargo(item):
    return {
        "id": item.id,
        "usuario": _usuario_min(item.usuario),
        "usuario_id": item.usuario_id,
        "cargo_codigo": item.cargo_codigo,
        "cargo_label": item.get_cargo_codigo_display(),
        "tipo_designacion": item.tipo_designacion,
        "tipo_designacion_label": item.get_tipo_designacion_display(),
        "unidad_organizacional": _unidad_min(item.unidad_organizacional),
        "unidad_organizacional_id": item.unidad_organizacional_id,
        "carrera": _carrera_min(item.carrera),
        "carrera_id": item.carrera_id,
        "vigente_desde": _date(item.vigente_desde),
        "vigente_hasta": _date(item.vigente_hasta),
        "activo": item.activo,
        "label": str(item),
    }


def _apply_search(qs, request, fields):
    query = (request.GET.get("q") or request.GET.get("search") or "").strip()
    if not query:
        return qs
    condition = Q()
    for field in fields:
        condition |= Q(**{f"{field}__icontains": query})
    return qs.filter(condition)


def _set_fields(instance, data, allowed_fields, fk_fields=None):
    fk_fields = fk_fields or {}
    for field in allowed_fields:
        if field not in data:
            continue
        value = data[field]
        if value == "":
            value = None
        setattr(instance, field, value)
    for input_key, field_name in fk_fields.items():
        if input_key not in data:
            continue
        value = data[input_key]
        setattr(instance, field_name, int(value) if value not in ("", None) else None)


@require_GET
@api_login_required
def roles_view(request):
    if not _can_read_admin(request.user):
        return _deny()
    qs = _apply_search(Group.objects.order_by("name"), request, ["name"])
    total, page, page_size, items = _paginate(request, qs)
    return JsonResponse(
        {
            "ok": True,
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [{"id": item.id, "name": item.name, "label": item.name} for item in items],
        }
    )


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def usuarios_collection_view(request):
    if request.method == "GET":
        if not _can_read_admin(request.user):
            return _deny()
        qs = Usuario.objects.select_related("grado_empleo").prefetch_related("groups", "asignaciones_cargo").order_by("username")
        qs = _apply_search(qs, request, ["username", "nombre_completo", "email", "correo"])
        estado = request.GET.get("estado_cuenta") or request.GET.get("estado")
        if estado:
            qs = qs.filter(estado_cuenta=estado)
        rol = request.GET.get("rol")
        if rol:
            qs = qs.filter(groups__name=rol)
        total, page, page_size, items = _paginate(request, qs.distinct())
        return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [_serialize_usuario(item) for item in items]})

    if not _can_write_admin(request.user):
        return _deny()
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida.", "errors": {"__all__": ["JSON inválido."]}}, status=400)
    user = Usuario(username=(data.get("username") or "").strip())
    return _save_usuario(user, data, created=True)


@require_http_methods(["GET", "PATCH"])
@csrf_protect
@api_login_required
def usuarios_detail_view(request, pk):
    try:
        item = Usuario.objects.select_related("grado_empleo").prefetch_related("groups", "asignaciones_cargo").get(pk=pk)
    except Usuario.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Usuario no encontrado."}, status=404)

    if request.method == "GET":
        if not _can_read_admin(request.user):
            return _deny()
        return JsonResponse({"ok": True, "item": _serialize_usuario(item)})

    if not _can_write_admin(request.user):
        return _deny()
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida.", "errors": {"__all__": ["JSON inválido."]}}, status=400)
    return _save_usuario(item, data, created=False)


def _save_usuario(user, data, created=False):
    _set_fields(
        user,
        data,
        ["username", "nombre_completo", "email", "correo", "telefono", "titulo_profesional", "cedula_profesional", "estado_cuenta", "is_active"],
        {"grado_empleo": "grado_empleo_id", "grado_empleo_id": "grado_empleo_id"},
    )
    password = data.get("password")
    if created and password:
        user.set_password(password)
    elif created:
        user.set_unusable_password()
    try:
        user.full_clean()
        user.save()
        rol = data.get("rol") or data.get("grupo") or data.get("group")
        roles = data.get("roles")
        role_name = rol or (roles[0] if isinstance(roles, list) and roles else None)
        if role_name:
            group = Group.objects.get(name=role_name)
            user.groups.set([group])
        return JsonResponse({"ok": True, "item": _serialize_usuario(user)}, status=201 if created else 200)
    except Group.DoesNotExist:
        return JsonResponse({"ok": False, "message": "No fue posible guardar el registro.", "errors": {"rol": ["Rol no válido."]}}, status=400)
    except (ValidationError, IntegrityError) as exc:
        return _error_response(exc)


@require_POST
@csrf_protect
@api_login_required
def usuario_estado_view(request, pk, activo):
    if not _can_write_admin(request.user):
        return _deny()
    try:
        item = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Usuario no encontrado."}, status=404)
    item.is_active = activo
    item.estado_cuenta = Usuario.ESTADO_ACTIVO if activo else Usuario.ESTADO_INACTIVO
    item.save(update_fields=["is_active", "estado_cuenta"])
    return JsonResponse({"ok": True, "item": _serialize_usuario(item)})


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def grados_collection_view(request):
    return _simple_collection(request, GradoEmpleo.objects.order_by("tipo", "abreviatura"), _serialize_grado, ["clave", "abreviatura", "nombre"], _save_grado)


@require_http_methods(["GET", "PATCH"])
@csrf_protect
@api_login_required
def grados_detail_view(request, pk):
    return _simple_detail(request, GradoEmpleo, pk, _serialize_grado, _save_grado, "Grado/empleo no encontrado.")


def _save_grado(item, data, created=False):
    _set_fields(item, data, ["clave", "abreviatura", "nombre", "tipo", "activo"])
    try:
        item.full_clean()
        item.save()
        return JsonResponse({"ok": True, "item": _serialize_grado(item)}, status=201 if created else 200)
    except (ValidationError, IntegrityError) as exc:
        return _error_response(exc)


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def unidades_collection_view(request):
    qs = UnidadOrganizacional.objects.select_related("padre", "carrera").order_by("orden", "tipo_unidad", "nombre")
    return _simple_collection(request, qs, _serialize_unidad, ["clave", "nombre", "carrera__clave"], _save_unidad)


@require_http_methods(["GET", "PATCH"])
@csrf_protect
@api_login_required
def unidades_detail_view(request, pk):
    return _simple_detail(request, UnidadOrganizacional, pk, _serialize_unidad, _save_unidad, "Unidad organizacional no encontrada.", select_related=("padre", "carrera"))


def _save_unidad(item, data, created=False):
    _set_fields(
        item,
        data,
        ["clave", "nombre", "tipo_unidad", "activo", "orden"],
        {"padre": "padre_id", "padre_id": "padre_id", "carrera": "carrera_id", "carrera_id": "carrera_id"},
    )
    try:
        item.save()
        return JsonResponse({"ok": True, "item": _serialize_unidad(item)}, status=201 if created else 200)
    except (ValidationError, IntegrityError) as exc:
        return _error_response(exc)


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def cargos_collection_view(request):
    qs = AsignacionCargo.objects.select_related("usuario", "unidad_organizacional", "carrera").order_by("-activo", "-vigente_desde")
    return _simple_collection(request, qs, _serialize_cargo, ["usuario__username", "usuario__nombre_completo", "cargo_codigo", "unidad_organizacional__nombre"], _save_cargo)


@require_http_methods(["GET", "PATCH"])
@csrf_protect
@api_login_required
def cargos_detail_view(request, pk):
    return _simple_detail(request, AsignacionCargo, pk, _serialize_cargo, _save_cargo, "Asignación de cargo no encontrada.", select_related=("usuario", "unidad_organizacional", "carrera"))


def _save_cargo(item, data, created=False):
    _set_fields(
        item,
        data,
        ["cargo_codigo", "tipo_designacion", "vigente_desde", "vigente_hasta", "activo"],
        {
            "usuario": "usuario_id",
            "usuario_id": "usuario_id",
            "unidad_organizacional": "unidad_organizacional_id",
            "unidad_organizacional_id": "unidad_organizacional_id",
            "carrera": "carrera_id",
            "carrera_id": "carrera_id",
        },
    )
    try:
        item.save()
        return JsonResponse({"ok": True, "item": _serialize_cargo(item)}, status=201 if created else 200)
    except (ValidationError, IntegrityError) as exc:
        return _error_response(exc)


@require_POST
@csrf_protect
@api_login_required
def cargo_cerrar_view(request, pk):
    if not _can_write_admin(request.user):
        return _deny()
    try:
        item = AsignacionCargo.objects.get(pk=pk)
    except AsignacionCargo.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Asignación de cargo no encontrada."}, status=404)
    data = _json_body(request) or {}
    item.vigente_hasta = data.get("vigente_hasta") or item.vigente_hasta
    item.activo = False
    try:
        item.save()
        return JsonResponse({"ok": True, "item": _serialize_cargo(item)})
    except ValidationError as exc:
        return _error_response(exc)


@require_POST
@csrf_protect
@api_login_required
def simple_estado_view(request, resource, pk, activo):
    mapping = {
        "grados-empleos": (GradoEmpleo, _serialize_grado, "activo"),
        "unidades-organizacionales": (UnidadOrganizacional, _serialize_unidad, "activo"),
        "asignaciones-cargo": (AsignacionCargo, _serialize_cargo, "activo"),
    }
    if resource not in mapping:
        return JsonResponse({"ok": False, "message": "Recurso no encontrado."}, status=404)
    if not _can_write_admin(request.user):
        return _deny()
    model, serializer, field = mapping[resource]
    try:
        item = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Registro no encontrado."}, status=404)
    setattr(item, field, activo)
    try:
        item.save()
        return JsonResponse({"ok": True, "item": serializer(item)})
    except ValidationError as exc:
        return _error_response(exc)


def _simple_collection(request, qs, serializer, search_fields, save_func):
    if request.method == "GET":
        if not _can_read_admin(request.user):
            return _deny()
        qs = _apply_search(qs, request, search_fields)
        activo = request.GET.get("activo")
        if activo in {"true", "false"} and hasattr(qs.model, "activo"):
            qs = qs.filter(activo=activo == "true")
        total, page, page_size, items = _paginate(request, qs)
        return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [serializer(item) for item in items]})

    if not _can_write_admin(request.user):
        return _deny()
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida.", "errors": {"__all__": ["JSON inválido."]}}, status=400)
    return save_func(qs.model(), data, created=True)


def _simple_detail(request, model, pk, serializer, save_func, not_found, select_related=()):
    try:
        qs = model.objects.all()
        if select_related:
            qs = qs.select_related(*select_related)
        item = qs.get(pk=pk)
    except model.DoesNotExist:
        return JsonResponse({"ok": False, "message": not_found}, status=404)

    if request.method == "GET":
        if not _can_read_admin(request.user):
            return _deny()
        return JsonResponse({"ok": True, "item": serializer(item)})

    if not _can_write_admin(request.user):
        return _deny()
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida.", "errors": {"__all__": ["JSON inválido."]}}, status=400)
    return save_func(item, data, created=False)
