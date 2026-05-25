from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class NotificacionUsuario(models.Model):
    TIPO_INFO = "INFO"
    TIPO_ACTA = "ACTA"
    TIPO_VALIDACION = "VALIDACION"
    TIPO_PERIODO = "PERIODO"
    TIPO_TRAYECTORIA = "TRAYECTORIA"
    TIPO_SISTEMA = "SISTEMA"

    TIPO_CHOICES = [
        (TIPO_INFO, "Información"),
        (TIPO_ACTA, "Acta"),
        (TIPO_VALIDACION, "Validación"),
        (TIPO_PERIODO, "Periodo"),
        (TIPO_TRAYECTORIA, "Trayectoria"),
        (TIPO_SISTEMA, "Sistema"),
    ]

    PRIORIDAD_BAJA = "BAJA"
    PRIORIDAD_NORMAL = "NORMAL"
    PRIORIDAD_ALTA = "ALTA"
    PRIORIDAD_CRITICA = "CRITICA"

    PRIORIDAD_CHOICES = [
        (PRIORIDAD_BAJA, "Baja"),
        (PRIORIDAD_NORMAL, "Normal"),
        (PRIORIDAD_ALTA, "Alta"),
        (PRIORIDAD_CRITICA, "Crítica"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones_portal",
        verbose_name="Usuario",
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default=TIPO_INFO, verbose_name="Tipo")
    titulo = models.CharField(max_length=160, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    url_destino = models.CharField(max_length=300, blank=True, verbose_name="URL destino")
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default=PRIORIDAD_NORMAL,
        verbose_name="Prioridad",
    )
    leida = models.BooleanField(default=False, verbose_name="Leída")
    creada_en = models.DateTimeField(auto_now_add=True, verbose_name="Creada en")
    leida_en = models.DateTimeField(null=True, blank=True, verbose_name="Leída en")

    class Meta:
        ordering = ["-creada_en"]
        verbose_name = "Notificación de usuario"
        verbose_name_plural = "Notificaciones de usuario"
        indexes = [
            models.Index(fields=["usuario", "leida", "-creada_en"], name="idx_notif_usuario_leida"),
        ]

    def marcar_leida(self):
        if not self.leida:
            self.leida = True
            self.leida_en = timezone.now()
            self.save(update_fields=["leida", "leida_en"])

    def __str__(self):
        return f"{self.usuario} - {self.titulo}"


class EventoCalendarioInstitucional(models.Model):
    TIPO_INICIO_PERIODO = "INICIO_PERIODO"
    TIPO_CIERRE_CAPTURA = "CIERRE_CAPTURA"
    TIPO_PUBLICACION_ACTA = "PUBLICACION_ACTA"
    TIPO_VALIDACION_ACTA = "VALIDACION_ACTA"
    TIPO_CIERRE_PERIODO = "CIERRE_PERIODO"
    TIPO_APERTURA_PERIODO = "APERTURA_PERIODO"
    TIPO_EXTRAORDINARIO = "EXTRAORDINARIO"
    TIPO_REINGRESO = "REINGRESO"
    TIPO_EVENTO_INSTITUCIONAL = "EVENTO_INSTITUCIONAL"

    TIPO_EVENTO_CHOICES = [
        (TIPO_INICIO_PERIODO, "Inicio de periodo"),
        (TIPO_CIERRE_CAPTURA, "Cierre de captura"),
        (TIPO_PUBLICACION_ACTA, "Publicación de acta"),
        (TIPO_VALIDACION_ACTA, "Validación de acta"),
        (TIPO_CIERRE_PERIODO, "Cierre de periodo"),
        (TIPO_APERTURA_PERIODO, "Apertura de periodo"),
        (TIPO_EXTRAORDINARIO, "Extraordinario"),
        (TIPO_REINGRESO, "Reingreso"),
        (TIPO_EVENTO_INSTITUCIONAL, "Evento institucional"),
    ]

    titulo = models.CharField(max_length=180, verbose_name="Título")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    tipo_evento = models.CharField(
        max_length=40,
        choices=TIPO_EVENTO_CHOICES,
        default=TIPO_EVENTO_INSTITUCIONAL,
        verbose_name="Tipo de evento",
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    periodo = models.ForeignKey(
        "catalogos.PeriodoEscolar",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_calendario",
        verbose_name="Periodo académico",
    )
    carrera = models.ForeignKey(
        "catalogos.Carrera",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_calendario",
        verbose_name="Carrera",
    )
    grupo = models.ForeignKey(
        "catalogos.GrupoAcademico",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_calendario",
        verbose_name="Grupo académico",
    )
    roles_destino = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Roles destino",
        help_text="Lista opcional de roles/cargos destino. Vacío significa evento general.",
    )
    url_destino = models.CharField(max_length=300, blank=True, verbose_name="URL destino")
    visible = models.BooleanField(default=True, verbose_name="Visible")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_calendario_creados",
        verbose_name="Creado por",
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    class Meta:
        ordering = ["fecha_inicio", "titulo"]
        verbose_name = "Evento de calendario institucional"
        verbose_name_plural = "Eventos de calendario institucional"
        indexes = [
            models.Index(fields=["visible", "fecha_inicio"], name="idx_evento_visible_fecha"),
        ]

    def clean(self):
        errors = {}
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            errors["fecha_fin"] = "No puede ser anterior a fecha_inicio."
        if self.grupo_id:
            if self.periodo_id and self.grupo.periodo_id != self.periodo_id:
                errors["grupo"] = "El grupo debe pertenecer al periodo seleccionado."
            carrera_grupo = self.grupo.antiguedad.plan_estudios.carrera
            carrera_grupo_id = getattr(carrera_grupo, "id", None)
            if self.carrera_id and carrera_grupo_id and carrera_grupo_id != self.carrera_id:
                errors["carrera"] = "La carrera debe coincidir con la carrera del grupo."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha_inicio} - {self.titulo}"


class AccesoRapidoUsuario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accesos_rapidos_portal",
        verbose_name="Usuario",
    )
    etiqueta = models.CharField(max_length=120, verbose_name="Etiqueta")
    url = models.CharField(max_length=300, verbose_name="URL")
    icono = models.CharField(max_length=60, blank=True, verbose_name="Icono")
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    class Meta:
        ordering = ["orden", "etiqueta"]
        verbose_name = "Acceso rápido de usuario"
        verbose_name_plural = "Accesos rápidos de usuario"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "url"],
                condition=models.Q(activo=True),
                name="uq_acceso_rapido_activo_usuario_url",
            )
        ]

    def __str__(self):
        return f"{self.usuario} - {self.etiqueta}"
