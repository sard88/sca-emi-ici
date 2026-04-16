from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    @property
    def roles(self):
        return list(self.groups.values_list("name", flat=True))

    def tiene_rol(self, nombre_rol: str) -> bool:
        return self.groups.filter(name=nombre_rol).exists()

    def save(self, *args, **kwargs):
        if self.correo and not self.email:
            self.email = self.correo
        elif self.email and not self.correo:
            self.correo = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class AsignacionCargo(models.Model):
    DESIGNACION_TITULAR = "titular"
    DESIGNACION_SUPLENTE = "suplente"
    DESIGNACION_ACCIDENTAL = "accidental"

    TIPO_DESIGNACION_CHOICES = [
        (DESIGNACION_TITULAR, "Titular"),
        (DESIGNACION_SUPLENTE, "Suplente"),
        (DESIGNACION_ACCIDENTAL, "Accidental"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="asignaciones_cargo",
    )
    cargo_codigo = models.CharField(max_length=50)
    tipo_designacion = models.CharField(
        max_length=20,
        choices=TIPO_DESIGNACION_CHOICES,
    )
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-activo", "-vigente_desde", "cargo_codigo"]

    def clean(self):
        if self.vigente_hasta and self.vigente_hasta < self.vigente_desde:
            raise ValidationError(
                {"vigente_hasta": "No puede ser anterior a 'vigente_desde'."}
            )

    def __str__(self) -> str:
        return f"{self.usuario.username} - {self.cargo_codigo}"
