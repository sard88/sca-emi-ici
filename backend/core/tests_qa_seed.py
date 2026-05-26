from io import StringIO

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

from catalogos.models import Carrera, GrupoAcademico, Materia, PeriodoEscolar, PlanEstudios, ProgramaAsignatura
from evaluacion.models import Acta, EsquemaEvaluacion
from relaciones.models import AsignacionDocente, Discente, InscripcionMateria
from usuarios.models import AsignacionCargo, Usuario


class SeedDemoQaIntegralTests(TestCase):
    def test_dry_run_no_escribe_datos(self):
        out = StringIO()

        call_command("seed_demo_qa_integral", "--size", "small", "--dry-run", stdout=out)

        self.assertIn("DRY-RUN Bloque 11A", out.getvalue())
        self.assertFalse(Carrera.objects.filter(clave__startswith="QA_").exists())
        self.assertFalse(Usuario.objects.filter(username__startswith="qa_").exists())

    def test_size_small_crea_dataset_minimo(self):
        out = StringIO()

        call_command("seed_demo_qa_integral", "--size", "small", stdout=out)

        self.assertTrue(Carrera.objects.filter(clave="QA_ICI").exists())
        self.assertTrue(PlanEstudios.objects.filter(clave="QA_PLAN_ICI_2026").exists())
        self.assertTrue(PeriodoEscolar.objects.filter(clave="QA_2026_1").exists())
        self.assertTrue(GrupoAcademico.objects.filter(clave_grupo="QA_ICI_4A").exists())
        self.assertTrue(Materia.objects.filter(clave="QA_ICI_S04_M01").exists())
        self.assertTrue(ProgramaAsignatura.objects.filter(materia__clave="QA_ICI_S04_M01").exists())
        self.assertTrue(EsquemaEvaluacion.objects.filter(programa_asignatura__materia__clave="QA_ICI_S04_M01").exists())
        self.assertTrue(Usuario.objects.filter(username="qa_admin", is_superuser=True).exists())
        self.assertTrue(Usuario.objects.filter(username="qa_docente_ici_01", groups__name="DOCENTE").exists())
        self.assertTrue(Usuario.objects.filter(username="qa_discente_ici_4a_01", groups__name="DISCENTE").exists())
        self.assertTrue(Discente.objects.filter(matricula__startswith="QA-MAT-ICI-4A").exists())
        self.assertTrue(AsignacionDocente.objects.filter(grupo_academico__clave_grupo="QA_ICI_4A").exists())
        self.assertTrue(InscripcionMateria.objects.filter(discente__matricula__startswith="QA-MAT-ICI-4A").exists())
        self.assertTrue(Acta.objects.filter(asignacion_docente__grupo_academico__clave_grupo__startswith="QA_").exists())

    def test_seed_es_idempotente(self):
        call_command("seed_demo_qa_integral", "--size", "small", stdout=StringIO())
        counts = {
            "usuarios": Usuario.objects.filter(username__startswith="qa_").count(),
            "carreras": Carrera.objects.filter(clave__startswith="QA_").count(),
            "grupos": GrupoAcademico.objects.filter(clave_grupo__startswith="QA_").count(),
            "inscripciones": InscripcionMateria.objects.filter(discente__matricula__startswith="QA-MAT-").count(),
        }

        call_command("seed_demo_qa_integral", "--size", "small", stdout=StringIO())

        self.assertEqual(counts["usuarios"], Usuario.objects.filter(username__startswith="qa_").count())
        self.assertEqual(counts["carreras"], Carrera.objects.filter(clave__startswith="QA_").count())
        self.assertEqual(counts["grupos"], GrupoAcademico.objects.filter(clave_grupo__startswith="QA_").count())
        self.assertEqual(counts["inscripciones"], InscripcionMateria.objects.filter(discente__matricula__startswith="QA-MAT-").count())

    def test_reset_qa_no_toca_carrera_real(self):
        Carrera.objects.create(clave="REAL_ICI", nombre="Carrera real", estado="activo")
        call_command("seed_demo_qa_integral", "--size", "small", stdout=StringIO())

        call_command("seed_demo_qa_integral", "--size", "small", "--reset-qa", stdout=StringIO())

        self.assertTrue(Carrera.objects.filter(clave="REAL_ICI", estado="activo").exists())
        self.assertTrue(Carrera.objects.filter(clave="QA_ICI", estado="activo").exists())

    def test_no_asigna_cargos_a_discentes(self):
        call_command("seed_demo_qa_integral", "--size", "small", stdout=StringIO())

        discente_users = Usuario.objects.filter(username__startswith="qa_discente_")

        self.assertFalse(AsignacionCargo.objects.filter(usuario__in=discente_users).exists())
        self.assertTrue(Group.objects.filter(name="DISCENTE").exists())
