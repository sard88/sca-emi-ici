from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from usuarios.models import Usuario

from .admin import RegistroExportacionAdmin
from .catalogo import CATALOGO_EXPORTACIONES
from .models import RegistroExportacion
from .services import ServicioExportacion, construir_nombre_archivo


class ReportesBloque9ATests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_user = Usuario.objects.create_superuser(
            username="admin",
            password="admin",
            nombre_completo="Administrador",
            estado_cuenta=Usuario.ESTADO_ACTIVO,
        )
        self.estadistica = self.crear_usuario_con_grupo("estadistica", "ENCARGADO_ESTADISTICA")
        self.docente = self.crear_usuario_con_grupo("docente", "DOCENTE")
        self.discente = self.crear_usuario_con_grupo("discente", "DISCENTE")
        self.otro_docente = self.crear_usuario_con_grupo("otrodocente", "DOCENTE")

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

    def crear_registro_directo(self, usuario, tipo=RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL):
        return RegistroExportacion.objects.create(
            usuario=usuario,
            tipo_documento=tipo,
            formato=RegistroExportacion.FORMATO_PDF,
            nombre_documento="Documento de prueba",
            nombre_archivo="documento-prueba.pdf",
            estado=RegistroExportacion.ESTADO_SOLICITADA,
        )

    def test_servicio_crea_registro_exportacion_exitoso(self):
        request = self.factory.get("/api/reportes/catalogo/", HTTP_USER_AGENT="TestAgent", REMOTE_ADDR="127.0.0.1")
        request.user = self.admin_user
        registro = ServicioExportacion(self.admin_user, request=request).registrar_solicitud(
            tipo_documento=RegistroExportacion.TIPO_REPORTE_EXPORTACIONES,
            formato=RegistroExportacion.FORMATO_XLSX,
            filtros={"estado": "GENERADA"},
        )

        self.assertEqual(registro.usuario, self.admin_user)
        self.assertEqual(registro.estado, RegistroExportacion.ESTADO_SOLICITADA)
        self.assertEqual(registro.ip_origen, "127.0.0.1")
        self.assertEqual(registro.user_agent, "TestAgent")
        self.assertEqual(registro.filtros_json, {"estado": "GENERADA"})

    def test_servicio_marca_registro_como_generada(self):
        registro = ServicioExportacion(self.admin_user).registrar_solicitud(
            tipo_documento=RegistroExportacion.TIPO_REPORTE_EXPORTACIONES,
            formato=RegistroExportacion.FORMATO_XLSX,
        )
        ServicioExportacion(self.admin_user).marcar_generada(registro, tamano_bytes=128, hash_archivo="abc123")
        registro.refresh_from_db()

        self.assertEqual(registro.estado, RegistroExportacion.ESTADO_GENERADA)
        self.assertEqual(registro.tamano_bytes, 128)
        self.assertEqual(registro.hash_archivo, "abc123")
        self.assertIsNotNone(registro.finalizado_en)

    def test_servicio_marca_registro_como_fallida(self):
        registro = ServicioExportacion(self.admin_user).registrar_solicitud(
            tipo_documento=RegistroExportacion.TIPO_REPORTE_EXPORTACIONES,
            formato=RegistroExportacion.FORMATO_XLSX,
        )
        ServicioExportacion(self.admin_user).marcar_fallida(registro, "Error controlado")
        registro.refresh_from_db()

        self.assertEqual(registro.estado, RegistroExportacion.ESTADO_FALLIDA)
        self.assertIn("Error controlado", registro.mensaje_error)
        self.assertIsNotNone(registro.finalizado_en)

    def test_usuario_autenticado_consulta_solo_sus_exportaciones(self):
        propia = self.crear_registro_directo(self.docente)
        self.crear_registro_directo(self.otro_docente)

        self.client.force_login(self.docente)
        response = self.client.get("/api/exportaciones/")

        self.assertEqual(response.status_code, 200)
        ids = [item["id"] for item in response.json()["items"]]
        self.assertEqual(ids, [propia.id])

    def test_usuario_anonimo_no_consulta_catalogo_ni_exportaciones(self):
        catalogo_response = self.client.get("/api/reportes/catalogo/")
        exportaciones_response = self.client.get("/api/exportaciones/")

        self.assertEqual(catalogo_response.status_code, 401)
        self.assertEqual(exportaciones_response.status_code, 401)

    def test_discente_no_ve_kardex_oficial_como_exportable(self):
        self.client.force_login(self.discente)
        response = self.client.get("/api/reportes/catalogo/")

        self.assertEqual(response.status_code, 200)
        codigos = {item["codigo"] for item in response.json()["items"]}
        self.assertNotIn(RegistroExportacion.TIPO_KARDEX_OFICIAL, codigos)

    def test_docente_no_ve_reportes_globales_como_exportables(self):
        self.client.force_login(self.docente)
        response = self.client.get("/api/reportes/catalogo/")

        self.assertEqual(response.status_code, 200)
        codigos = {item["codigo"] for item in response.json()["items"]}
        self.assertIn(RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL, codigos)
        self.assertNotIn(RegistroExportacion.TIPO_REPORTE_DESEMPENO, codigos)
        self.assertNotIn(RegistroExportacion.TIPO_REPORTE_ACTAS_ESTADO, codigos)

    def test_estadistica_ve_catalogo_institucional(self):
        self.client.force_login(self.estadistica)
        response = self.client.get("/api/reportes/catalogo/")

        self.assertEqual(response.status_code, 200)
        codigos = {item["codigo"] for item in response.json()["items"]}
        self.assertIn(RegistroExportacion.TIPO_KARDEX_OFICIAL, codigos)
        self.assertIn(RegistroExportacion.TIPO_REPORTE_DESEMPENO, codigos)
        self.assertIn(RegistroExportacion.TIPO_REPORTE_EXPORTACIONES, codigos)

    def test_admin_ve_catalogo_completo(self):
        self.client.force_login(self.admin_user)
        response = self.client.get("/api/reportes/catalogo/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), len(CATALOGO_EXPORTACIONES))

    def test_nombre_archivo_se_normaliza_sin_caracteres_peligrosos(self):
        nombre = construir_nombre_archivo(
            RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL,
            RegistroExportacion.FORMATO_PDF,
            objeto_repr="Seguridad Computacional / P1: Niño Águila",
            timestamp="20260513-101500",
        )

        self.assertEqual(nombre, "acta-de-evaluacion-parcial_seguridad-computacional-p1-nino-aguila_20260513-101500.pdf")
        self.assertNotIn("/", nombre)
        self.assertNotIn(" ", nombre)
        self.assertNotIn("ñ", nombre)

    def test_filtros_json_no_guarda_datos_sensibles(self):
        registro = ServicioExportacion(self.admin_user).registrar_solicitud(
            tipo_documento=RegistroExportacion.TIPO_REPORTE_EXPORTACIONES,
            formato=RegistroExportacion.FORMATO_XLSX,
            filtros={
                "periodo": "2026-1",
                "password": "secreto",
                "csrf_token": "abc",
                "nested": {"authorization": "Bearer token", "estado": "ok"},
            },
        )

        self.assertEqual(registro.filtros_json["periodo"], "2026-1")
        self.assertNotIn("password", registro.filtros_json)
        self.assertNotIn("csrf_token", registro.filtros_json)
        self.assertEqual(registro.filtros_json["nested"], {"estado": "ok"})

    def test_admin_registro_exportacion_no_permite_edicion_ordinaria(self):
        model_admin = RegistroExportacionAdmin(RegistroExportacion, admin.site)
        request = self.factory.get("/admin/reportes/registroexportacion/")
        request.user = self.admin_user

        readonly = model_admin.get_readonly_fields(request)
        self.assertIn("filtros_json", readonly)
        self.assertIn("parametros_json", readonly)
        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))
        self.assertNotIn("delete_selected", model_admin.get_actions(request))

    def test_endpoint_prueba_solo_admin_o_estadistica(self):
        self.client.force_login(self.docente)
        denied = self.client.post(
            "/api/exportaciones/registrar-evento-prueba/",
            data={"formato": "PDF"},
            content_type="application/json",
        )
        self.assertEqual(denied.status_code, 403)

        self.client.force_login(self.estadistica)
        allowed = self.client.post(
            "/api/exportaciones/registrar-evento-prueba/",
            data={"formato": "PDF", "filtros": {"token": "no-guardar", "tipo": "prueba"}},
            content_type="application/json",
        )
        self.assertEqual(allowed.status_code, 201)
        registro = RegistroExportacion.objects.get(id=allowed.json()["item"]["id"])
        self.assertEqual(registro.estado, RegistroExportacion.ESTADO_GENERADA)
        self.assertEqual(registro.filtros_json, {"tipo": "prueba"})

    def test_servicio_rechaza_exportacion_no_autorizada_para_docente(self):
        with self.assertRaises(PermissionDenied):
            ServicioExportacion(self.docente).registrar_solicitud(
                tipo_documento=RegistroExportacion.TIPO_REPORTE_DESEMPENO,
                formato=RegistroExportacion.FORMATO_XLSX,
            )
