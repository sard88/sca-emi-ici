from datetime import date
from decimal import Decimal
from io import BytesIO
import json
import subprocess
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from catalogos.models import Antiguedad, Carrera, GrupoAcademico, Materia, PeriodoEscolar, PlanEstudios, ProgramaAsignatura
from evaluacion.models import Acta, CalificacionComponente, ComponenteEvaluacion, DetalleActa, EsquemaEvaluacion
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria
from usuarios.models import AsignacionCargo, UnidadOrganizacional, Usuario

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


class ReportesBloque9BActasTests(TestCase):
    def setUp(self):
        self.grupo_docente, _ = Group.objects.get_or_create(name="DOCENTE")
        self.grupo_discente, _ = Group.objects.get_or_create(name="DISCENTE")
        self.grupo_estadistica, _ = Group.objects.get_or_create(name="ENCARGADO_ESTADISTICA")
        self.grupo_jefe_carrera, _ = Group.objects.get_or_create(name=AsignacionCargo.ROL_JEFE_SUB_EJEC_CTR)
        self.grupo_jefe_academico, _ = Group.objects.get_or_create(name=AsignacionCargo.ROL_JEFE_ACADEMICO)
        self.admin_user = Usuario.objects.create_superuser(
            username="admin9b",
            password="admin",
            nombre_completo="Administrador 9B",
            estado_cuenta=Usuario.ESTADO_ACTIVO,
        )
        self.estadistica = self.crear_usuario("estadistica9b", "ENCARGADO_ESTADISTICA")
        self.docente = self.crear_usuario(
            "docente9b",
            "DOCENTE",
            nombre="Docente Responsable",
            titulo_profesional="Maestro en ingeniería",
            cedula_profesional="1234567",
        )
        self.otro_docente = self.crear_usuario("otradocente9b", "DOCENTE", nombre="Docente Ajeno")

        self.carrera = Carrera.objects.create(clave="R9BICI", nombre="Ingeniería en Computación e Informática")
        self.crear_jefaturas()
        self.plan = PlanEstudios.objects.create(carrera=self.carrera, clave="R9BPLAN", nombre="Plan 9B")
        self.antiguedad = Antiguedad.objects.create(
            plan_estudios=self.plan,
            clave="R9BANT",
            nombre="Antigüedad 9B",
            anio_inicio=2025,
            anio_fin=2029,
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="R9BPER",
            anio_escolar="2025-2026",
            periodo_academico=1,
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2026, 1, 31),
        )
        self.grupo = GrupoAcademico.objects.create(
            clave_grupo="R9BG1",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )
        self.materia = Materia.objects.create(clave="R9BMAT", nombre="Seguridad Computacional", horas_totales=64)
        self.programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=self.materia,
            semestre_numero=1,
        )
        self.esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa,
            version="v9b",
            num_parciales=EsquemaEvaluacion.PARCIALES_3,
            permite_exencion=True,
        )
        self.componentes = self.crear_componentes()
        self.discentes = [self.crear_discente(idx) for idx in range(1, 4)]
        self.asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.docente,
            grupo_academico=self.grupo,
            programa_asignatura=self.programa,
        )
        self.inscripciones = list(self.asignacion.inscripciones_materia.order_by("discente__matricula"))
        self.acta_p1 = self.crear_acta(
            ComponenteEvaluacion.CORTE_P1,
            [Decimal("5.0"), Decimal("8.0"), Decimal("5.0")],
            estado=Acta.ESTADO_BORRADOR_DOCENTE,
            causas="",
            sugerencias="",
        )
        self.acta_p2 = self.crear_acta(ComponenteEvaluacion.CORTE_P2, [Decimal("7.0"), Decimal("8.0"), Decimal("6.0")])
        self.acta_p3 = self.crear_acta(ComponenteEvaluacion.CORTE_P3, [Decimal("6.0"), Decimal("9.0"), Decimal("6.0")])
        self.acta_final = self.crear_acta(
            ComponenteEvaluacion.CORTE_FINAL,
            [Decimal("8.0"), Decimal("9.0"), Decimal("7.0")],
            estado=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            formalizada=True,
            causas="N/A",
            sugerencias="N/A",
        )
        for inscripcion, calificacion in zip(self.inscripciones, [Decimal("6.70"), Decimal("8.55"), Decimal("5.95")]):
            inscripcion.calificacion_final = calificacion
            inscripcion.codigo_resultado_oficial = "APROBADO" if calificacion >= Decimal("6.0") else "REPROBADO"
            inscripcion.save(update_fields=["calificacion_final", "codigo_resultado_oficial"])

    def crear_usuario(self, username, grupo, nombre=None, **extra_fields):
        user = Usuario.objects.create_user(
            username=username,
            password="admin",
            nombre_completo=nombre or username.title(),
            estado_cuenta=Usuario.ESTADO_ACTIVO,
            **extra_fields,
        )
        user.groups.add(Group.objects.get(name=grupo))
        return user

    def crear_jefaturas(self):
        seccion_academica = UnidadOrganizacional.objects.create(
            clave=UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
            nombre="Sección Académica",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )
        subseccion_carrera = UnidadOrganizacional.objects.create(
            clave="SUB_EJEC_R9B",
            nombre="Subsección de Ejecución y Control ICI",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=seccion_academica,
            carrera=self.carrera,
        )
        self.jefe_carrera = self.crear_usuario(
            "jefecarrera9b",
            AsignacionCargo.ROL_JEFE_SUB_EJEC_CTR,
            nombre="Jefe Carrera ICI",
        )
        self.jefe_academico = self.crear_usuario(
            "jefeacademico9b",
            AsignacionCargo.ROL_JEFE_ACADEMICO,
            nombre="Jefe Académico",
        )
        AsignacionCargo.objects.create(
            usuario=self.jefe_carrera,
            carrera=self.carrera,
            unidad_organizacional=subseccion_carrera,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_SUB_EJEC_CTR,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )
        AsignacionCargo.objects.create(
            usuario=self.jefe_academico,
            unidad_organizacional=seccion_academica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_ACADEMICO,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

    def crear_discente(self, idx):
        usuario = self.crear_usuario(f"discente9b{idx}", "DISCENTE", nombre=f"Discente {idx}")
        discente = Discente.objects.create(
            usuario=usuario,
            matricula=f"R9B00{idx}",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )
        AdscripcionGrupo.objects.create(discente=discente, grupo_academico=self.grupo)
        return discente

    def crear_componentes(self):
        data = [
            (ComponenteEvaluacion.CORTE_P1, "Tareas", Decimal("40.00"), False, 1),
            (ComponenteEvaluacion.CORTE_P1, "Proyecto", Decimal("60.00"), False, 2),
            (ComponenteEvaluacion.CORTE_P2, "Práctica", Decimal("100.00"), False, 1),
            (ComponenteEvaluacion.CORTE_P3, "Participación", Decimal("100.00"), False, 1),
            (ComponenteEvaluacion.CORTE_FINAL, "Trabajo extraclase", Decimal("30.00"), False, 1),
            (ComponenteEvaluacion.CORTE_FINAL, "Examen final", Decimal("70.00"), True, 2),
        ]
        componentes = {}
        for corte, nombre, porcentaje, es_examen, orden in data:
            componentes.setdefault(corte, []).append(
                ComponenteEvaluacion.objects.create(
                    esquema=self.esquema,
                    corte_codigo=corte,
                    nombre=nombre,
                    porcentaje=porcentaje,
                    es_examen=es_examen,
                    orden=orden,
                )
            )
        return componentes

    def crear_acta(self, corte, resultados, *, estado=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA, formalizada=False, causas="N/A", sugerencias="N/A"):
        acta = Acta.objects.create(
            asignacion_docente=self.asignacion,
            corte_codigo=corte,
            estado_acta=estado,
            esquema=self.esquema,
            esquema_version_snapshot=self.esquema.version,
            peso_parciales_snapshot=self.esquema.peso_parciales,
            peso_final_snapshot=self.esquema.peso_final,
            umbral_exencion_snapshot=self.esquema.umbral_exencion,
            probables_causas_reprobacion=causas,
            sugerencias_academicas=sugerencias,
            creado_por=self.docente,
        )
        if formalizada:
            from django.utils import timezone

            acta.formalizada_en = timezone.now()
            acta.save(update_fields=["formalizada_en"])
        for inscripcion, resultado in zip(self.inscripciones, resultados):
            detalle = DetalleActa.objects.create(
                acta=acta,
                inscripcion_materia=inscripcion,
                resultado_corte=resultado,
                resultado_corte_visible=resultado,
                resultado_final_preliminar=resultado if corte == ComponenteEvaluacion.CORTE_FINAL else None,
                resultado_final_preliminar_visible=resultado if corte == ComponenteEvaluacion.CORTE_FINAL else None,
                resultado_preliminar=DetalleActa.RESULTADO_APROBATORIO if resultado >= Decimal("6.0") else DetalleActa.RESULTADO_REPROBATORIO,
                completo=True,
            )
            self.crear_calificaciones_componentes(detalle, corte, resultado)
        return acta

    def crear_calificaciones_componentes(self, detalle, corte, resultado):
        componentes = self.componentes[corte]
        if corte == ComponenteEvaluacion.CORTE_P1:
            capturados = [resultado, resultado]
        elif corte == ComponenteEvaluacion.CORTE_FINAL:
            capturados = [resultado, resultado]
        else:
            capturados = [resultado]
        for componente, valor_capturado in zip(componentes, capturados):
            CalificacionComponente.objects.create(
                detalle=detalle,
                componente=componente,
                componente_nombre_snapshot=componente.nombre,
                componente_porcentaje_snapshot=componente.porcentaje,
                componente_es_examen_snapshot=componente.es_examen,
                valor_capturado=valor_capturado,
                valor_calculado=valor_capturado * componente.porcentaje / Decimal("100"),
            )

    def abrir_xlsx(self, response):
        from openpyxl import load_workbook

        return load_workbook(BytesIO(response.content), data_only=True)

    def valores_xlsx(self, response):
        wb = self.abrir_xlsx(response)
        ws = wb.active
        return [cell.value for row in ws.iter_rows() for cell in row if cell.value is not None]

    def test_exporta_acta_parcial_pdf_con_usuario_autorizado(self):
        self.client.force_login(self.docente)
        with patch("reportes.exportadores.actas_pdf.convertir_xlsx_a_pdf", return_value=b"%PDF-1.4\nmock"):
            response = self.client.get(f"/api/exportaciones/actas/{self.acta_p1.id}/pdf/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertEqual(RegistroExportacion.objects.latest("id").estado, RegistroExportacion.ESTADO_GENERADA)

    def test_exporta_acta_parcial_xlsx_con_usuario_autorizado_y_contenido(self):
        self.client.force_login(self.docente)
        response = self.client.get(f"/api/exportaciones/actas/{self.acta_p1.id}/xlsx/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        valores = self.valores_xlsx(response)
        self.assertIn("DOCUMENTO NO OFICIAL", " ".join(str(valor) for valor in valores))
        self.assertIn("Probables causas de reprobación: N/A", valores)
        self.assertIn("Tareas\n40%", valores)
        self.assertIn(2, valores)
        self.assertIn("Alumnos reprobados:", valores)
        self.assertIn(2, valores)
        self.assertIn("Media:", valores)
        self.assertIn(6, valores)
        self.assertIn("Moda:", valores)
        self.assertIn(5, valores)
        wb = self.abrir_xlsx(response)
        ws = wb.active
        self.assertIn("A1:AX1", {str(rng) for rng in ws.merged_cells.ranges})
        self.assertNotIn("Matrícula", valores)
        self.assertFalse(ws.row_dimensions[18].hidden)
        self.assertTrue(ws.row_dimensions[19].hidden)
        self.assertIn("Maestro en ingeniería", valores)
        self.assertIn("Docente Responsable", " ".join(str(valor) for valor in valores))
        self.assertIn("Cédula profesional: 1234567", valores)
        self.assertIn("Jefe Carrera ICI", " ".join(str(valor) for valor in valores))
        self.assertIn("Jefe Académico", " ".join(str(valor) for valor in valores))

    def test_endpoint_actas_disponibles_docente_lista_solo_propias(self):
        otro_grupo = GrupoAcademico.objects.create(
            clave_grupo="R9BG3",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )
        otra_asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.otro_docente,
            grupo_academico=otro_grupo,
            programa_asignatura=self.programa,
        )
        acta_ajena = Acta.objects.create(
            asignacion_docente=otra_asignacion,
            corte_codigo=ComponenteEvaluacion.CORTE_P1,
            estado_acta=Acta.ESTADO_BORRADOR_DOCENTE,
            esquema=self.esquema,
            esquema_version_snapshot=self.esquema.version,
            peso_parciales_snapshot=self.esquema.peso_parciales,
            peso_final_snapshot=self.esquema.peso_final,
            umbral_exencion_snapshot=self.esquema.umbral_exencion,
            creado_por=self.otro_docente,
        )

        self.client.force_login(self.docente)
        response = self.client.get("/api/exportaciones/actas-disponibles/")

        self.assertEqual(response.status_code, 200)
        ids = {item["acta_id"] for item in response.json()["items"]}
        self.assertIn(self.acta_p1.id, ids)
        self.assertNotIn(acta_ajena.id, ids)

    def test_endpoint_actas_disponibles_discente_no_lista_actas_completas(self):
        self.client.force_login(self.discentes[0].usuario)
        response = self.client.get("/api/exportaciones/actas-disponibles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], [])

    def test_endpoint_actas_disponibles_estadistica_lista_actas_y_no_expone_matricula(self):
        self.client.force_login(self.estadistica)
        response = self.client.get("/api/exportaciones/actas-disponibles/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload["items"]), 4)
        serializado = json.dumps(payload, ensure_ascii=False)
        self.assertIn("url_pdf", payload["items"][0])
        self.assertNotIn("R9B001", serializado)
        self.assertNotIn("matricula", serializado.lower())

    def test_descarga_expone_headers_de_auditoria_para_frontend(self):
        self.client.force_login(self.docente)
        response = self.client.get(
            f"/api/exportaciones/actas/{self.acta_p1.id}/xlsx/",
            HTTP_ORIGIN="http://localhost:3000",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Registro-Exportacion-Id"], str(RegistroExportacion.objects.latest("id").id))
        self.assertIn("Content-Disposition", response["Access-Control-Expose-Headers"])
        self.assertIn("X-Registro-Exportacion-Id", response["Access-Control-Expose-Headers"])

    def test_exporta_evaluacion_final_pdf_y_xlsx(self):
        self.client.force_login(self.docente)
        with patch("reportes.exportadores.actas_pdf.convertir_xlsx_a_pdf", return_value=b"%PDF-1.4\nmock"):
            pdf = self.client.get(f"/api/exportaciones/actas/{self.acta_final.id}/pdf/")
        xlsx = self.client.get(f"/api/exportaciones/actas/{self.acta_final.id}/xlsx/")

        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(xlsx.status_code, 200)
        self.assertIn("Evaluación final", self.valores_xlsx(xlsx))
        wb = self.abrir_xlsx(xlsx)
        ws = wb.active
        self.assertIn("A1:H1", {str(rng) for rng in ws.merged_cells.ranges})
        self.assertFalse(ws.row_dimensions[16].hidden)
        self.assertTrue(ws.row_dimensions[17].hidden)

    def test_exporta_calificacion_final_pdf_y_xlsx(self):
        self.client.force_login(self.docente)
        with patch("reportes.exportadores.actas_pdf.convertir_xlsx_a_pdf", return_value=b"%PDF-1.4\nmock"):
            pdf = self.client.get(f"/api/exportaciones/asignaciones/{self.asignacion.id}/calificacion-final/pdf/")
        xlsx = self.client.get(f"/api/exportaciones/asignaciones/{self.asignacion.id}/calificacion-final/xlsx/")

        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(xlsx.status_code, 200)
        valores = self.valores_xlsx(xlsx)
        self.assertIn("Parcial\n1", valores)
        self.assertIn("Parcial \n2 ", valores)
        self.assertIn("Parcial \n3 ", valores)
        self.assertIn("Evaluación Final", valores)
        self.assertIn("Calificación final", valores)
        wb = self.abrir_xlsx(xlsx)
        ws = wb.active
        self.assertIn("A1:I1", {str(rng) for rng in ws.merged_cells.ranges})
        self.assertFalse(ws.row_dimensions[16].hidden)
        self.assertTrue(ws.row_dimensions[17].hidden)

    def test_docente_no_puede_exportar_acta_ajena(self):
        otro_grupo = GrupoAcademico.objects.create(
            clave_grupo="R9BG2",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )
        otra_asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.otro_docente,
            grupo_academico=otro_grupo,
            programa_asignatura=self.programa,
        )
        acta_ajena = Acta.objects.create(
            asignacion_docente=otra_asignacion,
            corte_codigo=ComponenteEvaluacion.CORTE_P1,
            estado_acta=Acta.ESTADO_BORRADOR_DOCENTE,
            esquema=self.esquema,
            esquema_version_snapshot=self.esquema.version,
            peso_parciales_snapshot=self.esquema.peso_parciales,
            peso_final_snapshot=self.esquema.peso_final,
            umbral_exencion_snapshot=self.esquema.umbral_exencion,
            creado_por=self.otro_docente,
        )

        self.client.force_login(self.docente)
        response = self.client.get(f"/api/exportaciones/actas/{acta_ajena.id}/pdf/")

        self.assertEqual(response.status_code, 403)

    def test_discente_no_puede_exportar_acta_completa(self):
        self.client.force_login(self.discentes[0].usuario)
        response = self.client.get(f"/api/exportaciones/actas/{self.acta_p1.id}/pdf/")

        self.assertEqual(response.status_code, 403)

    def test_estadistica_puede_exportar_acta_formalizada(self):
        self.client.force_login(self.estadistica)
        with patch("reportes.exportadores.actas_pdf.convertir_xlsx_a_pdf", return_value=b"%PDF-1.4\nmock"):
            response = self.client.get(f"/api/exportaciones/actas/{self.acta_final.id}/pdf/")

        self.assertEqual(response.status_code, 200)

    def test_exportacion_fallida_crea_registro_fallida(self):
        self.client.force_login(self.docente)
        with patch("reportes.exportadores.actas_pdf.convertir_xlsx_a_pdf", side_effect=RuntimeError("fallo controlado")):
            response = self.client.get(f"/api/exportaciones/actas/{self.acta_p1.id}/pdf/")

        self.assertEqual(response.status_code, 500)
        registro = RegistroExportacion.objects.latest("id")
        self.assertEqual(registro.estado, RegistroExportacion.ESTADO_FALLIDA)
        self.assertIn("fallo controlado", registro.mensaje_error)

    def test_nombre_archivo_no_contiene_datos_sensibles(self):
        self.client.force_login(self.docente)
        with patch("reportes.exportadores.actas_pdf.convertir_xlsx_a_pdf", return_value=b"%PDF-1.4\nmock"):
            response = self.client.get(f"/api/exportaciones/actas/{self.acta_p1.id}/pdf/")

        disposition = response["Content-Disposition"]
        filename = disposition.split('filename="', 1)[1].rstrip('"')
        self.assertNotIn("Discente", disposition)
        self.assertNotIn("R9B001", disposition)
        self.assertNotIn(" ", filename)

    def test_acta_formalizada_no_muestra_marca_borrador(self):
        self.client.force_login(self.docente)
        response = self.client.get(f"/api/exportaciones/actas/{self.acta_final.id}/xlsx/")

        valores = " ".join(str(valor) for valor in self.valores_xlsx(response))
        self.assertNotIn("DOCUMENTO NO OFICIAL", valores)
        self.assertNotIn("BORRADOR", valores)

    def test_calificacion_final_sin_acta_final_sale_no_oficial(self):
        self.acta_final.estado_acta = Acta.ESTADO_ARCHIVADO
        self.acta_final.save(update_fields=["estado_acta"])

        self.client.force_login(self.docente)
        response = self.client.get(f"/api/exportaciones/asignaciones/{self.asignacion.id}/calificacion-final/xlsx/")

        self.assertEqual(response.status_code, 200)
        valores = " ".join(str(valor) for valor in self.valores_xlsx(response))
        self.assertIn("DOCUMENTO NO OFICIAL", valores)

    def test_exportar_no_modifica_acta_ni_inscripcion(self):
        acta_estado = self.acta_p1.estado_acta
        inscripcion_valor = self.inscripciones[0].calificacion_final

        self.client.force_login(self.docente)
        response = self.client.get(f"/api/exportaciones/actas/{self.acta_p1.id}/xlsx/")

        self.assertEqual(response.status_code, 200)
        self.acta_p1.refresh_from_db()
        self.inscripciones[0].refresh_from_db()
        self.assertEqual(self.acta_p1.estado_acta, acta_estado)
        self.assertEqual(self.inscripciones[0].calificacion_final, inscripcion_valor)

    def test_conversion_pdf_usa_libreoffice_headless(self):
        from reportes.exportadores.actas_pdf import convertir_xlsx_a_pdf

        def fake_run(cmd, check, stdout, stderr, timeout, env):
            outdir = cmd[cmd.index("--outdir") + 1]
            pdf_path = f"{outdir}/acta.pdf"
            with open(pdf_path, "wb") as file:
                file.write(b"%PDF-1.4\nmock")
            return subprocess.CompletedProcess(cmd, 0, b"", b"")

        with patch("reportes.exportadores.actas_pdf._libreoffice_binary", return_value="soffice"), patch(
            "reportes.exportadores.actas_pdf.subprocess.run",
            side_effect=fake_run,
        ) as run_mock:
            contenido = convertir_xlsx_a_pdf(b"contenido xlsx")

        self.assertTrue(contenido.startswith(b"%PDF"))
        comando = run_mock.call_args.args[0]
        self.assertIn("--headless", comando)
        self.assertIn("--convert-to", comando)
        self.assertIn("pdf", comando)
