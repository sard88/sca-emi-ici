from datetime import date, timedelta
from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.test import TestCase
from django.utils import timezone

from .admin import AntiguedadAdmin, GrupoAcademicoAdmin, MateriaAdmin, ProgramaAsignaturaAdmin
from .forms import (
    AntiguedadAdminForm,
    MateriaAdminForm,
    ProgramaAsignaturaAdminForm,
    PlanEstudiosAdminForm,
    build_year_choices,
)
from .models import (
    Antiguedad,
    Carrera,
    GRUPO_SEMESTRE_MAX,
    GRUPO_SEMESTRE_MIN,
    GrupoAcademico,
    Materia,
    ProgramaAsignatura,
    MATERIA_PLAN_SEMESTRE_MAX,
    MATERIA_PLAN_SEMESTRE_MIN,
    PeriodoEscolar,
    PlanEstudios,
    build_anio_escolar_choices,
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
        self.antiguedad = Antiguedad.objects.create(
            plan_estudios=self.plan,
            clave="GEN_2025",
            nombre="Antiguedad 2025",
            anio_inicio=2025,
            anio_fin=2029,
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="PERIODO_2025-1",
            anio_escolar="2025-2026",
            periodo_academico=1,
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2026, 1, 31),
        )

    def _build_instances(self, value):
        return [
            Carrera(clave=value, nombre="Carrera prueba"),
            PlanEstudios(carrera=self.carrera, clave=value, nombre="Plan prueba"),
            Antiguedad(
                plan_estudios=self.plan,
                clave=value,
                nombre="Antiguedad prueba",
                anio_inicio=2025,
                anio_fin=2029,
            ),
            PeriodoEscolar(
                clave=value,
                anio_escolar="2025-2026",
                periodo_academico=1,
                fecha_inicio=date(2025, 8, 1),
                fecha_fin=date(2026, 1, 31),
            ),
            GrupoAcademico(
                clave_grupo=value,
                antiguedad=self.antiguedad,
                periodo=self.periodo,
                semestre_numero=1,
            ),
            Materia(clave=value, nombre="Materia prueba", horas_totales=64),
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
            fields=["clave_grupo", "antiguedad", "periodo", "semestre_numero", "estado", "cupo_maximo"],
        )
        form = grupo_form_class(
            data={
                "clave_grupo": "GRUPO/01",
                "antiguedad": self.antiguedad.pk,
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
    def test_antiguedad_model_uses_antiguedad_labels(self):
        self.assertEqual(Antiguedad._meta.verbose_name, "Antigüedad")
        self.assertEqual(Antiguedad._meta.verbose_name_plural, "Antigüedades")

    def test_grupo_academico_form_uses_antiguedad_field_label(self):
        grupo_form_class = modelform_factory(
            GrupoAcademico,
            fields=["clave_grupo", "antiguedad", "periodo", "semestre_numero", "estado", "cupo_maximo"],
        )
        form = grupo_form_class()

        self.assertEqual(form.fields["antiguedad"].label, "Antigüedad")


class GrupoAcademicoValidationTests(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(clave="GA_BASE", nombre="Carrera base")
        self.plan = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="GA_PLAN",
            nombre="Plan base",
        )
        self.antiguedad = Antiguedad.objects.create(
            plan_estudios=self.plan,
            clave="GA_GEN",
            nombre="Antiguedad base",
            anio_inicio=2025,
            anio_fin=2029,
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="GA_PERIODO",
            anio_escolar="2025-2026",
            periodo_academico=1,
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2026, 1, 31),
        )

    def _build_grupo(self, **overrides):
        payload = {
            "clave_grupo": "GA_GRUPO",
            "antiguedad": self.antiguedad,
            "periodo": self.periodo,
            "semestre_numero": 1,
            "estado": "activo",
            "cupo_maximo": 30,
        }
        payload.update(overrides)
        return GrupoAcademico(**payload)

    def _build_form_data(self, **overrides):
        payload = {
            "clave_grupo": "GA_GRUPO_FORM",
            "antiguedad": self.antiguedad.pk,
            "periodo": self.periodo.pk,
            "semestre_numero": 1,
            "estado": "activo",
            "cupo_maximo": 30,
        }
        payload.update(overrides)
        return payload

    def test_grupo_academico_usa_label_semestre_en_modelo_y_admin(self):
        admin = GrupoAcademicoAdmin(GrupoAcademico, AdminSite())
        admin_form_class = admin.get_form(request=None)
        form = admin_form_class()

        self.assertEqual(GrupoAcademico._meta.get_field("semestre_numero").verbose_name, "Semestre")
        self.assertEqual(form.fields["semestre_numero"].label, "Semestre")

    def test_grupo_academico_admin_usa_lista_del_1_al_12_para_semestre(self):
        admin = GrupoAcademicoAdmin(GrupoAcademico, AdminSite())
        admin_form_class = admin.get_form(request=None)
        form = admin_form_class()
        choice_values = [value for value, _ in form.fields["semestre_numero"].choices if isinstance(value, int)]

        self.assertEqual(form.fields["semestre_numero"].widget.__class__.__name__, "Select")
        self.assertEqual(
            choice_values,
            list(range(GRUPO_SEMESTRE_MIN, GRUPO_SEMESTRE_MAX + 1)),
        )

    def test_grupo_academico_rechaza_semestre_fuera_de_rango(self):
        for value in (0, -1, 13):
            with self.subTest(value=value):
                grupo = self._build_grupo(semestre_numero=value)

                with self.assertRaises(ValidationError) as exc:
                    grupo.full_clean()

                self.assertIn("semestre_numero", exc.exception.message_dict)

    def test_grupo_academico_save_aplica_validacion_backend_de_semestre(self):
        with self.assertRaises(ValidationError):
            self._build_grupo(semestre_numero=15).save()

    def test_grupo_academico_rechaza_cupo_maximo_no_positivo(self):
        for value in (0, -5):
            with self.subTest(value=value):
                grupo = self._build_grupo(cupo_maximo=value)

                with self.assertRaises(ValidationError) as exc:
                    grupo.full_clean()

                self.assertIn("cupo_maximo", exc.exception.message_dict)

    def test_grupo_academico_form_rechaza_cupo_maximo_no_positivo(self):
        grupo_form_class = modelform_factory(
            GrupoAcademico,
            fields=["clave_grupo", "antiguedad", "periodo", "semestre_numero", "estado", "cupo_maximo"],
        )
        form = grupo_form_class(data=self._build_form_data(cupo_maximo=0))

        self.assertFalse(form.is_valid())
        self.assertIn("cupo_maximo", form.errors)

    def test_grupo_academico_form_permite_cupo_maximo_vacio(self):
        grupo_form_class = modelform_factory(
            GrupoAcademico,
            fields=["clave_grupo", "antiguedad", "periodo", "semestre_numero", "estado", "cupo_maximo"],
        )
        form = grupo_form_class(data=self._build_form_data(cupo_maximo=""))

        self.assertTrue(form.is_valid(), form.errors)


class VigenciaCatalogosTests(TestCase):
    def test_creacion_autocompleta_vigente_desde_si_se_omite(self):
        hoy = timezone.localdate()

        carrera = Carrera.objects.create(clave="VIGENCIA_01", nombre="Carrera vigencia")

        self.assertEqual(carrera.vigente_desde, hoy)
        self.assertIsNone(carrera.vigente_hasta)

    def test_edicion_respeta_vigente_desde_existente(self):
        fecha_existente = timezone.localdate() - timedelta(days=10)
        carrera = Carrera.objects.create(
            clave="VIGENCIA_02",
            nombre="Carrera original",
            vigente_desde=fecha_existente,
        )

        carrera.nombre = "Carrera actualizada"
        carrera.save()
        carrera.refresh_from_db()

        self.assertEqual(carrera.vigente_desde, fecha_existente)

    def test_edicion_de_registro_legado_sin_vigente_desde_lo_autocompleta(self):
        carrera = Carrera.objects.create(clave="VIGENCIA_03", nombre="Carrera legado")
        Carrera.objects.filter(pk=carrera.pk).update(vigente_desde=None)

        carrera.refresh_from_db()
        self.assertIsNone(carrera.vigente_desde)

        carrera.nombre = "Carrera legado editada"
        carrera.save()
        carrera.refresh_from_db()

        self.assertEqual(carrera.vigente_desde, timezone.localdate())

    def test_modelform_no_exige_vigencias_y_autocompleta_vigente_desde(self):
        carrera_form_class = modelform_factory(
            Carrera,
            fields=["clave", "nombre", "estado", "vigente_desde", "vigente_hasta"],
        )
        form = carrera_form_class(
            data={
                "clave": "VIGENCIA_04",
                "nombre": "Carrera formulario",
                "estado": "activo",
                "vigente_desde": "",
                "vigente_hasta": "",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        carrera = form.save()

        self.assertEqual(carrera.vigente_desde, timezone.localdate())
        self.assertIsNone(carrera.vigente_hasta)

    def test_vigente_hasta_sigue_validando_consistencia_temporal(self):
        hoy = timezone.localdate()
        carrera = Carrera(
            clave="VIGENCIA_05",
            nombre="Carrera invalida",
            vigente_desde=hoy,
            vigente_hasta=hoy - timedelta(days=1),
        )

        with self.assertRaises(ValidationError) as exc:
            carrera.full_clean()

        self.assertIn("vigente_hasta", exc.exception.message_dict)


class AnioUiTests(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(clave="ANIO_BASE", nombre="Carrera base")
        self.plan = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="ANIO_PLAN",
            nombre="Plan base",
        )

    def test_antiguedad_model_uses_ano_labels(self):
        self.assertEqual(Antiguedad._meta.get_field("anio_inicio").verbose_name, "Año de inicio")
        self.assertEqual(Antiguedad._meta.get_field("anio_fin").verbose_name, "Año de fin")

    def test_antiguedad_model_uses_ano_error_message(self):
        antiguedad = Antiguedad(
            plan_estudios=self.plan,
            clave="ANIO_ERR",
            nombre="Antiguedad invalida",
            anio_inicio=2026,
            anio_fin=2025,
        )

        with self.assertRaises(ValidationError) as exc:
            antiguedad.full_clean()

        self.assertIn("anio_fin", exc.exception.message_dict)
        self.assertIn("No puede ser menor al año de inicio.", exc.exception.message_dict["anio_fin"])

    def test_antiguedad_admin_form_uses_select_widgets_for_years(self):
        form = AntiguedadAdminForm()

        self.assertEqual(form.fields["anio_inicio"].label, "Año de inicio")
        self.assertEqual(form.fields["anio_fin"].label, "Año de fin")
        self.assertEqual(form.fields["anio_inicio"].widget.__class__.__name__, "Select")
        self.assertEqual(form.fields["anio_fin"].widget.__class__.__name__, "Select")

    def test_antiguedad_admin_form_saves_selected_years(self):
        form = AntiguedadAdminForm(
            data={
                "clave": "ANIO_FORM",
                "nombre": "Antiguedad formulario",
                "plan_estudios": self.plan.pk,
                "anio_inicio": "2024",
                "anio_fin": "2028",
                "estado": "activo",
                "vigente_desde": "",
                "vigente_hasta": "",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        antiguedad = form.save()

        self.assertEqual(antiguedad.anio_inicio, 2024)
        self.assertEqual(antiguedad.anio_fin, 2028)

    def test_antiguedad_admin_form_keeps_legacy_year_available(self):
        antiguedad = Antiguedad.objects.create(
            plan_estudios=self.plan,
            clave="ANIO_LEGACY",
            nombre="Antiguedad legacy",
            anio_inicio=0,
            anio_fin=2029,
        )

        form = AntiguedadAdminForm(instance=antiguedad)
        inicio_choices = [value for value, _ in form.fields["anio_inicio"].choices]

        self.assertIn(0, inicio_choices)

    def test_build_year_choices_uses_dynamic_range(self):
        current_year = timezone.localdate().year
        choices = build_year_choices()
        choice_values = [value for value, _ in choices if value != ""]

        self.assertEqual(choice_values[0], current_year - 20)
        self.assertEqual(choice_values[-1], current_year + 10)


class PeriodoEscolarValidationTests(TestCase):
    def test_periodo_escolar_usa_label_periodo_academico(self):
        periodo_form_class = modelform_factory(
            PeriodoEscolar,
            fields=["clave", "anio_escolar", "periodo_academico", "fecha_inicio", "fecha_fin", "estado"],
        )
        form = periodo_form_class()

        self.assertEqual(
            PeriodoEscolar._meta.get_field("periodo_academico").verbose_name,
            "Periodo académico",
        )
        self.assertEqual(form.fields["periodo_academico"].label, "Periodo académico")

    def test_periodo_escolar_form_requiere_campos_obligatorios(self):
        periodo_form_class = modelform_factory(
            PeriodoEscolar,
            fields=["clave", "anio_escolar", "periodo_academico", "fecha_inicio", "fecha_fin", "estado"],
        )
        form = periodo_form_class(
            data={
                "clave": "PE_REQ",
                "anio_escolar": "",
                "periodo_academico": "",
                "fecha_inicio": "",
                "fecha_fin": "",
                "estado": "activo",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("anio_escolar", form.errors)
        self.assertIn("periodo_academico", form.errors)
        self.assertIn("fecha_inicio", form.errors)
        self.assertIn("fecha_fin", form.errors)

    def test_periodo_escolar_acepta_fechas_validas_dentro_del_ciclo(self):
        periodo = PeriodoEscolar.objects.create(
            clave="PE_VALIDO",
            anio_escolar="2023-2024",
            periodo_academico=1,
            fecha_inicio=date(2023, 8, 1),
            fecha_fin=date(2024, 7, 31),
            estado="activo",
        )

        self.assertEqual(periodo.anio_escolar, "2023-2024")

    def test_periodo_escolar_rechaza_fechas_iguales(self):
        periodo = PeriodoEscolar(
            clave="PE_IGUAL",
            anio_escolar="2023-2024",
            periodo_academico=1,
            fecha_inicio=date(2023, 8, 1),
            fecha_fin=date(2023, 8, 1),
            estado="activo",
        )

        with self.assertRaises(ValidationError) as exc:
            periodo.full_clean()

        self.assertIn("fecha_fin", exc.exception.message_dict)
        self.assertIn("Debe ser posterior a fecha_inicio.", exc.exception.message_dict["fecha_fin"])

    def test_periodo_escolar_rechaza_inicio_antes_del_ciclo(self):
        periodo = PeriodoEscolar(
            clave="PE_INICIO",
            anio_escolar="2023-2024",
            periodo_academico=1,
            fecha_inicio=date(2023, 7, 31),
            fecha_fin=date(2024, 1, 15),
            estado="activo",
        )

        with self.assertRaises(ValidationError) as exc:
            periodo.full_clean()

        self.assertIn("fecha_inicio", exc.exception.message_dict)
        self.assertIn(
            "No puede ser anterior al inicio del ciclo 2023-2024.",
            exc.exception.message_dict["fecha_inicio"],
        )

    def test_periodo_escolar_rechaza_fin_fuera_del_ciclo(self):
        periodo = PeriodoEscolar(
            clave="PE_FIN",
            anio_escolar="2023-2024",
            periodo_academico=2,
            fecha_inicio=date(2024, 1, 15),
            fecha_fin=date(2024, 8, 1),
            estado="activo",
        )

        with self.assertRaises(ValidationError) as exc:
            periodo.full_clean()

        self.assertIn("fecha_fin", exc.exception.message_dict)
        self.assertIn(
            "No puede ser posterior al cierre del ciclo 2023-2024.",
            exc.exception.message_dict["fecha_fin"],
        )

    def test_periodo_escolar_save_aplica_validacion_backend(self):
        with self.assertRaises(ValidationError):
            PeriodoEscolar.objects.create(
                clave="PE_BACK",
                anio_escolar="2023-2024",
                periodo_academico=1,
                fecha_inicio=date(2024, 7, 31),
                fecha_fin=date(2024, 7, 31),
                estado="activo",
            )

    def test_anio_escolar_choices_incluye_historicos_y_futuros(self):
        current_year = timezone.localdate().year
        choices = build_anio_escolar_choices()
        choice_values = [value for value, _ in choices]

        self.assertIn("2020-2021", choice_values)
        self.assertIn(f"{current_year + 9}-{current_year + 10}", choice_values)


class PlanEstudiosCarreraActivaTests(TestCase):
    def setUp(self):
        self.carrera_activa = Carrera.objects.create(
            clave="ICI",
            nombre="Ingenieria en Ciberseguridad",
            estado="activo",
        )
        self.carrera_inactiva = Carrera.objects.create(
            clave="II",
            nombre="Ingenieria Industrial",
            estado="inactivo",
        )

    def test_plan_estudios_rechaza_carrera_inactiva_en_modelo(self):
        plan = PlanEstudios(
            clave="PE-II-2026",
            nombre="Plan II",
            carrera=self.carrera_inactiva,
            estado="activo",
        )

        with self.assertRaises(ValidationError) as error:
            plan.full_clean()

        self.assertEqual(
            error.exception.message_dict["carrera"],
            ["Solo se puede asignar una carrera activa."],
        )

    def test_plan_estudios_no_guarda_carrera_inactiva_por_save_directo(self):
        with self.assertRaises(ValidationError):
            PlanEstudios.objects.create(
                clave="PE-II-2026",
                nombre="Plan II",
                carrera=self.carrera_inactiva,
                estado="activo",
            )

    def test_formulario_muestra_solo_carreras_activas_en_creacion(self):
        form = PlanEstudiosAdminForm()

        self.assertQuerySetEqual(
            form.fields["carrera"].queryset,
            [self.carrera_activa],
            transform=lambda carrera: carrera,
        )

    def test_formulario_de_edicion_legacy_no_lista_carrera_inactiva(self):
        plan = PlanEstudios.objects.create(
            clave="PE-ICI-2026",
            nombre="Plan ICI",
            carrera=self.carrera_activa,
            estado="activo",
        )
        PlanEstudios.objects.filter(pk=plan.pk).update(carrera=self.carrera_inactiva)
        plan.refresh_from_db()

        form = PlanEstudiosAdminForm(instance=plan)

        self.assertQuerySetEqual(
            form.fields["carrera"].queryset,
            [self.carrera_activa],
            transform=lambda carrera: carrera,
        )
        self.assertIn("est\u00e1 inactiva", form.fields["carrera"].help_text)


class ProgramaAsignaturaTests(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(
            clave="MP_CARRERA",
            nombre="Carrera MP",
            estado="activo",
        )
        self.plan_activo = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="MP_PLAN_ACT",
            nombre="Plan activo",
            estado="activo",
        )
        self.plan_inactivo = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="MP_PLAN_INA",
            nombre="Plan inactivo",
            estado="inactivo",
        )
        self.materia_activa = Materia.objects.create(
            clave="MP_MAT_ACT",
            nombre="Materia activa",
            horas_totales=64,
            estado="activo",
        )
        self.materia_inactiva = Materia.objects.create(
            clave="MP_MAT_INA",
            nombre="Materia inactiva",
            horas_totales=64,
            estado="inactivo",
        )

    def _build_programa_asignatura(self, **overrides):
        payload = {
            "plan_estudios": self.plan_activo,
            "materia": self.materia_activa,
            "semestre_numero": 1,
            "anio_formacion": 1,
            "obligatoria": True,
        }
        payload.update(overrides)
        return ProgramaAsignatura(**payload)

    def _build_form_data(self, **overrides):
        payload = {
            "plan_estudios": self.plan_activo.pk,
            "materia": self.materia_activa.pk,
            "semestre_numero": 1,
            "anio_formacion": 1,
            "obligatoria": "on",
        }
        payload.update(overrides)
        return payload

    def test_programa_asignatura_usa_programas_de_asignatura_en_ui_visible(self):
        self.assertEqual(ProgramaAsignatura._meta.verbose_name, "Programa de asignatura")
        self.assertEqual(ProgramaAsignatura._meta.verbose_name_plural, "Programas de asignatura")

    def test_programa_asignatura_admin_form_filtra_planes_y_materias_activas(self):
        form = ProgramaAsignaturaAdminForm()

        self.assertQuerySetEqual(
            form.fields["plan_estudios"].queryset,
            [self.plan_activo],
            transform=lambda plan: plan,
        )
        self.assertQuerySetEqual(
            form.fields["materia"].queryset,
            [self.materia_activa],
            transform=lambda materia: materia,
        )

    def test_programa_asignatura_admin_form_muestra_campos_derivados_solo_lectura(self):
        form = ProgramaAsignaturaAdminForm()

        self.assertTrue(form.fields["obligatoria"].disabled)
        self.assertTrue(form.fields["anio_formacion"].disabled)
        self.assertTrue(form.fields["obligatoria"].initial)
        self.assertEqual(form.fields["anio_formacion"].label, "Año de formación")

    def test_programa_asignatura_admin_usa_semestre_como_lista_del_1_al_12(self):
        admin = ProgramaAsignaturaAdmin(ProgramaAsignatura, AdminSite())
        admin_form_class = admin.get_form(request=None)
        form = admin_form_class()
        choice_values = [value for value, _ in form.fields["semestre_numero"].choices if isinstance(value, int)]

        self.assertEqual(form.fields["semestre_numero"].widget.__class__.__name__, "Select")
        self.assertEqual(
            choice_values,
            list(range(MATERIA_PLAN_SEMESTRE_MIN, MATERIA_PLAN_SEMESTRE_MAX + 1)),
        )

    def test_programa_asignatura_backend_rechaza_plan_inactivo(self):
        programa_asignatura = self._build_programa_asignatura(plan_estudios=self.plan_inactivo)

        with self.assertRaises(ValidationError) as exc:
            programa_asignatura.full_clean()

        self.assertEqual(
            exc.exception.message_dict["plan_estudios"],
            ["Solo se puede asignar un plan de estudios activo."],
        )

    def test_programa_asignatura_backend_rechaza_materia_inactiva(self):
        programa_asignatura = self._build_programa_asignatura(materia=self.materia_inactiva)

        with self.assertRaises(ValidationError) as exc:
            programa_asignatura.full_clean()

        self.assertEqual(
            exc.exception.message_dict["materia"],
            ["Solo se puede asignar una materia activa."],
        )

    def test_programa_asignatura_rechaza_semestres_fuera_de_rango(self):
        for value in (0, -1, 13):
            with self.subTest(value=value):
                programa_asignatura = self._build_programa_asignatura(semestre_numero=value)

                with self.assertRaises(ValidationError) as exc:
                    programa_asignatura.full_clean()

                self.assertIn("semestre_numero", exc.exception.message_dict)

    def test_programa_asignatura_calcula_anio_formacion_desde_semestre(self):
        programa_asignatura = self._build_programa_asignatura(semestre_numero=5, anio_formacion=1)
        programa_asignatura.full_clean()

        self.assertEqual(programa_asignatura.anio_formacion, 3)

    def test_programa_asignatura_save_fuerza_obligatoria_activa(self):
        programa_asignatura = self._build_programa_asignatura(
            obligatoria=False,
            semestre_numero=6,
            anio_formacion=1,
        )
        programa_asignatura.save()
        programa_asignatura.refresh_from_db()

        self.assertTrue(programa_asignatura.obligatoria)
        self.assertEqual(programa_asignatura.anio_formacion, 3)

    def test_programa_asignatura_form_calcula_anio_y_fuerza_obligatoria(self):
        form = ProgramaAsignaturaAdminForm(
            data=self._build_form_data(
                semestre_numero=12,
                anio_formacion=2,
            )
        )

        self.assertTrue(form.is_valid(), form.errors)
        programa_asignatura = form.save()

        self.assertEqual(programa_asignatura.anio_formacion, 6)
        self.assertTrue(programa_asignatura.obligatoria)

    def test_programa_asignatura_form_de_edicion_legacy_muestra_ayuda_si_hay_relaciones_inactivas(self):
        programa_asignatura = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan_activo,
            materia=self.materia_activa,
            semestre_numero=2,
            anio_formacion=1,
            obligatoria=True,
        )
        ProgramaAsignatura.objects.filter(pk=programa_asignatura.pk).update(
            plan_estudios=self.plan_inactivo,
            materia=self.materia_inactiva,
        )
        programa_asignatura.refresh_from_db()

        form = ProgramaAsignaturaAdminForm(instance=programa_asignatura)

        self.assertIn("inactivo", form.fields["plan_estudios"].help_text)
        self.assertIn("inactiva", form.fields["materia"].help_text)


class MateriaCreditosTests(TestCase):
    def test_materia_calcula_creditos_en_creacion(self):
        materia = Materia.objects.create(
            clave="MAT_AUTO_01",
            nombre="Materia automatica",
            horas_totales=64,
        )

        self.assertEqual(materia.creditos, Decimal("4.00"))

    def test_materia_recalcula_creditos_en_edicion(self):
        materia = Materia.objects.create(
            clave="MAT_AUTO_02",
            nombre="Materia editable",
            horas_totales=32,
        )

        materia.horas_totales = 48
        materia.save()
        materia.refresh_from_db()

        self.assertEqual(materia.creditos, Decimal("3.00"))

    def test_materia_redondea_creditos_a_dos_decimales(self):
        materia = Materia.objects.create(
            clave="MAT_AUTO_03",
            nombre="Materia redondeo",
            horas_totales=23,
        )

        self.assertEqual(materia.creditos, Decimal("1.44"))

    def test_materia_redondea_medio_con_dos_decimales(self):
        materia = Materia.objects.create(
            clave="MAT_AUTO_031",
            nombre="Materia medio arriba",
            horas_totales=8,
        )

        self.assertEqual(materia.creditos, Decimal("0.50"))

    def test_materia_redondea_hacia_arriba_en_la_segunda_cifra_decimal(self):
        materia = Materia.objects.create(
            clave="MAT_AUTO_032",
            nombre="Materia abajo",
            horas_totales=7,
        )

        self.assertEqual(materia.creditos, Decimal("0.44"))

    def test_materia_rechaza_horas_totales_en_cero(self):
        materia = Materia(
            clave="MAT_AUTO_04",
            nombre="Materia invalida",
            horas_totales=0,
        )

        with self.assertRaises(ValidationError) as exc:
            materia.full_clean()

        self.assertIn("horas_totales", exc.exception.message_dict)

    def test_materia_rechaza_horas_totales_negativas(self):
        materia = Materia(
            clave="MAT_AUTO_05",
            nombre="Materia negativa",
            horas_totales=-4,
        )

        with self.assertRaises(ValidationError) as exc:
            materia.full_clean()

        self.assertIn("horas_totales", exc.exception.message_dict)

    def test_materia_admin_form_no_expone_creditos_editables(self):
        form = MateriaAdminForm()

        self.assertNotIn("creditos", form.fields)

    def test_materia_admin_form_rechaza_horas_totales_en_cero(self):
        form = MateriaAdminForm(
            data={
                "clave": "MAT_AUTO_06",
                "nombre": "Materia admin",
                "horas_totales": 0,
                "estado": "activo",
                "vigente_desde": "",
                "vigente_hasta": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("horas_totales", form.errors)

    def test_materia_admin_usa_creditos_como_solo_lectura(self):
        admin = MateriaAdmin(Materia, AdminSite())

        self.assertIn("creditos", admin.get_readonly_fields(request=None))
