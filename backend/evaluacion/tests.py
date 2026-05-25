import json
from datetime import date
from decimal import Decimal

from django.forms.formsets import DELETION_FIELD_NAME
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import inlineformset_factory
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ValidationError
from django.urls import reverse

from catalogos.models import (
    Antiguedad,
    Carrera,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
)
from evaluacion.admin import (
    ComponenteEvaluacionInline,
    ComponenteEvaluacionInlineFormSet,
    EsquemaEvaluacionAdmin,
)
from evaluacion.forms import EsquemaEvaluacionAdminForm
from evaluacion.models import (
    Acta,
    CalificacionComponente,
    CapturaCalificacionPreliminar,
    ConformidadDiscente,
    DetalleActa,
    ComponenteEvaluacion,
    EsquemaEvaluacion,
    ValidacionActa,
)
from evaluacion.services import (
    ServicioCalculoAcademico,
    crear_o_regenerar_borrador_acta,
    formalizar_acta_jefatura_academica,
    publicar_acta,
    registrar_conformidad_discente,
    remitir_acta,
    validar_acta_jefatura_carrera,
    redondear_visualizacion_un_decimal,
)
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria
from usuarios.models import AsignacionCargo, GradoEmpleo, UnidadOrganizacional


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
        self.assertEqual(esquema_default.umbral_exencion, 9)

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

    def test_activo_muestra_un_label_funcional_para_el_admin(self):
        field = EsquemaEvaluacion._meta.get_field("activo")

        self.assertEqual(field.verbose_name, "Disponible para evaluación")
        self.assertIn("consulta histórica", field.help_text)

    def test_esquema_admin_carga_script_para_estado_inmediato_del_inline(self):
        esquema_admin = admin.site._registry[EsquemaEvaluacion]

        self.assertIn(
            "evaluacion/admin/esquema_evaluacion.js",
            str(esquema_admin.media),
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
        self.request = RequestFactory().get("/admin/evaluacion/esquemaevaluacion/")
        self.request.user = get_user_model().objects.create_superuser(
            username="admin_eval",
            password="admin",
        )

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
            "activo": "on",
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

    def test_formset_permite_desactivar_esquema_sin_modificar_componentes(self):
        data = {}
        componentes = [
            self.componente_p1_1,
            self.componente_p1_2,
            self.componente_p2,
            self.componente_final,
        ]

        for index, componente in enumerate(componentes):
            data.update(self._build_existing_form_data(index, componente))

        data.update(self._build_management_data(total_forms=4, initial_forms=4))
        data.pop("activo")

        formset = self.formset_class(data=data, instance=self.esquema)

        self.assertTrue(formset.is_valid(), formset.non_form_errors())

    def test_formset_rechaza_modificar_componentes_si_esquema_se_desactiva(self):
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
        data.pop("activo")

        formset = self.formset_class(data=data, instance=self.esquema)

        self.assertFalse(formset.is_valid())
        self.assertIn(
            "Los componentes no se pueden modificar si el esquema no está disponible "
            "para evaluación.",
            formset.non_form_errors(),
        )

    def test_formset_muestra_labels_claros_para_examen_final_y_eliminacion(self):
        formset = self.formset_class(instance=self.esquema)

        self.assertEqual(formset.forms[0].fields["es_examen"].label, "Es examen final")
        self.assertEqual(formset.forms[0].fields[DELETION_FIELD_NAME].label, "Eliminar completamente")

    def test_inline_renderiza_controles_aunque_esquema_este_inactivo(self):
        self.esquema.activo = False
        inline = ComponenteEvaluacionInline(
            EsquemaEvaluacion,
            admin.site,
        )

        self.assertTrue(inline.has_add_permission(self.request, self.esquema))
        self.assertTrue(inline.has_change_permission(self.request, self.esquema))
        self.assertTrue(inline.has_delete_permission(self.request, self.esquema))

    def test_inline_de_componentes_permite_edicion_si_esquema_esta_activo(self):
        inline = ComponenteEvaluacionInline(
            EsquemaEvaluacion,
            admin.site,
        )

        self.assertTrue(inline.has_add_permission(self.request, self.esquema))
        self.assertTrue(inline.has_change_permission(self.request, self.esquema))
        self.assertTrue(inline.has_delete_permission(self.request, self.esquema))


class CapturaCalificacionPreliminarBaseTests(TestCase):
    def setUp(self):
        self.grupo_docente, _ = Group.objects.get_or_create(name="DOCENTE")
        self.grupo_discente, _ = Group.objects.get_or_create(name="DISCENTE")
        self.carrera = Carrera.objects.create(clave="CAP_ICI", nombre="Carrera captura")
        self.plan = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="CAP_PLAN",
            nombre="Plan captura",
        )
        self.antiguedad = Antiguedad.objects.create(
            plan_estudios=self.plan,
            clave="CAP_ANT",
            nombre="Antigüedad captura",
            anio_inicio=2025,
            anio_fin=2029,
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="CAP_PER",
            anio_escolar="2025-2026",
            periodo_academico=1,
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2026, 1, 31),
        )
        self.grupo = GrupoAcademico.objects.create(
            clave_grupo="CAP_G1",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )
        self.materia = Materia.objects.create(
            clave="CAP_MAT",
            nombre="Materia captura",
            horas_totales=64,
        )
        self.programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=self.materia,
            semestre_numero=1,
        )
        usuario_model = get_user_model()
        self.usuario_docente = usuario_model.objects.create_user(
            username="docente_cap",
            password="segura123",
        )
        self.usuario_docente.groups.add(self.grupo_docente)
        self.otro_docente = usuario_model.objects.create_user(
            username="otro_docente_cap",
            password="segura123",
        )
        self.otro_docente.groups.add(self.grupo_docente)
        self.usuario_discente = usuario_model.objects.create_user(
            username="discente_cap",
            password="segura123",
        )
        self.usuario_discente.groups.add(self.grupo_discente)
        self.discente = Discente.objects.create(
            usuario=self.usuario_discente,
            matricula="CAP0001",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )
        AdscripcionGrupo.objects.create(
            discente=self.discente,
            grupo_academico=self.grupo,
        )
        self.asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.usuario_docente,
            grupo_academico=self.grupo,
            programa_asignatura=self.programa,
        )
        self.inscripcion = InscripcionMateria.objects.get(
            discente=self.discente,
            asignacion_docente=self.asignacion,
        )
        self.esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa,
            version="v-cap",
            num_parciales=2,
            permite_exencion=True,
        )
        self.componente_p1_tareas = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo=ComponenteEvaluacion.CORTE_P1,
            nombre="Tareas",
            porcentaje=40,
            orden=1,
        )
        self.componente_p1_examen = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo=ComponenteEvaluacion.CORTE_P1,
            nombre="Examen",
            porcentaje=60,
            orden=2,
        )
        self.componente_p2 = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo=ComponenteEvaluacion.CORTE_P2,
            nombre="Proyecto",
            porcentaje=100,
            orden=1,
        )
        self.componente_final = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
            nombre="Examen final",
            porcentaje=100,
            es_examen=True,
            orden=1,
        )

    def capturar(self, componente, valor):
        return CapturaCalificacionPreliminar.objects.create(
            inscripcion_materia=self.inscripcion,
            componente=componente,
            valor=Decimal(str(valor)),
            capturado_por=self.usuario_docente,
        )

    def capturar_parciales(self, p1_tareas="9.0", p1_examen="9.0", p2="9.0"):
        self.capturar(self.componente_p1_tareas, p1_tareas)
        self.capturar(self.componente_p1_examen, p1_examen)
        self.capturar(self.componente_p2, p2)


class CapturaCalificacionPreliminarTests(CapturaCalificacionPreliminarBaseTests):
    def test_rechaza_calificaciones_fuera_de_escala(self):
        for valor in (Decimal("-0.1"), Decimal("10.1")):
            captura = CapturaCalificacionPreliminar(
                inscripcion_materia=self.inscripcion,
                componente=self.componente_p1_tareas,
                valor=valor,
                capturado_por=self.usuario_docente,
            )

            with self.assertRaises(ValidationError):
                captura.full_clean()

    def test_permite_guardar_valores_validos(self):
        captura = self.capturar(self.componente_p1_tareas, "9.5")

        self.assertEqual(captura.valor, Decimal("9.5"))
        self.assertEqual(captura.corte_codigo, ComponenteEvaluacion.CORTE_P1)

    def test_calcula_corte_con_componentes_ponderados(self):
        self.capturar(self.componente_p1_tareas, "8.0")
        self.capturar(self.componente_p1_examen, "10.0")

        resultado = ServicioCalculoAcademico(self.inscripcion).calcular()

        self.assertEqual(
            resultado["cortes"][ComponenteEvaluacion.CORTE_P1]["resultado"],
            Decimal("9.2"),
        )

    def test_no_redondea_resultados_intermedios_ni_promedio_para_exencion(self):
        self.componente_p1_tareas.porcentaje = Decimal("33.33")
        self.componente_p1_tareas.save()
        self.componente_p1_examen.porcentaje = Decimal("66.67")
        self.componente_p1_examen.save()
        self.capturar(self.componente_p1_tareas, "8.9")
        self.capturar(self.componente_p1_examen, "9.0")
        self.capturar(self.componente_p2, "9.0")
        self.capturar(self.componente_final, "9.0")

        resultado = ServicioCalculoAcademico(self.inscripcion).calcular()

        self.assertEqual(
            resultado["cortes"][ComponenteEvaluacion.CORTE_P1]["resultado"],
            Decimal("8.96667"),
        )
        self.assertEqual(
            resultado["cortes"][ComponenteEvaluacion.CORTE_P1]["resultado_visual"],
            Decimal("9.0"),
        )
        self.assertEqual(resultado["promedio_parciales"], Decimal("8.983335"))
        self.assertEqual(resultado["promedio_parciales_visual"], Decimal("9.0"))
        self.assertFalse(resultado["exencion_aplica"])
        self.assertEqual(resultado["resultado_final"], Decimal("9.0"))
        self.assertEqual(resultado["resultado_final_visual"], Decimal("9.0"))
        self.assertEqual(resultado["calificacion_final_preliminar"], Decimal("8.99250075"))
        self.assertEqual(resultado["calificacion_final_preliminar_visual"], Decimal("9.0"))

    def test_visualizacion_final_redondea_a_un_decimal_sin_banker_rounding(self):
        self.assertEqual(redondear_visualizacion_un_decimal(Decimal("8.9999")), Decimal("9.0"))
        self.assertEqual(redondear_visualizacion_un_decimal(Decimal("8.94")), Decimal("8.9"))
        self.assertEqual(redondear_visualizacion_un_decimal(Decimal("8.95")), Decimal("9.0"))

    def test_calcula_promedio_de_parciales(self):
        self.capturar(self.componente_p1_tareas, "8.0")
        self.capturar(self.componente_p1_examen, "10.0")
        self.capturar(self.componente_p2, "8.8")

        resultado = ServicioCalculoAcademico(self.inscripcion).calcular()

        self.assertEqual(resultado["promedio_parciales"], Decimal("9.0"))

    def test_impide_exencion_en_materia_de_un_parcial(self):
        self.esquema.num_parciales = EsquemaEvaluacion.PARCIALES_1
        self.esquema.permite_exencion = False
        self.esquema.save()
        self.capturar(self.componente_p1_tareas, "10.0")
        self.capturar(self.componente_p1_examen, "10.0")
        self.capturar(self.componente_final, "6.0")

        resultado = ServicioCalculoAcademico(self.inscripcion).calcular()

        self.assertFalse(resultado["exencion_aplica"])
        self.assertEqual(resultado["resultado_final"], Decimal("6.0"))

    def test_aplica_exencion_con_dos_parciales_y_promedio_mayor_o_igual_a_nueve(self):
        self.capturar_parciales("9.0", "9.0", "9.0")

        resultado = ServicioCalculoAcademico(self.inscripcion).calcular()

        self.assertTrue(resultado["exencion_aplica"])
        self.assertEqual(resultado["resultado_final"], Decimal("9.0"))
        self.assertEqual(resultado["calificacion_final_preliminar"], Decimal("9.0"))

    def test_exencion_respeta_umbral_configurado_en_esquema(self):
        self.esquema.umbral_exencion = Decimal("9.10")
        self.esquema.save()
        self.capturar_parciales("9.0", "9.0", "9.0")
        self.capturar(self.componente_final, "6.0")

        resultado = ServicioCalculoAcademico(self.inscripcion).calcular()

        self.assertFalse(resultado["exencion_aplica"])
        self.assertEqual(resultado["resultado_final"], Decimal("6.0"))

    def test_respeta_pesos_configurados(self):
        self.esquema.permite_exencion = False
        self.esquema.peso_parciales = Decimal("50.00")
        self.esquema.peso_final = Decimal("50.00")
        self.esquema.save()
        self.capturar_parciales("8.0", "8.0", "8.0")
        self.capturar(self.componente_final, "10.0")

        resultado = ServicioCalculoAcademico(self.inscripcion).calcular()

        self.assertEqual(resultado["calificacion_final_preliminar"], Decimal("9.0"))

    def test_docente_no_puede_capturar_asignacion_de_otro_docente(self):
        self.client.force_login(self.otro_docente)
        field_name = f"cal_{self.inscripcion.pk}_{self.componente_p1_tareas.pk}"

        response = self.client.post(
            reverse(
                "evaluacion:captura-calificaciones",
                args=[self.asignacion.pk, ComponenteEvaluacion.CORTE_P1],
            ),
            data={field_name: "9.0"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(CapturaCalificacionPreliminar.objects.exists())

    def test_dejar_campo_vacio_elimina_captura_previa(self):
        captura = self.capturar(self.componente_p1_tareas, "9.0")
        self.client.force_login(self.usuario_docente)
        field_name = f"cal_{self.inscripcion.pk}_{self.componente_p1_tareas.pk}"

        response = self.client.post(
            reverse(
                "evaluacion:captura-calificaciones",
                args=[self.asignacion.pk, ComponenteEvaluacion.CORTE_P1],
            ),
            data={field_name: ""},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            CapturaCalificacionPreliminar.objects.filter(pk=captura.pk).exists()
        )

    def test_docente_asignado_puede_ver_pantalla_de_captura(self):
        self.client.force_login(self.usuario_docente)

        response = self.client.get(
            reverse(
                "evaluacion:captura-calificaciones",
                args=[self.asignacion.pk, ComponenteEvaluacion.CORTE_P1],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Captura preliminar")

    def test_docente_asignado_puede_ver_resumen_de_calculo(self):
        grado = GradoEmpleo.objects.create(
            clave="CADETE",
            abreviatura="Cadete",
            nombre="Cadete",
            tipo=GradoEmpleo.TIPO_MILITAR_ACTIVO,
        )
        self.usuario_discente.grado_empleo = grado
        self.usuario_discente.nombre_completo = "Discente Captura"
        self.usuario_discente.save()
        self.client.force_login(self.usuario_docente)

        response = self.client.get(
            reverse("evaluacion:resumen-calculo", args=[self.asignacion.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resumen de cálculo")
        self.assertContains(response, "Evaluación final")
        self.assertContains(response, "Resultado final preliminar")
        self.assertContains(response, "Estado preliminar")
        self.assertContains(response, "Cadete")
        self.assertContains(response, "Discente Captura")

    def test_corte_final_se_muestra_como_evaluacion_final(self):
        self.client.force_login(self.usuario_docente)

        response = self.client.get(
            reverse(
                "evaluacion:captura-calificaciones",
                args=[self.asignacion.pk, ComponenteEvaluacion.CORTE_FINAL],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evaluación final")

    def test_captura_final_muestra_exencion_del_examen_final(self):
        self.capturar_parciales("9.0", "9.0", "9.0")
        self.client.force_login(self.usuario_docente)

        response = self.client.get(
            reverse(
                "evaluacion:captura-calificaciones",
                args=[self.asignacion.pk, ComponenteEvaluacion.CORTE_FINAL],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Examen final sustituido")

    def test_no_actualiza_campos_oficiales_de_inscripcion_materia(self):
        self.capturar_parciales("9.0", "9.0", "9.0")
        ServicioCalculoAcademico(self.inscripcion).calcular()
        self.inscripcion.refresh_from_db()

        self.assertIsNone(self.inscripcion.calificacion_final)
        self.assertIsNone(self.inscripcion.codigo_resultado_oficial)
        self.assertIsNone(self.inscripcion.codigo_marca)
        self.assertIsNone(self.inscripcion.cerrado_en)


class ActaFormalBloque6Tests(CapturaCalificacionPreliminarBaseTests):
    def setUp(self):
        super().setUp()
        self.grupo_jefe_carrera, _ = Group.objects.get_or_create(name="JEFE_SUB_EJEC_CTR")
        self.grupo_jefe_planeacion, _ = Group.objects.get_or_create(name="JEFE_SUB_PLAN_EVAL")
        self.grupo_jefe_academico, _ = Group.objects.get_or_create(name="JEFE_ACADEMICO")
        self.grupo_estadistica, _ = Group.objects.get_or_create(name="ENCARGADO_ESTADISTICA")
        usuario_model = get_user_model()
        self.usuario_jefe_carrera = usuario_model.objects.create_user(
            username="jefe_carrera_acta",
            password="segura123",
        )
        self.usuario_jefe_carrera.groups.add(self.grupo_jefe_carrera)
        self.usuario_jefe_planeacion = usuario_model.objects.create_user(
            username="jefe_planeacion_acta",
            password="segura123",
        )
        self.usuario_jefe_planeacion.groups.add(self.grupo_jefe_planeacion)
        self.usuario_jefe_academico = usuario_model.objects.create_user(
            username="jefe_academico_acta",
            password="segura123",
        )
        self.usuario_jefe_academico.groups.add(self.grupo_jefe_academico)
        self.usuario_estadistica = usuario_model.objects.create_user(
            username="estadistica_acta",
            password="segura123",
        )
        self.usuario_estadistica.groups.add(self.grupo_estadistica)
        self.seccion_academica = UnidadOrganizacional.objects.create(
            clave=UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
            nombre="Seccion Academica",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )
        self.seccion_pedagogica = UnidadOrganizacional.objects.create(
            clave=UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA,
            nombre="Seccion Pedagogica",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )
        self.subseccion_ejecucion = UnidadOrganizacional.objects.create(
            clave="ACTA_SUB_EC",
            nombre="Subseccion de Ejecucion y Control",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=self.seccion_academica,
            carrera=self.carrera,
        )
        self.subseccion_planeacion = UnidadOrganizacional.objects.create(
            clave="ACTA_SUB_PE",
            nombre="Subseccion de Planeacion y Evaluacion",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=self.seccion_pedagogica,
            carrera=self.carrera,
        )
        self.cargo_jefe_carrera = AsignacionCargo.objects.create(
            usuario=self.usuario_jefe_carrera,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_SUB_EJEC_CTR,
            carrera=self.carrera,
            unidad_organizacional=self.subseccion_ejecucion,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )
        self.cargo_jefe_planeacion = AsignacionCargo.objects.create(
            usuario=self.usuario_jefe_planeacion,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_SUB_PLAN_EVAL,
            carrera=self.carrera,
            unidad_organizacional=self.subseccion_planeacion,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )
        self.cargo_jefe_academico = AsignacionCargo.objects.create(
            usuario=self.usuario_jefe_academico,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_ACADEMICO,
            unidad_organizacional=self.seccion_academica,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

    def capturar_p1_completo(self):
        self.capturar(self.componente_p1_tareas, "8.0")
        self.capturar(self.componente_p1_examen, "10.0")

    def capturar_final_completo_sin_exencion(self):
        self.esquema.permite_exencion = False
        self.esquema.save()
        self.capturar_parciales("8.0", "8.0", "8.0")
        self.capturar(self.componente_final, "9.0")

    def publicar_acta_p1(self):
        self.capturar_p1_completo()
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_P1,
            self.usuario_docente,
        )
        publicar_acta(acta, self.usuario_docente)
        return acta

    def remitir_acta_p1(self):
        acta = self.publicar_acta_p1()
        remitir_acta(acta, self.usuario_docente)
        return acta

    def crear_acta_directa(
        self,
        asignacion=None,
        esquema=None,
        corte_codigo=ComponenteEvaluacion.CORTE_P1,
        estado_acta=Acta.ESTADO_BORRADOR_DOCENTE,
    ):
        asignacion = asignacion or self.asignacion
        esquema = esquema or self.esquema
        return Acta.objects.create(
            asignacion_docente=asignacion,
            corte_codigo=corte_codigo,
            estado_acta=estado_acta,
            esquema=esquema,
            esquema_version_snapshot=esquema.version,
            peso_parciales_snapshot=esquema.peso_parciales,
            peso_final_snapshot=esquema.peso_final,
            umbral_exencion_snapshot=esquema.umbral_exencion,
            creado_por=self.usuario_docente,
        )

    def crear_acta_otra_carrera(self, estado_acta=Acta.ESTADO_REMITIDO_JEFATURA_CARRERA):
        suffix = Acta.objects.count() + 1
        carrera = Carrera.objects.create(
            clave=f"AJENA{suffix}",
            nombre=f"Carrera ajena {suffix}",
        )
        plan = PlanEstudios.objects.create(
            carrera=carrera,
            clave=f"PLAN-AJENO-{suffix}",
            nombre=f"Plan ajeno {suffix}",
        )
        antiguedad = Antiguedad.objects.create(
            plan_estudios=plan,
            clave=f"ANT-AJENA-{suffix}",
            nombre=f"Antiguedad ajena {suffix}",
            anio_inicio=2025,
            anio_fin=2029,
        )
        grupo = GrupoAcademico.objects.create(
            clave_grupo=f"AJENO-{suffix}",
            antiguedad=antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )
        materia = Materia.objects.create(
            clave=f"MAT-AJENA-{suffix}",
            nombre=f"Materia ajena {suffix}",
            horas_totales=64,
        )
        programa = ProgramaAsignatura.objects.create(
            plan_estudios=plan,
            materia=materia,
            semestre_numero=1,
        )
        asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.usuario_docente,
            grupo_academico=grupo,
            programa_asignatura=programa,
        )
        esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=programa,
            version=f"v-ajena-{suffix}",
            num_parciales=2,
        )
        return self.crear_acta_directa(
            asignacion=asignacion,
            esquema=esquema,
            estado_acta=estado_acta,
        )

    def test_impide_duplicidad_de_acta_activa_por_asignacion_y_corte(self):
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_P1,
            self.usuario_docente,
        )

        with self.assertRaises(ValidationError):
            Acta.objects.create(
                asignacion_docente=self.asignacion,
                corte_codigo=ComponenteEvaluacion.CORTE_P1,
                esquema=self.esquema,
                esquema_version_snapshot=self.esquema.version,
                peso_parciales_snapshot=self.esquema.peso_parciales,
                peso_final_snapshot=self.esquema.peso_final,
                umbral_exencion_snapshot=self.esquema.umbral_exencion,
                creado_por=self.usuario_docente,
            )

        self.assertEqual(
            Acta.objects.filter(
                asignacion_docente=self.asignacion,
                corte_codigo=ComponenteEvaluacion.CORTE_P1,
            ).count(),
            1,
        )
        self.assertEqual(acta.estado_acta, Acta.ESTADO_BORRADOR_DOCENTE)

    def test_crea_borrador_con_roster_componentes_y_snapshots(self):
        self.capturar_p1_completo()

        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_P1,
            self.usuario_docente,
        )

        self.assertEqual(acta.detalles.count(), 1)
        detalle = acta.detalles.get()
        self.assertEqual(detalle.inscripcion_materia, self.inscripcion)
        self.assertEqual(detalle.resultado_corte_visible, Decimal("9.2"))
        self.assertEqual(detalle.calificaciones_componentes.count(), 2)
        self.assertTrue(
            CalificacionComponente.objects.filter(
                detalle=detalle,
                componente_nombre_snapshot="Tareas",
                componente_porcentaje_snapshot=Decimal("40.00"),
                valor_capturado=Decimal("8.0"),
            ).exists()
        )

    def test_vista_acta_muestra_tabla_por_corte_con_componentes_snapshot(self):
        grado = GradoEmpleo.objects.create(
            clave="TTE_PAS_ICI",
            abreviatura="Tte. Pas. I.C.I.",
            nombre="Teniente pasante ICI",
            tipo=GradoEmpleo.TIPO_MILITAR_ACTIVO,
        )
        self.usuario_discente.grado_empleo = grado
        self.usuario_discente.nombre_completo = "Discente Acta"
        self.usuario_discente.save()
        self.capturar_p1_completo()
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_P1,
            self.usuario_docente,
        )
        self.client.force_login(self.usuario_docente)

        response = self.client.get(reverse("evaluacion:acta-detalle", args=[acta.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acta de calificaciones por corte")
        self.assertContains(response, "No.")
        self.assertContains(response, "Grado y empleo")
        self.assertContains(response, "Nombre")
        self.assertContains(response, "Tareas")
        self.assertContains(response, "40.00%")
        self.assertContains(response, "Examen")
        self.assertContains(response, "60.00%")
        self.assertContains(response, "8.0")
        self.assertContains(response, "10.0")
        self.assertNotContains(response, "3.200000")
        self.assertNotContains(response, "6.000000")
        self.assertContains(response, "Calificación Parcial 1")
        self.assertContains(response, "9.2")
        self.assertContains(response, "Conformidad")
        self.assertNotContains(response, "Firma de conformidad")
        self.assertContains(response, "Tte. Pas. I.C.I.")
        self.assertContains(response, "Discente Acta")
        self.assertNotContains(response, "CAP0001")

    def test_impide_publicar_si_faltan_capturas_requeridas(self):
        self.capturar(self.componente_p1_tareas, "8.0")
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_P1,
            self.usuario_docente,
        )

        with self.assertRaises(ValidationError):
            publicar_acta(acta, self.usuario_docente)

        acta.refresh_from_db()
        self.assertEqual(acta.estado_acta, Acta.ESTADO_BORRADOR_DOCENTE)

    def test_permite_publicar_final_si_exencion_del_examen_es_valida(self):
        self.capturar_parciales("9.0", "9.0", "9.0")
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_FINAL,
            self.usuario_docente,
        )

        publicar_acta(acta, self.usuario_docente)
        detalle = acta.detalles.get()

        self.assertEqual(acta.estado_acta, Acta.ESTADO_PUBLICADO_DISCENTE)
        self.assertTrue(detalle.exencion_aplica)
        calificacion_examen = detalle.calificaciones_componentes.get(
            componente=self.componente_final
        )
        self.assertTrue(calificacion_examen.sustituido_por_exencion)
        self.assertIsNone(calificacion_examen.valor_capturado)
        self.assertEqual(calificacion_examen.valor_calculado, Decimal("9.000000"))

    def test_conformidad_discente_no_bloquea_remision(self):
        acta = self.publicar_acta_p1()
        detalle = acta.detalles.get()

        conformidad = registrar_conformidad_discente(
            detalle,
            self.usuario_discente,
            ConformidadDiscente.ESTADO_CONFORME,
            "Enterado",
        )
        remitir_acta(acta, self.usuario_docente)

        acta.refresh_from_db()
        self.assertTrue(conformidad.vigente)
        self.assertEqual(acta.estado_acta, Acta.ESTADO_REMITIDO_JEFATURA_CARRERA)

    def test_conformidad_inconforme_exige_comentario(self):
        acta = self.publicar_acta_p1()
        detalle = acta.detalles.get()

        with self.assertRaises(ValidationError) as exc:
            registrar_conformidad_discente(
                detalle,
                self.usuario_discente,
                ConformidadDiscente.ESTADO_INCONFORME,
                "",
            )

        self.assertIn("comentario es obligatorio", str(exc.exception))
        self.assertFalse(detalle.conformidades.exists())

    def test_discente_detalle_muestra_error_si_inconformidad_no_tiene_comentario(self):
        acta = self.publicar_acta_p1()
        detalle = acta.detalles.get()
        self.client.force_login(self.usuario_discente)

        response = self.client.post(
            reverse("evaluacion:discente-acta-detalle", args=[detalle.pk]),
            data={
                "estado_conformidad": ConformidadDiscente.ESTADO_INCONFORME,
                "comentario": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "El comentario es obligatorio cuando se registra inconformidad.",
        )
        self.assertFalse(detalle.conformidades.exists())

    def test_acta_detalle_muestra_comentarios_en_seccion_secundaria(self):
        acta = self.publicar_acta_p1()
        detalle = acta.detalles.get()
        registrar_conformidad_discente(
            detalle,
            self.usuario_discente,
            ConformidadDiscente.ESTADO_INCONFORME,
            "Solicito revisión del componente de examen.",
        )
        self.client.force_login(self.usuario_docente)

        response = self.client.get(reverse("evaluacion:acta-detalle", args=[acta.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conformidad")
        self.assertContains(response, "Inconforme")
        self.assertContains(response, "Observaciones de conformidad")
        self.assertContains(response, "Solicito revisión del componente de examen.")

    def test_conformidad_queda_solo_lectura_despues_de_remitir(self):
        acta = self.publicar_acta_p1()
        detalle = acta.detalles.get()
        remitir_acta(acta, self.usuario_docente)

        with self.assertRaises(ValidationError) as error:
            registrar_conformidad_discente(
                detalle,
                self.usuario_discente,
                ConformidadDiscente.ESTADO_CONFORME,
                "Enterado después de remisión.",
            )

        self.assertIn("solo lectura", str(error.exception))
        self.assertFalse(detalle.conformidades.exists())

    def test_discente_detalle_oculta_formulario_de_conformidad_despues_de_remitir(self):
        acta = self.publicar_acta_p1()
        detalle = acta.detalles.get()
        remitir_acta(acta, self.usuario_docente)
        self.client.force_login(self.usuario_discente)

        response = self.client.get(reverse("evaluacion:discente-acta-detalle", args=[detalle.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Registrar conformidad")
        self.assertContains(response, "La conformidad quedó en solo lectura")

    def test_bloquea_captura_preliminar_si_acta_ya_fue_publicada(self):
        captura = self.capturar(self.componente_p1_tareas, "8.0")
        self.capturar(self.componente_p1_examen, "10.0")
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_P1,
            self.usuario_docente,
        )
        publicar_acta(acta, self.usuario_docente)
        self.client.force_login(self.usuario_docente)
        field_name = f"cal_{self.inscripcion.pk}_{self.componente_p1_tareas.pk}"

        response_get = self.client.get(
            reverse(
                "evaluacion:captura-calificaciones",
                args=[self.asignacion.pk, ComponenteEvaluacion.CORTE_P1],
            )
        )

        self.assertContains(
            response_get,
            "La captura preliminar ya no puede modificarse",
        )
        self.assertContains(response_get, "disabled")
        self.assertNotContains(response_get, "Guardar captura preliminar")

        response = self.client.post(
            reverse(
                "evaluacion:captura-calificaciones",
                args=[self.asignacion.pk, ComponenteEvaluacion.CORTE_P1],
            ),
            data={field_name: "9.0"},
            follow=True,
        )

        captura.refresh_from_db()
        self.assertEqual(captura.valor, Decimal("8.0"))
        self.assertContains(response, "La captura preliminar quedó bloqueada")

    def test_regenerar_solo_aparece_en_borrador_y_backend_bloquea_publicada(self):
        self.capturar_p1_completo()
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_P1,
            self.usuario_docente,
        )
        self.client.force_login(self.usuario_docente)

        response_borrador = self.client.get(reverse("evaluacion:acta-detalle", args=[acta.pk]))
        self.assertContains(response_borrador, "Regenerar desde captura preliminar")

        publicar_acta(acta, self.usuario_docente)
        response_publicada = self.client.get(reverse("evaluacion:acta-detalle", args=[acta.pk]))
        self.assertNotContains(response_publicada, "Regenerar desde captura preliminar")

        response_post = self.client.post(
            reverse("evaluacion:acta-regenerar", args=[acta.pk]),
            follow=True,
        )
        acta.refresh_from_db()
        self.assertEqual(acta.estado_acta, Acta.ESTADO_PUBLICADO_DISCENTE)
        self.assertContains(response_post, "Solo se puede regenerar un acta en estado borrador docente.")

    def test_impide_remision_si_usuario_no_es_docente_responsable(self):
        acta = self.publicar_acta_p1()
        self.client.force_login(self.otro_docente)

        response = self.client.post(reverse("evaluacion:acta-remitir", args=[acta.pk]))

        self.assertEqual(response.status_code, 403)
        acta.refresh_from_db()
        self.assertEqual(acta.estado_acta, Acta.ESTADO_PUBLICADO_DISCENTE)

    def test_estadistica_accede_consulta_general_de_actas(self):
        acta = self.crear_acta_directa()
        self.client.force_login(self.usuario_estadistica)

        response = self.client.get(reverse("evaluacion:estadistica-actas"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Consulta de actas de calificaciones")
        self.assertContains(response, acta.asignacion_docente.programa_asignatura.materia.nombre)

    def test_estadistica_ve_detalle_en_solo_lectura(self):
        acta = self.crear_acta_directa()
        self.client.force_login(self.usuario_estadistica)

        response = self.client.get(reverse("evaluacion:acta-detalle", args=[acta.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Consulta de actas de calificaciones")
        self.assertNotContains(response, "Actas docentes")
        self.assertNotContains(response, "Regenerar desde captura preliminar")
        self.assertNotContains(response, "Publicar a discentes")
        self.assertNotContains(response, "Remitir a jefatura de carrera")
        self.assertNotContains(response, "Validar como jefatura de carrera")
        self.assertNotContains(response, "Formalizar como jefatura académica")

    def test_detalle_acta_muestra_enlace_regreso_segun_perfil_no_docente(self):
        acta = self.crear_acta_directa()
        perfiles = (
            (self.usuario_estadistica, "Consulta de actas de calificaciones"),
            (self.usuario_jefe_carrera, "Actas por validar"),
            (self.usuario_jefe_planeacion, "Consulta de actas de Planeación y Evaluación"),
            (self.usuario_jefe_academico, "Actas por formalizar"),
        )

        for usuario, texto_esperado in perfiles:
            with self.subTest(usuario=usuario.username):
                self.client.force_login(usuario)
                response = self.client.get(reverse("evaluacion:acta-detalle", args=[acta.pk]))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, texto_esperado)
                self.assertNotContains(response, "Actas docentes")

    def test_estadistica_no_puede_operar_flujo_de_actas_por_url_directa(self):
        acta = self.crear_acta_directa()
        self.client.force_login(self.usuario_estadistica)

        rutas = [
            "evaluacion:acta-publicar",
            "evaluacion:acta-remitir",
            "evaluacion:acta-validar-carrera",
            "evaluacion:acta-formalizar",
        ]

        for ruta in rutas:
            with self.subTest(ruta=ruta):
                response = self.client.post(reverse(ruta, args=[acta.pk]))
                self.assertEqual(response.status_code, 403)

        acta.refresh_from_db()
        self.assertEqual(acta.estado_acta, Acta.ESTADO_BORRADOR_DOCENTE)

    def test_jefatura_carrera_no_accede_a_consulta_general_de_estadistica(self):
        self.client.force_login(self.usuario_jefe_carrera)

        response = self.client.get(reverse("evaluacion:estadistica-actas"))

        self.assertEqual(response.status_code, 403)

    def test_jefatura_carrera_consulta_solo_actas_de_su_ambito(self):
        acta_propia = self.crear_acta_directa()
        acta_ajena = self.crear_acta_otra_carrera()
        self.client.force_login(self.usuario_jefe_carrera)

        response = self.client.get(reverse("evaluacion:jefatura-carrera-consulta-actas"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, acta_propia.asignacion_docente.programa_asignatura.materia.nombre)
        self.assertNotContains(response, acta_ajena.asignacion_docente.programa_asignatura.materia.nombre)

    def test_jefatura_planeacion_consulta_actas_solo_lectura_de_su_ambito(self):
        acta_propia = self.crear_acta_directa()
        acta_ajena = self.crear_acta_otra_carrera()
        self.client.force_login(self.usuario_jefe_planeacion)

        consulta = self.client.get(reverse("evaluacion:jefatura-planeacion-consulta-actas"))
        detalle = self.client.get(reverse("evaluacion:acta-detalle", args=[acta_propia.pk]))
        validar = self.client.post(reverse("evaluacion:acta-validar-carrera", args=[acta_propia.pk]))
        bandeja_validacion = self.client.get(reverse("evaluacion:jefatura-carrera-actas"))

        self.assertEqual(consulta.status_code, 200)
        self.assertContains(consulta, acta_propia.asignacion_docente.programa_asignatura.materia.nombre)
        self.assertNotContains(consulta, acta_ajena.asignacion_docente.programa_asignatura.materia.nombre)
        self.assertEqual(detalle.status_code, 200)
        self.assertContains(detalle, "Consulta de actas de Planeación y Evaluación")
        self.assertNotContains(detalle, "Validar como jefatura de carrera")
        self.assertEqual(validar.status_code, 403)
        self.assertEqual(bandeja_validacion.status_code, 403)

    def test_jefatura_planeacion_no_consulta_detalle_de_acta_ajena(self):
        acta_ajena = self.crear_acta_otra_carrera()
        self.client.force_login(self.usuario_jefe_planeacion)

        response = self.client.get(reverse("evaluacion:acta-detalle", args=[acta_ajena.pk]))

        self.assertEqual(response.status_code, 403)

    def test_jefatura_carrera_no_consulta_detalle_de_acta_ajena(self):
        acta_ajena = self.crear_acta_otra_carrera()
        self.client.force_login(self.usuario_jefe_carrera)

        response = self.client.get(reverse("evaluacion:acta-detalle", args=[acta_ajena.pk]))

        self.assertEqual(response.status_code, 403)

    def test_jefatura_carrera_no_valida_acta_ajena(self):
        acta_ajena = self.crear_acta_otra_carrera()
        self.client.force_login(self.usuario_jefe_carrera)

        response = self.client.post(reverse("evaluacion:acta-validar-carrera", args=[acta_ajena.pk]))

        self.assertEqual(response.status_code, 403)
        acta_ajena.refresh_from_db()
        self.assertEqual(acta_ajena.estado_acta, Acta.ESTADO_REMITIDO_JEFATURA_CARRERA)

    def test_impide_regenerar_despues_de_remitir(self):
        acta = self.remitir_acta_p1()

        with self.assertRaises(ValidationError):
            crear_o_regenerar_borrador_acta(
                self.asignacion,
                ComponenteEvaluacion.CORTE_P1,
                self.usuario_docente,
            )

        acta.refresh_from_db()
        self.assertTrue(acta.solo_lectura)

    def test_permite_validacion_por_jefatura_de_carrera_vigente(self):
        acta = self.remitir_acta_p1()

        validar_acta_jefatura_carrera(acta, self.usuario_jefe_carrera)

        acta.refresh_from_db()
        self.assertEqual(acta.estado_acta, Acta.ESTADO_VALIDADO_JEFATURA_CARRERA)
        self.assertTrue(
            ValidacionActa.objects.filter(
                acta=acta,
                etapa_validacion=ValidacionActa.ETAPA_JEFATURA_CARRERA,
                accion=ValidacionActa.ACCION_VALIDA,
                asignacion_cargo=self.cargo_jefe_carrera,
            ).exists()
        )

    def test_impide_formalizacion_sin_validacion_previa(self):
        acta = self.remitir_acta_p1()
        acta.estado_acta = Acta.ESTADO_VALIDADO_JEFATURA_CARRERA
        acta.save(update_fields=["estado_acta"])

        with self.assertRaises(ValidationError):
            formalizar_acta_jefatura_academica(acta, self.usuario_jefe_academico)

    def test_permite_formalizacion_por_jefatura_academica_vigente(self):
        acta = self.remitir_acta_p1()
        validar_acta_jefatura_carrera(acta, self.usuario_jefe_carrera)

        formalizar_acta_jefatura_academica(acta, self.usuario_jefe_academico)

        acta.refresh_from_db()
        self.inscripcion.refresh_from_db()
        self.assertEqual(acta.estado_acta, Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA)
        self.assertTrue(acta.solo_lectura)
        self.assertIsNone(self.inscripcion.calificacion_final)

    def test_jefatura_academica_consulta_actas_formalizadas_sin_reformalizar(self):
        acta = self.remitir_acta_p1()
        validar_acta_jefatura_carrera(acta, self.usuario_jefe_carrera)
        formalizar_acta_jefatura_academica(acta, self.usuario_jefe_academico)
        self.client.force_login(self.usuario_jefe_academico)

        response = self.client.get(reverse("evaluacion:jefatura-academica-actas"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Actas formalizadas")
        self.assertContains(response, "Consultar")
        self.assertContains(response, acta.asignacion_docente.programa_asignatura.materia.nombre)
        self.assertNotContains(response, "Formalizar como jefatura académica")

    def test_vistas_de_actas_redirigen_a_login_si_no_hay_sesion(self):
        acta = self.publicar_acta_p1()
        self.client.logout()

        detalle_response = self.client.get(reverse("evaluacion:acta-detalle", args=[acta.pk]))
        jefatura_response = self.client.get(reverse("evaluacion:jefatura-academica-actas"))

        self.assertEqual(detalle_response.status_code, 302)
        self.assertEqual(jefatura_response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), detalle_response["Location"])
        self.assertIn(reverse("usuarios:login"), jefatura_response["Location"])

    def test_actualiza_campos_oficiales_solo_al_formalizar_acta_final(self):
        self.capturar_final_completo_sin_exencion()
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_FINAL,
            self.usuario_docente,
        )
        publicar_acta(acta, self.usuario_docente)
        remitir_acta(acta, self.usuario_docente)
        validar_acta_jefatura_carrera(acta, self.usuario_jefe_carrera)

        formalizar_acta_jefatura_academica(acta, self.usuario_jefe_academico)

        self.inscripcion.refresh_from_db()
        self.assertEqual(self.inscripcion.calificacion_final, Decimal("8.6"))
        self.assertEqual(self.inscripcion.codigo_resultado_oficial, "APROBADO")
        self.assertEqual(self.inscripcion.codigo_marca, "")
        self.assertIsNotNone(self.inscripcion.cerrado_en)

    def post_json(self, path, payload=None):
        return self.client.post(
            path,
            data=json.dumps(payload or {}),
            content_type="application/json",
        )

    def test_api_anonimo_no_accede_a_operacion_docente(self):
        self.client.logout()

        response = self.client.get("/api/docente/asignaciones/")

        self.assertEqual(response.status_code, 401)

    def test_api_docente_lista_solo_asignaciones_propias_sin_matricula(self):
        self.client.force_login(self.usuario_docente)

        response = self.client.get("/api/docente/asignaciones/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["items"][0]["asignacion_id"], self.asignacion.id)
        self.assertNotIn("CAP0001", response.content.decode())

    def test_api_docente_no_accede_a_asignacion_ajena(self):
        self.client.force_login(self.otro_docente)

        response = self.client.get(f"/api/docente/asignaciones/{self.asignacion.id}/")

        self.assertEqual(response.status_code, 403)

    def test_api_docente_guarda_y_borra_captura_preliminar(self):
        self.client.force_login(self.usuario_docente)
        path = f"/api/docente/asignaciones/{self.asignacion.id}/captura/P1/"

        response = self.post_json(
            path,
            {
                "valores": [
                    {
                        "inscripcion_id": self.inscripcion.id,
                        "componente_id": self.componente_p1_tareas.id,
                        "valor": "8.5",
                    }
                ]
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            CapturaCalificacionPreliminar.objects.filter(
                inscripcion_materia=self.inscripcion,
                componente=self.componente_p1_tareas,
                valor=Decimal("8.5"),
            ).exists()
        )

        response = self.post_json(
            path,
            {
                "valores": [
                    {
                        "inscripcion_id": self.inscripcion.id,
                        "componente_id": self.componente_p1_tareas.id,
                        "valor": "",
                    }
                ]
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            CapturaCalificacionPreliminar.objects.filter(
                inscripcion_materia=self.inscripcion,
                componente=self.componente_p1_tareas,
            ).exists()
        )

    def test_api_docente_rechaza_captura_fuera_de_rango(self):
        self.client.force_login(self.usuario_docente)

        response = self.post_json(
            f"/api/docente/asignaciones/{self.asignacion.id}/captura/P1/",
            {
                "valores": [
                    {
                        "inscripcion_id": self.inscripcion.id,
                        "componente_id": self.componente_p1_tareas.id,
                        "valor": "12.0",
                    }
                ]
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(CapturaCalificacionPreliminar.objects.exists())

    def test_api_captura_bloqueada_si_existe_acta_avanzada(self):
        acta = self.publicar_acta_p1()
        self.client.force_login(self.usuario_docente)

        response = self.post_json(
            f"/api/docente/asignaciones/{self.asignacion.id}/captura/P1/",
            {
                "valores": [
                    {
                        "inscripcion_id": self.inscripcion.id,
                        "componente_id": self.componente_p1_tareas.id,
                        "valor": "9.0",
                    }
                ]
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(acta.estado_acta, Acta.ESTADO_PUBLICADO_DISCENTE)

    def test_api_docente_genera_publica_y_remite_acta(self):
        self.capturar_p1_completo()
        self.client.force_login(self.usuario_docente)

        generar = self.post_json(
            f"/api/docente/asignaciones/{self.asignacion.id}/actas/generar/",
            {"corte_codigo": "P1"},
        )
        acta_id = generar.json()["item"]["acta_id"]
        publicar = self.post_json(f"/api/docente/actas/{acta_id}/publicar/")
        remitir = self.post_json(f"/api/docente/actas/{acta_id}/remitir/")

        self.assertEqual(generar.status_code, 200)
        self.assertEqual(publicar.status_code, 200)
        self.assertEqual(remitir.status_code, 200)
        self.assertEqual(remitir.json()["item"]["estado_acta"], Acta.ESTADO_REMITIDO_JEFATURA_CARRERA)

    def test_api_discente_lista_solo_sus_actas_y_no_muestra_matricula(self):
        acta = self.publicar_acta_p1()
        self.client.force_login(self.usuario_discente)

        response = self.client.get("/api/discente/actas/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["acta_id"], acta.id)
        self.assertNotIn("CAP0001", response.content.decode())

    def test_api_discente_inconformidad_sin_comentario_se_rechaza(self):
        acta = self.publicar_acta_p1()
        detalle = acta.detalles.get()
        self.client.force_login(self.usuario_discente)

        response = self.post_json(
            f"/api/discente/actas/{detalle.id}/conformidad/",
            {"tipo_conformidad": ConformidadDiscente.ESTADO_INCONFORME, "comentario": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(detalle.conformidades.exists())

    def test_api_jefatura_carrera_valida_acta_remitida_de_su_ambito(self):
        acta = self.remitir_acta_p1()
        self.client.force_login(self.usuario_jefe_carrera)

        response = self.post_json(f"/api/jefatura-carrera/actas/{acta.id}/validar/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["item"]["estado_acta"], Acta.ESTADO_VALIDADO_JEFATURA_CARRERA)

    def test_api_estadistica_consulta_pero_no_valida(self):
        acta = self.remitir_acta_p1()
        self.client.force_login(self.usuario_estadistica)

        listado = self.client.get("/api/estadistica/actas/")
        validar = self.post_json(f"/api/jefatura-carrera/actas/{acta.id}/validar/")

        self.assertEqual(listado.status_code, 200)
        self.assertEqual(validar.status_code, 403)

    def test_api_jefatura_academica_formaliza_acta_final_y_actualiza_oficiales(self):
        self.capturar_final_completo_sin_exencion()
        acta = crear_o_regenerar_borrador_acta(
            self.asignacion,
            ComponenteEvaluacion.CORTE_FINAL,
            self.usuario_docente,
        )
        publicar_acta(acta, self.usuario_docente)
        remitir_acta(acta, self.usuario_docente)
        validar_acta_jefatura_carrera(acta, self.usuario_jefe_carrera)
        self.client.force_login(self.usuario_jefe_academico)

        response = self.post_json(f"/api/jefatura-academica/actas/{acta.id}/formalizar/")

        self.assertEqual(response.status_code, 200)
        self.inscripcion.refresh_from_db()
        self.assertEqual(self.inscripcion.calificacion_final, Decimal("8.6"))
