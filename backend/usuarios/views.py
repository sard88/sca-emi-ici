from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from .forms import LoginFormulario


class LoginUsuarioView(LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginFormulario
    redirect_authenticated_user = True


class LogoutUsuarioView(LogoutView):
    next_page = reverse_lazy("usuarios:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/dashboard.html"
    login_url = reverse_lazy("usuarios:login")
