from django.urls import path

from .views import DashboardView, LoginUsuarioView, LogoutUsuarioView

app_name = "usuarios"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("login/", LoginUsuarioView.as_view(), name="login"),
    path("logout/", LogoutUsuarioView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
