import json
from decimal import Decimal

from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST

from core.api_views import api_login_required
from core.portal_services import portal_context
from evaluacion.models import ComponenteEvaluacion, EsquemaEvaluacion
from trayectoria.models import CatalogoResultadoAcademico, CatalogoSituacionAcademica

from .models import (
    ESTADO_ACTIVO,
    ESTADO_INACTIVO,
    Antiguedad,
    Carrera,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
)


CATALOG_ROLES = {
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

WRITE_ROLES = {"ADMIN", "ADMIN_SISTEMA", "ENCARGADO_ESTADISTICA", "ESTADISTICA"}


def _roles(user):
    return set(user.groups.values_list("name", flat=True))


def _is_admin(user):
    roles = _roles(user)
    return user.is_superuser or user.is_staff or bool(roles & {"ADMIN", "ADMIN_SISTEMA"})


def _can_read(user):
    return _is_admin(user) or bool(_roles(user) & CATALOG_ROLES)


def _can_write(user):
    return _is_admin(user) or bool(_roles(user) & WRITE_ROLES)


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


def _date(value):
    return value.isoformat() if value else None


def _decimal(value):
    if value is None:
        return None
    return str(value)


def _min(item, label=None):
    if not item:
        return None
    return {"id": item.id, "label": label or str(item)}


def _estado_activo(value):
    return value == ESTADO_ACTIVO


def _apply_search(qs, request, fields):
    query = (request.GET.get("q") or request.GET.get("search") or "").strip()
    if not query:
        return qs
    condition = Q()
    for field in fields:
        condition |= Q(**{f"{field}__icontains": query})
    return qs.filter(condition)


def _filter_active(qs, request):
    activo = request.GET.get("activo")
    if activo not in {"true", "false"}:
        return qs
    if _has_field(qs.model, "estado"):
        return qs.filter(estado=ESTADO_ACTIVO if activo == "true" else ESTADO_INACTIVO)
    if _has_field(qs.model, "activo"):
        return qs.filter(activo=activo == "true")
    return qs


def _filter_scope(qs, request):
    ctx = portal_context(request.user)
    if ctx.has_consulta_amplia or not ctx.is_jefatura_carrera or not ctx.carrera_ids:
        return qs
    model = qs.model
    if model is Carrera:
        return qs.filter(id__in=ctx.carrera_ids)
    if model is PlanEstudios:
        return qs.filter(carrera_id__in=ctx.carrera_ids)
    if model is Antiguedad:
        return qs.filter(plan_estudios__carrera_id__in=ctx.carrera_ids)
    if model is GrupoAcademico:
        return qs.filter(antiguedad__plan_estudios__carrera_id__in=ctx.carrera_ids)
    if model is ProgramaAsignatura:
        return qs.filter(plan_estudios__carrera_id__in=ctx.carrera_ids)
    if model is EsquemaEvaluacion:
        return qs.filter(programa_asignatura__plan_estudios__carrera_id__in=ctx.carrera_ids)
    if model is ComponenteEvaluacion:
        return qs.filter(esquema__programa_asignatura__plan_estudios__carrera_id__in=ctx.carrera_ids)
    return qs


def _has_field(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


def _field_value(field, value):
    if value == "":
        return None
    if value is None:
        return None
    internal_type = field.get_internal_type()
    if internal_type in {"DateField", "DateTimeField"} and isinstance(value, str):
        return parse_date(value) if internal_type == "DateField" else value
    if internal_type in {"DecimalField"}:
        return Decimal(str(value))
    return value


def _set_fields(instance, data, fields, fk_fields=None):
    fk_fields = fk_fields or {}
    for field_name in fields:
        if field_name not in data:
            continue
        field = instance._meta.get_field(field_name)
        setattr(instance, field_name, _field_value(field, data[field_name]))
    for input_key, field_name in fk_fields.items():
        if input_key not in data:
            continue
        value = data[input_key]
        setattr(instance, field_name, int(value) if value not in ("", None) else None)


def _save(instance):
    instance.full_clean()
    instance.save()


def _collection(request, slug):
    config = RESOURCE_CONFIG[slug]
    if request.method == "GET":
        if not _can_read(request.user):
            return _deny()
        qs = _filter_scope(config["queryset"](), request)
        qs = _filter_active(_apply_search(qs, request, config["search"]), request)
        total, page, page_size, items = _paginate(request, qs.distinct())
        return JsonResponse({"ok": True, "total": total, "page": page, "page_size": page_size, "items": [config["serializer"](item) for item in items]})

    if not _can_write(request.user):
        return _deny()
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida.", "errors": {"__all__": ["JSON inválido."]}}, status=400)
    instance = config["model"]()
    return config["save"](instance, data, True)


def _detail(request, slug, pk):
    config = RESOURCE_CONFIG[slug]
    try:
        item = _filter_scope(config["queryset"](), request).get(pk=pk)
    except config["model"].DoesNotExist:
        return JsonResponse({"ok": False, "message": "Registro no encontrado."}, status=404)

    if request.method == "GET":
        if not _can_read(request.user):
            return _deny()
        return JsonResponse({"ok": True, "item": config["serializer"](item)})

    if not _can_write(request.user):
        return _deny()
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida.", "errors": {"__all__": ["JSON inválido."]}}, status=400)
    return config["save"](item, data, False)


def _activate(request, slug, pk, active):
    config = RESOURCE_CONFIG[slug]
    if not _can_write(request.user):
        return _deny()
    try:
        item = config["queryset"]().get(pk=pk)
    except config["model"].DoesNotExist:
        return JsonResponse({"ok": False, "message": "Registro no encontrado."}, status=404)
    if _has_field(config["model"], "estado"):
        item.estado = ESTADO_ACTIVO if active else ESTADO_INACTIVO
    elif _has_field(config["model"], "activo"):
        item.activo = active
    else:
        return JsonResponse({"ok": False, "message": "Este recurso no admite activación/inactivación desde el portal."}, status=400)
    try:
        _save(item)
        return JsonResponse({"ok": True, "item": config["serializer"](item)})
    except (ValidationError, IntegrityError) as exc:
        return _error_response(exc)


def _save_simple(instance, data, created=False):
    config = RESOURCE_CONFIG[data.pop("_slug")]
    _set_fields(instance, data, config["fields"], config.get("fk_fields"))
    try:
        _save(instance)
        return JsonResponse({"ok": True, "item": config["serializer"](instance)}, status=201 if created else 200)
    except (ValidationError, IntegrityError) as exc:
        return _error_response(exc)


def _simple_save_for(slug):
    def save(instance, data, created=False):
        payload = dict(data)
        payload["_slug"] = slug
        return _save_simple(instance, payload, created)

    return save


def serialize_carrera(item):
    return {
        "id": item.id,
        "clave": item.clave,
        "nombre": item.nombre,
        "estado": item.estado,
        "activo": _estado_activo(item.estado),
        "vigente_desde": _date(item.vigente_desde),
        "vigente_hasta": _date(item.vigente_hasta),
        "label": str(item),
    }


def serialize_plan(item):
    return {
        **serialize_carrera(item),
        "carrera": _min(item.carrera),
        "carrera_id": item.carrera_id,
        "version": item.version,
        "label": str(item),
    }


def serialize_antiguedad(item):
    return {
        "id": item.id,
        "clave": item.clave,
        "nombre": item.nombre,
        "estado": item.estado,
        "activo": _estado_activo(item.estado),
        "plan_estudios": _min(item.plan_estudios),
        "plan_estudios_id": item.plan_estudios_id,
        "anio_inicio": item.anio_inicio,
        "anio_fin": item.anio_fin,
        "vigente_desde": _date(item.vigente_desde),
        "vigente_hasta": _date(item.vigente_hasta),
        "label": str(item),
    }


def serialize_periodo(item):
    return {
        "id": item.id,
        "clave": item.clave,
        "anio_escolar": item.anio_escolar,
        "periodo_academico": item.periodo_academico,
        "periodo_academico_label": item.get_periodo_academico_display(),
        "fecha_inicio": _date(item.fecha_inicio),
        "fecha_fin": _date(item.fecha_fin),
        "estado": item.estado,
        "estado_label": item.get_estado_display(),
        "activo": item.estado == ESTADO_ACTIVO,
        "label": str(item),
    }


def serialize_grupo(item):
    return {
        "id": item.id,
        "clave_grupo": item.clave_grupo,
        "nombre": item.clave_grupo,
        "antiguedad": _min(item.antiguedad),
        "antiguedad_id": item.antiguedad_id,
        "periodo": _min(item.periodo),
        "periodo_id": item.periodo_id,
        "semestre_numero": item.semestre_numero,
        "estado": item.estado,
        "activo": item.estado == ESTADO_ACTIVO,
        "cupo_maximo": item.cupo_maximo,
        "carrera": _min(item.antiguedad.plan_estudios.carrera) if item.antiguedad_id else None,
        "label": str(item),
    }


def serialize_materia(item):
    return {
        "id": item.id,
        "clave": item.clave,
        "nombre": item.nombre,
        "horas_totales": item.horas_totales,
        "creditos": _decimal(item.creditos),
        "estado": item.estado,
        "activo": item.estado == ESTADO_ACTIVO,
        "vigente_desde": _date(item.vigente_desde),
        "vigente_hasta": _date(item.vigente_hasta),
        "label": str(item),
    }


def serialize_programa(item):
    return {
        "id": item.id,
        "plan_estudios": _min(item.plan_estudios),
        "plan_estudios_id": item.plan_estudios_id,
        "materia": _min(item.materia),
        "materia_id": item.materia_id,
        "semestre_numero": item.semestre_numero,
        "anio_formacion": item.anio_formacion,
        "obligatoria": item.obligatoria,
        "ubicacion_excepcional": item.ubicacion_excepcional,
        "activo": item.plan_estudios.estado == ESTADO_ACTIVO and item.materia.estado == ESTADO_ACTIVO,
        "label": str(item),
    }


def serialize_esquema(item):
    return {
        "id": item.id,
        "programa_asignatura": _min(item.programa_asignatura),
        "programa_asignatura_id": item.programa_asignatura_id,
        "version": item.version,
        "num_parciales": item.num_parciales,
        "permite_exencion": item.permite_exencion,
        "peso_parciales": _decimal(item.peso_parciales),
        "peso_final": _decimal(item.peso_final),
        "umbral_exencion": _decimal(item.umbral_exencion),
        "activo": item.activo,
        "componentes": [serialize_componente(componente) for componente in item.componentes.all()],
        "label": str(item),
    }


def serialize_componente(item):
    return {
        "id": item.id,
        "esquema": _min(item.esquema),
        "esquema_id": item.esquema_id,
        "corte_codigo": item.corte_codigo,
        "corte_label": item.get_corte_codigo_display(),
        "nombre": item.nombre,
        "porcentaje": _decimal(item.porcentaje),
        "es_examen": item.es_examen,
        "orden": item.orden,
        "activo": True,
        "label": str(item),
    }


def serialize_situacion(item):
    return {"id": item.id, "clave": item.clave, "nombre": item.nombre, "activo": item.activo, "label": str(item)}


def serialize_resultado(item):
    return {"id": item.id, "clave": item.clave, "nombre": item.nombre, "activo": item.activo, "label": str(item)}


RESOURCE_CONFIG = {
    "carreras": {
        "model": Carrera,
        "queryset": lambda: Carrera.objects.order_by("clave"),
        "serializer": serialize_carrera,
        "search": ["clave", "nombre"],
        "fields": ["clave", "nombre", "estado", "vigente_desde", "vigente_hasta"],
    },
    "planes": {
        "model": PlanEstudios,
        "queryset": lambda: PlanEstudios.objects.select_related("carrera").order_by("carrera__clave", "clave"),
        "serializer": serialize_plan,
        "search": ["clave", "nombre", "carrera__clave", "carrera__nombre"],
        "fields": ["clave", "nombre", "version", "estado", "vigente_desde", "vigente_hasta"],
        "fk_fields": {"carrera": "carrera_id", "carrera_id": "carrera_id"},
    },
    "antiguedades": {
        "model": Antiguedad,
        "queryset": lambda: Antiguedad.objects.select_related("plan_estudios", "plan_estudios__carrera").order_by("-anio_inicio", "clave"),
        "serializer": serialize_antiguedad,
        "search": ["clave", "nombre", "plan_estudios__clave", "plan_estudios__carrera__clave"],
        "fields": ["clave", "nombre", "anio_inicio", "anio_fin", "estado", "vigente_desde", "vigente_hasta"],
        "fk_fields": {"plan_estudios": "plan_estudios_id", "plan_estudios_id": "plan_estudios_id"},
    },
    "periodos": {
        "model": PeriodoEscolar,
        "queryset": lambda: PeriodoEscolar.objects.order_by("-anio_escolar", "-periodo_academico", "clave"),
        "serializer": serialize_periodo,
        "search": ["clave", "anio_escolar"],
        "fields": ["clave", "anio_escolar", "periodo_academico", "fecha_inicio", "fecha_fin", "estado"],
    },
    "grupos": {
        "model": GrupoAcademico,
        "queryset": lambda: GrupoAcademico.objects.select_related("antiguedad", "antiguedad__plan_estudios", "antiguedad__plan_estudios__carrera", "periodo").order_by("clave_grupo"),
        "serializer": serialize_grupo,
        "search": ["clave_grupo", "antiguedad__clave", "periodo__clave"],
        "fields": ["clave_grupo", "semestre_numero", "estado", "cupo_maximo"],
        "fk_fields": {"antiguedad": "antiguedad_id", "antiguedad_id": "antiguedad_id", "periodo": "periodo_id", "periodo_id": "periodo_id"},
    },
    "materias": {
        "model": Materia,
        "queryset": lambda: Materia.objects.order_by("clave", "nombre"),
        "serializer": serialize_materia,
        "search": ["clave", "nombre"],
        "fields": ["clave", "nombre", "horas_totales", "estado", "vigente_desde", "vigente_hasta"],
    },
    "programas-asignatura": {
        "model": ProgramaAsignatura,
        "queryset": lambda: ProgramaAsignatura.objects.select_related("plan_estudios", "materia", "plan_estudios__carrera").order_by("plan_estudios__clave", "materia__clave"),
        "serializer": serialize_programa,
        "search": ["plan_estudios__clave", "materia__clave", "materia__nombre"],
        "fields": ["semestre_numero", "ubicacion_excepcional"],
        "fk_fields": {"plan_estudios": "plan_estudios_id", "plan_estudios_id": "plan_estudios_id", "materia": "materia_id", "materia_id": "materia_id"},
    },
    "esquemas-evaluacion": {
        "model": EsquemaEvaluacion,
        "queryset": lambda: EsquemaEvaluacion.objects.select_related("programa_asignatura", "programa_asignatura__plan_estudios", "programa_asignatura__materia").prefetch_related("componentes").order_by("-activo", "programa_asignatura__materia__clave"),
        "serializer": serialize_esquema,
        "search": ["version", "programa_asignatura__materia__clave", "programa_asignatura__materia__nombre"],
        "fields": ["version", "num_parciales", "permite_exencion", "peso_parciales", "peso_final", "umbral_exencion", "activo"],
        "fk_fields": {"programa_asignatura": "programa_asignatura_id", "programa_asignatura_id": "programa_asignatura_id"},
    },
    "situaciones-academicas": {
        "model": CatalogoSituacionAcademica,
        "queryset": lambda: CatalogoSituacionAcademica.objects.order_by("clave"),
        "serializer": serialize_situacion,
        "search": ["clave", "nombre"],
        "fields": ["clave", "nombre", "activo"],
    },
    "resultados-academicos": {
        "model": CatalogoResultadoAcademico,
        "queryset": lambda: CatalogoResultadoAcademico.objects.order_by("clave"),
        "serializer": serialize_resultado,
        "search": ["clave", "nombre"],
        "fields": ["clave", "nombre", "activo"],
    },
}

for _slug, _config in RESOURCE_CONFIG.items():
    _config["save"] = _simple_save_for(_slug)


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def collection_view(request, slug):
    if slug not in RESOURCE_CONFIG:
        return JsonResponse({"ok": False, "message": "Catálogo no encontrado."}, status=404)
    return _collection(request, slug)


@require_http_methods(["GET", "PATCH"])
@csrf_protect
@api_login_required
def detail_view(request, slug, pk):
    if slug not in RESOURCE_CONFIG:
        return JsonResponse({"ok": False, "message": "Catálogo no encontrado."}, status=404)
    return _detail(request, slug, pk)


@require_POST
@csrf_protect
@api_login_required
def activar_view(request, slug, pk):
    if slug not in RESOURCE_CONFIG:
        return JsonResponse({"ok": False, "message": "Catálogo no encontrado."}, status=404)
    return _activate(request, slug, pk, True)


@require_POST
@csrf_protect
@api_login_required
def inactivar_view(request, slug, pk):
    if slug not in RESOURCE_CONFIG:
        return JsonResponse({"ok": False, "message": "Catálogo no encontrado."}, status=404)
    return _activate(request, slug, pk, False)


@require_http_methods(["GET", "POST"])
@csrf_protect
@api_login_required
def componentes_collection_view(request, esquema_id):
    if request.method == "GET":
        if not _can_read(request.user):
            return _deny()
        qs = ComponenteEvaluacion.objects.select_related("esquema").filter(esquema_id=esquema_id).order_by("corte_codigo", "orden")
        return JsonResponse({"ok": True, "total": qs.count(), "page": 1, "page_size": qs.count(), "items": [serialize_componente(item) for item in qs]})
    if not _can_write(request.user):
        return _deny()
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida.", "errors": {"__all__": ["JSON inválido."]}}, status=400)
    componente = ComponenteEvaluacion(esquema_id=esquema_id)
    return _save_componente(componente, data, True)


@require_http_methods(["GET", "PATCH"])
@csrf_protect
@api_login_required
def componente_detail_view(request, esquema_id, componente_id):
    try:
        item = ComponenteEvaluacion.objects.select_related("esquema").get(pk=componente_id, esquema_id=esquema_id)
    except ComponenteEvaluacion.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Componente no encontrado."}, status=404)
    if request.method == "GET":
        if not _can_read(request.user):
            return _deny()
        return JsonResponse({"ok": True, "item": serialize_componente(item)})
    if not _can_write(request.user):
        return _deny()
    data = _json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "message": "Solicitud inválida.", "errors": {"__all__": ["JSON inválido."]}}, status=400)
    return _save_componente(item, data, False)


def _save_componente(item, data, created=False):
    _set_fields(item, data, ["corte_codigo", "nombre", "porcentaje", "es_examen", "orden"])
    try:
        _save(item)
        return JsonResponse({"ok": True, "item": serialize_componente(item)}, status=201 if created else 200)
    except (ValidationError, IntegrityError) as exc:
        return _error_response(exc)
