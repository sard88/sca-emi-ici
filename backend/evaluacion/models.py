from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum

from catalogos.models import ESTADO_ACTIVO, ProgramaAsignatura


class EsquemaEvaluacion(models.Model):
    PARCIALES_1 = 1
    PARCIALES_2 = 2
    PARCIALES_3 = 3

    NUM_PARCIALES_CHOICES = [
        (PARCIALES_1, "1 parcial"),
        (PARCIALES_2, "2 parciales"),
        (PARCIALES_3, "3 parciales"),
    ]

    programa_asignatura = models.ForeignKey(
        ProgramaAsignatura,
        on_delete=models.PROTECT,
        db_column="materia_plan_id",
        related_name="esquemas_evaluacion",
        verbose_name="Programa de asignatura",
    )
    version = models.CharField(max_length=20, default="v1", verbose_name="Versión")
    num_parciales = models.PositiveSmallIntegerField(
        choices=NUM_PARCIALES_CHOICES,
        default=PARCIALES_2,
        verbose_name="Número de parciales",
    )
    permite_exencion = models.BooleanField(default=False, verbose_name="Permite exención")
    peso_parciales = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("45.00"),
        verbose_name="Peso parciales",
    )
    peso_final = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("55.00"),
        verbose_name="Peso final",
    )
    umbral_exencion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("9.00"),
        verbose_name="Umbral de exención",
        help_text="Calificación mínima para exentar en escala de 0 a 10.",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Disponible para evaluación",
        help_text=(
            "Indica si este esquema puede usarse en actas y cálculos. "
            "Si se desactiva, queda solo para consulta histórica."
        ),
    )

    class Meta:
        ordering = [
            "-activo",
            "programa_asignatura__plan_estudios__clave",
            "programa_asignatura__materia__clave",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["programa_asignatura", "version"],
                name="uq_esquemaevaluacion_materiaplan_version",
            )
        ]
        verbose_name = "Esquema de evaluación"
        verbose_name_plural = "Esquemas de evaluación"

    def cortes_esperados(self):
        cortes = ["P1"]
        if self.num_parciales >= self.PARCIALES_2:
            cortes.append("P2")
        if self.num_parciales >= self.PARCIALES_3:
            cortes.append("P3")
        cortes.append("FINAL")
        return cortes

    def validar_componentes_por_corte(self):
        sumas = (
            self.componentes.values("corte_codigo")
            .annotate(total=Sum("porcentaje"))
            .order_by("corte_codigo")
        )
        totales = {item["corte_codigo"]: item["total"] or Decimal("0.00") for item in sumas}

        errores = {}
        for corte in self.cortes_esperados():
            total = totales.get(corte, Decimal("0.00"))
            if total != Decimal("100.00"):
                errores[corte] = (
                    f"La suma de porcentajes del corte {corte} debe ser 100 "
                    f"(actual: {total})."
                )

        if self.num_parciales == self.PARCIALES_1 and not self.componentes.filter(
            corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
            es_examen=True,
        ).exists():
            errores["FINAL"] = "En materias de 1 parcial, el examen final es obligatorio."

        if errores:
            raise ValidationError(list(errores.values()))

    def programa_asignatura_activo(self):
        if not self.programa_asignatura_id:
            return True

        return (
            self.programa_asignatura.plan_estudios.estado == ESTADO_ACTIVO
            and self.programa_asignatura.materia.estado == ESTADO_ACTIVO
        )

    def clean(self):
        if self.num_parciales not in (self.PARCIALES_1, self.PARCIALES_2, self.PARCIALES_3):
            raise ValidationError({"num_parciales": "Solo se permiten 1, 2 o 3 parciales."})

        if self.programa_asignatura_id and not self.programa_asignatura_activo():
            raise ValidationError(
                {"programa_asignatura": "Solo se puede asignar un programa de asignatura activo."}
            )

        total = (self.peso_parciales or Decimal("0.00")) + (self.peso_final or Decimal("0.00"))
        if total != Decimal("100.00"):
            raise ValidationError(
                {"peso_final": "La suma de peso_parciales y peso_final debe ser 100."}
            )

        if self.permite_exencion and self.num_parciales == self.PARCIALES_1:
            raise ValidationError(
                {
                    "permite_exencion": (
                        "La exención solo aplica cuando la materia opera con 2 o 3 parciales."
                    )
                }
            )

        if self.umbral_exencion < Decimal("0.00") or self.umbral_exencion > Decimal("10.00"):
            raise ValidationError(
                {"umbral_exencion": "El umbral de exención debe estar entre 0 y 10."}
            )

    def __str__(self):
        return f"{self.programa_asignatura} - {self.version}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ComponenteEvaluacion(models.Model):
    CORTE_P1 = "P1"
    CORTE_P2 = "P2"
    CORTE_P3 = "P3"
    CORTE_FINAL = "FINAL"

    CORTE_CHOICES = [
        (CORTE_P1, "Parcial 1"),
        (CORTE_P2, "Parcial 2"),
        (CORTE_P3, "Parcial 3"),
        (CORTE_FINAL, "Final"),
    ]

    esquema = models.ForeignKey(
        EsquemaEvaluacion,
        on_delete=models.CASCADE,
        related_name="componentes",
        verbose_name="Esquema",
    )
    corte_codigo = models.CharField(max_length=10, choices=CORTE_CHOICES, verbose_name="Corte")
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje")
    es_examen = models.BooleanField(default=False, verbose_name="Es examen")
    orden = models.PositiveSmallIntegerField(default=1, verbose_name="Orden")

    class Meta:
        ordering = ["esquema", "corte_codigo", "orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["esquema", "corte_codigo", "orden"],
                name="uq_componenteevaluacion_esquema_corte_orden",
            )
        ]
        verbose_name = "Componente de evaluación"
        verbose_name_plural = "Componentes de evaluación"

    def clean(self):
        if self.porcentaje is not None and (
            self.porcentaje <= Decimal("0.00") or self.porcentaje > Decimal("100.00")
        ):
            raise ValidationError({"porcentaje": "El porcentaje debe estar entre 0 y 100."})

        if self.esquema_id and self.corte_codigo:
            cortes_validos = self.esquema.cortes_esperados()
            if self.corte_codigo not in cortes_validos:
                raise ValidationError(
                    {"corte_codigo": f"El corte {self.corte_codigo} no aplica a este esquema."}
                )

        if self.es_examen and self.corte_codigo and self.corte_codigo != self.CORTE_FINAL:
            raise ValidationError(
                {"es_examen": "El componente de examen debe pertenecer al corte FINAL."}
            )

    def __str__(self):
        return f"{self.esquema} - {self.corte_codigo} - {self.nombre}"


class CapturaCalificacionPreliminar(models.Model):
    inscripcion_materia = models.ForeignKey(
        "relaciones.InscripcionMateria",
        on_delete=models.PROTECT,
        related_name="capturas_preliminares",
        verbose_name="Inscripción a asignatura",
    )
    componente = models.ForeignKey(
        ComponenteEvaluacion,
        on_delete=models.PROTECT,
        related_name="capturas_preliminares",
        verbose_name="Componente de evaluación",
    )
    corte_codigo = models.CharField(
        max_length=10,
        choices=ComponenteEvaluacion.CORTE_CHOICES,
        editable=False,
        verbose_name="Corte académico",
    )
    valor = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.0"), message="La calificación mínima es 0.0."),
            MaxValueValidator(Decimal("10.0"), message="La calificación máxima es 10.0."),
        ],
        verbose_name="Valor capturado",
    )
    capturado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="capturas_calificacion_preliminar",
        verbose_name="Usuario que captura",
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de captura")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        ordering = [
            "inscripcion_materia__discente__matricula",
            "corte_codigo",
            "componente__orden",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["inscripcion_materia", "componente"],
                name="uq_capturacalificacionpreliminar_inscripcion_componente",
            )
        ]
        verbose_name = "Captura preliminar de calificación"
        verbose_name_plural = "Capturas preliminares de calificaciones"

    def clean(self):
        errors = {}

        if self.componente_id:
            self.corte_codigo = self.componente.corte_codigo

            if not self.componente.esquema.activo:
                errors["componente"] = "Solo se puede capturar con un esquema de evaluación activo."

        if self.valor is not None and (
            self.valor < Decimal("0.0") or self.valor > Decimal("10.0")
        ):
            errors["valor"] = "La calificación debe estar entre 0.0 y 10.0."

        if self.inscripcion_materia_id and self.componente_id:
            programa_inscripcion_id = (
                self.inscripcion_materia.asignacion_docente.programa_asignatura_id
            )
            programa_componente_id = self.componente.esquema.programa_asignatura_id
            if programa_inscripcion_id != programa_componente_id:
                errors["componente"] = (
                    "El componente no pertenece al programa de asignatura de la inscripción."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.inscripcion_materia} - {self.componente}: {self.valor}"
