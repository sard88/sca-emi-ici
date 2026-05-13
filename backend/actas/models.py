from django.conf import settings
from django.db import models


class ProcesoCierrePeriodo(models.Model):
    ESTADO_BLOQUEADO = "BLOQUEADO"
    ESTADO_CERRADO = "CERRADO"

    ESTADO_CHOICES = [
        (ESTADO_BLOQUEADO, "Bloqueado"),
        (ESTADO_CERRADO, "Cerrado"),
    ]

    periodo = models.ForeignKey(
        "catalogos.PeriodoEscolar",
        on_delete=models.PROTECT,
        related_name="procesos_cierre",
        verbose_name="Periodo académico",
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, verbose_name="Estado")
    ejecutado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="procesos_cierre_periodo",
        verbose_name="Ejecutado por",
    )
    ejecutado_en = models.DateTimeField(auto_now_add=True, verbose_name="Ejecutado en")
    resumen_json = models.JSONField(default=dict, blank=True, verbose_name="Resumen")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        ordering = ["-ejecutado_en"]
        verbose_name = "Proceso de cierre de periodo"
        verbose_name_plural = "Procesos de cierre de periodo"

    def __str__(self):
        return f"{self.periodo} - {self.estado}"


class DetalleCierrePeriodoDiscente(models.Model):
    CLASIFICACION_PROMOVIBLE = "PROMOVIBLE"
    CLASIFICACION_EXTRAORDINARIO_PENDIENTE = "EXTRAORDINARIO_PENDIENTE"
    CLASIFICACION_BAJA_TEMPORAL = "BAJA_TEMPORAL"
    CLASIFICACION_BAJA_DEFINITIVA = "BAJA_DEFINITIVA"
    CLASIFICACION_EGRESABLE = "EGRESABLE"
    CLASIFICACION_NO_PROMOVIBLE = "NO_PROMOVIBLE"

    CLASIFICACION_CHOICES = [
        (CLASIFICACION_PROMOVIBLE, "Promovible"),
        (CLASIFICACION_EXTRAORDINARIO_PENDIENTE, "Extraordinario pendiente"),
        (CLASIFICACION_BAJA_TEMPORAL, "Baja temporal"),
        (CLASIFICACION_BAJA_DEFINITIVA, "Baja definitiva"),
        (CLASIFICACION_EGRESABLE, "Egresable"),
        (CLASIFICACION_NO_PROMOVIBLE, "No promovible"),
    ]

    proceso_cierre = models.ForeignKey(
        ProcesoCierrePeriodo,
        on_delete=models.CASCADE,
        related_name="detalles_discente",
        verbose_name="Proceso de cierre",
    )
    discente = models.ForeignKey(
        "relaciones.Discente",
        on_delete=models.PROTECT,
        related_name="detalles_cierre_periodo",
        verbose_name="Discente",
    )
    grupo_origen = models.ForeignKey(
        "catalogos.GrupoAcademico",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="detalles_cierre_origen",
        verbose_name="Grupo origen",
    )
    clasificacion = models.CharField(
        max_length=40,
        choices=CLASIFICACION_CHOICES,
        verbose_name="Clasificación",
    )
    motivo = models.TextField(blank=True, verbose_name="Motivo")
    promovible = models.BooleanField(default=False, verbose_name="Promovible")
    requiere_extraordinario = models.BooleanField(
        default=False,
        verbose_name="Requiere extraordinario",
    )
    situacion_detectada = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Situación detectada",
    )

    class Meta:
        ordering = ["grupo_origen__clave_grupo", "discente__matricula"]
        verbose_name = "Detalle de cierre por discente"
        verbose_name_plural = "Detalles de cierre por discente"
        constraints = [
            models.UniqueConstraint(
                fields=["proceso_cierre", "discente"],
                name="uq_detalle_cierre_proceso_discente",
            )
        ]

    def __str__(self):
        return f"{self.proceso_cierre} - {self.discente} - {self.clasificacion}"


class ProcesoAperturaPeriodo(models.Model):
    ESTADO_EJECUTADO = "EJECUTADO"
    ESTADO_BLOQUEADO = "BLOQUEADO"

    ESTADO_CHOICES = [
        (ESTADO_EJECUTADO, "Ejecutado"),
        (ESTADO_BLOQUEADO, "Bloqueado"),
    ]

    periodo_origen = models.ForeignKey(
        "catalogos.PeriodoEscolar",
        on_delete=models.PROTECT,
        related_name="procesos_apertura_origen",
        verbose_name="Periodo origen",
    )
    periodo_destino = models.ForeignKey(
        "catalogos.PeriodoEscolar",
        on_delete=models.PROTECT,
        related_name="procesos_apertura_destino",
        verbose_name="Periodo destino",
    )
    ejecutado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="procesos_apertura_periodo",
        verbose_name="Ejecutado por",
    )
    ejecutado_en = models.DateTimeField(auto_now_add=True, verbose_name="Ejecutado en")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, verbose_name="Estado")
    resumen_json = models.JSONField(default=dict, blank=True, verbose_name="Resumen")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        ordering = ["-ejecutado_en"]
        verbose_name = "Proceso de apertura de periodo"
        verbose_name_plural = "Procesos de apertura de periodo"

    def __str__(self):
        return f"{self.periodo_origen} -> {self.periodo_destino} - {self.estado}"
