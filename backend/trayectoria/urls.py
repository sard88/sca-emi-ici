from django.urls import path

from .views import (
    HistorialBusquedaView,
    HistorialDetalleView,
    KardexBusquedaView,
    KardexDetalleView,
    MiHistorialAcademicoView,
    RegistrarExtraordinarioView,
    RegistrarSituacionAcademicaView,
)


app_name = "trayectoria"

urlpatterns = [
    path("mi-historial/", MiHistorialAcademicoView.as_view(), name="mi-historial"),
    path("historial/", HistorialBusquedaView.as_view(), name="historial-busqueda"),
    path("historial/<int:pk>/", HistorialDetalleView.as_view(), name="historial-detalle"),
    path("kardex/", KardexBusquedaView.as_view(), name="kardex-busqueda"),
    path("kardex/<int:pk>/", KardexDetalleView.as_view(), name="kardex-detalle"),
    path(
        "extraordinarios/registrar/",
        RegistrarExtraordinarioView.as_view(),
        name="extraordinario-registrar",
    ),
    path(
        "situaciones/registrar/",
        RegistrarSituacionAcademicaView.as_view(),
        name="situacion-registrar",
    ),
]
