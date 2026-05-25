from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone

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
        (CORTE_FINAL, "Evaluación final"),
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


class Acta(models.Model):
    ESTADO_BORRADOR_DOCENTE = "BORRADOR_DOCENTE"
    ESTADO_PUBLICADO_DISCENTE = "PUBLICADO_DISCENTE"
    ESTADO_REMITIDO_JEFATURA_CARRERA = "REMITIDO_JEFATURA_CARRERA"
    ESTADO_VALIDADO_JEFATURA_CARRERA = "VALIDADO_JEFATURA_CARRERA"
    ESTADO_FORMALIZADO_JEFATURA_ACADEMICA = "FORMALIZADO_JEFATURA_ACADEMICA"
    ESTADO_ARCHIVADO = "ARCHIVADO"

    ESTADO_ACTA_CHOICES = [
        (ESTADO_BORRADOR_DOCENTE, "Borrador docente"),
        (ESTADO_PUBLICADO_DISCENTE, "Publicado a discentes"),
        (ESTADO_REMITIDO_JEFATURA_CARRERA, "Remitido a jefatura de carrera"),
        (ESTADO_VALIDADO_JEFATURA_CARRERA, "Validado por jefatura de carrera"),
        (ESTADO_FORMALIZADO_JEFATURA_ACADEMICA, "Formalizado por jefatura académica"),
        (ESTADO_ARCHIVADO, "Archivado"),
    ]

    asignacion_docente = models.ForeignKey(
        "relaciones.AsignacionDocente",
        on_delete=models.PROTECT,
        related_name="actas",
        verbose_name="Asignación docente",
    )
    corte_codigo = models.CharField(
        max_length=10,
        choices=ComponenteEvaluacion.CORTE_CHOICES,
        verbose_name="Corte académico",
    )
    estado_acta = models.CharField(
        max_length=40,
        choices=ESTADO_ACTA_CHOICES,
        default=ESTADO_BORRADOR_DOCENTE,
        verbose_name="Estado del acta",
    )
    esquema = models.ForeignKey(
        EsquemaEvaluacion,
        on_delete=models.PROTECT,
        related_name="actas",
        verbose_name="Esquema de evaluación usado",
    )
    esquema_version_snapshot = models.CharField(max_length=20, verbose_name="Versión del esquema")
    peso_parciales_snapshot = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Peso parciales usado",
    )
    peso_final_snapshot = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Peso final usado",
    )
    umbral_exencion_snapshot = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Umbral de exención usado",
    )
    probables_causas_reprobacion = models.TextField(
        blank=True,
        verbose_name="Probables causas de reprobación",
    )
    sugerencias_academicas = models.TextField(
        blank=True,
        verbose_name="Sugerencias académicas",
    )
    publicada_en = models.DateTimeField(null=True, blank=True, verbose_name="Publicada en")
    remitida_en = models.DateTimeField(null=True, blank=True, verbose_name="Remitida en")
    formalizada_en = models.DateTimeField(null=True, blank=True, verbose_name="Formalizada en")
    archivada_en = models.DateTimeField(null=True, blank=True, verbose_name="Archivada en")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="actas_creadas",
        verbose_name="Creado por",
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        ordering = ["-creado_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["asignacion_docente", "corte_codigo"],
                condition=~models.Q(estado_acta="ARCHIVADO"),
                name="uq_acta_activa_asignacion_corte",
            )
        ]
        verbose_name = "Acta"
        verbose_name_plural = "Actas"

    @property
    def es_final(self):
        return self.corte_codigo == ComponenteEvaluacion.CORTE_FINAL

    @property
    def permite_regenerar(self):
        return self.estado_acta == self.ESTADO_BORRADOR_DOCENTE

    @property
    def solo_lectura(self):
        return self.estado_acta in {
            self.ESTADO_REMITIDO_JEFATURA_CARRERA,
            self.ESTADO_VALIDADO_JEFATURA_CARRERA,
            self.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            self.ESTADO_ARCHIVADO,
        }

    def clean(self):
        errors = {}

        if self.esquema_id and self.corte_codigo:
            if self.corte_codigo not in self.esquema.cortes_esperados():
                errors["corte_codigo"] = "El corte no aplica al esquema de evaluación usado."

        if self.asignacion_docente_id and self.esquema_id:
            if self.asignacion_docente.programa_asignatura_id != self.esquema.programa_asignatura_id:
                errors["esquema"] = "El esquema no pertenece al programa de la asignación docente."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.asignacion_docente} - {self.corte_codigo} - {self.estado_acta}"


class DetalleActa(models.Model):
    RESULTADO_INCOMPLETO = "INCOMPLETO"
    RESULTADO_APROBATORIO = "APROBATORIO"
    RESULTADO_REPROBATORIO = "REPROBATORIO"

    acta = models.ForeignKey(
        Acta,
        on_delete=models.CASCADE,
        related_name="detalles",
        verbose_name="Acta",
    )
    inscripcion_materia = models.ForeignKey(
        "relaciones.InscripcionMateria",
        on_delete=models.PROTECT,
        related_name="detalles_acta",
        verbose_name="Inscripción a asignatura",
    )
    resultado_corte = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Resultado del corte",
    )
    resultado_corte_visible = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Resultado visible del corte",
    )
    promedio_parciales = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Promedio de parciales",
    )
    promedio_parciales_visible = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Promedio de parciales visible",
    )
    resultado_final_preliminar = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Resultado final preliminar",
    )
    resultado_final_preliminar_visible = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Resultado final preliminar visible",
    )
    resultado_preliminar = models.CharField(
        max_length=20,
        default=RESULTADO_INCOMPLETO,
        verbose_name="Estado preliminar",
    )
    exencion_aplica = models.BooleanField(default=False, verbose_name="Exención aplicable")
    completo = models.BooleanField(default=False, verbose_name="Completo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        ordering = ["inscripcion_materia__discente__matricula"]
        constraints = [
            models.UniqueConstraint(
                fields=["acta", "inscripcion_materia"],
                name="uq_detalleacta_acta_inscripcion",
            )
        ]
        verbose_name = "Detalle de acta"
        verbose_name_plural = "Detalles de acta"

    def __str__(self):
        return f"{self.acta} - {self.inscripcion_materia}"


class CalificacionComponente(models.Model):
    detalle = models.ForeignKey(
        DetalleActa,
        on_delete=models.CASCADE,
        related_name="calificaciones_componentes",
        verbose_name="Detalle de acta",
    )
    componente = models.ForeignKey(
        ComponenteEvaluacion,
        on_delete=models.PROTECT,
        related_name="calificaciones_acta",
        verbose_name="Componente original",
    )
    componente_nombre_snapshot = models.CharField(
        max_length=120,
        verbose_name="Nombre del componente usado",
    )
    componente_porcentaje_snapshot = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Porcentaje del componente usado",
    )
    componente_es_examen_snapshot = models.BooleanField(
        default=False,
        verbose_name="Era examen final",
    )
    valor_capturado = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Valor capturado",
    )
    valor_calculado = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Valor ponderado",
    )
    sustituido_por_exencion = models.BooleanField(
        default=False,
        verbose_name="Sustituido por exención",
    )

    class Meta:
        ordering = ["componente__orden", "componente_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["detalle", "componente"],
                name="uq_calificacioncomponente_detalle_componente",
            )
        ]
        verbose_name = "Calificación por componente de acta"
        verbose_name_plural = "Calificaciones por componente de acta"

    def clean(self):
        if self.valor_capturado is not None and (
            self.valor_capturado < Decimal("0.0") or self.valor_capturado > Decimal("10.0")
        ):
            raise ValidationError({"valor_capturado": "La calificación debe estar entre 0.0 y 10.0."})

    def __str__(self):
        return f"{self.detalle} - {self.componente_nombre_snapshot}"


class ConformidadDiscente(models.Model):
    ESTADO_ACUSE = "ACUSE"
    ESTADO_CONFORME = "CONFORME"
    ESTADO_INCONFORME = "INCONFORME"

    ESTADO_CONFORMIDAD_CHOICES = [
        (ESTADO_ACUSE, "Acuse de recibo"),
        (ESTADO_CONFORME, "Conforme"),
        (ESTADO_INCONFORME, "Inconforme"),
    ]

    detalle = models.ForeignKey(
        DetalleActa,
        on_delete=models.CASCADE,
        related_name="conformidades",
        verbose_name="Detalle de acta",
    )
    discente = models.ForeignKey(
        "relaciones.Discente",
        on_delete=models.PROTECT,
        related_name="conformidades_acta",
        verbose_name="Discente",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="conformidades_acta",
        verbose_name="Usuario que registra",
    )
    estado_conformidad = models.CharField(
        max_length=20,
        choices=ESTADO_CONFORMIDAD_CHOICES,
        default=ESTADO_ACUSE,
        verbose_name="Conformidad",
    )
    comentario = models.TextField(blank=True, verbose_name="Comentario")
    vigente = models.BooleanField(default=True, verbose_name="Vigente")
    registrado_en = models.DateTimeField(auto_now_add=True, verbose_name="Registrado en")
    invalidado_en = models.DateTimeField(null=True, blank=True, verbose_name="Invalidado en")

    class Meta:
        ordering = ["-registrado_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["detalle", "discente"],
                condition=models.Q(vigente=True),
                name="uq_conformidaddiscente_vigente_detalle_discente",
            )
        ]
        verbose_name = "Conformidad de discente"
        verbose_name_plural = "Conformidades de discentes"

    def clean(self):
        errors = {}
        if self.detalle_id and self.discente_id:
            if self.detalle.inscripcion_materia.discente_id != self.discente_id:
                errors["discente"] = "El discente no corresponde al detalle del acta."

        if (
            self.vigente
            and self.estado_conformidad == self.ESTADO_INCONFORME
            and not (self.comentario or "").strip()
        ):
            errors["comentario"] = (
                "El comentario es obligatorio cuando se registra inconformidad."
            )

        if errors:
            raise ValidationError(errors)

    def invalidar(self):
        self.vigente = False
        self.invalidado_en = timezone.now()
        self.save(update_fields=["vigente", "invalidado_en"])

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.discente} - {self.detalle.acta} - {self.estado_conformidad}"


class ValidacionActa(models.Model):
    ETAPA_JEFATURA_CARRERA = "JEFATURA_CARRERA"
    ETAPA_JEFATURA_ACADEMICA = "JEFATURA_ACADEMICA"
    ETAPA_DOCENTE = "DOCENTE"
    ETAPA_SISTEMA = "SISTEMA"

    ETAPA_VALIDACION_CHOICES = [
        (ETAPA_DOCENTE, "Docente"),
        (ETAPA_JEFATURA_CARRERA, "Jefatura de carrera"),
        (ETAPA_JEFATURA_ACADEMICA, "Jefatura académica"),
        (ETAPA_SISTEMA, "Sistema"),
    ]

    ACCION_PUBLICA = "PUBLICA"
    ACCION_REMITE = "REMITE"
    ACCION_VALIDA = "VALIDA"
    ACCION_FORMALIZA = "FORMALIZA"
    ACCION_ARCHIVA = "ARCHIVA"

    ACCION_CHOICES = [
        (ACCION_PUBLICA, "Publica"),
        (ACCION_REMITE, "Remite"),
        (ACCION_VALIDA, "Valida"),
        (ACCION_FORMALIZA, "Formaliza"),
        (ACCION_ARCHIVA, "Archiva"),
    ]

    acta = models.ForeignKey(
        Acta,
        on_delete=models.CASCADE,
        related_name="validaciones",
        verbose_name="Acta",
    )
    asignacion_cargo = models.ForeignKey(
        "usuarios.AsignacionCargo",
        on_delete=models.PROTECT,
        related_name="validaciones_acta",
        null=True,
        blank=True,
        verbose_name="Asignación de cargo",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="validaciones_acta",
        verbose_name="Usuario",
    )
    etapa_validacion = models.CharField(
        max_length=30,
        choices=ETAPA_VALIDACION_CHOICES,
        verbose_name="Etapa de validación",
    )
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES, verbose_name="Acción")
    fecha_hora = models.DateTimeField(default=timezone.now, verbose_name="Fecha y hora")
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP origen")
    comentario = models.TextField(blank=True, verbose_name="Comentario")

    class Meta:
        ordering = ["-fecha_hora"]
        verbose_name = "Validación de acta"
        verbose_name_plural = "Validaciones de acta"

    def __str__(self):
        return f"{self.acta} - {self.etapa_validacion} - {self.accion}"
