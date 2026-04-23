from datetime import date
from decimal import Decimal, ROUND_FLOOR

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .validators import CLAVE_MAX_LENGTH, clave_format_validator


ESTADO_ACTIVO = "activo"
ESTADO_INACTIVO = "inactivo"

ESTADO_CHOICES = [
    (ESTADO_ACTIVO, "Activo"),
    (ESTADO_INACTIVO, "Inactivo"),
]

ANIO_ESCOLAR_START_YEAR = 2020
ANIO_ESCOLAR_FUTURE_OFFSET = 9


def build_anio_escolar_choices():
    current_year = timezone.localdate().year
    end_year = current_year + ANIO_ESCOLAR_FUTURE_OFFSET
    return [
        (f"{year}-{year + 1}", f"{year}-{year + 1}")
        for year in range(ANIO_ESCOLAR_START_YEAR, end_year + 1)
    ]

SEMESTRE_OPERATIVO_CHOICES = [
    (1, "Primer semestre"),
    (2, "Segundo semestre"),
]

CREDITOS_FACTOR = Decimal("0.0625")
CREDITOS_ROUNDING_OFFSET = Decimal("0.5")


class CatalogoAcademicoBase(models.Model):
    clave = models.CharField(
        max_length=CLAVE_MAX_LENGTH,
        validators=[clave_format_validator],
    )
    nombre = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)
    vigente_desde = models.DateField(
        null=True,
        blank=True,
        default=timezone.localdate,
    )
    vigente_hasta = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

    def _ensure_vigencia_defaults(self):
        if not self.vigente_desde:
            self.vigente_desde = timezone.localdate()

    def clean(self):
        self._ensure_vigencia_defaults()
        if self.vigente_desde and self.vigente_hasta:
            if self.vigente_hasta < self.vigente_desde:
                raise ValidationError(
                    {"vigente_hasta": "No puede ser anterior a 'vigente_desde'."}
                )

    def save(self, *args, **kwargs):
        self._ensure_vigencia_defaults()
        super().save(*args, **kwargs)


class Carrera(CatalogoAcademicoBase):
    class Meta:
        ordering = ["clave", "nombre"]
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
        constraints = [
            models.UniqueConstraint(fields=["clave"], name="uq_carrera_clave"),
        ]

    def __str__(self) -> str:
        return f"{self.clave} - {self.nombre}"


class PlanEstudios(CatalogoAcademicoBase):
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.PROTECT,
        related_name="planes_estudio",
    )
    version = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["carrera__clave", "clave"]
        verbose_name = "Plan de estudio"
        verbose_name_plural = "Planes de estudio"
        constraints = [
            models.UniqueConstraint(
                fields=["carrera", "clave"],
                name="uq_planestudios_carrera_clave",
            )
        ]

    def clean(self):
        super().clean()
        if self.carrera_id and self.carrera.estado != ESTADO_ACTIVO:
            raise ValidationError(
                {"carrera": "Solo se puede asignar una carrera activa."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.carrera.clave} - {self.clave}"


class Generacion(CatalogoAcademicoBase):
    plan_estudios = models.ForeignKey(
        PlanEstudios,
        on_delete=models.PROTECT,
        related_name="generaciones",
    )
    anio_inicio = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Año de inicio",
    )
    anio_fin = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Año de fin",
    )

    class Meta:
        ordering = ["-anio_inicio", "clave"]
        verbose_name = "Antigüedad"
        verbose_name_plural = "Antigüedades"
        constraints = [
            models.UniqueConstraint(
                fields=["plan_estudios", "clave"],
                name="uq_generacion_plan_clave",
            )
        ]

    def clean(self):
        super().clean()
        if self.anio_inicio and self.anio_fin and self.anio_fin < self.anio_inicio:
            raise ValidationError({"anio_fin": "No puede ser menor al año de inicio."})

    def __str__(self) -> str:
        return f"{self.plan_estudios.clave} - {self.clave}"


class PeriodoEscolar(models.Model):
    clave = models.CharField(
        max_length=CLAVE_MAX_LENGTH,
        validators=[clave_format_validator],
        verbose_name="Clave",
    )
    anio_escolar = models.CharField(
        max_length=20,
        choices=build_anio_escolar_choices,
        verbose_name="Año escolar",
    )
    semestre_operativo = models.PositiveSmallIntegerField(
        choices=SEMESTRE_OPERATIVO_CHOICES,
        null=True,
        verbose_name="Periodo académico",
    )
    fecha_inicio = models.DateField(null=True, verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(null=True, verbose_name="Fecha de fin")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name="Estado",
    )

    class Meta:
        ordering = ["-anio_escolar", "-semestre_operativo", "clave"]
        verbose_name = "Periodo escolar"
        verbose_name_plural = "Periodo escolar"
        constraints = [
            models.UniqueConstraint(fields=["clave"], name="uq_periodoescolar_clave"),
        ]

    @staticmethod
    def get_ciclo_escolar_bounds(anio_escolar: str) -> tuple[date, date]:
        try:
            inicio_str, fin_str = anio_escolar.split("-")
            inicio_anio = int(inicio_str)
            fin_anio = int(fin_str)
        except (AttributeError, TypeError, ValueError):
            raise ValidationError({"anio_escolar": "Debe tener formato AAAA-AAAA."})

        if fin_anio != inicio_anio + 1:
            raise ValidationError({"anio_escolar": "Debe abarcar dos años consecutivos."})

        return date(inicio_anio, 8, 1), date(fin_anio, 7, 31)

    def clean(self):
        errors = {}

        if not self.anio_escolar:
            errors["anio_escolar"] = "Este campo es obligatorio."
        if self.semestre_operativo is None:
            errors["semestre_operativo"] = "Este campo es obligatorio."
        if not self.fecha_inicio:
            errors["fecha_inicio"] = "Este campo es obligatorio."
        if not self.fecha_fin:
            errors["fecha_fin"] = "Este campo es obligatorio."

        if errors:
            raise ValidationError(errors)

        ciclo_inicio, ciclo_fin = self.get_ciclo_escolar_bounds(self.anio_escolar)

        if self.fecha_inicio >= self.fecha_fin:
            errors["fecha_fin"] = "Debe ser posterior a fecha_inicio."

        if self.fecha_inicio < ciclo_inicio:
            errors["fecha_inicio"] = f"No puede ser anterior al inicio del ciclo {self.anio_escolar}."
        elif self.fecha_inicio > ciclo_fin:
            errors["fecha_inicio"] = f"No puede ser posterior al cierre del ciclo {self.anio_escolar}."

        if self.fecha_fin < ciclo_inicio:
            errors["fecha_fin"] = f"No puede ser anterior al inicio del ciclo {self.anio_escolar}."
        elif self.fecha_fin > ciclo_fin:
            errors["fecha_fin"] = f"No puede ser posterior al cierre del ciclo {self.anio_escolar}."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.clave} - {self.anio_escolar} S{self.semestre_operativo}"


class GrupoAcademico(models.Model):
    clave_grupo = models.CharField(
        max_length=CLAVE_MAX_LENGTH,
        validators=[clave_format_validator],
        verbose_name="Clave de grupo",
    )
    generacion = models.ForeignKey(
        Generacion,
        on_delete=models.PROTECT,
        related_name="grupos_academicos",
        verbose_name="Antigüedad",
    )
    periodo = models.ForeignKey(
        PeriodoEscolar,
        on_delete=models.PROTECT,
        related_name="grupos_academicos",
        verbose_name="Periodo escolar",
    )
    semestre_numero = models.PositiveSmallIntegerField(default=1, verbose_name="Semestre número")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name="Estado",
    )
    cupo_maximo = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Cupo máximo",
    )

    class Meta:
        ordering = ["periodo__anio_escolar", "periodo__semestre_operativo", "clave_grupo"]
        verbose_name = "Grupo académico"
        verbose_name_plural = "Grupos académicos"
        constraints = [
            models.UniqueConstraint(
                fields=["generacion", "periodo", "clave_grupo"],
                name="uq_grupo_generacion_periodo_clave",
            )
        ]

    def __str__(self) -> str:
        return f"{self.periodo.clave} - {self.clave_grupo}"


class Materia(CatalogoAcademicoBase):
    creditos = models.PositiveIntegerField(default=0, editable=False)
    horas_totales = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="Debe ser mayor a 0.")],
        help_text="Los creditos se calculan automaticamente a partir de las horas totales.",
    )

    class Meta:
        ordering = ["clave", "nombre"]
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        constraints = [
            models.UniqueConstraint(fields=["clave"], name="uq_materia_clave"),
        ]

    @staticmethod
    def calculate_creditos(horas_totales: int) -> int:
        valor = Decimal(horas_totales) * CREDITOS_FACTOR
        return int((valor + CREDITOS_ROUNDING_OFFSET).to_integral_value(rounding=ROUND_FLOOR))

    def clean(self):
        super().clean()
        if self.horas_totales is None or self.horas_totales <= 0:
            raise ValidationError({"horas_totales": "Debe ser mayor a 0."})
        self.creditos = self.calculate_creditos(self.horas_totales)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.clave} - {self.nombre}"


class MateriaPlan(models.Model):
    plan_estudios = models.ForeignKey(
        PlanEstudios,
        on_delete=models.PROTECT,
        related_name="materias_plan",
        verbose_name="Plan de estudio",
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.PROTECT,
        related_name="planes_estudio",
        verbose_name="Materia",
    )
    semestre_numero = models.PositiveSmallIntegerField(default=1, verbose_name="Semestre número")
    anio_escolar_numero = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Año escolar número",
    )
    obligatoria = models.BooleanField(default=True, verbose_name="Obligatoria")

    class Meta:
        ordering = ["plan_estudios__clave", "anio_escolar_numero", "semestre_numero", "materia__clave"]
        verbose_name = "Plan de materia"
        verbose_name_plural = "Planes de materias"
        constraints = [
            models.UniqueConstraint(
                fields=["plan_estudios", "materia"],
                name="uq_materiaplan_plan_materia",
            )
        ]

    def __str__(self) -> str:
        return f"{self.plan_estudios.clave} - {self.materia.clave}"
