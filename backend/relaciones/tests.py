from datetime import date

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from catalogos.models import (
    Antiguedad,
    Carrera,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
)
from usuarios.models import AsignacionCargo, Usuario

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

        self.carrera = Carrera.objects.create(
            clave="REL_ICI",
            nombre="Ingenieria en Computacion",
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
        movimiento = MovimientoAcademico.objects.create(
            discente=self.discente,
            periodo=self.periodo,
            tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO,
            grupo_origen=self.grupo,
            grupo_destino=self.grupo_destino,
            observaciones="Cambio solicitado por ajuste operativo.",
        )

        self.assertEqual(movimiento.grupo_origen, self.grupo)
        self.assertEqual(movimiento.grupo_destino, self.grupo_destino)


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
        usuario = Usuario.objects.create_user(
            username="estadistica",
            password="segura123",
        )
        grupo, _ = Group.objects.get_or_create(name="ESTADISTICA")
        usuario.groups.add(grupo)
        self.client.force_login(usuario)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asignaciones docentes")

    def test_vista_permite_cargo_estadistica_activo(self):
        usuario = Usuario.objects.create_user(
            username="cargo_estadistica",
            password="segura123",
        )
        AsignacionCargo.objects.create(
            usuario=usuario,
            cargo_codigo="estadistica",
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            activo=True,
        )
        self.client.force_login(usuario)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
