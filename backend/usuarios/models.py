from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ESTADO_ACTIVO = "activo"
    ESTADO_INACTIVO = "inactivo"
    ESTADO_BLOQUEADO = "bloqueado"

    ESTADO_CUENTA_CHOICES = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_INACTIVO, "Inactivo"),
        (ESTADO_BLOQUEADO, "Bloqueado"),
    ]

    estado_cuenta = models.CharField(
        max_length=20,
        choices=ESTADO_CUENTA_CHOICES,
        default=ESTADO_ACTIVO,
    )
    nombre_completo = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.username
