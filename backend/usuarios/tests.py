from datetime import date, timedelta
from io import StringIO

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.forms import modelform_factory
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalogos.models import ESTADO_INACTIVO, Carrera
from catalogos.models import Antiguedad, GrupoAcademico, Materia, PeriodoEscolar, PlanEstudios, ProgramaAsignatura
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria

from .admin import UsuarioAdmin
from .forms import LoginFormulario, UsuarioAdminCreationForm, UsuarioAdminForm
from .models import AsignacionCargo, GradoEmpleo, UnidadOrganizacional, Usuario
from .signals import crear_roles_base


class VigenciaAsignacionCargoTests(TestCase):
    def setUp(self):
        self.grupo_discente, _ = Group.objects.get_or_create(name=AsignacionCargo.ROL_DISCENTE)
        self.grupo_docente, _ = Group.objects.get_or_create(name=AsignacionCargo.ROL_DOCENTE)
        self.grupo_jefe_pedagogica, _ = Group.objects.get_or_create(
            name=AsignacionCargo.ROL_JEFE_PEDAGOGICA
        )
        self.grupo_jefe_academico, _ = Group.objects.get_or_create(
            name=AsignacionCargo.ROL_JEFE_ACADEMICO
        )
        self.grupo_jefatura_academica, _ = Group.objects.get_or_create(
            name=AsignacionCargo.ROL_JEFATURA_ACADEMICA
        )
        self.grupo_jefe_carrera, _ = Group.objects.get_or_create(
            name=AsignacionCargo.ROL_JEFE_CARRERA
        )
        self.grupo_jefatura_carrera, _ = Group.objects.get_or_create(
            name=AsignacionCargo.ROL_JEFATURA_CARRERA
        )
        self.usuario = Usuario.objects.create_user(
            username="usuario_vigencia",
            password="segura123",
        )
        self.usuario.groups.add(
            self.grupo_docente,
            self.grupo_jefe_pedagogica,
            self.grupo_jefe_academico,
            self.grupo_jefe_carrera,
        )
        self.carrera_icis = Carrera.objects.create(
            clave="ICIS",
            nombre="Ingenieros en Comunicaciones e Informática",
        )
        self.carrera_ices = Carrera.objects.create(
            clave="ICES",
            nombre="Ingenieros Constructores",
        )
        self.seccion_pedagogica = UnidadOrganizacional.objects.create(
            clave=UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA,
            nombre="Sección Pedagógica",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )
        self.seccion_academica = UnidadOrganizacional.objects.create(
            clave=UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
            nombre="Sección Académica",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )
        self.subseccion_academica_icis = UnidadOrganizacional.objects.create(
            clave="SUB_ACAD_ICIS",
            nombre="Subsección de Ejecución y Control ICI",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=self.seccion_academica,
            carrera=self.carrera_icis,
        )
        self.subseccion_pedagogica_icis = UnidadOrganizacional.objects.create(
            clave="SUB_PED_ICIS",
            nombre="Subsección de Planeación y Evaluación ICI",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=self.seccion_pedagogica,
            carrera=self.carrera_icis,
        )

    def test_creacion_autocompleta_vigente_desde_si_se_omite(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            carrera=self.carrera_icis,
            unidad_organizacional=self.subseccion_academica_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        self.assertEqual(asignacion.vigente_desde, timezone.localdate())
        self.assertIsNone(asignacion.vigente_hasta)

    def test_crea_unidad_organizacional_basica(self):
        unidad = UnidadOrganizacional.objects.create(
            clave="SEC_PED",
            nombre="Sección Pedagógica",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )

        self.assertEqual(str(unidad), "Sección Pedagógica")
        self.assertTrue(unidad.activo)

    def test_unidad_no_permite_subseccion_sin_padre(self):
        unidad = UnidadOrganizacional(
            clave="SUB_SIN_PADRE",
            nombre="Subsección sin padre",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
        )

        with self.assertRaises(ValidationError) as exc:
            unidad.full_clean()

        self.assertIn("padre", exc.exception.message_dict)

    def test_unidad_no_permite_subseccion_con_padre_subseccion(self):
        seccion = UnidadOrganizacional.objects.create(
            clave="SEC_BASE",
            nombre="Sección base",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )
        subseccion_padre = UnidadOrganizacional.objects.create(
            clave="SUB_PADRE",
            nombre="Subsección padre",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=seccion,
        )
        unidad = UnidadOrganizacional(
            clave="SUB_HIJA",
            nombre="Subsección hija",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=subseccion_padre,
        )

        with self.assertRaises(ValidationError) as exc:
            unidad.full_clean()

        self.assertIn("padre", exc.exception.message_dict)

    def test_unidad_no_permite_seccion_con_carrera(self):
        unidad = UnidadOrganizacional(
            clave="SEC_CARRERA",
            nombre="Sección con carrera",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
            carrera=self.carrera_icis,
        )

        with self.assertRaises(ValidationError) as exc:
            unidad.full_clean()

        self.assertIn("carrera", exc.exception.message_dict)

    def test_unidad_permite_subseccion_con_padre_seccion(self):
        seccion = UnidadOrganizacional.objects.create(
            clave="SEC_PLAN",
            nombre="Sección Planeación",
            tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
        )
        unidad = UnidadOrganizacional.objects.create(
            clave="SUB_PLAN_ICIS",
            nombre="Subsección de Planeación y Evaluación",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=seccion,
            carrera=self.carrera_icis,
        )

        self.assertEqual(unidad.padre, seccion)
        self.assertEqual(unidad.carrera, self.carrera_icis)

    def test_asignacion_cargo_conserva_carrera_y_acepta_unidad_opcional(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            carrera=self.carrera_icis,
            unidad_organizacional=self.subseccion_academica_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        self.assertEqual(asignacion.carrera, self.carrera_icis)
        self.assertEqual(asignacion.unidad_organizacional, self.subseccion_academica_icis)

    def test_edicion_respeta_vigente_desde_existente(self):
        fecha_existente = timezone.localdate() - timedelta(days=15)
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_DOCENTE,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_desde=fecha_existente,
            vigente_hasta=fecha_existente + timedelta(days=5),
        )

        asignacion.activo = False
        asignacion.save()
        asignacion.refresh_from_db()

        self.assertEqual(asignacion.vigente_desde, fecha_existente)

    def test_edicion_de_registro_legado_sin_vigente_desde_lo_autocompleta(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_DOCENTE,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )
        AsignacionCargo.objects.filter(pk=asignacion.pk).update(vigente_desde=None)

        asignacion.refresh_from_db()
        self.assertIsNone(asignacion.vigente_desde)

        asignacion.activo = True
        asignacion.save()
        asignacion.refresh_from_db()

        self.assertEqual(asignacion.vigente_desde, timezone.localdate())

    def test_modelform_no_exige_vigencias_y_autocompleta_vigente_desde(self):
        asignacion_form_class = modelform_factory(
            AsignacionCargo,
            fields=[
                "usuario",
                "cargo_codigo",
                "tipo_designacion",
                "vigente_desde",
                "vigente_hasta",
                "activo",
            ],
        )
        form = asignacion_form_class(
            data={
                "usuario": self.usuario.pk,
                "cargo_codigo": AsignacionCargo.CARGO_DOCENTE,
                "tipo_designacion": AsignacionCargo.DESIGNACION_TITULAR,
                "vigente_desde": "",
                "vigente_hasta": "",
                "activo": "on",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        asignacion = form.save()

        self.assertEqual(asignacion.vigente_desde, timezone.localdate())
        self.assertIsNone(asignacion.vigente_hasta)

    def test_vigente_hasta_sigue_validando_consistencia_temporal(self):
        hoy = timezone.localdate()
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_DOCENTE,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            vigente_desde=hoy,
            vigente_hasta=hoy - timedelta(days=1),
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("vigente_hasta", exc.exception.message_dict)

    def test_usuario_puede_tener_multiples_asignaciones_de_cargo(self):
        asignacion_titular = AsignacionCargo.objects.create(
            usuario=self.usuario,
            carrera=self.carrera_icis,
            unidad_organizacional=self.subseccion_academica_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )
        asignacion_accidental = AsignacionCargo.objects.create(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_DOCENTE,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_hasta=timezone.localdate() + timedelta(days=10),
        )

        self.assertEqual(self.usuario.asignaciones_cargo.count(), 2)
        self.assertIn(asignacion_titular, self.usuario.asignaciones_cargo.all())
        self.assertIn(asignacion_accidental, self.usuario.asignaciones_cargo.all())

    def test_cargo_codigo_es_lista_controlada_y_no_texto_libre(self):
        asignacion_form_class = modelform_factory(
            AsignacionCargo,
            fields=["usuario", "cargo_codigo", "tipo_designacion"],
        )

        form = asignacion_form_class(
            data={
                "usuario": self.usuario.pk,
                "cargo_codigo": "CARGO_ESCRITO_A_MANO",
                "tipo_designacion": AsignacionCargo.DESIGNACION_TITULAR,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("cargo_codigo", form.errors)

    def test_lista_de_cargos_mantiene_jefaturas_dinamicas_y_no_coordinador(self):
        choices = dict(AsignacionCargo.CARGO_CHOICES)

        self.assertEqual(choices[AsignacionCargo.CARGO_JEFE_CARRERA], "Jefe de carrera")
        self.assertEqual(choices[AsignacionCargo.CARGO_JEFE_PEDAGOGICA], "Jefe de Pedagógica")
        self.assertEqual(
            choices[AsignacionCargo.CARGO_JEFE_SUBSECCION_PEDAGOGICA],
            "Jefe de subsección de Planeación y Evaluación",
        )
        self.assertNotIn("JEFE_CARRERA_ICIS", choices)
        self.assertNotIn("JEFE_CARRERA_ICES", choices)
        self.assertNotIn("JEFE_SUBSECCION", choices)
        self.assertNotIn("COORDINADOR", choices)

    def test_admin_asignacion_cargo_carga_js_para_ocultar_carrera_si_no_aplica(self):
        asignacion_admin = admin.site._registry[AsignacionCargo]

        self.assertIn(
            "usuarios/admin/asignacion_cargo.js",
            asignacion_admin.media._js,
        )

    def test_admin_unidad_organizacional_muestra_jerarquia_en_dropdown(self):
        asignacion_admin = admin.site._registry[AsignacionCargo]
        db_field = AsignacionCargo._meta.get_field("unidad_organizacional")
        formfield = asignacion_admin.formfield_for_foreignkey(db_field, request=None)

        self.assertEqual(
            formfield.label_from_instance(self.seccion_academica),
            "Sección Académica",
        )
        self.assertEqual(
            formfield.label_from_instance(self.subseccion_academica_icis),
            "Sección Académica -> Subsección de Ejecución y Control ICI",
        )
        self.assertEqual(
            formfield.label_from_instance(self.subseccion_pedagogica_icis),
            "Sección Pedagógica -> Subsección de Planeación y Evaluación ICI",
        )

    def test_jefe_carrera_exige_subseccion_academica_con_carrera(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("unidad_organizacional", exc.exception.message_dict)

        subseccion_sin_carrera = UnidadOrganizacional.objects.create(
            clave="SUB_ACAD_SIN_CARR",
            nombre="Subsección académica sin carrera",
            tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
            padre=self.seccion_academica,
        )
        asignacion.unidad_organizacional = subseccion_sin_carrera

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("unidad_organizacional", exc.exception.message_dict)

    def test_jefe_pedagogica_es_cargo_de_seccion_sin_carrera(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        asignacion.full_clean()

        asignacion.carrera = self.carrera_icis
        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()
        self.assertIn("carrera", exc.exception.message_dict)

    def test_jefe_academico_requiere_seccion_academica(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_ACADEMICO,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("unidad_organizacional", exc.exception.message_dict)

        asignacion.unidad_organizacional = self.seccion_academica
        asignacion.full_clean()

    def test_jefe_subseccion_pedagogica_requiere_subseccion_de_pedagogica_con_carrera(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            unidad_organizacional=self.subseccion_academica_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_SUBSECCION_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("unidad_organizacional", exc.exception.message_dict)

        asignacion.unidad_organizacional = self.subseccion_pedagogica_icis
        asignacion.full_clean()

    def test_carrera_de_asignacion_debe_coincidir_con_unidad(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            carrera=self.carrera_ices,
            unidad_organizacional=self.subseccion_academica_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("carrera", exc.exception.message_dict)

    def test_discente_no_puede_recibir_cargos_institucionales(self):
        usuario_discente = Usuario.objects.create_user(username="discente_cargo", password="segura123")
        usuario_discente.groups.add(self.grupo_discente)
        asignacion = AsignacionCargo(
            usuario=usuario_discente,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("usuario", exc.exception.message_dict)

    def test_docente_requiere_grupo_docente(self):
        usuario_sin_docente = Usuario.objects.create_user(
            username="sin_rol_docente",
            password="segura123",
        )
        usuario_sin_docente.groups.add(self.grupo_jefe_carrera)
        asignacion = AsignacionCargo(
            usuario=usuario_sin_docente,
            cargo_codigo=AsignacionCargo.CARGO_DOCENTE,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("usuario", exc.exception.message_dict)

        usuario_sin_docente.groups.add(self.grupo_docente)
        asignacion.full_clean()

    def test_jefaturas_requieren_grupo_compatible(self):
        usuario_docente = Usuario.objects.create_user(username="docente_no_jefe", password="segura123")
        usuario_docente.groups.add(self.grupo_docente)
        asignacion = AsignacionCargo(
            usuario=usuario_docente,
            unidad_organizacional=self.seccion_academica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_ACADEMICO,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("usuario", exc.exception.message_dict)

        usuario_docente.groups.add(self.grupo_jefatura_academica)
        asignacion.full_clean()

    def test_jefe_subseccion_pedagogica_acepta_temporalmente_grupo_jefe_pedagogica(self):
        usuario_jefe_pedagogica = Usuario.objects.create_user(
            username="jefe_sub_ped",
            password="segura123",
        )
        usuario_jefe_pedagogica.groups.add(self.grupo_jefe_pedagogica)
        asignacion = AsignacionCargo(
            usuario=usuario_jefe_pedagogica,
            unidad_organizacional=self.subseccion_pedagogica_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_SUBSECCION_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        asignacion.full_clean()

    def test_jefe_carrera_acepta_alias_jefatura_carrera(self):
        usuario_jefatura = Usuario.objects.create_user(username="jefatura_carrera", password="segura123")
        usuario_jefatura.groups.add(self.grupo_jefatura_carrera)
        asignacion = AsignacionCargo(
            usuario=usuario_jefatura,
            carrera=self.carrera_icis,
            unidad_organizacional=self.subseccion_academica_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        asignacion.full_clean()

    def test_cargo_global_no_permite_carrera(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            carrera=self.carrera_icis,
            cargo_codigo=AsignacionCargo.CARGO_DOCENTE,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("carrera", exc.exception.message_dict)

    def test_descripcion_de_cargo_incluye_carrera_cuando_aplica(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            carrera=self.carrera_icis,
            unidad_organizacional=self.subseccion_academica_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        self.assertEqual(
            asignacion.cargo_descripcion(),
            f"Jefe de carrera de {self.carrera_icis}",
        )

    def test_no_permite_dos_titulares_activos_traslapados_mismo_cargo_unidad(self):
        AsignacionCargo.objects.create(
            usuario=self.usuario,
            unidad_organizacional=self.seccion_academica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_ACADEMICO,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            vigente_desde=date(2026, 1, 1),
        )
        otro_usuario = Usuario.objects.create_user(username="otro_titular", password="segura123")
        asignacion = AsignacionCargo(
            usuario=otro_usuario,
            unidad_organizacional=self.seccion_academica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_ACADEMICO,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            vigente_desde=date(2026, 6, 1),
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("tipo_designacion", exc.exception.message_dict)

    def test_permite_titular_y_accidental_mismo_cargo_unidad(self):
        AsignacionCargo.objects.create(
            usuario=self.usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
            vigente_desde=date(2026, 1, 1),
        )
        otro_usuario = Usuario.objects.create_user(username="jefe_accidental", password="segura123")
        otro_usuario.groups.add(self.grupo_jefe_pedagogica)
        asignacion = AsignacionCargo(
            usuario=otro_usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_desde=date(2026, 3, 1),
            vigente_hasta=date(2026, 3, 31),
        )

        asignacion.full_clean()

    def test_accidental_exige_vigente_hasta(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_desde=date(2026, 3, 1),
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("vigente_hasta", exc.exception.message_dict)

    def test_no_permite_accidentales_traslapados_mismo_cargo_unidad(self):
        AsignacionCargo.objects.create(
            usuario=self.usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_desde=date(2026, 3, 1),
            vigente_hasta=date(2026, 3, 31),
        )
        otro_usuario = Usuario.objects.create_user(username="otro_accidental", password="segura123")
        asignacion = AsignacionCargo(
            usuario=otro_usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_desde=date(2026, 3, 15),
            vigente_hasta=date(2026, 4, 15),
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("tipo_designacion", exc.exception.message_dict)

    def test_permite_accidentales_no_traslapados_mismo_cargo_unidad(self):
        AsignacionCargo.objects.create(
            usuario=self.usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_desde=date(2026, 3, 1),
            vigente_hasta=date(2026, 3, 31),
        )
        otro_usuario = Usuario.objects.create_user(username="accidental_posterior", password="segura123")
        otro_usuario.groups.add(self.grupo_jefe_pedagogica)
        asignacion = AsignacionCargo(
            usuario=otro_usuario,
            unidad_organizacional=self.seccion_pedagogica,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_desde=date(2026, 4, 1),
            vigente_hasta=date(2026, 4, 30),
        )

        asignacion.full_clean()

    def test_tipo_designacion_solo_permite_titular_y_accidental(self):
        choices = [codigo for codigo, _ in AsignacionCargo.TIPO_DESIGNACION_CHOICES]

        self.assertEqual(
            choices,
            [
                AsignacionCargo.DESIGNACION_TITULAR,
                AsignacionCargo.DESIGNACION_ACCIDENTAL,
            ],
        )


class SeedUnidadesOrganizacionalesCommandTests(TestCase):
    def setUp(self):
        self.carrera_activa = Carrera.objects.create(
            clave="ICIS",
            nombre="Ingenieros en Comunicaciones e Informática",
        )
        self.carrera_inactiva = Carrera.objects.create(
            clave="INACT",
            nombre="Carrera inactiva",
            estado=ESTADO_INACTIVO,
        )

    def test_comando_crea_unidades_base_para_carreras_activas(self):
        salida = StringIO()

        call_command("seed_unidades_organizacionales", stdout=salida)

        seccion_pedagogica = UnidadOrganizacional.objects.get(
            clave=UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA
        )
        seccion_academica = UnidadOrganizacional.objects.get(
            clave=UnidadOrganizacional.CLAVE_SECCION_ACADEMICA
        )
        subseccion_pedagogica = UnidadOrganizacional.objects.get(
            clave="SUB_PLAN_EVAL_ICIS"
        )
        subseccion_academica = UnidadOrganizacional.objects.get(
            clave="SUB_EJEC_CTRL_ICIS"
        )

        self.assertEqual(seccion_pedagogica.tipo_unidad, UnidadOrganizacional.TIPO_SECCION)
        self.assertIsNone(seccion_pedagogica.padre)
        self.assertIsNone(seccion_pedagogica.carrera)
        self.assertEqual(seccion_academica.tipo_unidad, UnidadOrganizacional.TIPO_SECCION)
        self.assertIsNone(seccion_academica.padre)
        self.assertIsNone(seccion_academica.carrera)

        self.assertEqual(subseccion_pedagogica.tipo_unidad, UnidadOrganizacional.TIPO_SUBSECCION)
        self.assertEqual(subseccion_pedagogica.padre, seccion_pedagogica)
        self.assertEqual(subseccion_pedagogica.carrera, self.carrera_activa)
        self.assertEqual(subseccion_academica.tipo_unidad, UnidadOrganizacional.TIPO_SUBSECCION)
        self.assertEqual(subseccion_academica.padre, seccion_academica)
        self.assertEqual(subseccion_academica.carrera, self.carrera_activa)

        self.assertFalse(
            UnidadOrganizacional.objects.filter(clave="SUB_PLAN_EVAL_INACT").exists()
        )
        self.assertFalse(
            UnidadOrganizacional.objects.filter(clave="SUB_EJEC_CTRL_INACT").exists()
        )

    def test_comando_es_idempotente_y_no_duplica_unidades(self):
        call_command("seed_unidades_organizacionales", stdout=StringIO())
        total_inicial = UnidadOrganizacional.objects.count()

        call_command("seed_unidades_organizacionales", stdout=StringIO())

        self.assertEqual(UnidadOrganizacional.objects.count(), total_inicial)


class UsuarioUltimoAccesoTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_acceso",
            password="segura123",
        )

    def test_fechas_de_sistema_no_son_editables_en_modelform(self):
        usuario_form_class = modelform_factory(Usuario, fields="__all__")
        form = usuario_form_class()

        self.assertNotIn("last_login", form.fields)
        self.assertNotIn("date_joined", form.fields)
        self.assertNotIn("ultimo_acceso", form.fields)

    def test_fechas_de_sistema_son_solo_lectura_en_admin_y_no_aparecen_en_alta(self):
        usuario_admin = admin.site._registry[Usuario]

        self.assertIsInstance(usuario_admin, UsuarioAdmin)
        self.assertIn("last_login", usuario_admin.readonly_fields)
        self.assertIn("date_joined", usuario_admin.readonly_fields)
        self.assertIn("ultimo_acceso", usuario_admin.readonly_fields)

        add_fields = [
            field
            for _, fieldset_options in usuario_admin.add_fieldsets
            for field in fieldset_options.get("fields", ())
        ]

        self.assertNotIn("last_login", add_fields)
        self.assertNotIn("date_joined", add_fields)
        self.assertNotIn("ultimo_acceso", add_fields)

    def test_signal_de_login_actualiza_ultimo_acceso(self):
        self.assertIsNone(self.usuario.ultimo_acceso)
        antes = timezone.now()

        user_logged_in.send(
            sender=Usuario,
            request=None,
            user=self.usuario,
        )

        self.usuario.refresh_from_db()

        self.assertIsNotNone(self.usuario.ultimo_acceso)
        self.assertGreaterEqual(self.usuario.ultimo_acceso, antes)


class RolesPermisosAutomaticosTests(TestCase):
    def setUp(self):
        crear_roles_base(sender=None)

    def permiso(self, app_label, modelo, accion):
        return Permission.objects.get(
            content_type__app_label=app_label,
            content_type__model=modelo,
            codename=f"{accion}_{modelo}",
        )

    def test_jefatura_carrera_opera_asignacion_docente(self):
        grupo = Group.objects.get(name="JEFE_CARRERA")

        self.assertIn(
            self.permiso("relaciones", "asignaciondocente", "add"),
            grupo.permissions.all(),
        )
        self.assertIn(
            self.permiso("relaciones", "asignaciondocente", "change"),
            grupo.permissions.all(),
        )
        self.assertIn(
            self.permiso("relaciones", "inscripcionmateria", "view"),
            grupo.permissions.all(),
        )

    def test_estadistica_consulta_asignacion_docente_sin_operarla(self):
        grupo = Group.objects.get(name="ENCARGADO_ESTADISTICA")

        self.assertIn(
            self.permiso("relaciones", "asignaciondocente", "view"),
            grupo.permissions.all(),
        )
        self.assertNotIn(
            self.permiso("relaciones", "asignaciondocente", "add"),
            grupo.permissions.all(),
        )
        self.assertNotIn(
            self.permiso("relaciones", "asignaciondocente", "change"),
            grupo.permissions.all(),
        )

    def test_docente_y_discente_reciben_permisos_de_consulta(self):
        docente = Group.objects.get(name="DOCENTE")
        discente = Group.objects.get(name="DISCENTE")

        self.assertIn(
            self.permiso("relaciones", "asignaciondocente", "view"),
            docente.permissions.all(),
        )
        self.assertIn(
            self.permiso("relaciones", "inscripcionmateria", "view"),
            discente.permissions.all(),
        )

    def test_admin_sistema_recibe_permisos_globales(self):
        grupo = Group.objects.get(name="ADMIN_SISTEMA")

        self.assertIn(
            self.permiso("usuarios", "usuario", "change"),
            grupo.permissions.all(),
        )
        self.assertIn(
            self.permiso("auth", "group", "change"),
            grupo.permissions.all(),
        )


class FrontTemporalValidacionRolTests(TestCase):
    def setUp(self):
        self.rol_discente, _ = Group.objects.get_or_create(name="DISCENTE")
        self.rol_docente, _ = Group.objects.get_or_create(name="DOCENTE")
        self.rol_jefatura, _ = Group.objects.get_or_create(name="JEFE_CARRERA")
        self.rol_estadistica, _ = Group.objects.get_or_create(name="ENCARGADO_ESTADISTICA")

        self.carrera = Carrera.objects.create(clave="FRONT_ICI", nombre="ICI")
        self.plan = PlanEstudios.objects.create(
            carrera=self.carrera,
            clave="FRONT_PLAN",
            nombre="Plan front",
        )
        self.antiguedad = Antiguedad.objects.create(
            plan_estudios=self.plan,
            clave="FRONT_ANT",
            nombre="Antiguedad front",
            anio_inicio=2025,
            anio_fin=2029,
        )
        self.periodo = PeriodoEscolar.objects.create(
            clave="FRONT_PER",
            anio_escolar="2025-2026",
            periodo_academico=1,
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2026, 1, 31),
        )
        self.grupo = GrupoAcademico.objects.create(
            clave_grupo="FRONT_G1",
            antiguedad=self.antiguedad,
            periodo=self.periodo,
            semestre_numero=1,
        )
        self.materia = Materia.objects.create(
            clave="FRONT_M1",
            nombre="Materia front 1",
            horas_totales=64,
        )
        self.programa = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=self.materia,
            semestre_numero=1,
        )
        self.materia_dos = Materia.objects.create(
            clave="FRONT_M2",
            nombre="Materia front 2",
            horas_totales=64,
        )
        self.programa_dos = ProgramaAsignatura.objects.create(
            plan_estudios=self.plan,
            materia=self.materia_dos,
            semestre_numero=1,
        )

        self.usuario_discente = self.crear_usuario("discente_front", self.rol_discente)
        self.usuario_otro_discente = self.crear_usuario("discente_otro", self.rol_discente)
        self.usuario_docente = self.crear_usuario("docente_front", self.rol_docente)
        self.usuario_otro_docente = self.crear_usuario("docente_otro", self.rol_docente)
        self.usuario_jefatura = self.crear_usuario("jefatura_front", self.rol_jefatura)
        self.usuario_estadistica = self.crear_usuario("estadistica_front", self.rol_estadistica)

        self.discente = Discente.objects.create(
            usuario=self.usuario_discente,
            matricula="F0001",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )
        self.otro_discente = Discente.objects.create(
            usuario=self.usuario_otro_discente,
            matricula="F0002",
            plan_estudios=self.plan,
            antiguedad=self.antiguedad,
        )
        AdscripcionGrupo.objects.create(discente=self.discente, grupo_academico=self.grupo)
        AdscripcionGrupo.objects.create(discente=self.otro_discente, grupo_academico=self.grupo)
        self.asignacion = AsignacionDocente.objects.create(
            usuario_docente=self.usuario_docente,
            grupo_academico=self.grupo,
            programa_asignatura=self.programa,
        )

    def crear_usuario(self, username, rol):
        usuario = Usuario.objects.create_user(username=username, password="segura123")
        usuario.groups.add(rol)
        return usuario

    def test_usuario_discente_solo_ve_su_carga(self):
        self.client.force_login(self.usuario_discente)

        response = self.client.get("/validacion/discente/carga/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "F0001")
        self.assertNotContains(response, "F0002")
        self.assertContains(response, "Materia front 1")

    def test_usuario_docente_solo_ve_sus_asignaciones(self):
        AsignacionDocente.objects.create(
            usuario_docente=self.usuario_otro_docente,
            grupo_academico=self.grupo,
            programa_asignatura=self.programa_dos,
        )
        self.client.force_login(self.usuario_docente)

        response = self.client.get("/validacion/docente/asignaciones/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Materia front 1")
        self.assertNotContains(response, "Materia front 2")

    def test_jefe_carrera_puede_operar_asignaciones_docentes(self):
        self.client.force_login(self.usuario_jefatura)

        response = self.client.get("/relaciones/asignaciones-docentes/crear/")

        self.assertEqual(response.status_code, 200)

    def test_jefatura_crea_asignacion_y_genera_inscripciones(self):
        self.client.force_login(self.usuario_jefatura)

        response = self.client.post(
            "/relaciones/asignaciones-docentes/crear/",
            data={
                "usuario_docente": self.usuario_otro_docente.pk,
                "grupo_academico": self.grupo.pk,
                "programa_asignatura": self.programa_dos.pk,
                "vigente_desde": "",
                "vigente_hasta": "",
                "activo": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        asignacion = AsignacionDocente.objects.get(programa_asignatura=self.programa_dos)
        self.assertEqual(
            InscripcionMateria.objects.filter(asignacion_docente=asignacion).count(),
            2,
        )

    def test_estadistica_consulta_carga_pero_no_crea_asignaciones(self):
        self.client.force_login(self.usuario_estadistica)

        consulta = self.client.get("/validacion/estadistica/carga/")
        crear = self.client.get("/relaciones/asignaciones-docentes/crear/")

        self.assertEqual(consulta.status_code, 200)
        self.assertContains(consulta, "Carga académica y movimientos")
        self.assertEqual(crear.status_code, 403)

    def test_usuario_sin_permisos_recibe_403(self):
        usuario = Usuario.objects.create_user(username="sin_permiso", password="segura123")
        self.client.force_login(usuario)

        response = self.client.get("/validacion/estadistica/carga/")

        self.assertEqual(response.status_code, 403)

    def test_superusuario_conserva_acceso_total(self):
        usuario = Usuario.objects.create_superuser(username="super_front", password="segura123")
        self.client.force_login(usuario)

        dashboard = self.client.get("/dashboard/")
        crear = self.client.get("/relaciones/asignaciones-docentes/crear/")
        tecnico = self.client.get("/validacion/admin/tecnico/")

        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(crear.status_code, 200)
        self.assertEqual(tecnico.status_code, 200)


class LoginUsuarioEstadoCuentaTests(TestCase):
    MENSAJE_GENERICO = "Usuario o contraseña incorrectos."

    def _crear_usuario(self, username, **kwargs):
        return Usuario.objects.create_user(
            username=username,
            password="segura123",
            **kwargs,
        )

    def _formulario_login(self, username):
        return LoginFormulario(
            request=None,
            data={
                "username": username,
                "password": "segura123",
            },
        )

    def test_usuario_activo_puede_ingresar(self):
        self._crear_usuario(
            "usuario_activo",
            estado_cuenta=Usuario.ESTADO_ACTIVO,
        )

        form = self._formulario_login("usuario_activo")

        self.assertTrue(form.is_valid(), form.errors)

    def test_usuario_inactivo_no_ingresa_y_recibe_mensaje_generico(self):
        self._crear_usuario(
            "usuario_inactivo",
            estado_cuenta=Usuario.ESTADO_INACTIVO,
        )

        form = self._formulario_login("usuario_inactivo")

        self.assertFalse(form.is_valid())
        self.assertIn(self.MENSAJE_GENERICO, form.non_field_errors())
        self.assertNotIn("inactivo", " ".join(form.non_field_errors()).lower())

    def test_usuario_bloqueado_no_ingresa_y_recibe_mensaje_generico(self):
        self._crear_usuario(
            "usuario_bloqueado",
            estado_cuenta=Usuario.ESTADO_BLOQUEADO,
        )

        form = self._formulario_login("usuario_bloqueado")

        self.assertFalse(form.is_valid())
        self.assertIn(self.MENSAJE_GENERICO, form.non_field_errors())
        self.assertNotIn("bloqueado", " ".join(form.non_field_errors()).lower())

    def test_usuario_desactivado_por_django_no_revela_estado(self):
        self._crear_usuario(
            "usuario_desactivado",
            estado_cuenta=Usuario.ESTADO_ACTIVO,
            is_active=False,
        )

        form = self._formulario_login("usuario_desactivado")

        self.assertFalse(form.is_valid())
        self.assertIn(self.MENSAJE_GENERICO, form.non_field_errors())
        self.assertNotIn("inact", " ".join(form.non_field_errors()).lower())


class UsuarioRolUnicoAdminTests(TestCase):
    def setUp(self):
        self.rol_docente, _ = Group.objects.get_or_create(name="DOCENTE")
        self.rol_discente, _ = Group.objects.get_or_create(name="DISCENTE")

    def test_admin_usa_formularios_con_rol_unico(self):
        usuario_admin = admin.site._registry[Usuario]

        self.assertIs(usuario_admin.form, UsuarioAdminForm)
        self.assertIs(usuario_admin.add_form, UsuarioAdminCreationForm)
        self.assertIn("permisos_heredados_por_rol", usuario_admin.readonly_fields)

    def test_usuario_con_grado_muestra_nombre_institucional(self):
        grado = GradoEmpleo.objects.create(
            clave="TTE_COR_ICI",
            abreviatura="Tte. Cor. I.C.I.",
            nombre="Teniente Coronel Ingeniero en Computación e Informática",
            tipo=GradoEmpleo.TIPO_MILITAR_ACTIVO,
        )
        usuario = Usuario.objects.create_user(
            username="usuario_grado",
            password="segura123",
            nombre_completo="Juan Pérez",
            grado_empleo=grado,
        )

        self.assertEqual(usuario.nombre_institucional, "Tte. Cor. I.C.I. Juan Pérez")

    def test_usuario_sin_grado_muestra_solo_nombre_visible(self):
        usuario = Usuario.objects.create_user(
            username="usuario_sin_grado",
            password="segura123",
            nombre_completo="Juan Pérez",
        )

        self.assertEqual(usuario.nombre_institucional, "Juan Pérez")

    def test_admin_alta_usuario_no_incluye_usable_password(self):
        usuario_admin = admin.site._registry[Usuario]
        campos = [
            field
            for _name, opciones in usuario_admin.add_fieldsets
            for field in opciones["fields"]
        ]

        self.assertNotIn("usable_password", campos)
        self.assertIn("password1", campos)
        self.assertIn("password2", campos)

    def test_admin_popup_alta_usuario_renderiza_desde_discente(self):
        admin_user = Usuario.objects.create_superuser(
            username="admin_popup_usuario",
            password="segura123XYZ",
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:usuarios_usuario_add"),
            {"_to_field": "id", "_popup": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rol")

    def test_formulario_de_alta_exige_rol(self):
        form = UsuarioAdminCreationForm(
            data={
                "username": "usuario_sin_rol",
                "password1": "segura123XYZ",
                "password2": "segura123XYZ",
                "estado_cuenta": Usuario.ESTADO_ACTIVO,
                "nombre_completo": "Usuario sin rol",
                "correo": "sinrol@example.com",
                "telefono": "1234567890",
                "groups": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["groups"],
            ["Debe seleccionar un rol para el usuario."],
        )

    def test_formulario_de_alta_solo_permite_un_rol(self):
        form = UsuarioAdminCreationForm()

        self.assertEqual(form.fields["groups"].label, "Rol")
        self.assertFalse(form.fields["groups"].widget.allow_multiple_selected)
        self.assertIn("grado_empleo", form.fields)

    def test_formulario_de_edicion_aclara_permisos_directos(self):
        form = UsuarioAdminForm()

        self.assertEqual(form.fields["user_permissions"].label, "Permisos directos adicionales")
        self.assertIn("permisos del rol/grupo", form.fields["user_permissions"].help_text)

    def test_formulario_de_alta_guarda_unico_rol(self):
        form = UsuarioAdminCreationForm(
            data={
                "username": "usuario_con_rol",
                "password1": "segura123XYZ",
                "password2": "segura123XYZ",
                "estado_cuenta": Usuario.ESTADO_ACTIVO,
                "nombre_completo": "Usuario con rol",
                "correo": "conrol@example.com",
                "telefono": "1234567890",
                "groups": self.rol_docente.pk,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()
        form.save_m2m()

        self.assertEqual(list(usuario.groups.all()), [self.rol_docente])

    def test_formulario_de_edicion_muestra_un_unico_rol_actual(self):
        usuario = Usuario.objects.create_user(username="usuario_edicion", password="segura123")
        usuario.groups.add(self.rol_discente)

        form = UsuarioAdminForm(instance=usuario)

        self.assertEqual(form.initial["groups"], self.rol_discente.pk)

    def test_admin_muestra_permisos_heredados_por_rol(self):
        permiso = Permission.objects.get(
            content_type__app_label="usuarios",
            codename="view_usuario",
        )
        self.rol_docente.permissions.add(permiso)
        usuario = Usuario.objects.create_user(username="usuario_con_permiso", password="segura123")
        usuario.groups.add(self.rol_docente)
        usuario_admin = admin.site._registry[Usuario]

        html = str(usuario_admin.permisos_heredados_por_rol(usuario))

        self.assertIn("DOCENTE", html)
        self.assertIn("usuarios.view_usuario", html)
