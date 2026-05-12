from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from catalogos.models import PeriodoEscolar
from relaciones.models import Discente, InscripcionMateria


CALIFICACION_APROBATORIA = Decimal("6.0")


class CatalogoSituacionAcademica(models.Model):
    CLAVE_ACTIVO = "ACTIVO"
    CLAVE_BAJA_TEMPORAL = "BAJA_TEMPORAL"
    CLAVE_BAJA_DEFINITIVA = "BAJA_DEFINITIVA"
    CLAVE_REINGRESO = "REINGRESO"
    CLAVE_EGRESADO = "EGRESADO"

    clave = models.CharField(max_length=40, unique=True, verbose_name="Clave")
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ["clave"]
        verbose_name = "Situación académica"
        verbose_name_plural = "Situaciones académicas"

    def __str__(self):
        return self.nombre


class CatalogoResultadoAcademico(models.Model):
    CLAVE_APROBADO = "APROBADO"
    CLAVE_REPROBADO = "REPROBADO"
    CLAVE_APROBADO_EXTRAORDINARIO = "APROBADO_EXTRAORDINARIO"
    CLAVE_EE = "EE"
    CLAVE_ACREDITADA = "ACREDITADA"
    CLAVE_APROBADO_NO_NUMERICO = "APROBADO_NO_NUMERICO"
    CLAVE_EXCEPTUADO = "EXCEPTUADO"

    clave = models.CharField(max_length=40, unique=True, verbose_name="Clave")
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ["clave"]
        verbose_name = "Resultado académico"
        verbose_name_plural = "Resultados académicos"

    def __str__(self):
        return self.nombre


class EventoSituacionAcademica(models.Model):
    discente = models.ForeignKey(
        Discente,
        on_delete=models.PROTECT,
        related_name="eventos_situacion",
        verbose_name="Discente",
    )
    situacion = models.ForeignKey(
        CatalogoSituacionAcademica,
        on_delete=models.PROTECT,
        related_name="eventos",
        verbose_name="Situación",
    )
    fecha_inicio = models.DateField(default=timezone.localdate, verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    periodo = models.ForeignKey(
        PeriodoEscolar,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_situacion_academica",
        verbose_name="Periodo académico",
    )
    motivo = models.TextField(blank=True, verbose_name="Motivo")
    inscripcion_materia = models.ForeignKey(
        InscripcionMateria,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_situacion_academica",
        verbose_name="Inscripción relacionada",
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_situacion_registrados",
        verbose_name="Registrado por",
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        ordering = ["discente__matricula", "-fecha_inicio", "-creado_en"]
        verbose_name = "Evento de situación académica"
        verbose_name_plural = "Eventos de situación académica"

    def clean(self):
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({"fecha_fin": "No puede ser anterior a la fecha de inicio."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.discente} - {self.situacion} - {self.fecha_inicio}"


def inscripcion_tiene_acta_final_formalizada(inscripcion):
    from evaluacion.models import Acta, ComponenteEvaluacion, DetalleActa

    return DetalleActa.objects.filter(
        inscripcion_materia=inscripcion,
        acta__corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
        acta__estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
    ).exists()


class Extraordinario(models.Model):
    inscripcion_materia = models.OneToOneField(
        InscripcionMateria,
        on_delete=models.PROTECT,
        related_name="extraordinario",
        verbose_name="Inscripción a asignatura",
    )
    fecha_aplicacion = models.DateField(default=timezone.localdate, verbose_name="Fecha de aplicación")
    calificacion = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("10.0"))],
        verbose_name="Calificación",
    )
    aprobado = models.BooleanField(default=False, editable=False, verbose_name="Aprobado")
    codigo_resultado_oficial = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Código de resultado oficial",
    )
    codigo_marca = models.CharField(max_length=20, blank=True, verbose_name="Código de marca")
    calificacion_ordinaria = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Calificación ordinaria preservada",
    )
    codigo_resultado_ordinario = models.CharField(
        max_length=40,
        blank=True,
        editable=False,
        verbose_name="Resultado ordinario preservado",
    )
    codigo_marca_ordinaria = models.CharField(
        max_length=20,
        blank=True,
        editable=False,
        verbose_name="Marca ordinaria preservada",
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="extraordinarios_registrados",
        verbose_name="Registrado por",
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        ordering = ["-fecha_aplicacion", "inscripcion_materia__discente__matricula"]
        verbose_name = "Extraordinario"
        verbose_name_plural = "Extraordinarios"

    def _preservar_resultado_ordinario(self):
        inscripcion = self.inscripcion_materia
        if self.calificacion_ordinaria is None:
            self.calificacion_ordinaria = inscripcion.calificacion_final
        if not self.codigo_resultado_ordinario:
            self.codigo_resultado_ordinario = inscripcion.codigo_resultado_oficial or ""
        if not self.codigo_marca_ordinaria:
            self.codigo_marca_ordinaria = inscripcion.codigo_marca or ""

    def clean(self):
        errors = {}

        if self.calificacion is not None and (
            self.calificacion < Decimal("0.0") or self.calificacion > Decimal("10.0")
        ):
            errors["calificacion"] = "La calificación debe estar entre 0.0 y 10.0."

        if self.inscripcion_materia_id:
            inscripcion = self.inscripcion_materia
            if not inscripcion_tiene_acta_final_formalizada(inscripcion):
                errors["inscripcion_materia"] = (
                    "Solo se permite extraordinario si existe acta FINAL formalizada."
                )
            elif inscripcion.calificacion_final is None:
                errors["inscripcion_materia"] = "La inscripción no tiene resultado ordinario consolidado."
            elif not self.pk and inscripcion.calificacion_final >= CALIFICACION_APROBATORIA:
                errors["inscripcion_materia"] = (
                    "Solo se permite extraordinario con resultado ordinario reprobatorio menor a 6.0."
                )
            elif not self.pk:
                self._preservar_resultado_ordinario()

        if self.calificacion is not None:
            self.aprobado = self.calificacion >= CALIFICACION_APROBATORIA
            if self.aprobado:
                self.codigo_resultado_oficial = CatalogoResultadoAcademico.CLAVE_APROBADO_EXTRAORDINARIO
                self.codigo_marca = CatalogoResultadoAcademico.CLAVE_EE
            else:
                self.codigo_resultado_oficial = CatalogoResultadoAcademico.CLAVE_REPROBADO
                self.codigo_marca = ""

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.inscripcion_materia} - Extraordinario {self.calificacion}"
