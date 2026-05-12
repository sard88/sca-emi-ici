from datetime import date
from decimal import Decimal

from django.apps import apps
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalogos.models import (
    Antiguedad,
    Carrera,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
)
from evaluacion.models import (
    Acta,
    CapturaCalificacionPreliminar,
    ComponenteEvaluacion,
    DetalleActa,
    EsquemaEvaluacion,
)
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria
from usuarios.models import AsignacionCargo, UnidadOrganizacional, Usuario

from .models import (
    CALIFICACION_APROBATORIA,
    CatalogoResultadoAcademico,
    CatalogoSituacionAcademica,
    EventoSituacionAcademica,
    Extraordinario,
)
from .services import (
    construir_historial_discente,
    construir_kardex_discente,
    registrar_baja_temporal,
    registrar_evento_situacion,
    registrar_extraordinario,
    registrar_reingreso,
)


class TrayectoriaBloque7Tests(TestCase):
    def setUp(self):
        self.grupo_discente, _ = Group.objects.get_or_create(name="DISCENTE")
        self.grupo_docente, _ = Group.objects.get_or_create(name="DOCENTE")
        self.grupo_estadistica, _ = Group.objects.get_or_create(name="ENCARGADO_ESTADISTICA")
        self.grupo_jefatura_carrera, _ = Group.objects.get_or_create(name="JEFE_SUB_EJEC_CTR")

        self.usuario_discente = self.crear_usuario("discente_historial", self.grupo_discente)
        self.usuario_otro_discente = self.crear_usuario("discente_ajeno", self.grupo_discente)
        self.usuario_docente = self.crear_usuario("docente_historial", self.grupo_docente)
        self.usuario_estadistica = self.crear_usuario("estadistica_historial", self.grupo_estadistica)
        self.usuario_jefatura = self.crear_usuario("jefatura_historial", self.grupo_jefatura_carrera)

        self.carrera = Carrera.objects.create(
            clave="ICI",
            nombre="Ingeniería en Computación e Informática",
            estado="activo",
        )
        self.plan = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="PLAN-ICI",
            nombre="Plan ICI",
            estado="activo",
        )
        self.antiguedad = Antiguedad.objects.create(
            plan_estudios=self.plan,
            clave="ANT-ICI-2024",
            nombre="Antigüedad ICI 2024",
            anio_inicio=2024,
            anio_fin=2028,
            estado="activo",
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="2024-2025-S1",
            anio_escolar="2024-2025",
            periodo_academico=1,
            fecha_inicio=date(2024, 8, 1),
            fecha_fin=date(2024, 12, 15),
            estado="activo",
        )
        self.grupo = GrupoAcademico.objects.create(
            clave_grupo="ICI-1A",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
            estado="activo",
        )
        self.materia = Materia.objects.create(
            clave="MAT-HIST",
            nombre="Materia de historial",
            horas_totales=80,
            estado="activo",
        )
        self.programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=self.materia,
            semestre_numero=1,
            obligatoria=True,
        )
        self.esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa,
            version="v1",
            num_parciales=2,
            permite_exencion=True,
            peso_parciales=Decimal("45.00"),
            peso_final=Decimal("55.00"),
            umbral_exencion=Decimal("9.00"),
            activo=True,
        )
        self.componente_p1 = ComponenteEvaluacion.objects.create(
            esquema=self.esquema,
            corte_codigo=ComponenteEvaluacion.CORTE_P1,
            nombre="Tareas",
            porcentaje=Decimal("100.00"),
            orden=1,
        )
        self.discente = Discente.objects.create(
            usuario=self.usuario_discente,
            matricula="A-100",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
            activo=True,
        )
        self.otro_discente = Discente.objects.create(
            usuario=self.usuario_otro_discente,
            matricula="A-101",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
            activo=True,
        )
        AdscripcionGrupo.objects.create(
            discente=self.discente,
            grupo_academico=self.grupo,
            activo=True,
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

    def crear_usuario(self, username, grupo):
        usuario = Usuario.objects.create_user(
            username=username,
            password="segura123",
            nombre_completo=username.replace("_", " ").title(),
            estado_cuenta=Usuario.ESTADO_ACTIVO,
        )
        usuario.groups.add(grupo)
        return usuario

    def formalizar_final(self, inscripcion=None, calificacion=Decimal("5.0"), esquema=None):
        inscripcion = inscripcion or self.inscripcion
        esquema = esquema or self.esquema
        acta = Acta.objects.create(
            asignacion_docente=inscripcion.asignacion_docente,
            corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
            estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            esquema=esquema,
            esquema_version_snapshot=esquema.version,
            peso_parciales_snapshot=esquema.peso_parciales,
            peso_final_snapshot=esquema.peso_final,
            umbral_exencion_snapshot=esquema.umbral_exencion,
            creado_por=self.usuario_docente,
            formalizada_en=timezone.now(),
        )
        DetalleActa.objects.create(
            acta=acta,
            inscripcion_materia=inscripcion,
            resultado_final_preliminar=calificacion,
            resultado_final_preliminar_visible=calificacion.quantize(Decimal("0.1")),
            resultado_preliminar=(
                DetalleActa.RESULTADO_APROBATORIO
                if calificacion >= CALIFICACION_APROBATORIA
                else DetalleActa.RESULTADO_REPROBATORIO
            ),
            completo=True,
        )
        inscripcion.calificacion_final = calificacion
        inscripcion.codigo_resultado_oficial = (
            CatalogoResultadoAcademico.CLAVE_APROBADO
            if calificacion >= CALIFICACION_APROBATORIA
            else CatalogoResultadoAcademico.CLAVE_REPROBADO
        )
        inscripcion.codigo_marca = ""
        inscripcion.cerrado_en = timezone.now()
        inscripcion.save(
            update_fields=[
                "calificacion_final",
                "codigo_resultado_oficial",
                "codigo_marca",
                "cerrado_en",
            ]
        )
        return acta

    def crear_inscripcion_para_materia(self, clave, nombre):
        materia = Materia.objects.create(
            clave=clave,
            nombre=nombre,
            horas_totales=80,
            estado="activo",
        )
        programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=materia,
            semestre_numero=1,
            obligatoria=True,
        )
        esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=programa,
            version="v1",
            num_parciales=2,
            permite_exencion=True,
            peso_parciales=Decimal("45.00"),
            peso_final=Decimal("55.00"),
            umbral_exencion=Decimal("9.00"),
            activo=True,
        )
        asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.usuario_docente,
            grupo_academico=self.grupo,
            programa_asignatura=programa,
            activo=True,
        )
        inscripcion = InscripcionMateria.objects.get(
            discente=self.discente,
            asignacion_docente=asignacion,
        )
        return inscripcion, esquema

    def asignar_jefatura_ambito(self):
        seccion, _ = UnidadOrganizacional.objects.get_or_create(
            clave=UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
            defaults={
                "nombre": "Sección Académica",
                "tipo_unidad": UnidadOrganizacional.TIPO_SECCION,
                "activo": True,
            },
        )
        subseccion, _ = UnidadOrganizacional.objects.get_or_create(
            clave="SUB_EJEC_TEST",
            defaults={
                "nombre": "Subsección de Ejecución y Control Test",
                "tipo_unidad": UnidadOrganizacional.TIPO_SUBSECCION,
                "padre": seccion,
                "carrera": self.carrera,
                "activo": True,
            },
        )
        AsignacionCargo.objects.create(
            usuario=self.usuario_jefatura,
            carrera=self.carrera,
            unidad_organizacional=subseccion,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_SUB_EJEC_CTR,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            vigente_desde=timezone.localdate(),
            activo=True,
        )

    def test_construye_historial_con_acta_final_formalizada(self):
        self.formalizar_final(calificacion=Decimal("8.0"))

        historial = construir_historial_discente(self.discente)

        self.assertEqual(len(historial["resultados"]), 1)
        self.assertEqual(historial["resultados"][0].tipo_resultado, "ORDINARIO")
        self.assertEqual(historial["resultados"][0].codigo_resultado, "APROBADO")

    def test_excluye_capturas_preliminares_y_actas_no_formalizadas(self):
        CapturaCalificacionPreliminar.objects.create(
            inscripcion_materia=self.inscripcion,
            componente=self.componente_p1,
            valor=Decimal("10.0"),
            capturado_por=self.usuario_docente,
        )
        Acta.objects.create(
            asignacion_docente=self.asignacion,
            corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
            estado_acta=Acta.ESTADO_BORRADOR_DOCENTE,
            esquema=self.esquema,
            esquema_version_snapshot=self.esquema.version,
            peso_parciales_snapshot=self.esquema.peso_parciales,
            peso_final_snapshot=self.esquema.peso_final,
            umbral_exencion_snapshot=self.esquema.umbral_exencion,
            creado_por=self.usuario_docente,
        )

        historial = construir_historial_discente(self.discente)

        self.assertEqual(list(historial["resultados"]), [])

    def test_impide_extraordinario_si_no_hay_reprobacion_ordinaria(self):
        self.formalizar_final(calificacion=Decimal("7.0"))

        with self.assertRaises(ValidationError):
            registrar_extraordinario(
                self.inscripcion,
                Decimal("8.0"),
                timezone.localdate(),
                self.usuario_estadistica,
            )

    def test_impide_extraordinario_sin_acta_final_formalizada(self):
        self.inscripcion.calificacion_final = Decimal("5.0")
        self.inscripcion.codigo_resultado_oficial = CatalogoResultadoAcademico.CLAVE_REPROBADO
        self.inscripcion.cerrado_en = timezone.now()
        self.inscripcion.save(
            update_fields=["calificacion_final", "codigo_resultado_oficial", "cerrado_en"]
        )

        with self.assertRaises(ValidationError):
            registrar_extraordinario(
                self.inscripcion,
                Decimal("7.0"),
                timezone.localdate(),
                self.usuario_estadistica,
            )

    def test_impide_mas_de_un_extraordinario_por_inscripcion(self):
        self.formalizar_final(calificacion=Decimal("5.0"))
        registrar_extraordinario(
            self.inscripcion,
            Decimal("8.0"),
            timezone.localdate(),
            self.usuario_estadistica,
        )

        with self.assertRaises(Exception):
            registrar_extraordinario(
                self.inscripcion,
                Decimal("8.0"),
                timezone.localdate(),
                self.usuario_estadistica,
            )

    def test_extraordinario_aprobado_marca_ee_y_preserva_ordinario(self):
        self.formalizar_final(calificacion=Decimal("5.0"))

        extraordinario = registrar_extraordinario(
            self.inscripcion,
            Decimal("8.0"),
            timezone.localdate(),
            self.usuario_estadistica,
        )
        self.inscripcion.refresh_from_db()

        self.assertTrue(extraordinario.aprobado)
        self.assertEqual(self.inscripcion.codigo_resultado_oficial, "APROBADO")
        self.assertEqual(self.inscripcion.codigo_marca, "EE")
        self.assertEqual(extraordinario.calificacion_ordinaria, Decimal("5.0"))

    def test_extraordinario_reprobado_genera_baja_temporal(self):
        self.formalizar_final(calificacion=Decimal("5.0"))

        extraordinario = registrar_extraordinario(
            self.inscripcion,
            Decimal("4.0"),
            timezone.localdate(),
            self.usuario_estadistica,
        )
        self.discente.refresh_from_db()

        self.assertFalse(extraordinario.aprobado)
        self.assertEqual(self.discente.situacion_actual, Discente.SITUACION_BAJA_TEMPORAL)
        self.assertTrue(
            EventoSituacionAcademica.objects.filter(
                discente=self.discente,
                situacion__clave=CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL,
            ).exists()
        )

    def test_reingreso_cierra_baja_temporal_previa(self):
        registrar_baja_temporal(
            self.discente,
            fecha_inicio=date(2025, 1, 10),
            registrado_por=self.usuario_estadistica,
        )

        registrar_reingreso(
            self.discente,
            fecha_inicio=date(2025, 2, 1),
            registrado_por=self.usuario_estadistica,
        )
        self.discente.refresh_from_db()

        baja = EventoSituacionAcademica.objects.get(
            discente=self.discente,
            situacion__clave=CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL,
        )
        self.assertEqual(baja.fecha_fin, date(2025, 2, 1))
        self.assertEqual(self.discente.situacion_actual, Discente.SITUACION_REGULAR)

    def test_registra_baja_definitiva_y_actualiza_situacion_actual(self):
        situacion = CatalogoSituacionAcademica.objects.get(
            clave=CatalogoSituacionAcademica.CLAVE_BAJA_DEFINITIVA
        )

        evento = registrar_evento_situacion(
            self.discente,
            situacion=situacion,
            fecha_inicio=date(2025, 3, 1),
            motivo="Baja definitiva de prueba.",
            registrado_por=self.usuario_estadistica,
        )
        self.discente.refresh_from_db()

        self.assertEqual(evento.situacion.clave, CatalogoSituacionAcademica.CLAVE_BAJA_DEFINITIVA)
        self.assertEqual(self.discente.situacion_actual, Discente.SITUACION_BAJA_DEFINITIVA)

    def test_discente_no_consulta_historial_ajeno(self):
        self.client.force_login(self.usuario_otro_discente)

        response = self.client.get(reverse("trayectoria:historial-detalle", args=[self.discente.pk]))

        self.assertEqual(response.status_code, 403)

    def test_estadistica_consulta_historial_y_registra_extraordinario(self):
        self.formalizar_final(calificacion=Decimal("5.0"))
        self.client.force_login(self.usuario_estadistica)

        consulta = self.client.get(reverse("trayectoria:historial-detalle", args=[self.discente.pk]))
        registro = self.client.post(
            reverse("trayectoria:extraordinario-registrar"),
            data={
                "inscripcion_materia": self.inscripcion.pk,
                "fecha_aplicacion": "2025-01-20",
                "calificacion": "8.0",
            },
        )

        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(registro.status_code, 302)
        self.assertTrue(Extraordinario.objects.filter(inscripcion_materia=self.inscripcion).exists())

    def test_jefatura_consulta_historial_sin_accesos_operativos_de_trayectoria(self):
        self.client.force_login(self.usuario_jefatura)

        response = self.client.get(reverse("trayectoria:historial-busqueda"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Registrar extraordinario")
        self.assertNotContains(response, "Registrar situación académica")

    def test_jefatura_no_accede_por_url_directa_a_operaciones_de_trayectoria(self):
        self.client.force_login(self.usuario_jefatura)

        extraordinario = self.client.get(reverse("trayectoria:extraordinario-registrar"))
        situacion = self.client.get(reverse("trayectoria:situacion-registrar"))

        self.assertEqual(extraordinario.status_code, 403)
        self.assertEqual(situacion.status_code, 403)

    def test_historial_preserva_evidencia_ordinaria_con_extraordinario(self):
        self.formalizar_final(calificacion=Decimal("5.0"))
        registrar_extraordinario(
            self.inscripcion,
            Decimal("8.0"),
            timezone.localdate(),
            self.usuario_estadistica,
        )

        historial = construir_historial_discente(self.discente)
        resultado = historial["resultados"][0]

        self.assertEqual(resultado.tipo_resultado, "EXTRAORDINARIO")
        self.assertEqual(resultado.calificacion_ordinaria, Decimal("5.0"))
        self.assertEqual(resultado.codigo_resultado_ordinario, "REPROBADO")

    def test_kardex_construye_resultados_desde_acta_final_formalizada(self):
        self.formalizar_final(calificacion=Decimal("8.0"))

        kardex = construir_kardex_discente(self.discente)

        self.assertEqual(kardex.discente, self.discente)
        self.assertEqual(len(kardex.anios), 1)
        self.assertEqual(kardex.anios[0].anio_formacion, 1)
        self.assertEqual(kardex.anios[0].asignaturas[0].clave_materia, "MAT-HIST")
        self.assertEqual(kardex.anios[0].asignaturas[0].calificacion_visible, Decimal("8.0"))
        self.assertEqual(kardex.anios[0].asignaturas[0].calificacion_letra, "OCHO")

    def test_kardex_excluye_capturas_preliminares_y_actas_no_formalizadas(self):
        CapturaCalificacionPreliminar.objects.create(
            inscripcion_materia=self.inscripcion,
            componente=self.componente_p1,
            valor=Decimal("10.0"),
            capturado_por=self.usuario_docente,
        )
        Acta.objects.create(
            asignacion_docente=self.asignacion,
            corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
            estado_acta=Acta.ESTADO_BORRADOR_DOCENTE,
            esquema=self.esquema,
            esquema_version_snapshot=self.esquema.version,
            peso_parciales_snapshot=self.esquema.peso_parciales,
            peso_final_snapshot=self.esquema.peso_final,
            umbral_exencion_snapshot=self.esquema.umbral_exencion,
            creado_por=self.usuario_docente,
        )

        kardex = construir_kardex_discente(self.discente)

        self.assertEqual(kardex.anios, [])

    def test_kardex_muestra_ee_cuando_existe_extraordinario_aprobado(self):
        self.formalizar_final(calificacion=Decimal("5.0"))
        registrar_extraordinario(
            self.inscripcion,
            Decimal("8.0"),
            timezone.localdate(),
            self.usuario_estadistica,
        )

        kardex = construir_kardex_discente(self.discente)
        asignatura = kardex.anios[0].asignaturas[0]

        self.assertTrue(asignatura.marca_ee)
        self.assertEqual(asignatura.codigo_marca, "EE")
        self.assertEqual(asignatura.calificacion_visible, Decimal("8.0"))

    def test_kardex_conserva_evidencia_ordinaria_en_historial_y_muestra_ee(self):
        self.formalizar_final(calificacion=Decimal("5.0"))
        registrar_extraordinario(
            self.inscripcion,
            Decimal("8.0"),
            timezone.localdate(),
            self.usuario_estadistica,
        )

        historial = construir_historial_discente(self.discente)
        kardex = construir_kardex_discente(self.discente)

        self.assertEqual(historial["resultados"][0].calificacion_ordinaria, Decimal("5.0"))
        self.assertTrue(kardex.anios[0].asignaturas[0].marca_ee)
        self.assertEqual(kardex.anios[0].asignaturas[0].calificacion, Decimal("8.0"))

    def test_kardex_excluye_resultados_no_numericos_del_promedio_anual(self):
        self.formalizar_final(calificacion=Decimal("7.0"))
        self.inscripcion.calificacion_final = None
        self.inscripcion.codigo_resultado_oficial = CatalogoResultadoAcademico.CLAVE_ACREDITADA
        self.inscripcion.save(update_fields=["calificacion_final", "codigo_resultado_oficial"])

        kardex = construir_kardex_discente(self.discente)
        asignatura = kardex.anios[0].asignaturas[0]

        self.assertFalse(asignatura.es_numerica)
        self.assertEqual(asignatura.resultado_no_numerico, CatalogoResultadoAcademico.CLAVE_ACREDITADA)
        self.assertIsNone(kardex.anios[0].promedio_anual)

    def test_kardex_calcula_promedio_anual_con_materias_numericas(self):
        self.formalizar_final(calificacion=Decimal("8.0"))
        segunda_inscripcion, segundo_esquema = self.crear_inscripcion_para_materia(
            "MAT-HIST-2",
            "Materia promedio",
        )
        self.formalizar_final(
            inscripcion=segunda_inscripcion,
            calificacion=Decimal("9.0"),
            esquema=segundo_esquema,
        )

        kardex = construir_kardex_discente(self.discente)

        self.assertEqual(kardex.anios[0].promedio_anual, Decimal("8.5"))

    def test_discente_no_consulta_kardex_propio_ni_ajeno(self):
        self.formalizar_final(calificacion=Decimal("8.0"))
        self.client.force_login(self.usuario_discente)

        response_propio = self.client.get(
            reverse("trayectoria:kardex-detalle", args=[self.discente.pk])
        )
        response_ruta_propia = self.client.get("/trayectoria/mi-kardex/")

        self.client.force_login(self.usuario_otro_discente)
        response_ajeno = self.client.get(
            reverse("trayectoria:kardex-detalle", args=[self.discente.pk])
        )

        self.assertEqual(response_propio.status_code, 403)
        self.assertEqual(response_ruta_propia.status_code, 404)
        self.assertEqual(response_ajeno.status_code, 403)

    def test_estadistica_consulta_kardex(self):
        self.formalizar_final(calificacion=Decimal("8.0"))
        self.client.force_login(self.usuario_estadistica)

        response = self.client.get(reverse("trayectoria:kardex-detalle", args=[self.discente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kárdex oficial")
        self.assertContains(response, "MAT-HIST")

    def test_jefatura_autorizada_consulta_kardex_de_su_ambito(self):
        self.asignar_jefatura_ambito()
        self.formalizar_final(calificacion=Decimal("8.0"))
        self.client.force_login(self.usuario_jefatura)

        response = self.client.get(reverse("trayectoria:kardex-detalle", args=[self.discente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MAT-HIST")

    def test_no_existe_tabla_transaccional_kardex_oficial(self):
        nombres_modelos = {model.__name__ for model in apps.get_models()}

        self.assertNotIn("KardexOficial", nombres_modelos)

    def test_kardex_no_ofrece_exportaciones_pdf_excel(self):
        self.formalizar_final(calificacion=Decimal("8.0"))
        self.client.force_login(self.usuario_estadistica)

        response = self.client.get(reverse("trayectoria:kardex-detalle", args=[self.discente.pk]))
        contenido = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("PDF", contenido)
        self.assertNotIn("Excel", contenido)
