from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

from usuarios.models import Usuario

from .admin import BitacoraEventoCriticoAdmin
from .eventos import MODULO_ACTAS, MODULO_AUTENTICACION, RESULTADO_EXITOSO, SEVERIDAD_INFO
from .models import BitacoraEventoCritico
from .services import limpiar_payload_auditoria, registrar_evento_exitoso


class BitacoraEventoCriticoTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="admin.audit",
            password="pass12345",
            nombre_completo="Admin Auditor",
            is_staff=True,
            is_superuser=True,
        )
        Group.objects.get_or_create(name="ESTADISTICA")

    def test_registrar_evento_sin_request(self):
        evento = registrar_evento_exitoso(
            usuario=self.user,
            modulo=MODULO_ACTAS,
            evento_codigo="ACTA_PUBLICADA",
            severidad=SEVERIDAD_INFO,
            resumen="Acta publicada en prueba.",
            metadatos={"acta_id": 10, "password": "no"},
        )
        self.assertIsNotNone(evento)
        self.assertEqual(evento.usuario, self.user)
        self.assertEqual(evento.resultado, RESULTADO_EXITOSO)
        self.assertEqual(evento.metadatos_json["password"], "[REDACTADO]")
        self.assertIn("ACTA_PUBLICADA", str(evento))

    def test_registrar_evento_con_request_extrae_contexto(self):
        request = RequestFactory().post(
            "/api/auth/login/",
            HTTP_USER_AGENT="UnitTest",
            HTTP_X_FORWARDED_FOR="10.0.0.1, 10.0.0.2",
            HTTP_X_REQUEST_ID="req-123",
        )
        request.user = self.user
        evento = registrar_evento_exitoso(
            request=request,
            modulo=MODULO_AUTENTICACION,
            evento_codigo="LOGIN_EXITOSO",
            resumen="Login exitoso.",
        )
        self.assertEqual(evento.ip_origen, "10.0.0.1")
        self.assertEqual(evento.user_agent, "UnitTest")
        self.assertEqual(evento.ruta, "/api/auth/login/")
        self.assertEqual(evento.metodo_http, "POST")
        self.assertEqual(evento.request_id, "req-123")

    def test_sanitiza_payload_sensible_y_limita_listas(self):
        payload = limpiar_payload_auditoria(
            {
                "password": "secreto",
                "token": "abc",
                "datos": [{"valor": index} for index in range(25)],
                "archivo": object(),
            }
        )
        self.assertEqual(payload["password"], "[REDACTADO]")
        self.assertEqual(payload["token"], "[REDACTADO]")
        self.assertEqual(len(payload["datos"]), 21)

    def test_append_only_no_permite_update_ni_delete_instancia(self):
        evento = registrar_evento_exitoso(
            usuario=self.user,
            modulo=MODULO_ACTAS,
            evento_codigo="ACTA_REMITIDA",
            resumen="Acta remitida.",
        )
        evento.resumen = "Modificado"
        with self.assertRaises(ValidationError):
            evento.save()
        with self.assertRaises(ValidationError):
            evento.delete()

    def test_admin_solo_lectura(self):
        model_admin = BitacoraEventoCriticoAdmin(BitacoraEventoCritico, admin.site)
        request = RequestFactory().get("/admin/auditoria/bitacoraeventocritico/")
        request.user = self.user
        evento = registrar_evento_exitoso(
            usuario=self.user,
            modulo=MODULO_ACTAS,
            evento_codigo="ACTA_VALIDADA_JEFATURA_CARRERA",
            resumen="Acta validada.",
        )
        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request, evento))
        self.assertFalse(model_admin.has_delete_permission(request, evento))
        self.assertEqual(model_admin.get_actions(request), {})
        self.assertIn("resumen", model_admin.get_readonly_fields(request, evento))

    def test_api_bloquea_anonimo_y_docente_pero_permite_admin(self):
        registrar_evento_exitoso(
            usuario=self.user,
            modulo=MODULO_ACTAS,
            evento_codigo="ACTA_FORMALIZADA_JEFATURA_ACADEMICA",
            resumen="Acta formalizada.",
        )
        anon = self.client.get("/api/auditoria/eventos/")
        self.assertEqual(anon.status_code, 401)

        docente_group, _ = Group.objects.get_or_create(name="DOCENTE")
        docente = Usuario.objects.create_user(username="docente", password="pass12345")
        docente.groups.add(docente_group)
        self.client.force_login(docente)
        bloqueado = self.client.get("/api/auditoria/eventos/")
        self.assertEqual(bloqueado.status_code, 403)

        self.client.force_login(self.user)
        response = self.client.get("/api/auditoria/eventos/?modulo=ACTAS")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertGreaterEqual(data["total"], 1)

    def test_api_detalle_y_resumen(self):
        evento = registrar_evento_exitoso(
            usuario=self.user,
            modulo=MODULO_ACTAS,
            evento_codigo="ACTA_PUBLICADA",
            resumen="Acta publicada.",
            metadatos={"csrfmiddlewaretoken": "token"},
        )
        self.client.force_login(self.user)
        detalle = self.client.get(f"/api/auditoria/eventos/{evento.id}/")
        self.assertEqual(detalle.status_code, 200)
        self.assertEqual(detalle.json()["item"]["metadatos_json"]["csrfmiddlewaretoken"], "[REDACTADO]")
        resumen = self.client.get("/api/auditoria/eventos/resumen/")
        self.assertEqual(resumen.status_code, 200)
        self.assertIn("por_modulo", resumen.json()["resumen"])
