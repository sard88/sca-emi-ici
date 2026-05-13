from django.contrib import admin
from django.urls import include, path

from core.views import health_check

admin.site.site_url = "/dashboard/"

urlpatterns = [
    path("api/auth/", include("usuarios.api_urls")),
    path("", include("usuarios.urls")),
    path("actas/", include("actas.urls")),
    path("relaciones/", include("relaciones.urls")),
    path("evaluacion/", include("evaluacion.urls")),
    path("trayectoria/", include("trayectoria.urls")),
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
]
