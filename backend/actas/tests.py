import json
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalogos.models import (
    ESTADO_ACTIVO,
    ESTADO_CERRADO,
    ESTADO_PLANIFICADO,
    Antiguedad,
    Carrera,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
)
from evaluacion.models import Acta, DetalleActa, EsquemaEvaluacion
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria
from usuarios.models import AsignacionCargo, UnidadOrganizacional, Usuario

from .models import DetalleCierrePeriodoDiscente, ProcesoAperturaPeriodo, ProcesoCierrePeriodo
from .services import (
    ServicioAperturaPeriodo,
    ServicioCierrePeriodo,
    ServicioDiagnosticoCierrePeriodo,
    listar_pendientes_asignacion_docente,
)


class Bloque85CierreAperturaTests(TestCase):
    def setUp(self):
        self.grupo_docente, _ = Group.objects.get_or_create(name="DOCENTE")
        self.grupo_discente, _ = Group.objects.get_or_create(name="DISCENTE")
        self.grupo_estadistica, _ = Group.objects.get_or_create(name="ESTADISTICA")
        self.grupo_jefe_ejec, _ = Group.objects.get_or_create(name="JEFE_SUB_EJEC_CTR")

        self.usuario_estadistica = Usuario.objects.create_user(
            username="estadistica85",
            password="segura123",
            nombre_completo="Estadística",
        )
        self.usuario_estadistica.groups.add(self.grupo_estadistica)
        self.usuario_docente = Usuario.objects.create_user(
            username="docente85",
            password="segura123",
            nombre_completo="Docente",
        )
        self.usuario_docente.groups.add(self.grupo_docente)
        self.usuario_discente = Usuario.objects.create_user(
            username="discente85",
            password="segura123",
            nombre_completo="Discente",
        )
        self.usuario_discente.groups.add(self.grupo_discente)
        self.usuario_jefe = Usuario.objects.create_user(
            username="jefe85",
            password="segura123",
            nombre_completo="Jefe de carrera",
        )
        self.usuario_jefe.groups.add(self.grupo_jefe_ejec)

        self.carrera = Carrera.objects.create(clave="ICI85", nombre="ICI", estado=ESTADO_ACTIVO)
        self.plan = PlanEstudios.objects.create(
            clave="PLAN85",
            nombre="Plan 85",
            carrera=self.carrera,
            estado=ESTADO_ACTIVO,
        )
        self.antiguedad = Antiguedad.objects.create(
            clave="ANT85",
            nombre="Antigüedad 85",
            plan_estudios=self.plan,
            anio_inicio=2024,
            anio_fin=2028,
            estado=ESTADO_ACTIVO,
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="2025-S1-85",
            anio_escolar="2025-2026",
            periodo_academico=1,
            fecha_inicio="2025-08-01",
            fecha_fin="2025-12-15",
            estado=ESTADO_ACTIVO,
        )
        self.periodo_destino = PeriodoEscolar.objects.create(
            clave="2025-S2-85",
            anio_escolar="2025-2026",
            periodo_academico=2,
            fecha_inicio="2026-01-10",
            fecha_fin="2026-07-15",
            estado=ESTADO_PLANIFICADO,
        )
        self.grupo = GrupoAcademico.objects.create(
            clave_grupo="ICI-5A",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=5,
            estado=ESTADO_ACTIVO,
            cupo_maximo=30,
        )
        self.discente = Discente.objects.create(
            usuario=self.usuario_discente,
            matricula="A-850001",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
            activo=True,
        )
        self.adscripcion = AdscripcionGrupo.objects.create(
            discente=self.discente,
            grupo_academico=self.grupo,
            activo=True,
        )
        self.materia = Materia.objects.create(
            clave="MAT85",
            nombre="Materia 85",
            estado=ESTADO_ACTIVO,
            horas_totales=64,
        )
        self.programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=self.materia,
            semestre_numero=5,
        )
        self.asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.usuario_docente,
            grupo_academico=self.grupo,
            programa_asignatura=self.programa,
            activo=True,
        )
        self.inscripcion = InscripcionMateria.objects.get(
            discente=self.discente,
            asignacion_docente=self.asignacion,
        )
        self.esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa,
            version="v1",
            num_parciales=1,
            permite_exencion=False,
            peso_parciales=Decimal("45.00"),
            peso_final=Decimal("55.00"),
            umbral_exencion=Decimal("9.00"),
            activo=True,
        )
        self.acta = Acta.objects.create(
            asignacion_docente=self.asignacion,
            corte_codigo="FINAL",
            estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            esquema=self.esquema,
            esquema_version_snapshot="v1",
            peso_parciales_snapshot=Decimal("45.00"),
            peso_final_snapshot=Decimal("55.00"),
            umbral_exencion_snapshot=Decimal("9.00"),
            creado_por=self.usuario_docente,
        )
        DetalleActa.objects.create(
            acta=self.acta,
            inscripcion_materia=self.inscripcion,
            resultado_final_preliminar=Decimal("8.000000"),
            resultado_final_preliminar_visible=Decimal("8.0"),
            resultado_preliminar=DetalleActa.RESULTADO_APROBATORIO,
            completo=True,
        )
        self.inscripcion.calificacion_final = Decimal("8.00")
        self.inscripcion.codigo_resultado_oficial = "APROBADO"
        self.inscripcion.cerrado_en = timezone.now()
        self.inscripcion.save(
            update_fields=["calificacion_final", "codigo_resultado_oficial", "cerrado_en"]
        )

        seccion = UnidadOrganizacional.objects.create(
            clave=UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
            nombre="Sección Académica",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
            activo=True,
        )
        subseccion = UnidadOrganizacional.objects.create(
            clave="SUB_EJEC_85",
            nombre="Subsección de Ejecución y Control ICI",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=seccion,
            carrera=self.carrera,
            activo=True,
        )
        AsignacionCargo.objects.create(
            usuario=self.usuario_jefe,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_SUB_EJEC_CTR,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            carrera=self.carrera,
            unidad_organizacional=subseccion,
            activo=True,
        )

    def test_diagnostico_detecta_acta_final_faltante(self):
        self.acta.delete()

        diagnostico = ServicioDiagnosticoCierrePeriodo(self.periodo).diagnosticar()

        self.assertTrue(
            any("Falta acta FINAL formalizada" in item for item in diagnostico["bloqueantes"])
        )

    def test_diagnostico_detecta_acta_viva_pendiente(self):
        self.acta.estado_acta = Acta.ESTADO_BORRADOR_DOCENTE
        self.acta.save(update_fields=["estado_acta"])

        diagnostico = ServicioDiagnosticoCierrePeriodo(self.periodo).diagnosticar()

        self.assertTrue(any("acta FINAL viva" in item for item in diagnostico["bloqueantes"]))

    def test_no_permite_cierre_con_bloqueantes(self):
        self.acta.delete()

        with self.assertRaises(ValidationError):
            ServicioCierrePeriodo(self.periodo, self.usuario_estadistica).cerrar()

        self.periodo.refresh_from_db()
        self.assertEqual(self.periodo.estado, ESTADO_ACTIVO)
        self.assertFalse(ProcesoCierrePeriodo.objects.filter(periodo=self.periodo).exists())

    def test_cierre_exitoso_crea_proceso_y_detalle(self):
        proceso = ServicioCierrePeriodo(self.periodo, self.usuario_estadistica).cerrar()

        self.periodo.refresh_from_db()
        self.assertEqual(self.periodo.estado, ESTADO_CERRADO)
        self.assertEqual(proceso.estado, ProcesoCierrePeriodo.ESTADO_CERRADO)
        detalle = proceso.detalles_discente.get(discente=self.discente)
        self.assertTrue(detalle.promovible)
        self.assertEqual(
            detalle.clasificacion,
            DetalleCierrePeriodoDiscente.CLASIFICACION_PROMOVIBLE,
        )

    def test_no_promueve_discente_en_baja_temporal(self):
        self.discente.situacion_actual = Discente.SITUACION_BAJA_TEMPORAL
        self.discente.save(update_fields=["situacion_actual"])

        proceso = ServicioCierrePeriodo(self.periodo, self.usuario_estadistica).cerrar()
        detalle = proceso.detalles_discente.get(discente=self.discente)

        self.assertFalse(detalle.promovible)
        self.assertEqual(
            detalle.clasificacion,
            DetalleCierrePeriodoDiscente.CLASIFICACION_BAJA_TEMPORAL,
        )

    def test_apertura_crea_grupo_destino_y_adscripcion_sin_duplicar(self):
        ServicioCierrePeriodo(self.periodo, self.usuario_estadistica).cerrar()

        proceso = ServicioAperturaPeriodo(
            self.periodo,
            self.periodo_destino,
            self.usuario_estadistica,
        ).abrir()
        proceso_2 = ServicioAperturaPeriodo(
            self.periodo,
            self.periodo_destino,
            self.usuario_estadistica,
        ).abrir()

        self.periodo_destino.refresh_from_db()
        self.assertEqual(self.periodo_destino.estado, ESTADO_ACTIVO)
        grupo_destino = GrupoAcademico.objects.get(
            periodo=self.periodo_destino,
            antiguedad=self.antiguedad,
            clave_grupo="ICI-6A",
        )
        self.assertFalse(
            AdscripcionGrupo.objects.get(pk=self.adscripcion.pk).activo
        )
        self.assertEqual(
            AdscripcionGrupo.objects.filter(
                discente=self.discente,
                grupo_academico=grupo_destino,
                activo=True,
            ).count(),
            1,
        )
        self.assertEqual(proceso.estado, ProcesoAperturaPeriodo.ESTADO_EJECUTADO)
        self.assertEqual(proceso_2.resumen_json["adscripciones_creadas"], 0)

    def test_apertura_requiere_periodo_destino_existente_y_origen_cerrado(self):
        with self.assertRaises(ValidationError):
            ServicioAperturaPeriodo(
                self.periodo,
                self.periodo_destino,
                self.usuario_estadistica,
            ).abrir()

    def test_pendientes_de_asignacion_docente_lista_programas_esperados(self):
        ServicioCierrePeriodo(self.periodo, self.usuario_estadistica).cerrar()
        ServicioAperturaPeriodo(
            self.periodo,
            self.periodo_destino,
            self.usuario_estadistica,
        ).abrir()
        materia_destino = Materia.objects.create(
            clave="MAT86",
            nombre="Materia 86",
            estado=ESTADO_ACTIVO,
            horas_totales=64,
        )
        programa_destino = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=materia_destino,
            semestre_numero=6,
        )

        pendientes = listar_pendientes_asignacion_docente(self.periodo_destino, self.usuario_jefe)

        self.assertTrue(any(item["programa"] == programa_destino for item in pendientes))

    def test_permisos_cierre_apertura(self):
        self.client.login(username="estadistica85", password="segura123")
        response = self.client.get(reverse("actas:periodos-cierre"))
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        self.client.login(username="docente85", password="segura123")
        response = self.client.get(reverse("actas:periodos-cierre"))
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.client.login(username="discente85", password="segura123")
        response = self.client.get(reverse("actas:apertura-periodo"))
        self.assertEqual(response.status_code, 403)

    def test_jefatura_carrera_consulta_pendientes(self):
        self.client.login(username="jefe85", password="segura123")

        response = self.client.get(reverse("actas:pendientes-asignacion-docente"))

        self.assertEqual(response.status_code, 200)

    def test_detalle_cierre_admin_no_permita_alta_o_borrado_manual(self):
        detalle_admin = admin.site._registry[DetalleCierrePeriodoDiscente]

        self.assertFalse(detalle_admin.has_add_permission(None))
        self.assertFalse(detalle_admin.has_delete_permission(None))


class CierreAperturaPortalApi10C6Tests(Bloque85CierreAperturaTests):
    def test_api_diagnostico_no_modifica_periodo_ni_expone_matricula(self):
        self.client.force_login(self.usuario_estadistica)

        response = self.client.get(f"/api/periodos/{self.periodo.pk}/diagnostico-cierre/")

        self.assertEqual(response.status_code, 200)
        self.periodo.refresh_from_db()
        self.assertEqual(self.periodo.estado, ESTADO_ACTIVO)
        self.assertNotIn("A-850001", response.content.decode())

    def test_api_cierre_valido_crea_proceso(self):
        self.client.force_login(self.usuario_estadistica)

        response = self.client.post(
            f"/api/periodos/{self.periodo.pk}/cerrar/",
            data=json.dumps({"observaciones": "Cierre API 10C-6"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.periodo.refresh_from_db()
        self.assertEqual(self.periodo.estado, ESTADO_CERRADO)
        self.assertTrue(ProcesoCierrePeriodo.objects.filter(periodo=self.periodo).exists())

    def test_api_apertura_requiere_origen_cerrado(self):
        self.client.force_login(self.usuario_estadistica)

        response = self.client.post(
            "/api/aperturas/crear/",
            data=json.dumps({
                "periodo_origen_id": self.periodo.pk,
                "periodo_destino_id": self.periodo_destino.pk,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_api_jefatura_consulta_pendientes_de_asignacion(self):
        self.client.force_login(self.usuario_jefe)

        response = self.client.get(f"/api/pendientes-asignacion-docente/?periodo={self.periodo.pk}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

    def test_api_docente_no_consulta_periodos_operativos(self):
        self.client.force_login(self.usuario_docente)

        response = self.client.get("/api/periodos/")

        self.assertEqual(response.status_code, 403)
