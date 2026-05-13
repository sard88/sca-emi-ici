from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase

from catalogos.models import Antiguedad, Carrera, GrupoAcademico, Materia, PeriodoEscolar, PlanEstudios, ProgramaAsignatura
from relaciones.models import AsignacionDocente
from usuarios.models import Usuario

from .models import EventoCalendarioInstitucional, NotificacionUsuario


class PortalDatosVivosApiTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser(
            username="admin",
            password="admin",
            nombre_completo="Administrador",
            estado_cuenta=Usuario.ESTADO_ACTIVO,
        )
        self.docente = self.crear_usuario_con_grupo("docente", "DOCENTE")
        self.otro_docente = self.crear_usuario_con_grupo("docente2", "DOCENTE")
        self.discente_user = self.crear_usuario_con_grupo("discente", "DISCENTE")

    def crear_usuario_con_grupo(self, username, grupo):
        group, _ = Group.objects.get_or_create(name=grupo)
        user = Usuario.objects.create_user(
            username=username,
            password="admin",
            nombre_completo=username.title(),
            estado_cuenta=Usuario.ESTADO_ACTIVO,
        )
        user.groups.add(group)
        return user

    def crear_catalogos_asignacion(self, docente, clave_grupo="1A"):
        carrera, _ = Carrera.objects.get_or_create(
            clave="ICI",
            defaults={"nombre": "Ingeniería en Computación e Informática", "estado": "activo"},
        )
        plan, _ = PlanEstudios.objects.get_or_create(
            carrera=carrera,
            clave="ICI-2026",
            defaults={"nombre": "Plan ICI 2026", "estado": "activo"},
        )
        antiguedad, _ = Antiguedad.objects.get_or_create(
            plan_estudios=plan,
            clave=f"ANT-{clave_grupo}",
            defaults={"nombre": f"Antigüedad {clave_grupo}", "estado": "activo", "anio_inicio": 2025, "anio_fin": 2026},
        )
        periodo, _ = PeriodoEscolar.objects.get_or_create(
            clave="2025-2026-1",
            defaults={
                "anio_escolar": "2025-2026",
                "periodo_academico": 1,
                "fecha_inicio": date(2025, 8, 1),
                "fecha_fin": date(2026, 1, 31),
                "estado": "activo",
            },
        )
        grupo = GrupoAcademico.objects.create(
            clave_grupo=clave_grupo,
            antiguedad=antiguedad,
            periodo=periodo,
            semestre_numero=1,
            estado="activo",
        )
        materia = Materia.objects.create(
            clave=f"MAT-{clave_grupo}",
            nombre=f"Materia {clave_grupo}",
            estado="activo",
            horas_totales=64,
        )
        programa = ProgramaAsignatura.objects.create(
            plan_estudios=plan,
            materia=materia,
            semestre_numero=1,
        )
        return AsignacionDocente.objects.create(
            usuario_docente=docente,
            grupo_academico=grupo,
            programa_asignatura=programa,
            activo=True,
        )

    def test_dashboard_resumen_rechaza_anonimo(self):
        response = self.client.get("/api/dashboard/resumen/")
        self.assertEqual(response.status_code, 401)

    def test_dashboard_resumen_admin_autenticado(self):
        self.client.force_login(self.admin)
        response = self.client.get("/api/dashboard/resumen/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["cards"])
        self.assertEqual(data["perfil"], "ADMIN")

    def test_docente_recibe_solo_sus_asignaciones_en_resumen(self):
        self.crear_catalogos_asignacion(self.docente, "1A")
        self.crear_catalogos_asignacion(self.otro_docente, "1B")
        self.client.force_login(self.docente)
        response = self.client.get("/api/dashboard/resumen/")
        self.assertEqual(response.status_code, 200)
        cards = {item["title"]: item["value"] for item in response.json()["cards"]}
        self.assertEqual(cards["Asignaciones activas"], 1)

    def test_notificaciones_solo_usuario_dueno_y_marcar_leida(self):
        propia = NotificacionUsuario.objects.create(usuario=self.docente, titulo="Propia", mensaje="Mensaje")
        NotificacionUsuario.objects.create(usuario=self.otro_docente, titulo="Ajena", mensaje="Mensaje")
        self.client.force_login(self.docente)
        response = self.client.get("/api/notificaciones/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["unread_count"], 1)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["id"], propia.id)

        read_response = self.client.post(f"/api/notificaciones/{propia.id}/leer/", data={}, content_type="application/json")
        self.assertEqual(read_response.status_code, 200)
        propia.refresh_from_db()
        self.assertTrue(propia.leida)

    def test_calendario_filtra_por_rol_destino(self):
        EventoCalendarioInstitucional.objects.create(
            titulo="Evento docente",
            tipo_evento=EventoCalendarioInstitucional.TIPO_EVENTO_INSTITUCIONAL,
            fecha_inicio=date(2026, 5, 20),
            roles_destino=["DOCENTE"],
            visible=True,
        )
        EventoCalendarioInstitucional.objects.create(
            titulo="Evento discente",
            tipo_evento=EventoCalendarioInstitucional.TIPO_EVENTO_INSTITUCIONAL,
            fecha_inicio=date(2026, 5, 21),
            roles_destino=["DISCENTE"],
            visible=True,
        )
        self.client.force_login(self.docente)
        response = self.client.get("/api/calendario/mes/?year=2026&month=5")
        self.assertEqual(response.status_code, 200)
        titulos = [item["titulo"] for item in response.json()["eventos"]]
        self.assertIn("Evento docente", titulos)
        self.assertNotIn("Evento discente", titulos)

    def test_busqueda_discente_no_expone_kardex_oficial(self):
        self.client.force_login(self.discente_user)
        response = self.client.get("/api/busqueda/?q=kardex")
        self.assertEqual(response.status_code, 200)
        labels = [group["label"] for group in response.json()["groups"]]
        self.assertNotIn("Kárdex institucional", labels)

    def test_perfil_me_devuelve_datos_autenticado(self):
        self.client.force_login(self.docente)
        response = self.client.get("/api/perfil/me/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "docente")
        self.assertIn("DOCENTE", data["roles"])
