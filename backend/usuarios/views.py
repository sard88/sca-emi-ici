from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from catalogos.models import GrupoAcademico
from relaciones.models import (
    AdscripcionGrupo,
    AsignacionDocente,
    Discente,
    InscripcionMateria,
    MovimientoAcademico,
)
from relaciones.permisos import (
    puede_consultar_asignacion_docente,
    puede_consultar_relaciones,
    puede_operar_asignacion_docente,
    usuario_es_admin_soporte,
    usuario_es_discente,
    usuario_es_docente,
    usuario_es_estadistica,
    usuario_es_jefatura_carrera,
    usuario_es_jefatura_planeacion,
)
from relaciones.services import sincronizar_carga_academica
from trayectoria.permisos import (
    puede_consultar_historiales,
    puede_consultar_kardex,
    puede_operar_trayectoria,
)
from actas.permisos import (
    puede_consultar_cierre_periodo,
    puede_consultar_pendientes_docente,
    puede_operar_cierre_apertura,
)

from .forms import LoginFormulario
from .models import AsignacionCargo


class LoginUsuarioView(LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginFormulario
    redirect_authenticated_user = True


class LogoutUsuarioView(LogoutView):
    next_page = reverse_lazy("usuarios:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/dashboard.html"
    login_url = reverse_lazy("usuarios:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "roles": user.groups.order_by("name"),
                "cargos_activos": cargos_activos_usuario(user),
                "accesos": accesos_permitidos(user),
            }
        )
        return context


def cargos_activos_usuario(user):
    hoy = timezone.localdate()
    return (
        AsignacionCargo.objects.filter(
            Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
            Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
            usuario=user,
            activo=True,
        )
        .select_related("carrera")
        .order_by("cargo_codigo")
    )


def accesos_permitidos(user):
    accesos = []

    if usuario_es_discente(user) or usuario_es_admin_soporte(user):
        accesos.append(("Mis actas publicadas", "evaluacion:discente-actas"))
        accesos.append(("Mi historial académico", "trayectoria:mi-historial"))
        accesos.append(("Mi carga académica", "usuarios:discente-carga"))
    if usuario_es_docente(user) or usuario_es_admin_soporte(user):
        accesos.append(("Mis asignaciones", "usuarios:docente-asignaciones"))
        accesos.append(("Actas docentes", "evaluacion:docente-actas"))
    if puede_consultar_asignacion_docente(user):
        accesos.append(("Asignaciones docentes", "usuarios:jefatura-asignaciones"))
    if usuario_es_jefatura_carrera(user) or usuario_es_admin_soporte(user):
        accesos.append(("Actas por validar", "evaluacion:jefatura-carrera-actas"))
        accesos.append(("Consulta de actas de mi ámbito", "evaluacion:jefatura-carrera-consulta-actas"))
    if usuario_es_jefatura_planeacion(user) or usuario_es_admin_soporte(user):
        accesos.append((
            "Consulta de actas de Planeación y Evaluación",
            "evaluacion:jefatura-planeacion-consulta-actas",
        ))
    if user.groups.filter(name__in=("JEFE_ACADEMICO", "JEFATURA_ACADEMICA")).exists() or usuario_es_admin_soporte(user):
        accesos.append(("Actas por formalizar", "evaluacion:jefatura-academica-actas"))
    if usuario_es_estadistica(user) or usuario_es_admin_soporte(user):
        accesos.append(("Consulta de actas de calificaciones", "evaluacion:estadistica-actas"))
    if puede_consultar_historiales(user):
        accesos.append(("Historial académico", "trayectoria:historial-busqueda"))
    if puede_consultar_kardex(user):
        accesos.append(("Kárdex oficial", "trayectoria:kardex-busqueda"))
    if puede_operar_trayectoria(user):
        accesos.append(("Registrar extraordinario", "trayectoria:extraordinario-registrar"))
        accesos.append(("Registrar situación académica", "trayectoria:situacion-registrar"))
    if puede_consultar_cierre_periodo(user):
        accesos.append(("Cierre de periodo académico", "actas:periodos-cierre"))
    if puede_operar_cierre_apertura(user):
        accesos.append(("Apertura de periodo académico", "actas:apertura-periodo"))
    if puede_consultar_pendientes_docente(user):
        accesos.append(("Pendientes de asignación docente", "actas:pendientes-asignacion-docente"))
    if puede_consultar_relaciones(user):
        accesos.append(("Carga académica y movimientos", "usuarios:estadistica-carga"))
    if usuario_es_admin_soporte(user):
        accesos.append(("Administración técnica", "usuarios:admin-tecnico"))

    return accesos


class FrontValidacionAutorizadoMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("usuarios:login")

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("No tienes permiso para acceder a esta vista.")
        return super().handle_no_permission()


class DiscenteCargaView(FrontValidacionAutorizadoMixin, TemplateView):
    template_name = "usuarios/validacion/discente_carga.html"

    def test_func(self):
        return usuario_es_discente(self.request.user) or usuario_es_admin_soporte(self.request.user)

    def get_discente(self):
        return (
            Discente.objects.filter(usuario=self.request.user, activo=True)
            .select_related("usuario", "plan_estudios", "antiguedad")
            .first()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        discente = self.get_discente()
        adscripcion = None
        inscripciones = InscripcionMateria.objects.none()

        if discente:
            adscripcion = (
                AdscripcionGrupo.objects.filter(discente=discente, activo=True)
                .select_related("grupo_academico", "grupo_academico__periodo")
                .order_by("-vigente_desde")
                .first()
            )
            inscripciones = (
                InscripcionMateria.objects.filter(discente=discente)
                .select_related(
                    "asignacion_docente",
                    "asignacion_docente__usuario_docente",
                    "asignacion_docente__grupo_academico",
                    "asignacion_docente__grupo_academico__periodo",
                    "asignacion_docente__programa_asignatura",
                    "asignacion_docente__programa_asignatura__materia",
                )
                .order_by(
                    "asignacion_docente__grupo_academico__periodo__anio_escolar",
                    "asignacion_docente__programa_asignatura__materia__clave",
                )
            )

        context.update(
            {
                "discente": discente,
                "adscripcion": adscripcion,
                "inscripciones": inscripciones,
            }
        )
        return context


class DocenteAsignacionesView(FrontValidacionAutorizadoMixin, ListView):
    model = AsignacionDocente
    template_name = "usuarios/validacion/docente_asignaciones.html"
    context_object_name = "asignaciones"

    def test_func(self):
        return usuario_es_docente(self.request.user) or usuario_es_admin_soporte(self.request.user)

    def get_queryset(self):
        queryset = AsignacionDocente.objects.filter(activo=True).select_related(
            "grupo_academico",
            "grupo_academico__periodo",
            "programa_asignatura",
            "programa_asignatura__materia",
            "usuario_docente",
        )
        if usuario_es_admin_soporte(self.request.user):
            return queryset.order_by("grupo_academico__clave_grupo")
        return queryset.filter(usuario_docente=self.request.user).order_by("grupo_academico__clave_grupo")


class DocenteAsignacionDetalleView(FrontValidacionAutorizadoMixin, DetailView):
    model = AsignacionDocente
    template_name = "usuarios/validacion/docente_asignacion_detalle.html"
    context_object_name = "asignacion"

    def test_func(self):
        asignacion = self.get_object()
        return usuario_es_admin_soporte(self.request.user) or (
            usuario_es_docente(self.request.user)
            and asignacion.usuario_docente_id == self.request.user.id
        )

    def get_queryset(self):
        return AsignacionDocente.objects.select_related(
            "usuario_docente",
            "grupo_academico",
            "grupo_academico__periodo",
            "programa_asignatura",
            "programa_asignatura__materia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inscripciones"] = (
            self.object.inscripciones_materia.select_related("discente", "discente__usuario")
            .order_by("discente__matricula")
        )
        return context


class JefaturaAsignacionesView(FrontValidacionAutorizadoMixin, ListView):
    model = AsignacionDocente
    template_name = "usuarios/validacion/jefatura_asignaciones.html"
    context_object_name = "asignaciones"

    def test_func(self):
        return puede_consultar_asignacion_docente(self.request.user)

    def get_queryset(self):
        return (
            AsignacionDocente.objects.select_related(
                "usuario_docente",
                "grupo_academico",
                "grupo_academico__periodo",
                "programa_asignatura",
                "programa_asignatura__materia",
            )
            .all()
            .order_by("grupo_academico__periodo__anio_escolar", "grupo_academico__clave_grupo")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["puede_operar_asignacion_docente"] = puede_operar_asignacion_docente(
            self.request.user
        )
        return context


class SincronizarAsignacionDocenteView(FrontValidacionAutorizadoMixin, View):
    def test_func(self):
        return puede_operar_asignacion_docente(self.request.user)

    def post(self, request, pk):
        asignacion = get_object_or_404(AsignacionDocente, pk=pk)
        creadas = sincronizar_carga_academica(asignacion)
        messages.success(
            request,
            f"Sincronización completada. Inscripciones a asignatura creadas: {creadas}.",
        )
        return redirect("usuarios:jefatura-asignaciones")


class EstadisticaCargaView(FrontValidacionAutorizadoMixin, TemplateView):
    template_name = "usuarios/validacion/estadistica_carga.html"

    def test_func(self):
        return puede_consultar_relaciones(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "grupos": GrupoAcademico.objects.select_related(
                    "periodo", "antiguedad", "antiguedad__plan_estudios"
                ).order_by("periodo__anio_escolar", "clave_grupo"),
                "discentes": Discente.objects.select_related(
                    "usuario", "plan_estudios", "antiguedad"
                ).order_by("matricula"),
                "inscripciones": InscripcionMateria.objects.select_related(
                    "discente",
                    "discente__usuario",
                    "asignacion_docente",
                    "asignacion_docente__usuario_docente",
                    "asignacion_docente__grupo_academico",
                    "asignacion_docente__programa_asignatura",
                    "asignacion_docente__programa_asignatura__materia",
                ).order_by("discente__matricula"),
                "movimientos": MovimientoAcademico.objects.select_related(
                    "discente",
                    "discente__usuario",
                    "periodo",
                    "grupo_origen",
                    "grupo_destino",
                ).order_by("-fecha_movimiento"),
                "puede_operar_asignacion_docente": puede_operar_asignacion_docente(
                    self.request.user
                ),
            }
        )
        return context


class AdminTecnicoView(FrontValidacionAutorizadoMixin, TemplateView):
    template_name = "usuarios/validacion/admin_tecnico.html"

    def test_func(self):
        return usuario_es_admin_soporte(self.request.user)
