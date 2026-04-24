from django.urls import path

from .views import (
    AdminTecnicoView,
    DashboardView,
    DiscenteCargaView,
    DocenteAsignacionDetalleView,
    DocenteAsignacionesView,
    EstadisticaCargaView,
    JefaturaAsignacionesView,
    LoginUsuarioView,
    LogoutUsuarioView,
    SincronizarAsignacionDocenteView,
)

app_name = "usuarios"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("login/", LoginUsuarioView.as_view(), name="login"),
    path("logout/", LogoutUsuarioView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("validacion/discente/carga/", DiscenteCargaView.as_view(), name="discente-carga"),
    path("validacion/docente/asignaciones/", DocenteAsignacionesView.as_view(), name="docente-asignaciones"),
    path(
        "validacion/docente/asignaciones/<int:pk>/",
        DocenteAsignacionDetalleView.as_view(),
        name="docente-asignacion-detalle",
    ),
    path(
        "validacion/jefatura/asignaciones-docentes/",
        JefaturaAsignacionesView.as_view(),
        name="jefatura-asignaciones",
    ),
    path(
        "validacion/jefatura/asignaciones-docentes/<int:pk>/sincronizar/",
        SincronizarAsignacionDocenteView.as_view(),
        name="jefatura-asignacion-sincronizar",
    ),
    path("validacion/estadistica/carga/", EstadisticaCargaView.as_view(), name="estadistica-carga"),
    path("validacion/admin/tecnico/", AdminTecnicoView.as_view(), name="admin-tecnico"),
]
