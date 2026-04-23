from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.test import TestCase
from django.utils import timezone

from .admin import UsuarioAdmin
from .models import AsignacionCargo, Usuario


class VigenciaAsignacionCargoTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_vigencia",
            password="segura123",
        )

    def test_creacion_autocompleta_vigente_desde_si_se_omite(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            cargo_codigo="JEFATURA",
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        self.assertEqual(asignacion.vigente_desde, timezone.localdate())
        self.assertIsNone(asignacion.vigente_hasta)

    def test_edicion_respeta_vigente_desde_existente(self):
        fecha_existente = timezone.localdate() - timedelta(days=15)
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            cargo_codigo="DOCENCIA",
            tipo_designacion=AsignacionCargo.DESIGNACION_SUPLENTE,
            vigente_desde=fecha_existente,
        )

        asignacion.activo = False
        asignacion.save()
        asignacion.refresh_from_db()

        self.assertEqual(asignacion.vigente_desde, fecha_existente)

    def test_edicion_de_registro_legado_sin_vigente_desde_lo_autocompleta(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            cargo_codigo="RELACION",
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
        )
        AsignacionCargo.objects.filter(pk=asignacion.pk).update(vigente_desde=None)

        asignacion.refresh_from_db()
        self.assertIsNone(asignacion.vigente_desde)

        asignacion.activo = True
        asignacion.save()
        asignacion.refresh_from_db()

        self.assertEqual(asignacion.vigente_desde, timezone.localdate())

    def test_modelform_no_exige_vigencias_y_autocompleta_vigente_desde(self):
        asignacion_form_class = modelform_factory(
            AsignacionCargo,
            fields=[
                "usuario",
                "cargo_codigo",
                "tipo_designacion",
                "vigente_desde",
                "vigente_hasta",
                "activo",
            ],
        )
        form = asignacion_form_class(
            data={
                "usuario": self.usuario.pk,
                "cargo_codigo": "ADMIN",
                "tipo_designacion": AsignacionCargo.DESIGNACION_TITULAR,
                "vigente_desde": "",
                "vigente_hasta": "",
                "activo": "on",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        asignacion = form.save()

        self.assertEqual(asignacion.vigente_desde, timezone.localdate())
        self.assertIsNone(asignacion.vigente_hasta)

    def test_vigente_hasta_sigue_validando_consistencia_temporal(self):
        hoy = timezone.localdate()
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            cargo_codigo="MANDO",
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            vigente_desde=hoy,
            vigente_hasta=hoy - timedelta(days=1),
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("vigente_hasta", exc.exception.message_dict)


class UsuarioUltimoAccesoTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_acceso",
            password="segura123",
        )

    def test_fechas_de_sistema_no_son_editables_en_modelform(self):
        usuario_form_class = modelform_factory(Usuario, fields="__all__")
        form = usuario_form_class()

        self.assertNotIn("last_login", form.fields)
        self.assertNotIn("date_joined", form.fields)
        self.assertNotIn("ultimo_acceso", form.fields)

    def test_fechas_de_sistema_son_solo_lectura_en_admin_y_no_aparecen_en_alta(self):
        usuario_admin = admin.site._registry[Usuario]

        self.assertIsInstance(usuario_admin, UsuarioAdmin)
        self.assertIn("last_login", usuario_admin.readonly_fields)
        self.assertIn("date_joined", usuario_admin.readonly_fields)
        self.assertIn("ultimo_acceso", usuario_admin.readonly_fields)

        add_fields = [
            field
            for _, fieldset_options in usuario_admin.add_fieldsets
            for field in fieldset_options.get("fields", ())
        ]

        self.assertNotIn("last_login", add_fields)
        self.assertNotIn("date_joined", add_fields)
        self.assertNotIn("ultimo_acceso", add_fields)

    def test_signal_de_login_actualiza_ultimo_acceso(self):
        self.assertIsNone(self.usuario.ultimo_acceso)
        antes = timezone.now()

        user_logged_in.send(
            sender=Usuario,
            request=None,
            user=self.usuario,
        )

        self.usuario.refresh_from_db()

        self.assertIsNotNone(self.usuario.ultimo_acceso)
        self.assertGreaterEqual(self.usuario.ultimo_acceso, antes)
