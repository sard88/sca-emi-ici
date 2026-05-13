from django.urls import path

from .views import (
    AperturaPeriodoView,
    DiagnosticoCierrePeriodoView,
    EjecutarCierrePeriodoView,
    PendientesAsignacionDocenteView,
    PeriodosCierreListView,
    ProcesoAperturaDetalleView,
    ProcesoCierreDetalleView,
)


app_name = "actas"

urlpatterns = [
    path("periodos/", PeriodosCierreListView.as_view(), name="periodos-cierre"),
    path(
        "periodos/<int:pk>/diagnostico/",
        DiagnosticoCierrePeriodoView.as_view(),
        name="diagnostico-cierre",
    ),
    path(
        "periodos/<int:pk>/cerrar/",
        EjecutarCierrePeriodoView.as_view(),
        name="ejecutar-cierre",
    ),
    path(
        "cierres/<int:pk>/",
        ProcesoCierreDetalleView.as_view(),
        name="proceso-cierre-detalle",
    ),
    path("apertura/", AperturaPeriodoView.as_view(), name="apertura-periodo"),
    path(
        "aperturas/<int:pk>/",
        ProcesoAperturaDetalleView.as_view(),
        name="proceso-apertura-detalle",
    ),
    path(
        "pendientes-asignacion-docente/",
        PendientesAsignacionDocenteView.as_view(),
        name="pendientes-asignacion-docente",
    ),
]
