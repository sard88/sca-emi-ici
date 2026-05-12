from django.urls import path

from .views import (
    ActaDetalleView,
    CapturaCalificacionesCorteView,
    CrearBorradorActaView,
    DiscenteActasPublicadasView,
    DiscenteDetalleActaView,
    DocenteActasListView,
    EstadisticaActasView,
    FormalizarActaView,
    JefaturaAcademicaActasPendientesView,
    JefaturaCarreraConsultaActasView,
    JefaturaCarreraActasPendientesView,
    JefaturaPlaneacionConsultaActasView,
    PublicarActaView,
    RegenerarActaView,
    RemitirActaView,
    ResumenCalculoAsignacionView,
    ValidarActaCarreraView,
)


app_name = "evaluacion"

urlpatterns = [
    path("actas/docente/", DocenteActasListView.as_view(), name="docente-actas"),
    path("actas/<int:pk>/", ActaDetalleView.as_view(), name="acta-detalle"),
    path("actas/<int:pk>/regenerar/", RegenerarActaView.as_view(), name="acta-regenerar"),
    path("actas/<int:pk>/publicar/", PublicarActaView.as_view(), name="acta-publicar"),
    path("actas/<int:pk>/remitir/", RemitirActaView.as_view(), name="acta-remitir"),
    path(
        "actas/<int:pk>/validar-carrera/",
        ValidarActaCarreraView.as_view(),
        name="acta-validar-carrera",
    ),
    path(
        "actas/<int:pk>/formalizar/",
        FormalizarActaView.as_view(),
        name="acta-formalizar",
    ),
    path(
        "actas/discente/",
        DiscenteActasPublicadasView.as_view(),
        name="discente-actas",
    ),
    path(
        "actas/discente/detalle/<int:pk>/",
        DiscenteDetalleActaView.as_view(),
        name="discente-acta-detalle",
    ),
    path(
        "actas/jefatura-carrera/pendientes/",
        JefaturaCarreraActasPendientesView.as_view(),
        name="jefatura-carrera-actas",
    ),
    path(
        "actas/jefatura-carrera/consulta/",
        JefaturaCarreraConsultaActasView.as_view(),
        name="jefatura-carrera-consulta-actas",
    ),
    path(
        "actas/planeacion-evaluacion/consulta/",
        JefaturaPlaneacionConsultaActasView.as_view(),
        name="jefatura-planeacion-consulta-actas",
    ),
    path(
        "actas/jefatura-academica/pendientes/",
        JefaturaAcademicaActasPendientesView.as_view(),
        name="jefatura-academica-actas",
    ),
    path(
        "actas/estadistica/",
        EstadisticaActasView.as_view(),
        name="estadistica-actas",
    ),
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
    path(
        "docente/asignaciones/<int:pk>/actas/<str:corte_codigo>/crear-borrador/",
        CrearBorradorActaView.as_view(),
        name="acta-crear-borrador",
    ),
]
