from datetime import timedelta

from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.test import TestCase
from django.utils import timezone

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
