from datetime import date, timedelta

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.test import TestCase
from django.utils import timezone

from catalogos.models import Carrera
from catalogos.models import Antiguedad, GrupoAcademico, Materia, PeriodoEscolar, PlanEstudios, ProgramaAsignatura
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria

from .admin import UsuarioAdmin
from .forms import LoginFormulario, UsuarioAdminCreationForm, UsuarioAdminForm
from .models import AsignacionCargo, Usuario


class VigenciaAsignacionCargoTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_vigencia",
            password="segura123",
        )
        self.carrera_icis = Carrera.objects.create(
            clave="ICIS",
            nombre="Ingenieros en Comunicaciones e Informática",
        )
        self.carrera_ices = Carrera.objects.create(
            clave="ICES",
            nombre="Ingenieros Constructores",
        )

    def test_creacion_autocompleta_vigente_desde_si_se_omite(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            carrera=self.carrera_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        self.assertEqual(asignacion.vigente_desde, timezone.localdate())
        self.assertIsNone(asignacion.vigente_hasta)

    def test_edicion_respeta_vigente_desde_existente(self):
        fecha_existente = timezone.localdate() - timedelta(days=15)
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_DOCENTE,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
            vigente_desde=fecha_existente,
        )

        asignacion.activo = False
        asignacion.save()
        asignacion.refresh_from_db()

        self.assertEqual(asignacion.vigente_desde, fecha_existente)

    def test_edicion_de_registro_legado_sin_vigente_desde_lo_autocompleta(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            carrera=self.carrera_ices,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
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
                "cargo_codigo": AsignacionCargo.CARGO_JEFE_ACADEMICO,
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
            carrera=self.carrera_ices,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
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
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )
        asignacion_accidental = AsignacionCargo.objects.create(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_ACADEMICO,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
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
        self.assertNotIn("JEFE_CARRERA_ICIS", choices)
        self.assertNotIn("JEFE_CARRERA_ICES", choices)
        self.assertNotIn("COORDINADOR", choices)

    def test_jefatura_de_carrera_exige_carrera(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("carrera", exc.exception.message_dict)

    def test_jefatura_pedagogica_exige_carrera(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            tipo_designacion=AsignacionCargo.DESIGNACION_ACCIDENTAL,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("carrera", exc.exception.message_dict)

    def test_cargo_global_no_permite_carrera(self):
        asignacion = AsignacionCargo(
            usuario=self.usuario,
            carrera=self.carrera_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_ACADEMICO,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        with self.assertRaises(ValidationError) as exc:
            asignacion.full_clean()

        self.assertIn("carrera", exc.exception.message_dict)

    def test_descripcion_de_cargo_incluye_carrera_cuando_aplica(self):
        asignacion = AsignacionCargo.objects.create(
            usuario=self.usuario,
            carrera=self.carrera_icis,
            cargo_codigo=AsignacionCargo.CARGO_JEFE_CARRERA,
            tipo_designacion=AsignacionCargo.DESIGNACION_TITULAR,
        )

        self.assertEqual(
            asignacion.cargo_descripcion(),
            f"Jefe de carrera de {self.carrera_icis}",
        )

    def test_tipo_designacion_solo_permite_titular_y_accidental(self):
        choices = [codigo for codigo, _ in AsignacionCargo.TIPO_DESIGNACION_CHOICES]

        self.assertEqual(
            choices,
            [
                AsignacionCargo.DESIGNACION_TITULAR,
                AsignacionCargo.DESIGNACION_ACCIDENTAL,
            ],
        )


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
