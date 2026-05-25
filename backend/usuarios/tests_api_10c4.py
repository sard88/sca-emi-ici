from django.contrib.auth.models import Group
from django.test import Client, TestCase

from .models import AsignacionCargo, GradoEmpleo, Usuario


class AdministracionPortalApi10C4Tests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser(username="adminapi10c4", password="pw")
        self.estadistica = Usuario.objects.create_user(username="estadisticaapi10c4", password="pw")
        self.docente = Usuario.objects.create_user(username="docenteapi10c4", password="pw")
        self.discente = Usuario.objects.create_user(username="discenteapi10c4", password="pw")
        self.group_estadistica = Group.objects.get_or_create(name="ESTADISTICA")[0]
        self.group_docente = Group.objects.get_or_create(name="DOCENTE")[0]
        self.group_discente = Group.objects.get_or_create(name="DISCENTE")[0]
        self.estadistica.groups.add(self.group_estadistica)
        self.docente.groups.add(self.group_docente)
        self.discente.groups.add(self.group_discente)
        self.client = Client()

    def test_usuario_no_autenticado_no_accede_a_administracion(self):
        response = self.client.get("/api/admin/usuarios/")
        self.assertEqual(response.status_code, 401)

    def test_docente_y_discente_no_acceden_a_administracion(self):
        self.client.force_login(self.docente)
        docente_response = self.client.get("/api/admin/usuarios/")
        self.assertEqual(docente_response.status_code, 403)

        self.client.force_login(self.discente)
        discente_response = self.client.get("/api/admin/usuarios/")
        self.assertEqual(discente_response.status_code, 403)

    def test_admin_lista_y_crea_usuario_sin_exponer_password(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/admin/usuarios/",
            data={"username": "nuevo10c4", "nombre_completo": "Usuario Nuevo", "correo": "nuevo@example.test", "rol": "DOCENTE", "password": "Temporal123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()["item"]
        self.assertNotIn("password", data)
        self.assertTrue(Usuario.objects.filter(username="nuevo10c4", groups__name="DOCENTE").exists())

    def test_estadistica_solo_lee_administracion(self):
        self.client.force_login(self.estadistica)
        list_response = self.client.get("/api/admin/grados-empleos/")
        self.assertEqual(list_response.status_code, 200)

        create_response = self.client.post(
            "/api/admin/grados-empleos/",
            data={"clave": "G10C4", "abreviatura": "G", "nombre": "Grado prueba", "tipo": "CIVIL"},
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 403)

    def test_admin_crea_e_inactiva_grado_empleo(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/admin/grados-empleos/",
            data={"clave": "GE10C4", "abreviatura": "GE", "nombre": "Grado Empleo 10C4", "tipo": "CIVIL", "activo": True},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        grado_id = response.json()["item"]["id"]

        inactive = self.client.post(f"/api/admin/grados-empleos/{grado_id}/inactivar/")
        self.assertEqual(inactive.status_code, 200)
        grado = GradoEmpleo.objects.get(pk=grado_id)
        self.assertFalse(grado.activo)

    def test_asignacion_cargo_rechaza_usuario_discente(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/admin/asignaciones-cargo/",
            data={"usuario_id": self.discente.id, "cargo_codigo": AsignacionCargo.CARGO_DOCENTE, "tipo_designacion": AsignacionCargo.DESIGNACION_TITULAR, "activo": True},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("usuario", response.json()["errors"])
