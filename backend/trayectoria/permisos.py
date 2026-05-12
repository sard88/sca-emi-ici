from django.db.models import Q
from django.utils import timezone

from relaciones.permisos import (
    usuario_es_admin_soporte,
    usuario_es_estadistica,
    usuario_es_jefatura_carrera,
    usuario_es_jefatura_planeacion,
)
from usuarios.models import AsignacionCargo


ROLES_JEFATURA_ACADEMICA = ("JEFE_ACADEMICO", "JEFATURA_ACADEMICA")
ROLES_JEFATURA_PEDAGOGICA = ("JEFE_PEDAGOGICA",)
CARGOS_JEFATURA_ACADEMICA = ("JEFE_ACADEMICO",)
CARGOS_JEFATURA_PEDAGOGICA = ("JEFE_PEDAGOGICA",)
CARGOS_CON_AMBITO_CARRERA = (
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_SUB_PLAN_EVAL",
    "JEFE_SUBSECCION_PEDAGOGICA",
)


def usuario_tiene_grupo(user, grupos):
    return user.is_authenticated and user.groups.filter(name__in=grupos).exists()


def usuario_tiene_cargo_activo(user, cargos):
    hoy = timezone.localdate()
    return AsignacionCargo.objects.filter(
        Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
        Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
        usuario=user,
        activo=True,
        cargo_codigo__in=cargos,
    ).exists()


def usuario_es_jefatura_academica(user):
    return usuario_tiene_grupo(user, ROLES_JEFATURA_ACADEMICA) or usuario_tiene_cargo_activo(
        user,
        CARGOS_JEFATURA_ACADEMICA,
    )


def usuario_es_jefatura_pedagogica(user):
    return usuario_tiene_grupo(user, ROLES_JEFATURA_PEDAGOGICA) or usuario_tiene_cargo_activo(
        user,
        CARGOS_JEFATURA_PEDAGOGICA,
    )


def carreras_ambito_usuario(user):
    hoy = timezone.localdate()
    cargos = AsignacionCargo.objects.filter(
        Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
        Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
        usuario=user,
        activo=True,
        cargo_codigo__in=CARGOS_CON_AMBITO_CARRERA,
    ).select_related("carrera", "unidad_organizacional", "unidad_organizacional__carrera")

    carrera_ids = set()
    for cargo in cargos:
        if cargo.carrera_id:
            carrera_ids.add(cargo.carrera_id)
        if cargo.unidad_organizacional_id and cargo.unidad_organizacional.carrera_id:
            carrera_ids.add(cargo.unidad_organizacional.carrera_id)
    return carrera_ids


def puede_operar_trayectoria(user):
    return usuario_es_admin_soporte(user) or usuario_es_estadistica(user)


def puede_consultar_historiales(user):
    return (
        usuario_es_admin_soporte(user)
        or usuario_es_estadistica(user)
        or usuario_es_jefatura_carrera(user)
        or usuario_es_jefatura_planeacion(user)
        or usuario_es_jefatura_academica(user)
        or usuario_es_jefatura_pedagogica(user)
    )


def filtrar_discentes_por_ambito(user, queryset):
    if (
        usuario_es_admin_soporte(user)
        or usuario_es_estadistica(user)
        or usuario_es_jefatura_academica(user)
        or usuario_es_jefatura_pedagogica(user)
    ):
        return queryset

    carrera_ids = carreras_ambito_usuario(user)
    if carrera_ids:
        return queryset.filter(plan_estudios__carrera_id__in=carrera_ids)
    return queryset.none()


def puede_consultar_historial_discente(user, discente):
    if not user.is_authenticated:
        return False

    if discente.usuario_id == user.id:
        return True

    if not puede_consultar_historiales(user):
        return False

    return filtrar_discentes_por_ambito(
        user,
        discente.__class__.objects.filter(pk=discente.pk),
    ).exists()
