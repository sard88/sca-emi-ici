from django.contrib import admin
from django.urls import include, path

from core.views import health_check

admin.site.site_url = "/dashboard/"

urlpatterns = [
    path("", include("usuarios.urls")),
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
]
