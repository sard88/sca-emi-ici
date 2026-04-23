from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone


ROLES_BASE = (
    "ADMIN_SISTEMA",
    "JEFATURA_CARRERA",
    "JEFATURA_ACADEMICA",
    "DOCENTE",
    "DISCENTE",
)


@receiver(post_migrate)
def crear_roles_base(sender, **kwargs):
    if sender.label != "usuarios":
        return

    for rol in ROLES_BASE:
        Group.objects.get_or_create(name=rol)


@receiver(user_logged_in)
def registrar_ultimo_acceso(sender, request, user, **kwargs):
    if not hasattr(user, "ultimo_acceso"):
        return

    user.ultimo_acceso = timezone.now()
    user.save(update_fields=["ultimo_acceso"])
