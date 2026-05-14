from django.conf import settings
from django.db import models
from django.utils import timezone


class RegistroExportacion(models.Model):
    FORMATO_PDF = "PDF"
    FORMATO_XLSX = "XLSX"
    FORMATO_CSV = "CSV"

    FORMATO_CHOICES = [
        (FORMATO_PDF, "PDF"),
        (FORMATO_XLSX, "Excel XLSX"),
        (FORMATO_CSV, "CSV"),
    ]

    ESTADO_SOLICITADA = "SOLICITADA"
    ESTADO_GENERADA = "GENERADA"
    ESTADO_FALLIDA = "FALLIDA"
    ESTADO_DESCARGADA = "DESCARGADA"

    ESTADO_CHOICES = [
        (ESTADO_SOLICITADA, "Solicitada"),
        (ESTADO_GENERADA, "Generada"),
        (ESTADO_FALLIDA, "Fallida"),
        (ESTADO_DESCARGADA, "Descargada"),
    ]

    TIPO_ACTA_EVALUACION_PARCIAL = "ACTA_EVALUACION_PARCIAL"
    TIPO_ACTA_EVALUACION_FINAL = "ACTA_EVALUACION_FINAL"
    TIPO_ACTA_CALIFICACION_FINAL = "ACTA_CALIFICACION_FINAL"
    TIPO_KARDEX_OFICIAL = "KARDEX_OFICIAL"
    TIPO_HISTORIAL_ACADEMICO = "HISTORIAL_ACADEMICO"
    TIPO_REPORTE_ACTAS_ESTADO = "REPORTE_ACTAS_ESTADO"
    TIPO_REPORTE_ACTAS_PENDIENTES = "REPORTE_ACTAS_PENDIENTES"
    TIPO_REPORTE_INCONFORMIDADES = "REPORTE_INCONFORMIDADES"
    TIPO_REPORTE_ACTAS_SIN_CONFORMIDAD = "REPORTE_ACTAS_SIN_CONFORMIDAD"
    TIPO_REPORTE_ACTAS_FORMALIZADAS = "REPORTE_ACTAS_FORMALIZADAS"
    TIPO_REPORTE_DESEMPENO = "REPORTE_DESEMPENO"
    TIPO_REPORTE_SITUACION_ACADEMICA = "REPORTE_SITUACION_ACADEMICA"
    TIPO_REPORTE_VALIDACIONES_ACTA = "REPORTE_VALIDACIONES_ACTA"
    TIPO_REPORTE_EXPORTACIONES = "REPORTE_EXPORTACIONES"
    TIPO_REPORTE_MOVIMIENTOS_ACADEMICOS = "REPORTE_MOVIMIENTOS_ACADEMICOS"
    TIPO_AUDITORIA_EVENTOS = "AUDITORIA_EVENTOS"
    TIPO_OTRO = "OTRO"

    TIPO_DOCUMENTO_CHOICES = [
        (TIPO_ACTA_EVALUACION_PARCIAL, "Acta de evaluación parcial"),
        (TIPO_ACTA_EVALUACION_FINAL, "Acta de evaluación final"),
        (TIPO_ACTA_CALIFICACION_FINAL, "Acta de calificación final"),
        (TIPO_KARDEX_OFICIAL, "Kárdex oficial"),
        (TIPO_HISTORIAL_ACADEMICO, "Historial académico"),
        (TIPO_REPORTE_ACTAS_ESTADO, "Reporte de actas por estado"),
        (TIPO_REPORTE_ACTAS_PENDIENTES, "Reporte de actas pendientes"),
        (TIPO_REPORTE_INCONFORMIDADES, "Reporte de inconformidades"),
        (TIPO_REPORTE_ACTAS_SIN_CONFORMIDAD, "Reporte de actas sin conformidad"),
        (TIPO_REPORTE_ACTAS_FORMALIZADAS, "Reporte de actas formalizadas"),
        (TIPO_REPORTE_DESEMPENO, "Reporte de desempeño"),
        (TIPO_REPORTE_SITUACION_ACADEMICA, "Reporte de situación académica"),
        (TIPO_REPORTE_VALIDACIONES_ACTA, "Reporte de validaciones de acta"),
        (TIPO_REPORTE_EXPORTACIONES, "Reporte de exportaciones"),
        (TIPO_REPORTE_MOVIMIENTOS_ACADEMICOS, "Reporte de movimientos académicos"),
        (TIPO_AUDITORIA_EVENTOS, "Auditoría de eventos"),
        (TIPO_OTRO, "Otro"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="registros_exportacion",
        verbose_name="Usuario",
    )
    tipo_documento = models.CharField(
        max_length=60,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de documento",
    )
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, verbose_name="Formato")
    nombre_documento = models.CharField(max_length=180, verbose_name="Nombre del documento")
    nombre_archivo = models.CharField(max_length=220, verbose_name="Nombre de archivo")
    objeto_tipo = models.CharField(max_length=120, blank=True, verbose_name="Tipo de objeto")
    objeto_id = models.CharField(max_length=80, blank=True, verbose_name="ID de objeto")
    objeto_repr = models.CharField(max_length=240, blank=True, verbose_name="Representación del objeto")
    filtros_json = models.JSONField(default=dict, blank=True, verbose_name="Filtros")
    parametros_json = models.JSONField(default=dict, blank=True, verbose_name="Parámetros")
    rol_contexto = models.CharField(max_length=80, blank=True, verbose_name="Rol de contexto")
    cargo_contexto = models.CharField(max_length=80, blank=True, verbose_name="Cargo de contexto")
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP de origen")
    user_agent = models.CharField(max_length=300, blank=True, verbose_name="User agent")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_SOLICITADA,
        verbose_name="Estado",
    )
    mensaje_error = models.TextField(blank=True, verbose_name="Mensaje de error")
    tamano_bytes = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="Tamaño en bytes")
    hash_archivo = models.CharField(max_length=128, blank=True, verbose_name="Hash del archivo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    finalizado_en = models.DateTimeField(null=True, blank=True, verbose_name="Finalizado en")

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Registro de exportación"
        verbose_name_plural = "Registros de exportación"
        indexes = [
            models.Index(fields=["usuario", "-creado_en"], name="idx_export_usuario_fecha"),
            models.Index(fields=["tipo_documento", "estado"], name="idx_export_tipo_estado"),
            models.Index(fields=["formato", "-creado_en"], name="idx_export_formato_fecha"),
        ]

    def marcar_generada(self, *, tamano_bytes=None, hash_archivo=""):
        self.estado = self.ESTADO_GENERADA
        self.mensaje_error = ""
        if tamano_bytes is not None:
            self.tamano_bytes = tamano_bytes
        if hash_archivo:
            self.hash_archivo = hash_archivo
        self.finalizado_en = timezone.now()
        self.save(update_fields=["estado", "mensaje_error", "tamano_bytes", "hash_archivo", "finalizado_en"])

    def marcar_fallida(self, mensaje_error):
        self.estado = self.ESTADO_FALLIDA
        self.mensaje_error = str(mensaje_error)[:2000]
        self.finalizado_en = timezone.now()
        self.save(update_fields=["estado", "mensaje_error", "finalizado_en"])

    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.formato} - {self.usuario} - {self.estado}"
