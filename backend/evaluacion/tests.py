from django.test import TestCase
from django.core.exceptions import ValidationError

from catalogos.models import Carrera, Materia, PlanEstudios, ProgramaAsignatura
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
