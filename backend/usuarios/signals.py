from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone


ROLES_BASE = (
    "ADMIN",
    "ADMIN_SISTEMA",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_PLAN_EVAL",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "DOCENTE",
    "DISCENTE",
)

CATALOGOS_MODELOS = (
    "antiguedad",
    "carrera",
    "grupoacademico",
    "materia",
    "periodoescolar",
    "planestudios",
    "programaasignatura",
)

RELACIONES_MODELOS = (
    "adscripciongrupo",
    "asignaciondocente",
    "discente",
    "inscripcionmateria",
    "movimientoacademico",
)

EVALUACION_MODELOS = (
    "componenteevaluacion",
    "esquemaevaluacion",
)


def permisos_modelos(app_label, modelos, acciones):
    return [
        (app_label, modelo, accion)
        for modelo in modelos
        for accion in acciones
    ]


PERMISOS_JEFATURA_CARRERA = (
    permisos_modelos("catalogos", CATALOGOS_MODELOS, ("view",))
    + permisos_modelos("evaluacion", EVALUACION_MODELOS, ("view",))
    + permisos_modelos(
        "relaciones",
        ("adscripciongrupo", "discente", "inscripcionmateria", "movimientoacademico"),
        ("view",),
    )
    + permisos_modelos("relaciones", ("asignaciondocente",), ("add", "change", "view"))
)

PERMISOS_JEFATURA_ACADEMICA = (
    permisos_modelos("catalogos", CATALOGOS_MODELOS, ("view",))
    + permisos_modelos("evaluacion", EVALUACION_MODELOS, ("view",))
    + permisos_modelos("relaciones", RELACIONES_MODELOS, ("view",))
)

PERMISOS_ESTADISTICA = (
    permisos_modelos("catalogos", CATALOGOS_MODELOS, ("view",))
    + permisos_modelos(
        "relaciones",
        ("adscripciongrupo", "asignaciondocente", "discente", "inscripcionmateria"),
        ("view",),
    )
    + permisos_modelos("relaciones", ("movimientoacademico",), ("add", "change", "view"))
)

PERMISOS_DOCENTE = (
    permisos_modelos("catalogos", ("grupoacademico", "periodoescolar", "programaasignatura"), ("view",))
    + permisos_modelos("evaluacion", EVALUACION_MODELOS, ("view",))
    + permisos_modelos(
        "relaciones",
        ("asignaciondocente", "discente", "inscripcionmateria"),
        ("view",),
    )
)

PERMISOS_DISCENTE = (
    permisos_modelos("catalogos", ("grupoacademico", "periodoescolar", "programaasignatura"), ("view",))
    + permisos_modelos("relaciones", ("adscripciongrupo", "discente", "inscripcionmateria"), ("view",))
)

PERMISOS_POR_ROL = {
    "JEFE_CARRERA": PERMISOS_JEFATURA_CARRERA,
    "JEFATURA_CARRERA": PERMISOS_JEFATURA_CARRERA,
    "JEFE_SUB_EJEC_CTR": PERMISOS_JEFATURA_CARRERA,
    "JEFE_SUB_PLAN_EVAL": PERMISOS_JEFATURA_ACADEMICA,
    "JEFE_ACADEMICO": PERMISOS_JEFATURA_ACADEMICA,
    "JEFATURA_ACADEMICA": PERMISOS_JEFATURA_ACADEMICA,
    "JEFE_PEDAGOGICA": PERMISOS_JEFATURA_ACADEMICA,
    "ENCARGADO_ESTADISTICA": PERMISOS_ESTADISTICA,
    "ESTADISTICA": PERMISOS_ESTADISTICA,
    "DOCENTE": PERMISOS_DOCENTE,
    "DISCENTE": PERMISOS_DISCENTE,
}


def obtener_permisos(especificaciones):
    permisos = []
    for app_label, modelo, accion in especificaciones:
        permiso = Permission.objects.filter(
            content_type__app_label=app_label,
            content_type__model=modelo,
            codename=f"{accion}_{modelo}",
        ).first()
        if permiso:
            permisos.append(permiso)
    return permisos


@receiver(post_migrate)
def crear_roles_base(sender, **kwargs):
    for rol in ROLES_BASE:
        grupo, _ = Group.objects.get_or_create(name=rol)
        if rol in {"ADMIN", "ADMIN_SISTEMA"}:
            grupo.permissions.add(*Permission.objects.all())
            continue

        permisos = obtener_permisos(PERMISOS_POR_ROL.get(rol, ()))
        if permisos:
            grupo.permissions.add(*permisos)


@receiver(user_logged_in)
def registrar_ultimo_acceso(sender, request, user, **kwargs):
    if not hasattr(user, "ultimo_acceso"):
        return

    user.ultimo_acceso = timezone.now()
    user.save(update_fields=["ultimo_acceso"])
