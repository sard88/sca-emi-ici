from django.db.models import Q
from django.utils import timezone

from usuarios.models import AsignacionCargo


ROLES_ADMIN = ("ADMIN_SISTEMA", "ADMIN")
ROLES_JEFATURA_CARRERA = ("JEFE_CARRERA", "JEFATURA_CARRERA")
ROLES_ESTADISTICA = ("ENCARGADO_ESTADISTICA", "ESTADISTICA")
ROLES_DISCENTE = ("DISCENTE",)
ROLES_DOCENTE = ("DOCENTE",)

CARGOS_ADMIN = ("ADMIN", "ADMIN_SISTEMA")
CARGOS_JEFATURA_CARRERA = ("JEFE_CARRERA", "JEFATURA_CARRERA")
CARGOS_ESTADISTICA = ("ENCARGADO_ESTADISTICA", "ESTADISTICA")


def usuario_tiene_rol(user, roles):
    return user.groups.filter(name__in=roles).exists()


def usuario_tiene_cargo_activo(user, cargos):
    hoy = timezone.localdate()
    cargos_filter = Q()
    for cargo in cargos:
        cargos_filter |= Q(cargo_codigo__iexact=cargo)

    return AsignacionCargo.objects.filter(
        Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
        Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
        cargos_filter,
        usuario=user,
        activo=True,
    ).exists()


def usuario_es_admin_soporte(user):
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser
        or usuario_tiene_rol(user, ROLES_ADMIN)
        or usuario_tiene_cargo_activo(user, CARGOS_ADMIN)
    )


def usuario_es_jefatura_carrera(user):
    if not user.is_authenticated:
        return False
    return usuario_tiene_rol(user, ROLES_JEFATURA_CARRERA) or usuario_tiene_cargo_activo(
        user,
        CARGOS_JEFATURA_CARRERA,
    )


def usuario_es_estadistica(user):
    if not user.is_authenticated:
        return False
    return usuario_tiene_rol(user, ROLES_ESTADISTICA) or usuario_tiene_cargo_activo(
        user,
        CARGOS_ESTADISTICA,
    )


def usuario_es_discente(user):
    if not user.is_authenticated:
        return False
    return usuario_tiene_rol(user, ROLES_DISCENTE)


def usuario_es_docente(user):
    if not user.is_authenticated:
        return False
    return usuario_tiene_rol(user, ROLES_DOCENTE)


def puede_consultar_relaciones(user):
    return (
        usuario_es_admin_soporte(user)
        or usuario_es_jefatura_carrera(user)
        or usuario_es_estadistica(user)
    )


def puede_operar_asignacion_docente(user):
    return usuario_es_admin_soporte(user) or usuario_es_jefatura_carrera(user)


def puede_consultar_asignacion_docente(user):
    return puede_operar_asignacion_docente(user) or usuario_es_estadistica(user)
