from django.forms.formsets import DELETION_FIELD_NAME
from django.contrib import admin
from django.forms import inlineformset_factory
from django.test import TestCase
from django.core.exceptions import ValidationError

from catalogos.models import Carrera, Materia, PlanEstudios, ProgramaAsignatura
from evaluacion.admin import (
    ComponenteEvaluacionInline,
    ComponenteEvaluacionInlineFormSet,
    EsquemaEvaluacionAdmin,
)
from evaluacion.forms import EsquemaEvaluacionAdminForm
from evaluacion.models import ComponenteEvaluacion, EsquemaEvaluacion


class EsquemaEvaluacionTestCase(TestCase):
    def setUp(self):
        carrera = Carrera.objects.create(clave="ICI", nombre="Ingeniería en Computación e Informática")
        plan = PlanEstudios.objects.create(
            carrera=carrera,
            clave="PLAN-ICI-2026",
            nombre="Plan ICI 2026",
        )
        materia = Materia.objects.create(clave="MAT101", nombre="Matemática 1", horas_totales=64)
        self.programa_asignatura = ProgramaAsignatura.objects.create(
            plan_estudios=plan,
            materia=materia,
            semestre_numero=1,
            anio_formacion=1,
            obligatoria=True,
        )

    def test_permite_esquemas_con_1_2_y_3_parciales(self):
        for num in [1, 2, 3]:
            esquema = EsquemaEvaluacion(
                programa_asignatura=self.programa_asignatura,
                version=f"v{num}",
                num_parciales=num,
            )
            esquema.full_clean()
            esquema.save()

        self.assertEqual(EsquemaEvaluacion.objects.count(), 3)

    def test_impide_exencion_cuando_num_parciales_es_1(self):
        esquema = EsquemaEvaluacion(
            programa_asignatura=self.programa_asignatura,
            version="v-exencion",
            num_parciales=1,
            permite_exencion=True,
        )
        with self.assertRaises(ValidationError):
            esquema.full_clean()

    def test_valida_suma_porcentajes_igual_100_por_corte(self):
        esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa_asignatura,
            version="v-suma-ok",
            num_parciales=2,
        )

        ComponenteEvaluacion.objects.create(
            esquema=esquema,
            corte_codigo="P1",
            nombre="Prácticas",
            porcentaje=40,
            orden=1,
        )
        ComponenteEvaluacion.objects.create(
            esquema=esquema,
            corte_codigo="P1",
            nombre="Proyecto",
            porcentaje=60,
            orden=2,
        )
        ComponenteEvaluacion.objects.create(
            esquema=esquema,
            corte_codigo="P2",
            nombre="Exposición",
            porcentaje=100,
            orden=1,
        )
        ComponenteEvaluacion.objects.create(
            esquema=esquema,
            corte_codigo="FINAL",
            nombre="Examen final",
            porcentaje=100,
            es_examen=True,
            orden=1,
        )

        esquema.validar_componentes_por_corte()

        esquema_invalido = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa_asignatura,
            version="v-suma-bad",
            num_parciales=2,
        )
        ComponenteEvaluacion.objects.create(
            esquema=esquema_invalido,
            corte_codigo="P1",
            nombre="Único componente",
            porcentaje=90,
            orden=1,
        )
        ComponenteEvaluacion.objects.create(
            esquema=esquema_invalido,
            corte_codigo="P2",
            nombre="Componente P2",
            porcentaje=100,
            orden=1,
        )
        ComponenteEvaluacion.objects.create(
            esquema=esquema_invalido,
            corte_codigo="FINAL",
            nombre="Examen final",
            porcentaje=100,
            es_examen=True,
            orden=1,
        )

        with self.assertRaises(ValidationError):
            esquema_invalido.validar_componentes_por_corte()

    def test_pesos_45_55_por_omision_y_persistencia_configurable(self):
        esquema_default = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa_asignatura,
            version="v-default",
            num_parciales=2,
        )
        self.assertEqual(esquema_default.peso_parciales, 45)
        self.assertEqual(esquema_default.peso_final, 55)
        self.assertEqual(esquema_default.umbral_exencion, 8)

        esquema_custom = EsquemaEvaluacion(
            programa_asignatura=self.programa_asignatura,
            version="v-custom",
            num_parciales=3,
            peso_parciales=50,
            peso_final=50,
        )
        esquema_custom.full_clean()
        esquema_custom.save()

        self.assertEqual(esquema_custom.peso_parciales, 50)
        self.assertEqual(esquema_custom.peso_final, 50)

    def test_umbral_exencion_debe_estar_en_escala_0_a_10(self):
        esquema_valido = EsquemaEvaluacion(
            programa_asignatura=self.programa_asignatura,
            version="v-umbral-ok",
            num_parciales=2,
            umbral_exencion=8.5,
        )
        esquema_valido.full_clean()

        esquema_invalido = EsquemaEvaluacion(
            programa_asignatura=self.programa_asignatura,
            version="v-umbral-bad",
            num_parciales=2,
            umbral_exencion=90,
        )

        with self.assertRaises(ValidationError) as exc:
            esquema_invalido.full_clean()

        self.assertEqual(
            exc.exception.message_dict["umbral_exencion"],
            ["El umbral de exención debe estar entre 0 y 10."],
        )


class EvaluacionAdminTests(TestCase):
    def test_componentes_no_aparecen_como_modulo_independiente_en_admin(self):
        self.assertIn(EsquemaEvaluacion, admin.site._registry)
        self.assertNotIn(ComponenteEvaluacion, admin.site._registry)

    def test_esquema_admin_mantiene_inline_de_componentes(self):
        esquema_admin = admin.site._registry[EsquemaEvaluacion]

        self.assertIsInstance(esquema_admin, EsquemaEvaluacionAdmin)
        self.assertIn(ComponenteEvaluacionInline, esquema_admin.inlines)

    def test_inline_usa_template_personalizado_para_texto_de_eliminacion(self):
        self.assertEqual(
            ComponenteEvaluacionInline.template,
            "admin/evaluacion/componenteevaluacion/tabular.html",
        )


class EsquemaEvaluacionProgramaAsignaturaActivoTests(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(clave="EVA_ACT", nombre="Carrera activa")
        self.plan_activo = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="PLAN_ACTIVO",
            nombre="Plan activo",
            estado="activo",
        )
        self.plan_inactivo = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="PLAN_INACT",
            nombre="Plan inactivo",
            estado="inactivo",
        )
        self.materia_activa = Materia.objects.create(
            clave="MAT_ACTIVA",
            nombre="Materia activa",
            horas_totales=64,
            estado="activo",
        )
        self.materia_inactiva = Materia.objects.create(
            clave="MAT_INACT",
            nombre="Materia inactiva",
            horas_totales=64,
            estado="inactivo",
        )
        self.materia_extra = Materia.objects.create(
            clave="MAT_EXTRA",
            nombre="Materia extra",
            horas_totales=64,
            estado="activo",
        )
        self.materia_extra_dos = Materia.objects.create(
            clave="MAT_EXTRA2",
            nombre="Materia extra dos",
            horas_totales=64,
            estado="activo",
        )
        self.programa_activo = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan_activo,
            materia=self.materia_activa,
            semestre_numero=1,
            anio_formacion=1,
            obligatoria=True,
        )
        self.programa_plan_legacy = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan_activo,
            materia=self.materia_extra,
            semestre_numero=2,
            anio_formacion=1,
            obligatoria=True,
        )
        self.programa_materia_legacy = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan_activo,
            materia=self.materia_extra_dos,
            semestre_numero=3,
            anio_formacion=2,
            obligatoria=True,
        )
        PlanEstudios.objects.filter(pk=self.plan_inactivo.pk).update(estado="activo")
        self.plan_inactivo.refresh_from_db()
        ProgramaAsignatura.objects.filter(pk=self.programa_plan_legacy.pk).update(
            plan_estudios=self.plan_inactivo
        )
        PlanEstudios.objects.filter(pk=self.plan_inactivo.pk).update(estado="inactivo")
        self.plan_inactivo.refresh_from_db()

        Materia.objects.filter(pk=self.materia_inactiva.pk).update(estado="activo")
        self.materia_inactiva.refresh_from_db()
        ProgramaAsignatura.objects.filter(pk=self.programa_materia_legacy.pk).update(
            materia=self.materia_inactiva
        )
        Materia.objects.filter(pk=self.materia_inactiva.pk).update(estado="inactivo")
        self.materia_inactiva.refresh_from_db()

        self.programa_plan_legacy.refresh_from_db()
        self.programa_materia_legacy.refresh_from_db()

    def test_backend_rechaza_programa_asignatura_inactivo(self):
        esquema = EsquemaEvaluacion(
            programa_asignatura=self.programa_plan_legacy,
            version="v1",
            num_parciales=2,
        )

        with self.assertRaises(ValidationError) as exc:
            esquema.full_clean()

        self.assertEqual(
            exc.exception.message_dict["programa_asignatura"],
            ["Solo se puede asignar un programa de asignatura activo."],
        )

    def test_save_directo_no_permite_programa_asignatura_inactivo(self):
        with self.assertRaises(ValidationError):
            EsquemaEvaluacion.objects.create(
                programa_asignatura=self.programa_materia_legacy,
                version="v1",
                num_parciales=2,
            )

    def test_admin_form_muestra_solo_programas_activos(self):
        form = EsquemaEvaluacionAdminForm()

        self.assertQuerySetEqual(
            form.fields["programa_asignatura"].queryset,
            [self.programa_activo],
            transform=lambda programa: programa,
        )

    def test_admin_form_de_edicion_legacy_ayuda_si_programa_actual_esta_inactivo(self):
        esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa_activo,
            version="v2",
            num_parciales=2,
        )
        EsquemaEvaluacion.objects.filter(pk=esquema.pk).update(
            programa_asignatura=self.programa_plan_legacy
        )
        esquema.refresh_from_db()

        form = EsquemaEvaluacionAdminForm(instance=esquema)

        self.assertQuerySetEqual(
            form.fields["programa_asignatura"].queryset,
            [self.programa_activo],
            transform=lambda programa: programa,
        )
        self.assertIn("est\u00e1 inactivo", form.fields["programa_asignatura"].help_text)

    def test_admin_form_aclara_que_umbral_exencion_usa_escala_0_a_10(self):
        form = EsquemaEvaluacionAdminForm()

        self.assertIn("escala de 0 a 10", form.fields["umbral_exencion"].help_text)


class ComponenteEvaluacionValidationTests(TestCase):
    def setUp(self):
        carrera = Carrera.objects.create(clave="EVAL_CARR", nombre="Carrera evaluacion")
        plan = PlanEstudios.objects.create(
            carrera=carrera,
            clave="EVAL_PLAN",
            nombre="Plan evaluacion",
        )
        materia = Materia.objects.create(clave="EVAL_MAT", nombre="Materia evaluacion", horas_totales=64)
        programa_asignatura = ProgramaAsignatura.objects.create(
            plan_estudios=plan,
            materia=materia,
            semestre_numero=1,
            anio_formacion=1,
            obligatoria=True,
        )
        self.esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=programa_asignatura,
            version="v-inline",
            num_parciales=2,
        )
        self.componente_p1_1 = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo="P1",
            nombre="Tareas",
            porcentaje=40,
            orden=1,
        )
        self.componente_p1_2 = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo="P1",
            nombre="Examen",
            porcentaje=60,
            orden=2,
        )
        self.componente_p2 = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo="P2",
            nombre="Proyecto",
            porcentaje=100,
            orden=1,
        )
        self.componente_final = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo="FINAL",
            nombre="Examen final",
            porcentaje=100,
            es_examen=True,
            orden=1,
        )
        self.formset_class = inlineformset_factory(
            EsquemaEvaluacion,
            ComponenteEvaluacion,
            formset=ComponenteEvaluacionInlineFormSet,
            fields=("corte_codigo", "nombre", "porcentaje", "es_examen", "orden"),
            extra=1,
            can_delete=True,
        )
        self.prefix = self.formset_class.get_default_prefix()

    def _build_existing_form_data(self, index, componente, **overrides):
        payload = {
            f"{self.prefix}-{index}-id": str(componente.pk),
            f"{self.prefix}-{index}-esquema": str(self.esquema.pk),
            f"{self.prefix}-{index}-corte_codigo": componente.corte_codigo,
            f"{self.prefix}-{index}-nombre": componente.nombre,
            f"{self.prefix}-{index}-porcentaje": str(componente.porcentaje),
            f"{self.prefix}-{index}-orden": str(componente.orden),
        }
        if componente.es_examen:
            payload[f"{self.prefix}-{index}-es_examen"] = "on"
        payload.update(overrides)
        return payload

    def _build_management_data(self, total_forms, initial_forms, **overrides):
        payload = {
            "num_parciales": str(self.esquema.num_parciales),
            f"{self.prefix}-TOTAL_FORMS": str(total_forms),
            f"{self.prefix}-INITIAL_FORMS": str(initial_forms),
            f"{self.prefix}-MIN_NUM_FORMS": "0",
            f"{self.prefix}-MAX_NUM_FORMS": "1000",
        }
        payload.update(overrides)
        return payload

    def test_model_full_clean_no_rompe_si_porcentaje_viene_none(self):
        componente = ComponenteEvaluacion(
            esquema=self.esquema,
            corte_codigo="P1",
            nombre="Fila incompleta",
            porcentaje=None,
            orden=1,
        )

        with self.assertRaises(ValidationError) as exc:
            componente.full_clean()

        self.assertIn("porcentaje", exc.exception.message_dict)

    def test_formset_ignora_fila_extra_vacia_y_suma_componentes_existentes(self):
        data = {}
        componentes = [
            self.componente_p1_1,
            self.componente_p1_2,
            self.componente_p2,
            self.componente_final,
        ]

        for index, componente in enumerate(componentes):
            data.update(self._build_existing_form_data(index, componente))

        data.update(
            {
                f"{self.prefix}-4-id": "",
                f"{self.prefix}-4-corte_codigo": "",
                f"{self.prefix}-4-nombre": "",
                f"{self.prefix}-4-porcentaje": "",
                f"{self.prefix}-4-orden": "1",
            }
        )
        data.update(self._build_management_data(total_forms=5, initial_forms=4))

        formset = self.formset_class(data=data, instance=self.esquema)

        self.assertTrue(formset.is_valid(), formset.errors)

    def test_formset_muestra_total_real_y_no_cero_cuando_un_corte_no_suma_100(self):
        data = {}
        componentes = [
            self.componente_p1_1,
            self.componente_p1_2,
            self.componente_p2,
            self.componente_final,
        ]

        for index, componente in enumerate(componentes):
            overrides = {}
            if componente.pk == self.componente_p1_2.pk:
                overrides[f"{self.prefix}-{index}-porcentaje"] = "50.00"
            data.update(self._build_existing_form_data(index, componente, **overrides))

        data.update(self._build_management_data(total_forms=4, initial_forms=4))

        formset = self.formset_class(data=data, instance=self.esquema)

        self.assertFalse(formset.is_valid())
        self.assertIn("La suma del corte P1 debe ser 100 (actual: 90.00).", formset.non_form_errors())

    def test_formset_usa_num_parciales_posteado_y_respeta_delete(self):
        data = {}
        componentes = [
            self.componente_p1_1,
            self.componente_p1_2,
            self.componente_p2,
            self.componente_final,
        ]

        for index, componente in enumerate(componentes):
            overrides = {}
            if componente.pk == self.componente_p2.pk:
                overrides[f"{self.prefix}-{index}-DELETE"] = "on"
            data.update(self._build_existing_form_data(index, componente, **overrides))

        data.update(
            self._build_management_data(
                total_forms=4,
                initial_forms=4,
                num_parciales=str(EsquemaEvaluacion.PARCIALES_1),
            )
        )

        formset = self.formset_class(data=data, instance=self.esquema)

        self.assertTrue(formset.is_valid(), formset.non_form_errors())

    def test_formset_muestra_labels_claros_para_examen_final_y_eliminacion(self):
        formset = self.formset_class(instance=self.esquema)

        self.assertEqual(formset.forms[0].fields["es_examen"].label, "Es examen final")
        self.assertEqual(formset.forms[0].fields[DELETION_FIELD_NAME].label, "Eliminar completamente")
