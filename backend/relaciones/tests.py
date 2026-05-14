import json
from datetime import date

from django.contrib import admin as django_admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from catalogos.models import (
    Antiguedad,
    Carrera,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
    ProgramaAsignaturaUbicacion,
)
from evaluacion.models import Acta, DetalleActa, EsquemaEvaluacion
from usuarios.models import AsignacionCargo, UnidadOrganizacional, Usuario

from .forms import InscripcionMateriaForm
from .models import (
    ROL_DISCENTE,
    ROL_DOCENTE,
    AdscripcionGrupo,
    Discente,
    AsignacionDocente,
    InscripcionMateria,
    MovimientoAcademico,
)
from .services import sincronizar_carga_academica


class RelacionesBaseTestCase(TestCase):
    def setUp(self):
        self.grupo_docente, _ = Group.objects.get_or_create(name=ROL_DOCENTE)
        self.grupo_discente, _ = Group.objects.get_or_create(name=ROL_DISCENTE)
        self.grupo_jefatura_carrera, _ = Group.objects.get_or_create(name="JEFE_CARRERA")
        self.grupo_estadistica, _ = Group.objects.get_or_create(name="ENCARGADO_ESTADISTICA")

        self.carrera = Carrera.objects.create(
            clave="REL_ICI",
            nombre="Ingenieria en Computacion",
        )
        self.seccion_academica = UnidadOrganizacional.objects.create(
            clave=UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
            nombre="Sección Académica",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )
        self.subseccion_academica = UnidadOrganizacional.objects.create(
            clave="REL_SUB_ACAD",
            nombre="Subsección de Ejecución y Control",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=self.seccion_academica,
            carrera=self.carrera,
        )
        self.plan = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="REL_PLAN",
            nombre="Plan relaciones",
        )
        self.antiguedad = Antiguedad.objects.create(
            plan_estudios=self.plan,
            clave="REL_ANT",
            nombre="Antiguedad relaciones",
            anio_inicio=2025,
            anio_fin=2029,
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="REL_PER",
            anio_escolar="2025-2026",
            periodo_academico=1,
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2026, 1, 31),
        )
        self.grupo = GrupoAcademico.objects.create(
            clave_grupo="REL_G1",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )
        self.grupo_destino = GrupoAcademico.objects.create(
            clave_grupo="REL_G2",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )
        self.materia = Materia.objects.create(
            clave="REL_MAT",
            nombre="Materia relaciones",
            horas_totales=64,
        )
        self.programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=self.materia,
            semestre_numero=1,
        )
        self.usuario_discente = Usuario.objects.create_user(
            username="discente_rel",
            password="segura123",
        )
        self.usuario_discente.groups.add(self.grupo_discente)
        self.usuario_docente = Usuario.objects.create_user(
            username="docente_rel",
            password="segura123",
        )
        self.usuario_docente.groups.add(self.grupo_docente)
        self.discente = Discente.objects.create(
            usuario=self.usuario_discente,
            matricula="REL0001",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )
        self.adscripcion = AdscripcionGrupo.objects.create(
            discente=self.discente,
            grupo_academico=self.grupo,
        )
        self.asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.usuario_docente,
            grupo_academico=self.grupo,
            programa_asignatura=self.programa,
        )

    def crear_usuario_discente(self, username):
        usuario = Usuario.objects.create_user(username=username, password="segura123")
        usuario.groups.add(self.grupo_discente)
        return usuario

    def crear_usuario_docente(self, username):
        usuario = Usuario.objects.create_user(username=username, password="segura123")
        usuario.groups.add(self.grupo_docente)
        return usuario

    def crear_usuario_jefatura_carrera(self, username):
        usuario = Usuario.objects.create_user(username=username, password="segura123")
        usuario.groups.add(self.grupo_jefatura_carrera)
        return usuario

    def crear_usuario_estadistica(self, username):
        usuario = Usuario.objects.create_user(username=username, password="segura123")
        usuario.groups.add(self.grupo_estadistica)
        return usuario

    def datos_asignacion_docente(self, **overrides):
        payload = {
            "usuario_docente": self.usuario_docente.pk,
            "grupo_academico": self.grupo_destino.pk,
            "programa_asignatura": self.programa.pk,
            "vigente_desde": "",
            "vigente_hasta": "",
            "activo": "on",
        }
        payload.update(overrides)
        return payload


class RelacionesModeloTests(RelacionesBaseTestCase):
    def test_discente_rechaza_usuario_sin_rol_discente(self):
        usuario = Usuario.objects.create_user(username="sin_rol_discente")
        discente = Discente(
            usuario=usuario,
            matricula="REL0002",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )

        with self.assertRaises(ValidationError) as exc:
            discente.full_clean()

        self.assertIn("usuario", exc.exception.message_dict)

    def test_discente_impide_mas_de_un_perfil_activo_por_usuario(self):
        duplicado = Discente(
            usuario=self.usuario_discente,
            matricula="REL0003",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )

        with self.assertRaises(ValidationError) as exc:
            duplicado.full_clean()

        self.assertIn("usuario", exc.exception.message_dict)

    def test_discente_rechaza_plan_inactivo(self):
        self.plan.estado = "inactivo"
        self.plan.save()

        discente = Discente(
            usuario=self.crear_usuario_discente("discente_inactivo"),
            matricula="REL0004",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )

        with self.assertRaises(ValidationError) as exc:
            discente.full_clean()

        self.assertIn("plan_estudios", exc.exception.message_dict)

    def test_adscripcion_grupo_rechaza_discente_inactivo(self):
        self.discente.activo = False
        self.discente.save()
        adscripcion = AdscripcionGrupo(
            discente=self.discente,
            grupo_academico=self.grupo_destino,
        )

        with self.assertRaises(ValidationError) as exc:
            adscripcion.full_clean()

        self.assertIn("discente", exc.exception.message_dict)

    def test_asignacion_docente_rechaza_usuario_sin_rol_docente(self):
        usuario = Usuario.objects.create_user(username="sin_rol_docente")
        asignacion = AsignacionDocente(
            usuario_docente=usuario,
            grupo_academico=self.grupo_destino,
            programa_asignatura=self.programa,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("usuario_docente", exc.exception.message_dict)

    def test_asignacion_docente_deriva_periodo_desde_grupo(self):
        self.assertEqual(self.asignacion.periodo, self.periodo)

    def test_asignacion_docente_rechaza_duplicado_activo_mismo_grupo_y_programa(self):
        duplicada = AsignacionDocente(
            usuario_docente=self.crear_usuario_docente("docente_rel_2"),
            grupo_academico=self.grupo,
            programa_asignatura=self.programa,
        )

        with self.assertRaises(ValidationError) as exc:
            duplicada.full_clean()

        self.assertIn("programa_asignatura", exc.exception.message_dict)

    def test_asignacion_docente_normal_rechaza_semestre_distinto_al_grupo(self):
        grupo_segundo = GrupoAcademico.objects.create(
            clave_grupo="REL_G3",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=2,
        )
        asignacion = AsignacionDocente(
            usuario_docente=self.crear_usuario_docente("docente_rel_3"),
            grupo_academico=grupo_segundo,
            programa_asignatura=self.programa,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("programa_asignatura", exc.exception.message_dict)

    def test_asignacion_docente_excepcional_permite_ubicacion_activa(self):
        grupo_segundo = GrupoAcademico.objects.create(
            clave_grupo="REL_G4",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=2,
        )
        materia = Materia.objects.create(
            clave="REL_MAT_EXC",
            nombre="Materia excepcional",
            horas_totales=64,
        )
        programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=materia,
            semestre_numero=1,
            ubicacion_excepcional=True,
        )
        ProgramaAsignaturaUbicacion.objects.create(
            programa_asignatura=programa,
            antiguedad=self.antiguedad,
            semestre_numero=2,
        )
        asignacion = AsignacionDocente(
            usuario_docente=self.crear_usuario_docente("docente_rel_4"),
            grupo_academico=grupo_segundo,
            programa_asignatura=programa,
        )

        asignacion.full_clean()

    def test_asignacion_docente_excepcional_rechaza_si_no_hay_ubicacion_activa(self):
        grupo_segundo = GrupoAcademico.objects.create(
            clave_grupo="REL_G5",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=2,
        )
        materia = Materia.objects.create(
            clave="REL_MAT_NOEX",
            nombre="Materia excepcional sin ubicacion",
            horas_totales=64,
        )
        programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=materia,
            semestre_numero=1,
            ubicacion_excepcional=True,
        )
        asignacion = AsignacionDocente(
            usuario_docente=self.crear_usuario_docente("docente_rel_5"),
            grupo_academico=grupo_segundo,
            programa_asignatura=programa,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("programa_asignatura", exc.exception.message_dict)

    def test_asignacion_docente_crea_inscripciones_automaticamente(self):
        self.assertTrue(
            InscripcionMateria.objects.filter(
                discente=self.discente,
                asignacion_docente=self.asignacion,
                estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
            ).exists()
        )

    def test_sincronizacion_de_carga_academica_es_idempotente(self):
        sincronizar_carga_academica(self.asignacion)
        sincronizar_carga_academica(self.asignacion)

        total = InscripcionMateria.objects.filter(
            discente=self.discente,
            asignacion_docente=self.asignacion,
            estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
        ).count()

        self.assertEqual(total, 1)

    def test_sincronizacion_crea_inscripcion_para_discente_agregado_despues(self):
        usuario = self.crear_usuario_discente("discente_rel_2")
        discente = Discente.objects.create(
            usuario=usuario,
            matricula="REL0005",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )
        AdscripcionGrupo.objects.create(
            discente=discente,
            grupo_academico=self.grupo,
        )

        creadas = sincronizar_carga_academica(self.asignacion)

        self.assertEqual(creadas, 1)
        self.assertTrue(
            InscripcionMateria.objects.filter(
                discente=discente,
                asignacion_docente=self.asignacion,
                estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
            ).exists()
        )

    def test_inscripcion_rechaza_duplicado_activo_misma_asignacion(self):
        duplicada = InscripcionMateria(
            discente=self.discente,
            asignacion_docente=self.asignacion,
        )

        with self.assertRaises(ValidationError) as exc:
            duplicada.full_clean()

        self.assertIn("asignacion_docente", exc.exception.message_dict)

    def test_campos_de_resultado_no_son_capturables_en_formulario_manual(self):
        form = InscripcionMateriaForm()

        self.assertNotIn("calificacion_final", form.fields)
        self.assertNotIn("codigo_resultado_oficial", form.fields)
        self.assertNotIn("codigo_marca", form.fields)
        self.assertNotIn("cerrado_en", form.fields)

    def test_inscripcion_form_no_falla_si_admin_excluye_discente(self):
        class FormSinDiscente(InscripcionMateriaForm):
            class Meta(InscripcionMateriaForm.Meta):
                fields = ["asignacion_docente", "estado_inscripcion", "intento_numero"]

        form = FormSinDiscente()

        self.assertNotIn("discente", form.fields)
        self.assertIn("asignacion_docente", form.fields)

    def test_movimiento_cambio_grupo_exige_grupo_destino(self):
        movimiento = MovimientoAcademico(
            discente=self.discente,
            periodo=self.periodo,
            tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
            grupo_origen=self.grupo,
        )

        with self.assertRaises(ValidationError) as exc:
            movimiento.full_clean()

        self.assertIn("grupo_destino", exc.exception.message_dict)

    def test_movimiento_cambio_grupo_exige_grupo_origen(self):
        movimiento = MovimientoAcademico(
            discente=self.discente,
            periodo=self.periodo,
            tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
            grupo_destino=self.grupo_destino,
        )

        with self.assertRaises(ValidationError) as exc:
            movimiento.full_clean()

        self.assertIn("grupo_origen", exc.exception.message_dict)

    def test_movimiento_cambio_grupo_rechaza_mismo_origen_y_destino(self):
        movimiento = MovimientoAcademico(
            discente=self.discente,
            periodo=self.periodo,
            tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
            grupo_origen=self.grupo,
            grupo_destino=self.grupo,
        )

        with self.assertRaises(ValidationError) as exc:
            movimiento.full_clean()

        self.assertIn("grupo_destino", exc.exception.message_dict)

    def test_movimiento_extemporaneo_exige_observaciones_minimas(self):
        movimiento = MovimientoAcademico(
            discente=self.discente,
            periodo=self.periodo,
            tipo_movimiento=MovimientoAcademico.ALTA_EXTEMPORANEA,
            observaciones="corto",
        )

        with self.assertRaises(ValidationError) as exc:
            movimiento.full_clean()

        self.assertIn("observaciones", exc.exception.message_dict)

    def test_movimiento_valido_conserva_grupos_y_observaciones(self):
        fecha_movimiento = self.adscripcion.vigente_desde
        movimiento = MovimientoAcademico.objects.create(
            discente=self.discente,
            periodo=self.periodo,
            tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
            grupo_origen=self.grupo,
            grupo_destino=self.grupo_destino,
            fecha_movimiento=fecha_movimiento,
            observaciones="Cambio solicitado por ajuste operativo.",
        )

        self.assertEqual(movimiento.grupo_origen, self.grupo)
        self.assertEqual(movimiento.grupo_destino, self.grupo_destino)

    def test_movimiento_cambio_grupo_actualiza_adscripcion_activa(self):
        fecha_movimiento = self.adscripcion.vigente_desde
        MovimientoAcademico.objects.create(
            discente=self.discente,
            periodo=self.periodo,
            tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
            grupo_origen=self.grupo,
            grupo_destino=self.grupo_destino,
            fecha_movimiento=fecha_movimiento,
            observaciones="Cambio solicitado por ajuste operativo.",
        )

        self.adscripcion.refresh_from_db()
        self.assertFalse(self.adscripcion.activo)
        self.assertEqual(self.adscripcion.vigente_hasta, fecha_movimiento)

        adscripcion_destino = AdscripcionGrupo.objects.get(
            discente=self.discente,
            grupo_academico=self.grupo_destino,
            activo=True,
        )
        self.assertEqual(adscripcion_destino.vigente_desde, fecha_movimiento)

        activas_periodo = AdscripcionGrupo.objects.filter(
            discente=self.discente,
            grupo_academico__periodo=self.periodo,
            activo=True,
        )
        self.assertEqual(activas_periodo.count(), 1)
        self.assertEqual(activas_periodo.get().grupo_academico, self.grupo_destino)

    def test_movimiento_cambio_grupo_da_baja_inscripciones_origen_y_crea_destino(self):
        asignacion_destino = AsignacionDocente.objects.create(
            usuario_docente=self.crear_usuario_docente("docente_destino"),
            grupo_academico=self.grupo_destino,
            programa_asignatura=self.programa,
        )
        inscripcion_origen = InscripcionMateria.objects.get(
            discente=self.discente,
            asignacion_docente=self.asignacion,
        )

        MovimientoAcademico.objects.create(
            discente=self.discente,
            periodo=self.periodo,
            tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
            grupo_origen=self.grupo,
            grupo_destino=self.grupo_destino,
            fecha_movimiento=self.adscripcion.vigente_desde,
            observaciones="Cambio solicitado por ajuste operativo.",
        )

        inscripcion_origen.refresh_from_db()
        self.assertEqual(inscripcion_origen.estado_inscripcion, InscripcionMateria.ESTADO_BAJA)
        self.assertTrue(
            InscripcionMateria.objects.filter(
                discente=self.discente,
                asignacion_docente=asignacion_destino,
                estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
            ).exists()
        )

    def test_movimiento_cambio_grupo_bloquea_inscripciones_con_actas_vivas(self):
        esquema = EsquemaEvaluacion.objects.create(
            programa_asignatura=self.programa,
            version="v-acta-movimiento",
        )
        acta = Acta.objects.create(
            asignacion_docente=self.asignacion,
            corte_codigo="P1",
            estado_acta=Acta.ESTADO_BORRADOR_DOCENTE,
            esquema=esquema,
            esquema_version_snapshot=esquema.version,
            peso_parciales_snapshot=esquema.peso_parciales,
            peso_final_snapshot=esquema.peso_final,
            umbral_exencion_snapshot=esquema.umbral_exencion,
            creado_por=self.usuario_docente,
        )
        DetalleActa.objects.create(
            acta=acta,
            inscripcion_materia=InscripcionMateria.objects.get(
                discente=self.discente,
                asignacion_docente=self.asignacion,
            ),
        )

        with self.assertRaises(ValidationError) as exc:
            MovimientoAcademico.objects.create(
                discente=self.discente,
                periodo=self.periodo,
                tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
                grupo_origen=self.grupo,
                grupo_destino=self.grupo_destino,
                fecha_movimiento=self.adscripcion.vigente_desde,
                observaciones="Cambio solicitado por ajuste operativo.",
            )

        self.assertIn("discente", exc.exception.message_dict)
        self.adscripcion.refresh_from_db()
        self.assertTrue(self.adscripcion.activo)
        self.assertFalse(
            MovimientoAcademico.objects.filter(
                discente=self.discente,
                grupo_origen=self.grupo,
                grupo_destino=self.grupo_destino,
            ).exists()
        )

    def test_movimiento_cambio_grupo_rechaza_origen_no_activo_y_no_guarda_movimiento(self):
        grupo_alterno = GrupoAcademico.objects.create(
            clave_grupo="REL_G6",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )

        with self.assertRaises(ValidationError) as exc:
            MovimientoAcademico.objects.create(
                discente=self.discente,
                periodo=self.periodo,
                tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
                grupo_origen=self.grupo_destino,
                grupo_destino=grupo_alterno,
                fecha_movimiento=date(2025, 9, 1),
                observaciones="Cambio solicitado por ajuste operativo.",
            )

        self.assertIn("grupo_origen", exc.exception.message_dict)
        self.assertFalse(
            MovimientoAcademico.objects.filter(
                discente=self.discente,
                grupo_origen=self.grupo_destino,
                grupo_destino=grupo_alterno,
            ).exists()
        )


class RelacionesPermisosViewTests(RelacionesBaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("relaciones:asignacion-docente-list")

    def test_vista_redirige_usuario_anonimo_a_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response["Location"])

    def test_vista_bloquea_usuario_sin_rol_o_cargo(self):
        usuario = Usuario.objects.create_user(
            username="usuario_simple",
            password="segura123",
        )
        self.client.force_login(usuario)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_vista_permite_grupo_estadistica(self):
        usuario = self.crear_usuario_estadistica("estadistica")
        self.client.force_login(usuario)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asignaciones docentes")

    def test_vista_permite_cargo_jefatura_carrera_activo(self):
        usuario = Usuario.objects.create_user(
            username="cargo_jefatura_carrera",
            password="segura123",
        )
        usuario.groups.add(self.grupo_jefatura_carrera)
        AsignacionCargo.objects.create(
            usuario=usuario,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            carrera=self.carrera,
            unidad_organizacional=self.subseccion_academica,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            activo=True,
        )
        self.client.force_login(usuario)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_jefatura_carrera_puede_crear_asignacion_docente(self):
        usuario = self.crear_usuario_jefatura_carrera("jefe_carrera")
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("relaciones:asignacion-docente-create"),
            data=self.datos_asignacion_docente(),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            AsignacionDocente.objects.filter(
                grupo_academico=self.grupo_destino,
                programa_asignatura=self.programa,
            ).exists()
        )

    def test_estadistica_no_puede_crear_asignacion_docente(self):
        usuario = self.crear_usuario_estadistica("estadistica_crea")
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("relaciones:asignacion-docente-create"),
            data=self.datos_asignacion_docente(),
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            AsignacionDocente.objects.filter(
                grupo_academico=self.grupo_destino,
                programa_asignatura=self.programa,
            ).exists()
        )

    def test_estadistica_no_puede_modificar_asignacion_docente(self):
        usuario = self.crear_usuario_estadistica("estadistica_edita")
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("relaciones:asignacion-docente-update", args=[self.asignacion.pk]),
            data=self.datos_asignacion_docente(
                grupo_academico=self.grupo.pk,
                vigente_hasta="",
            ),
        )

        self.assertEqual(response.status_code, 403)

    def test_superusuario_puede_modificar_asignacion_docente(self):
        usuario = Usuario.objects.create_superuser(
            username="admin_relaciones",
            password="segura123",
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("relaciones:asignacion-docente-update", args=[self.asignacion.pk]),
            data=self.datos_asignacion_docente(
                grupo_academico=self.grupo.pk,
                vigente_hasta="",
            ),
        )

        self.assertEqual(response.status_code, 302)

    def test_superusuario_puede_crear_asignacion_docente(self):
        usuario = Usuario.objects.create_superuser(
            username="admin_crea_relaciones",
            password="segura123",
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("relaciones:asignacion-docente-create"),
            data=self.datos_asignacion_docente(),
        )

        self.assertEqual(response.status_code, 302)

    def test_usuario_sin_cargo_no_puede_crear_asignacion_docente(self):
        usuario = Usuario.objects.create_user(
            username="sin_cargo_asignacion",
            password="segura123",
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("relaciones:asignacion-docente-create"),
            data=self.datos_asignacion_docente(),
        )

        self.assertEqual(response.status_code, 403)


class AsignacionDocenteAdminPermisosTests(RelacionesBaseTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.model_admin = django_admin.site._registry[AsignacionDocente]

    def build_request(self, usuario):
        request = self.factory.get("/admin/relaciones/asignaciondocente/")
        request.user = usuario
        return request

    def test_admin_estadistica_solo_consulta_asignacion_docente(self):
        usuario = self.crear_usuario_estadistica("admin_estadistica")
        usuario.is_staff = True
        usuario.save()
        request = self.build_request(usuario)

        self.assertTrue(self.model_admin.has_view_permission(request))
        self.assertFalse(self.model_admin.has_add_permission(request))
        self.assertFalse(self.model_admin.has_change_permission(request, self.asignacion))
        self.assertNotIn("sincronizar_carga_academica", self.model_admin.get_actions(request))

    def test_admin_jefatura_carrera_opera_asignacion_docente(self):
        usuario = self.crear_usuario_jefatura_carrera("admin_jefatura")
        usuario.is_staff = True
        usuario.save()
        request = self.build_request(usuario)

        self.assertTrue(self.model_admin.has_view_permission(request))
        self.assertTrue(self.model_admin.has_add_permission(request))
        self.assertTrue(self.model_admin.has_change_permission(request, self.asignacion))
        self.assertIn("sincronizar_carga_academica", self.model_admin.get_actions(request))


class RelacionesPortalApi10C6Tests(RelacionesBaseTestCase):
    def test_api_estadistica_crea_cambio_grupo_sin_exponer_matricula(self):
        usuario = self.crear_usuario_estadistica("estadistica_api_mov")
        self.client.force_login(usuario)

        response = self.client.post(
            "/api/relaciones/movimientos/cambio-grupo/",
            data=json.dumps({
                "discente_id": self.discente.pk,
                "periodo_id": self.periodo.pk,
                "grupo_origen_id": self.grupo.pk,
                "grupo_destino_id": self.grupo_destino.pk,
                "fecha_movimiento": date.today().isoformat(),
                "observaciones": "Cambio operativo de prueba",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content.decode())
        self.adscripcion.refresh_from_db()
        self.assertFalse(self.adscripcion.activo)
        self.assertTrue(
            AdscripcionGrupo.objects.filter(
                discente=self.discente,
                grupo_academico=self.grupo_destino,
                activo=True,
            ).exists()
        )
        self.assertNotIn("REL0001", response.content.decode())

    def test_api_docente_no_consulta_movimientos_globales(self):
        self.client.force_login(self.usuario_docente)

        response = self.client.get("/api/relaciones/movimientos/")

        self.assertEqual(response.status_code, 403)
