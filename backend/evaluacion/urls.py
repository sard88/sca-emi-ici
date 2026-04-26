from django.urls import path

from .views import CapturaCalificacionesCorteView, ResumenCalculoAsignacionView


app_name = "evaluacion"

urlpatterns = [
    path(
        "docente/asignaciones/<int:pk>/captura/<str:corte_codigo>/",
        CapturaCalificacionesCorteView.as_view(),
        name="captura-calificaciones",
    ),
    path(
        "docente/asignaciones/<int:pk>/resumen/",
        ResumenCalculoAsignacionView.as_view(),
        name="resumen-calculo",
    ),
]
