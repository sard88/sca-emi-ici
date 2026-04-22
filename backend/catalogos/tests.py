from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.test import TestCase

from .models import (
    Carrera,
    Generacion,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
)
from .validators import CLAVE_FORMAT_MESSAGE, CLAVE_MAX_LENGTH


class ClaveCatalogosValidationTests(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(clave="BASE_2025", nombre="Ingenieria en Computacion")
        self.plan = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="PLAN-2025_A",
            nombre="Plan 2025",
        )
        self.generacion = Generacion.objects.create(
            plan_estudios=self.plan,
            clave="GEN_2025",
            nombre="Generacion 2025",
            anio_inicio=2025,
            anio_fin=2029,
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="PERIODO_2025-1",
            anio_escolar="2025-2026",
            semestre_operativo=1,
        )

    def _build_instances(self, value):
        return [
            Carrera(clave=value, nombre="Carrera prueba"),
            PlanEstudios(carrera=self.carrera, clave=value, nombre="Plan prueba"),
            Generacion(
                plan_estudios=self.plan,
                clave=value,
                nombre="Generacion prueba",
                anio_inicio=2025,
                anio_fin=2029,
            ),
            PeriodoEscolar(
                clave=value,
                anio_escolar="2025-2026",
                semestre_operativo=1,
            ),
            GrupoAcademico(
                clave_grupo=value,
                generacion=self.generacion,
                periodo=self.periodo,
                semestre_numero=1,
            ),
            Materia(clave=value, nombre="Materia prueba"),
        ]

    def test_backend_accepts_valid_key_formats(self):
        valid_values = ["ICI_2025", "MATE-2023-G1", "ABC123", "grupo_1"]

        for value in valid_values:
            for instance in self._build_instances(value):
                with self.subTest(model=instance.__class__.__name__, value=value):
                    instance.full_clean()

    def test_backend_rejects_invalid_special_characters(self):
        invalid_values = ["ICI 2025", "MATE/2023", "CLAVE#1", "G-ICI- B"]

        for value in invalid_values:
            for instance in self._build_instances(value):
                field_name = "clave_grupo" if hasattr(instance, "clave_grupo") else "clave"
                with self.subTest(model=instance.__class__.__name__, value=value):
                    with self.assertRaises(ValidationError) as exc:
                        instance.full_clean()
                    self.assertIn(field_name, exc.exception.message_dict)
                    self.assertIn(CLAVE_FORMAT_MESSAGE, exc.exception.message_dict[field_name])

    def test_backend_rejects_keys_longer_than_20_characters(self):
        value = "ABCDEFGHIJKLMNOPQRSTU"

        for instance in self._build_instances(value):
            field_name = "clave_grupo" if hasattr(instance, "clave_grupo") else "clave"
            with self.subTest(model=instance.__class__.__name__):
                with self.assertRaises(ValidationError) as exc:
                    instance.full_clean()
                self.assertIn(field_name, exc.exception.message_dict)
                self.assertTrue(
                    any(str(CLAVE_MAX_LENGTH) in message for message in exc.exception.message_dict[field_name])
                )

    def test_modelform_rejects_invalid_clave_value(self):
        carrera_form_class = modelform_factory(Carrera, fields=["clave", "nombre", "estado"])
        form = carrera_form_class(
            data={
                "clave": "ICI 2025",
                "nombre": "Carrera prueba",
                "estado": "activo",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("clave", form.errors)
        self.assertIn(CLAVE_FORMAT_MESSAGE, form.errors["clave"])

    def test_modelform_rejects_invalid_clave_grupo_value(self):
        grupo_form_class = modelform_factory(
            GrupoAcademico,
            fields=["clave_grupo", "generacion", "periodo", "semestre_numero", "estado", "cupo_maximo"],
        )
        form = grupo_form_class(
            data={
                "clave_grupo": "GRUPO/01",
                "generacion": self.generacion.pk,
                "periodo": self.periodo.pk,
                "semestre_numero": 1,
                "estado": "activo",
                "cupo_maximo": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("clave_grupo", form.errors)
        self.assertIn(CLAVE_FORMAT_MESSAGE, form.errors["clave_grupo"])


class AntiguedadUiLabelTests(TestCase):
    def test_generacion_model_uses_antiguedad_labels(self):
        self.assertEqual(Generacion._meta.verbose_name, "Antigüedad")
        self.assertEqual(Generacion._meta.verbose_name_plural, "Antigüedades")

    def test_grupo_academico_form_uses_antiguedad_field_label(self):
        grupo_form_class = modelform_factory(
            GrupoAcademico,
            fields=["clave_grupo", "generacion", "periodo", "semestre_numero", "estado", "cupo_maximo"],
        )
        form = grupo_form_class()

        self.assertEqual(form.fields["generacion"].label, "Antigüedad")

