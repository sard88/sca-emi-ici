from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from catalogos.models import PeriodoEscolar

from .forms import AperturaPeriodoForm, CierrePeriodoForm
from .models import ProcesoAperturaPeriodo, ProcesoCierrePeriodo
from .permisos import (
    puede_consultar_cierre_periodo,
    puede_consultar_pendientes_docente,
    puede_operar_cierre_apertura,
)
from .services import (
    ServicioAperturaPeriodo,
    ServicioCierrePeriodo,
    ServicioDiagnosticoCierrePeriodo,
    listar_pendientes_asignacion_docente,
)


def mensajes_validation_error(error):
    if hasattr(error, "messages"):
        return error.messages
    return [str(error)]


class PeriodosCierreListView(LoginRequiredMixin, ListView):
    template_name = "actas/periodos_cierre_list.html"
    model = PeriodoEscolar
    context_object_name = "periodos"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_consultar_cierre_periodo(request.user):
            raise PermissionDenied("No tienes permiso para consultar cierres de periodo.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return PeriodoEscolar.objects.order_by("-anio_escolar", "-periodo_academico", "clave")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["puede_operar"] = puede_operar_cierre_apertura(self.request.user)
        return context


class DiagnosticoCierrePeriodoView(LoginRequiredMixin, TemplateView):
    template_name = "actas/diagnostico_cierre.html"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_consultar_cierre_periodo(request.user):
            raise PermissionDenied("No tienes permiso para consultar diagnósticos de cierre.")
        return super().dispatch(request, *args, **kwargs)

    def get_periodo(self):
        return get_object_or_404(PeriodoEscolar, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.get_periodo()
        context.update(
            {
                "periodo": periodo,
                "diagnostico": ServicioDiagnosticoCierrePeriodo(periodo).diagnosticar(),
                "form": CierrePeriodoForm(),
                "puede_operar": puede_operar_cierre_apertura(self.request.user),
            }
        )
        return context


class EjecutarCierrePeriodoView(LoginRequiredMixin, FormView):
    form_class = CierrePeriodoForm
    login_url = reverse_lazy("usuarios:login")
    http_method_names = ["post"]

    def dispatch(self, request, *args, **kwargs):
        if not puede_operar_cierre_apertura(request.user):
            raise PermissionDenied("No tienes permiso para cerrar periodos académicos.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        periodo = get_object_or_404(PeriodoEscolar, pk=self.kwargs["pk"])
        try:
            proceso = ServicioCierrePeriodo(
                periodo,
                self.request.user,
                observaciones=form.cleaned_data.get("observaciones", ""),
            ).cerrar()
        except ValidationError as error:
            for mensaje in mensajes_validation_error(error):
                messages.error(self.request, mensaje)
            return redirect("actas:diagnostico-cierre", pk=periodo.pk)

        messages.success(self.request, "Periodo académico cerrado correctamente.")
        return redirect("actas:proceso-cierre-detalle", pk=proceso.pk)


class ProcesoCierreDetalleView(LoginRequiredMixin, DetailView):
    template_name = "actas/proceso_cierre_detalle.html"
    model = ProcesoCierrePeriodo
    context_object_name = "proceso"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_consultar_cierre_periodo(request.user):
            raise PermissionDenied("No tienes permiso para consultar procesos de cierre.")
        return super().dispatch(request, *args, **kwargs)


class AperturaPeriodoView(LoginRequiredMixin, FormView):
    template_name = "actas/apertura_periodo.html"
    form_class = AperturaPeriodoForm
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_operar_cierre_apertura(request.user):
            raise PermissionDenied("No tienes permiso para abrir periodos académicos.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            proceso = ServicioAperturaPeriodo(
                form.cleaned_data["periodo_origen"],
                form.cleaned_data["periodo_destino"],
                self.request.user,
                observaciones=form.cleaned_data.get("observaciones", ""),
            ).abrir()
        except ValidationError as error:
            for mensaje in mensajes_validation_error(error):
                messages.error(self.request, mensaje)
            return self.form_invalid(form)

        messages.success(self.request, "Apertura de periodo ejecutada correctamente.")
        return redirect("actas:proceso-apertura-detalle", pk=proceso.pk)


class ProcesoAperturaDetalleView(LoginRequiredMixin, DetailView):
    template_name = "actas/proceso_apertura_detalle.html"
    model = ProcesoAperturaPeriodo
    context_object_name = "proceso"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_operar_cierre_apertura(request.user):
            raise PermissionDenied("No tienes permiso para consultar procesos de apertura.")
        return super().dispatch(request, *args, **kwargs)


class PendientesAsignacionDocenteView(LoginRequiredMixin, TemplateView):
    template_name = "actas/pendientes_asignacion_docente.html"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_consultar_pendientes_docente(request.user):
            raise PermissionDenied("No tienes permiso para consultar pendientes de asignación docente.")
        return super().dispatch(request, *args, **kwargs)

    def get_periodo(self):
        periodo_id = self.request.GET.get("periodo")
        if periodo_id:
            return get_object_or_404(PeriodoEscolar, pk=periodo_id)
        return PeriodoEscolar.objects.order_by("-anio_escolar", "-periodo_academico").first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.get_periodo()
        context.update(
            {
                "periodos": PeriodoEscolar.objects.order_by("-anio_escolar", "-periodo_academico"),
                "periodo": periodo,
                "pendientes": listar_pendientes_asignacion_docente(periodo, self.request.user)
                if periodo
                else [],
            }
        )
        return context
