from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .eventos import EVENTO_CHOICES, MODULO_CHOICES, RESULTADO_CHOICES, SEVERIDAD_CHOICES


class BitacoraEventoCritico(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="bitacora_eventos_criticos",
        verbose_name="Usuario",
    )
    username_snapshot = models.CharField(max_length=150, blank=True, verbose_name="Username snapshot")
    nombre_usuario_snapshot = models.CharField(max_length=240, blank=True, verbose_name="Nombre de usuario snapshot")
    rol_contexto = models.CharField(max_length=80, blank=True, verbose_name="Rol de contexto")
    cargo_contexto = models.CharField(max_length=120, blank=True, verbose_name="Cargo de contexto")
    modulo = models.CharField(max_length=40, choices=MODULO_CHOICES, verbose_name="Modulo")
    evento_codigo = models.CharField(max_length=80, choices=EVENTO_CHOICES, verbose_name="Codigo de evento")
    evento_nombre = models.CharField(max_length=180, verbose_name="Nombre de evento")
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES, verbose_name="Severidad")
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, verbose_name="Resultado")
    objeto_tipo = models.CharField(max_length=120, blank=True, verbose_name="Tipo de objeto")
    objeto_id = models.CharField(max_length=80, blank=True, verbose_name="ID de objeto")
    objeto_repr = models.CharField(max_length=240, blank=True, verbose_name="Representacion de objeto")
    estado_anterior = models.CharField(max_length=120, blank=True, verbose_name="Estado anterior")
    estado_nuevo = models.CharField(max_length=120, blank=True, verbose_name="Estado nuevo")
    resumen = models.TextField(verbose_name="Resumen")
    cambios_json = models.JSONField(default=dict, blank=True, verbose_name="Cambios")
    metadatos_json = models.JSONField(default=dict, blank=True, verbose_name="Metadatos")
    request_id = models.CharField(max_length=120, blank=True, verbose_name="Request ID")
    correlacion_id = models.CharField(max_length=120, blank=True, verbose_name="Correlacion ID")
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP de origen")
    user_agent = models.TextField(blank=True, verbose_name="User agent")
    ruta = models.CharField(max_length=500, blank=True, verbose_name="Ruta")
    metodo_http = models.CharField(max_length=12, blank=True, verbose_name="Metodo HTTP")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    class Meta:
        ordering = ["-creado_en", "-id"]
        verbose_name = "Bitacora de evento critico"
        verbose_name_plural = "Bitacora de eventos criticos"
        indexes = [
            models.Index(fields=["-creado_en"], name="idx_bitacora_fecha"),
            models.Index(fields=["usuario", "-creado_en"], name="idx_bitacora_usuario_fecha"),
            models.Index(fields=["modulo", "-creado_en"], name="idx_bitacora_modulo_fecha"),
            models.Index(fields=["evento_codigo", "-creado_en"], name="idx_bitacora_evento_fecha"),
            models.Index(fields=["resultado", "-creado_en"], name="idx_bitacora_resultado_fecha"),
            models.Index(fields=["objeto_tipo", "objeto_id"], name="idx_bitacora_objeto"),
            models.Index(fields=["ip_origen", "-creado_en"], name="idx_bitacora_ip_fecha"),
        ]

    def save(self, *args, **kwargs):
        if self.pk and not self._state.adding:
            raise ValidationError("La bitacora de eventos criticos es append-only; registre un nuevo evento.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("La bitacora de eventos criticos es append-only; no admite eliminacion ordinaria.")

    def __str__(self):
        usuario = self.username_snapshot or "anonimo"
        objeto = f"{self.objeto_tipo}:{self.objeto_id}" if self.objeto_tipo or self.objeto_id else "sin objeto"
        fecha = self.creado_en.isoformat() if self.creado_en else "sin fecha"
        return f"{fecha} - {self.evento_codigo} - {usuario} - {objeto}"
