from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView

from usuarios.models import AsignacionCargo

from .forms import AsignacionDocenteForm, MovimientoAcademicoForm
from .models import AsignacionDocente, InscripcionMateria, MovimientoAcademico


ROL_ADMIN = "ADMIN_SISTEMA"
ROL_ESTADISTICA = "ESTADISTICA"
CARGOS_AUTORIZADOS = ("ADMIN", "ADMIN_SISTEMA", "ESTADISTICA")


def usuario_autorizado_relaciones(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser or user.is_staff:
        return True

    if user.groups.filter(name__in=(ROL_ADMIN, ROL_ESTADISTICA)).exists():
        return True

    hoy = timezone.localdate()
    cargos_filter = Q()
    for cargo in CARGOS_AUTORIZADOS:
        cargos_filter |= Q(cargo_codigo__iexact=cargo)

    return AsignacionCargo.objects.filter(
        Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
        Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
        cargos_filter,
        usuario=user,
        activo=True,
    ).exists()


class RelacionesAutorizadasMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("usuarios:login")

    def test_func(self):
        return usuario_autorizado_relaciones(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class AsignacionDocenteListView(RelacionesAutorizadasMixin, ListView):
    model = AsignacionDocente
    template_name = "relaciones/asignacion_docente_list.html"
    context_object_name = "asignaciones"

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
        )


class AsignacionDocenteCreateView(RelacionesAutorizadasMixin, CreateView):
    model = AsignacionDocente
    form_class = AsignacionDocenteForm
    template_name = "relaciones/asignacion_docente_form.html"
    success_url = reverse_lazy("relaciones:asignacion-docente-list")


class InscripcionMateriaListView(RelacionesAutorizadasMixin, ListView):
    model = InscripcionMateria
    template_name = "relaciones/inscripcion_materia_list.html"
    context_object_name = "inscripciones"

    def get_queryset(self):
        return (
            InscripcionMateria.objects.select_related(
                "discente",
                "discente__usuario",
                "asignacion_docente",
                "asignacion_docente__grupo_academico",
                "asignacion_docente__programa_asignatura",
                "asignacion_docente__programa_asignatura__materia",
            )
            .all()
        )


class MovimientoAcademicoListView(RelacionesAutorizadasMixin, ListView):
    model = MovimientoAcademico
    template_name = "relaciones/movimiento_academico_list.html"
    context_object_name = "movimientos"

    def get_queryset(self):
        return (
            MovimientoAcademico.objects.select_related(
                "discente",
                "discente__usuario",
                "periodo",
                "grupo_origen",
                "grupo_destino",
            )
            .all()
        )


class MovimientoAcademicoCreateView(RelacionesAutorizadasMixin, CreateView):
    model = MovimientoAcademico
    form_class = MovimientoAcademicoForm
    template_name = "relaciones/movimiento_academico_form.html"
    success_url = reverse_lazy("relaciones:movimiento-academico-list")
