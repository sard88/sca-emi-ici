from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from catalogos.models import Carrera


class Usuario(AbstractUser):
    ESTADO_ACTIVO = "activo"
    ESTADO_INACTIVO = "inactivo"
    ESTADO_BLOQUEADO = "bloqueado"

    ESTADO_CUENTA_CHOICES = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_INACTIVO, "Inactivo"),
        (ESTADO_BLOQUEADO, "Bloqueado"),
    ]

    last_login = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Último ingreso",
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Fecha de creación",
    )
    estado_cuenta = models.CharField(
        max_length=20,
        choices=ESTADO_CUENTA_CHOICES,
        default=ESTADO_ACTIVO,
    )
    nombre_completo = models.CharField(max_length=255, blank=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    ultimo_acceso = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Último acceso",
    )

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
    CARGO_JEFE_CARRERA = "JEFE_CARRERA"
    CARGO_JEFE_ACADEMICO = "JEFE_ACADEMICO"
    CARGO_JEFE_PEDAGOGICA = "JEFE_PEDAGOGICA"
    CARGO_DOCENTE = "DOCENTE"

    CARGO_CHOICES = [
        (CARGO_JEFE_CARRERA, "Jefe de carrera"),
        (CARGO_JEFE_ACADEMICO, "Jefe académico"),
        (CARGO_JEFE_PEDAGOGICA, "Jefe de Pedagógica"),
        (CARGO_DOCENTE, "Docente"),
    ]

    CARGOS_POR_CARRERA = {CARGO_JEFE_CARRERA, CARGO_JEFE_PEDAGOGICA}

    DESIGNACION_TITULAR = "titular"
    DESIGNACION_ACCIDENTAL = "accidental"

    TIPO_DESIGNACION_CHOICES = [
        (DESIGNACION_TITULAR, "Titular"),
        (DESIGNACION_ACCIDENTAL, "Accidental"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="asignaciones_cargo",
    )
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.PROTECT,
        related_name="asignaciones_cargo",
        null=True,
        blank=True,
        verbose_name="Carrera",
        help_text="Obligatoria para Jefe de carrera y Jefe de Pedagógica.",
    )
    cargo_codigo = models.CharField(
        max_length=50,
        choices=CARGO_CHOICES,
        verbose_name="Cargo",
    )
    tipo_designacion = models.CharField(
        max_length=20,
        choices=TIPO_DESIGNACION_CHOICES,
    )
    vigente_desde = models.DateField(
        null=True,
        blank=True,
        default=timezone.localdate,
    )
    vigente_hasta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def _ensure_vigencia_defaults(self):
        if not self.vigente_desde:
            self.vigente_desde = timezone.localdate()

    class Meta:
        ordering = ["-activo", "-vigente_desde", "cargo_codigo"]

    def requiere_carrera(self):
        return self.cargo_codigo in self.CARGOS_POR_CARRERA

    def cargo_descripcion(self):
        descripcion = self.get_cargo_codigo_display()
        if self.carrera_id:
            return f"{descripcion} de {self.carrera}"
        return descripcion

    def clean(self):
        self._ensure_vigencia_defaults()
        errors = {}

        if self.requiere_carrera() and not self.carrera_id:
            errors["carrera"] = "Debe seleccionar la carrera para este cargo."
        elif self.carrera_id and not self.requiere_carrera():
            errors["carrera"] = "La carrera solo aplica para Jefe de carrera o Jefe de Pedagógica."

        if self.vigente_hasta and self.vigente_hasta < self.vigente_desde:
            errors["vigente_hasta"] = "No puede ser anterior a 'vigente_desde'."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self._ensure_vigencia_defaults()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.usuario.username} - {self.cargo_descripcion()}"
