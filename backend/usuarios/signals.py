from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver


ROLES_BASE = (
    "ADMIN_SISTEMA",
    "JEFATURA_CARRERA",
    "JEFATURA_ACADEMICA",
    "DOCENTE",
)


@receiver(post_migrate)
def crear_roles_base(sender, **kwargs):
    if sender.label != "usuarios":
        return

    for rol in ROLES_BASE:
        Group.objects.get_or_create(name=rol)
