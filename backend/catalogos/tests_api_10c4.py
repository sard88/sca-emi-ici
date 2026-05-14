from datetime import date

from django.contrib.auth.models import Group
from django.test import Client, TestCase

from evaluacion.models import EsquemaEvaluacion
from usuarios.models import Usuario

from .models import Antiguedad, Carrera, GrupoAcademico, Materia, PeriodoEscolar, PlanEstudios, ProgramaAsignatura


class CatalogosPortalApi10C4Tests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser(username="admin10c4", password="pw")
        self.estadistica = Usuario.objects.create_user(username="estadistica10c4", password="pw")
        self.docente = Usuario.objects.create_user(username="docente10c4", password="pw")
        Group.objects.get_or_create(name="ESTADISTICA")[0].user_set.add(self.estadistica)
        Group.objects.get_or_create(name="DOCENTE")[0].user_set.add(self.docente)
        self.client = Client()

        self.carrera = Carrera.objects.create(clave="C10C4", nombre="Carrera base 10C4")
        self.plan = PlanEstudios.objects.create(carrera=self.carrera, clave="P10C4", nombre="Plan base 10C4")
        self.antiguedad = Antiguedad.objects.create(plan_estudios=self.plan, clave="A10C4", nombre="Antiguedad 10C4", anio_inicio=2026)
        self.periodo = PeriodoEscolar.objects.create(
            clave="PER10C4",
            anio_escolar="2026-2027",
            periodo_academico=1,
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2027, 1, 31),
        )
        self.materia = Materia.objects.create(clave="MAT10C4", nombre="Materia base 10C4", horas_totales=64)
        self.programa = ProgramaAsignatura.objects.create(plan_estudios=self.plan, materia=self.materia, semestre_numero=3)

    def test_usuario_no_autenticado_no_accede(self):
        response = self.client.get("/api/catalogos/carreras/")
        self.assertEqual(response.status_code, 401)

    def test_docente_no_accede_a_catalogos(self):
        self.client.force_login(self.docente)
        response = self.client.get("/api/catalogos/carreras/")
        self.assertEqual(response.status_code, 403)

    def test_admin_y_estadistica_listan_catalogos(self):
        self.client.force_login(self.admin)
        response_admin = self.client.get("/api/catalogos/carreras/")
        self.assertEqual(response_admin.status_code, 200)
        self.assertTrue(response_admin.json()["ok"])

        self.client.force_login(self.estadistica)
        response_estadistica = self.client.get("/api/catalogos/carreras/")
        self.assertEqual(response_estadistica.status_code, 200)
        self.assertTrue(response_estadistica.json()["ok"])

    def test_admin_crea_carrera_valida_y_rechaza_clave_invalida(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/catalogos/carreras/",
            data={"clave": "ICI10C4", "nombre": "Ingenieria 10C4", "estado": "activo"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Carrera.objects.filter(clave="ICI10C4").exists())

        invalid = self.client.post(
            "/api/catalogos/carreras/",
            data={"clave": "ICI 10C4", "nombre": "Clave invalida"},
            content_type="application/json",
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("clave", invalid.json()["errors"])

    def test_materia_calcula_creditos_por_backend(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/catalogos/materias/",
            data={"clave": "MATCRED10C4", "nombre": "Materia creditos", "horas_totales": 80},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["item"]["creditos"], "5.00")

    def test_programa_calcula_anio_formacion_por_backend(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/catalogos/programas-asignatura/",
            data={"plan_estudios_id": self.plan.id, "materia_id": self.materia.id, "semestre_numero": 5},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("__all__", response.json()["errors"])

        nueva_materia = Materia.objects.create(clave="MATANIO10C4", nombre="Materia anio", horas_totales=40)
        ok = self.client.post(
            "/api/catalogos/programas-asignatura/",
            data={"plan_estudios_id": self.plan.id, "materia_id": nueva_materia.id, "semestre_numero": 5},
            content_type="application/json",
        )
        self.assertEqual(ok.status_code, 201)
        self.assertEqual(ok.json()["item"]["anio_formacion"], 3)

    def test_periodo_rechaza_fechas_invalidas_y_grupo_rechaza_cupo(self):
        self.client.force_login(self.admin)
        periodo = self.client.post(
            "/api/catalogos/periodos/",
            data={"clave": "PERBAD10C4", "anio_escolar": "2026-2027", "periodo_academico": 1, "fecha_inicio": "2027-01-31", "fecha_fin": "2027-01-31"},
            content_type="application/json",
        )
        self.assertEqual(periodo.status_code, 400)
        self.assertIn("fecha_fin", periodo.json()["errors"])

        grupo = self.client.post(
            "/api/catalogos/grupos/",
            data={"clave_grupo": "GBAD10C4", "antiguedad_id": self.antiguedad.id, "periodo_id": self.periodo.id, "semestre_numero": 1, "cupo_maximo": 0},
            content_type="application/json",
        )
        self.assertEqual(grupo.status_code, 400)
        self.assertIn("cupo_maximo", grupo.json()["errors"])

    def test_esquema_rechaza_exencion_con_un_parcial(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/catalogos/esquemas-evaluacion/",
            data={"programa_asignatura_id": self.programa.id, "version": "v10c4", "num_parciales": 1, "permite_exencion": True, "peso_parciales": "45.00", "peso_final": "55.00"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("permite_exencion", response.json()["errors"])

    def test_inactivacion_logica_no_elimina_registro(self):
        self.client.force_login(self.admin)
        response = self.client.post(f"/api/catalogos/carreras/{self.carrera.id}/inactivar/")
        self.assertEqual(response.status_code, 200)
        self.carrera.refresh_from_db()
        self.assertEqual(self.carrera.estado, "inactivo")
        self.assertTrue(Carrera.objects.filter(id=self.carrera.id).exists())
