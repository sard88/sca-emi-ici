# Generated manually for Bloque 9K.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import auditoria.eventos


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BitacoraEventoCritico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username_snapshot", models.CharField(blank=True, max_length=150, verbose_name="Username snapshot")),
                ("nombre_usuario_snapshot", models.CharField(blank=True, max_length=240, verbose_name="Nombre de usuario snapshot")),
                ("rol_contexto", models.CharField(blank=True, max_length=80, verbose_name="Rol de contexto")),
                ("cargo_contexto", models.CharField(blank=True, max_length=120, verbose_name="Cargo de contexto")),
                ("modulo", models.CharField(choices=auditoria.eventos.MODULO_CHOICES, max_length=40, verbose_name="Modulo")),
                ("evento_codigo", models.CharField(choices=auditoria.eventos.EVENTO_CHOICES, max_length=80, verbose_name="Codigo de evento")),
                ("evento_nombre", models.CharField(max_length=180, verbose_name="Nombre de evento")),
                ("severidad", models.CharField(choices=auditoria.eventos.SEVERIDAD_CHOICES, max_length=20, verbose_name="Severidad")),
                ("resultado", models.CharField(choices=auditoria.eventos.RESULTADO_CHOICES, max_length=20, verbose_name="Resultado")),
                ("objeto_tipo", models.CharField(blank=True, max_length=120, verbose_name="Tipo de objeto")),
                ("objeto_id", models.CharField(blank=True, max_length=80, verbose_name="ID de objeto")),
                ("objeto_repr", models.CharField(blank=True, max_length=240, verbose_name="Representacion de objeto")),
                ("estado_anterior", models.CharField(blank=True, max_length=120, verbose_name="Estado anterior")),
                ("estado_nuevo", models.CharField(blank=True, max_length=120, verbose_name="Estado nuevo")),
                ("resumen", models.TextField(verbose_name="Resumen")),
                ("cambios_json", models.JSONField(blank=True, default=dict, verbose_name="Cambios")),
                ("metadatos_json", models.JSONField(blank=True, default=dict, verbose_name="Metadatos")),
                ("request_id", models.CharField(blank=True, max_length=120, verbose_name="Request ID")),
                ("correlacion_id", models.CharField(blank=True, max_length=120, verbose_name="Correlacion ID")),
                ("ip_origen", models.GenericIPAddressField(blank=True, null=True, verbose_name="IP de origen")),
                ("user_agent", models.TextField(blank=True, verbose_name="User agent")),
                ("ruta", models.CharField(blank=True, max_length=500, verbose_name="Ruta")),
                ("metodo_http", models.CharField(blank=True, max_length=12, verbose_name="Metodo HTTP")),
                ("creado_en", models.DateTimeField(auto_now_add=True, verbose_name="Creado en")),
                ("usuario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="bitacora_eventos_criticos", to=settings.AUTH_USER_MODEL, verbose_name="Usuario")),
            ],
            options={
                "verbose_name": "Bitacora de evento critico",
                "verbose_name_plural": "Bitacora de eventos criticos",
                "ordering": ["-creado_en", "-id"],
            },
        ),
        migrations.AddIndex(model_name="bitacoraeventocritico", index=models.Index(fields=["-creado_en"], name="idx_bitacora_fecha")),
        migrations.AddIndex(model_name="bitacoraeventocritico", index=models.Index(fields=["usuario", "-creado_en"], name="idx_bitacora_usuario_fecha")),
        migrations.AddIndex(model_name="bitacoraeventocritico", index=models.Index(fields=["modulo", "-creado_en"], name="idx_bitacora_modulo_fecha")),
        migrations.AddIndex(model_name="bitacoraeventocritico", index=models.Index(fields=["evento_codigo", "-creado_en"], name="idx_bitacora_evento_fecha")),
        migrations.AddIndex(model_name="bitacoraeventocritico", index=models.Index(fields=["resultado", "-creado_en"], name="idx_bitacora_resultado_fecha")),
        migrations.AddIndex(model_name="bitacoraeventocritico", index=models.Index(fields=["objeto_tipo", "objeto_id"], name="idx_bitacora_objeto")),
        migrations.AddIndex(model_name="bitacoraeventocritico", index=models.Index(fields=["ip_origen", "-creado_en"], name="idx_bitacora_ip_fecha")),
    ]
