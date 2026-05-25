from django.urls import path

from . import api_views


app_name = "usuarios_api"

urlpatterns = [
    path("csrf/", api_views.csrf_view, name="csrf"),
    path("login/", api_views.login_view, name="login"),
    path("logout/", api_views.logout_view, name="logout"),
    path("me/", api_views.me_view, name="me"),
]
