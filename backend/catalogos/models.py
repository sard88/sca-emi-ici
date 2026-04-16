from django.core.exceptions import ValidationError
from django.db import models


ESTADO_ACTIVO = "activo"
ESTADO_INACTIVO = "inactivo"

ESTADO_CHOICES = [
    (ESTADO_ACTIVO, "Activo"),
    (ESTADO_INACTIVO, "Inactivo"),
]


class CatalogoAcademicoBase(models.Model):
    clave = models.CharField(max_length=30)
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


class PeriodoEscolar(CatalogoAcademicoBase):
    class Meta:
        ordering = ["-vigente_desde", "clave"]
        constraints = [
            models.UniqueConstraint(fields=["clave"], name="uq_periodoescolar_clave"),
        ]

    def __str__(self) -> str:
        return f"{self.clave} - {self.nombre}"


class GrupoAcademico(CatalogoAcademicoBase):
    TURNO_MATUTINO = "matutino"
    TURNO_VESPERTINO = "vespertino"
    TURNO_NOCTURNO = "nocturno"

    TURNO_CHOICES = [
        (TURNO_MATUTINO, "Matutino"),
        (TURNO_VESPERTINO, "Vespertino"),
        (TURNO_NOCTURNO, "Nocturno"),
    ]

    generacion = models.ForeignKey(
        Generacion,
        on_delete=models.PROTECT,
        related_name="grupos_academicos",
    )
    periodo_escolar = models.ForeignKey(
        PeriodoEscolar,
        on_delete=models.PROTECT,
        related_name="grupos_academicos",
    )
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, default=TURNO_MATUTINO)
    cupo_maximo = models.PositiveIntegerField(default=40)

    class Meta:
        ordering = ["periodo_escolar__clave", "clave"]
        constraints = [
            models.UniqueConstraint(
                fields=["generacion", "periodo_escolar", "clave"],
                name="uq_grupo_generacion_periodo_clave",
            )
        ]

    def __str__(self) -> str:
        return f"{self.periodo_escolar.clave} - {self.clave}"


class Materia(CatalogoAcademicoBase):
    creditos = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_totales = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["clave", "nombre"]
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
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.PROTECT,
        related_name="planes_estudio",
    )
    semestre = models.PositiveSmallIntegerField(default=1)
    orden_malla = models.PositiveIntegerField(default=1)
    obligatoria = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)
    vigente_desde = models.DateField(null=True, blank=True)
    vigente_hasta = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["plan_estudios__clave", "orden_malla", "materia__clave"]
        constraints = [
            models.UniqueConstraint(
                fields=["plan_estudios", "materia"],
                name="uq_materiaplan_plan_materia",
            )
        ]

    def clean(self):
        if self.vigente_desde and self.vigente_hasta:
            if self.vigente_hasta < self.vigente_desde:
                raise ValidationError(
                    {"vigente_hasta": "No puede ser anterior a 'vigente_desde'."}
                )

    def __str__(self) -> str:
        return f"{self.plan_estudios.clave} - {self.materia.clave}"
