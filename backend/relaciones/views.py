from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import AsignacionDocenteForm, MovimientoAcademicoForm
from .models import AsignacionDocente, InscripcionMateria, MovimientoAcademico
from .permisos import (
    puede_consultar_asignacion_docente,
    puede_consultar_relaciones,
    puede_operar_asignacion_docente,
)


class RelacionesAutorizadasMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("usuarios:login")

    def test_func(self):
        return puede_consultar_relaciones(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class AsignacionDocenteConsultaMixin(RelacionesAutorizadasMixin):
    def test_func(self):
        return puede_consultar_asignacion_docente(self.request.user)


class AsignacionDocenteOperacionMixin(RelacionesAutorizadasMixin):
    def test_func(self):
        return puede_operar_asignacion_docente(self.request.user)


class AsignacionDocenteListView(AsignacionDocenteConsultaMixin, ListView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["puede_operar_asignacion_docente"] = puede_operar_asignacion_docente(
            self.request.user
        )
        return context


class AsignacionDocenteCreateView(AsignacionDocenteOperacionMixin, CreateView):
    model = AsignacionDocente
    form_class = AsignacionDocenteForm
    template_name = "relaciones/asignacion_docente_form.html"
    success_url = reverse_lazy("relaciones:asignacion-docente-list")


class AsignacionDocenteUpdateView(AsignacionDocenteOperacionMixin, UpdateView):
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
