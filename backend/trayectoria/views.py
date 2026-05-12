from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView

from relaciones.models import Discente

from .forms import EventoSituacionAcademicaForm, ExtraordinarioForm
from .permisos import (
    filtrar_discentes_por_ambito,
    puede_consultar_kardex,
    puede_consultar_kardex_discente,
    puede_consultar_historial_discente,
    puede_consultar_historiales,
    puede_operar_trayectoria,
)
from .services import construir_historial_discente
from .services import construir_kardex_discente


def mensajes_validation_error(error):
    if hasattr(error, "messages"):
        return error.messages
    return [str(error)]


class MiHistorialAcademicoView(LoginRequiredMixin, TemplateView):
    template_name = "trayectoria/historial_detalle.html"
    login_url = reverse_lazy("usuarios:login")

    def get_discente(self):
        return get_object_or_404(
            Discente.objects.select_related("usuario", "plan_estudios", "plan_estudios__carrera"),
            usuario=self.request.user,
            activo=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        discente = self.get_discente()
        context.update(
            {
                "historial": construir_historial_discente(discente),
                "vista_propia": True,
            }
        )
        return context


class HistorialBusquedaView(LoginRequiredMixin, TemplateView):
    template_name = "trayectoria/historial_busqueda.html"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_consultar_historiales(request.user):
            raise PermissionDenied("No tienes permiso para consultar historiales académicos.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Discente.objects.select_related(
            "usuario",
            "plan_estudios",
            "plan_estudios__carrera",
            "antiguedad",
        ).order_by("matricula")
        queryset = filtrar_discentes_por_ambito(self.request.user, queryset)
        query = (self.request.GET.get("q") or "").strip()
        if query:
            queryset = queryset.filter(
                usuario__nombre_completo__icontains=query
            ) | queryset.filter(matricula__icontains=query)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "discentes": self.get_queryset(),
                "q": self.request.GET.get("q", ""),
                "puede_operar_trayectoria": puede_operar_trayectoria(self.request.user),
            }
        )
        return context


class KardexBusquedaView(LoginRequiredMixin, TemplateView):
    template_name = "trayectoria/kardex_busqueda.html"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_consultar_kardex(request.user):
            raise PermissionDenied("No tienes permiso para consultar kÃ¡rdex oficiales.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Discente.objects.select_related(
            "usuario",
            "usuario__grado_empleo",
            "plan_estudios",
            "plan_estudios__carrera",
            "antiguedad",
        ).order_by("matricula")
        queryset = filtrar_discentes_por_ambito(self.request.user, queryset)
        query = (self.request.GET.get("q") or "").strip()
        if query:
            queryset = queryset.filter(
                usuario__nombre_completo__icontains=query
            ) | queryset.filter(matricula__icontains=query)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "discentes": self.get_queryset(),
                "q": self.request.GET.get("q", ""),
            }
        )
        return context


class HistorialDetalleView(LoginRequiredMixin, DetailView):
    template_name = "trayectoria/historial_detalle.html"
    model = Discente
    context_object_name = "discente"
    login_url = reverse_lazy("usuarios:login")

    def get_queryset(self):
        return Discente.objects.select_related(
            "usuario",
            "plan_estudios",
            "plan_estudios__carrera",
            "antiguedad",
        )

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not puede_consultar_historial_discente(request.user, self.object):
            raise PermissionDenied("No tienes permiso para consultar este historial académico.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["historial"] = construir_historial_discente(self.object)
        context["puede_operar_trayectoria"] = puede_operar_trayectoria(self.request.user)
        return context


class KardexDetalleView(LoginRequiredMixin, DetailView):
    template_name = "trayectoria/kardex_detalle.html"
    model = Discente
    context_object_name = "discente"
    login_url = reverse_lazy("usuarios:login")

    def get_queryset(self):
        return Discente.objects.select_related(
            "usuario",
            "usuario__grado_empleo",
            "plan_estudios",
            "plan_estudios__carrera",
            "antiguedad",
        )

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not puede_consultar_kardex_discente(request.user, self.object):
            raise PermissionDenied("No tienes permiso para consultar este kÃ¡rdex oficial.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kardex"] = construir_kardex_discente(self.object)
        return context


class RegistrarExtraordinarioView(LoginRequiredMixin, TemplateView):
    template_name = "trayectoria/extraordinario_form.html"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_operar_trayectoria(request.user):
            raise PermissionDenied("No tienes permiso para registrar extraordinarios.")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        return ExtraordinarioForm(data=self.request.POST or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", self.get_form())
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                extraordinario = form.save(request.user)
            except ValidationError as error:
                for mensaje in mensajes_validation_error(error):
                    messages.error(request, mensaje)
            else:
                messages.success(request, "Extraordinario registrado correctamente.")
                return redirect(
                    "trayectoria:historial-detalle",
                    pk=extraordinario.inscripcion_materia.discente_id,
                )
        return self.render_to_response(self.get_context_data(form=form))


class RegistrarSituacionAcademicaView(LoginRequiredMixin, TemplateView):
    template_name = "trayectoria/situacion_form.html"
    login_url = reverse_lazy("usuarios:login")

    def dispatch(self, request, *args, **kwargs):
        if not puede_operar_trayectoria(request.user):
            raise PermissionDenied("No tienes permiso para registrar situaciones académicas.")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        return EventoSituacionAcademicaForm(data=self.request.POST or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", self.get_form())
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                evento = form.save(request.user)
            except ValidationError as error:
                for mensaje in mensajes_validation_error(error):
                    messages.error(request, mensaje)
            else:
                messages.success(request, "Situación académica registrada correctamente.")
                return redirect("trayectoria:historial-detalle", pk=evento.discente_id)
        return self.render_to_response(self.get_context_data(form=form))
