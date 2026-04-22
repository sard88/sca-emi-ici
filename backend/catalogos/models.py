from django.core.exceptions import ValidationError
from django.db import models

from .validators import CLAVE_MAX_LENGTH, clave_format_validator


ESTADO_ACTIVO = "activo"
ESTADO_INACTIVO = "inactivo"

ESTADO_CHOICES = [
    (ESTADO_ACTIVO, "Activo"),
    (ESTADO_INACTIVO, "Inactivo"),
]

ANIO_ESCOLAR_CHOICES = [
    ("2023-2024", "2023-2024"),
    ("2024-2025", "2024-2025"),
    ("2025-2026", "2025-2026"),
    ("2026-2027", "2026-2027"),
    ("2027-2028", "2027-2028"),
    ("2028-2029", "2028-2029"),
    ("2029-2030", "2029-2030"),
    ("2030-2031", "2030-2031"),
    ("2031-2032", "2031-2032"),
    ("2032-2033", "2032-2033"),
    ("2033-2034", "2033-2034"),
    ("2034-2035", "2034-2035"),
]

SEMESTRE_OPERATIVO_CHOICES = [
    (1, "Primer semestre"),
    (2, "Segundo semestre"),
]


class CatalogoAcademicoBase(models.Model):
    clave = models.CharField(
        max_length=CLAVE_MAX_LENGTH,
        validators=[clave_format_validator],
    )
    nombre = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)
    vigente_desde = models.DateField(null=True, blank=True)
    vigente_hasta = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.vigente_desde and self.vigente_hasta:
            if self.vigente_hasta < self.vigente_desde:
                raise ValidationError(
                    {"vigente_hasta": "No puede ser anterior a 'vigente_desde'."}
                )


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

    def __str__(self) -> str:
        return f"{self.carrera.clave} - {self.clave}"


class Generacion(CatalogoAcademicoBase):
    plan_estudios = models.ForeignKey(
        PlanEstudios,
        on_delete=models.PROTECT,
        related_name="generaciones",
    )
    anio_inicio = models.PositiveSmallIntegerField(null=True, blank=True)
    anio_fin = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-anio_inicio", "clave"]
        verbose_name = "GeneraciÃ³n"
        verbose_name_plural = "Generaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["plan_estudios", "clave"],
                name="uq_generacion_plan_clave",
            )
        ]

    def clean(self):
        super().clean()
        if self.anio_inicio and self.anio_fin and self.anio_fin < self.anio_inicio:
            raise ValidationError({"anio_fin": "No puede ser menor al anio_inicio."})

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
        choices=ANIO_ESCOLAR_CHOICES,
        blank=True,
        default="",
        verbose_name="AÃ±o escolar",
    )
    semestre_operativo = models.PositiveSmallIntegerField(
        choices=SEMESTRE_OPERATIVO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Semestre operativo",
    )
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
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

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({"fecha_fin": "No puede ser anterior a fecha_inicio."})

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
        verbose_name="GeneraciÃ³n",
    )
    periodo = models.ForeignKey(
        PeriodoEscolar,
        on_delete=models.PROTECT,
        related_name="grupos_academicos",
        verbose_name="Periodo escolar",
    )
    semestre_numero = models.PositiveSmallIntegerField(default=1, verbose_name="Semestre nÃºmero")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name="Estado",
    )
    cupo_maximo = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Cupo mÃ¡ximo",
    )

    class Meta:
        ordering = ["periodo__anio_escolar", "periodo__semestre_operativo", "clave_grupo"]
        verbose_name = "Grupo acadÃ©mico"
        verbose_name_plural = "Grupos acadÃ©micos"
        constraints = [
            models.UniqueConstraint(
                fields=["generacion", "periodo", "clave_grupo"],
                name="uq_grupo_generacion_periodo_clave",
            )
        ]

    def __str__(self) -> str:
        return f"{self.periodo.clave} - {self.clave_grupo}"


class Materia(CatalogoAcademicoBase):
    creditos = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_totales = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["clave", "nombre"]
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        constraints = [
            models.UniqueConstraint(fields=["clave"], name="uq_materia_clave"),
        ]

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
    semestre_numero = models.PositiveSmallIntegerField(default=1, verbose_name="Semestre nÃºmero")
    anio_escolar_numero = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="AÃ±o escolar nÃºmero",
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
