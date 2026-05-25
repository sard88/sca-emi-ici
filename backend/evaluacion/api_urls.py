from django.urls import path

from . import api_views


urlpatterns = [
    path("docente/asignaciones/", api_views.docente_asignaciones_view, name="api-docente-asignaciones"),
    path("docente/asignaciones/<int:pk>/", api_views.docente_asignacion_detalle_view, name="api-docente-asignacion-detalle"),
    path("docente/asignaciones/<int:pk>/captura/<str:corte_codigo>/", api_views.docente_captura_corte_view, name="api-docente-captura-corte"),
    path("docente/asignaciones/<int:pk>/resumen/", api_views.docente_resumen_asignacion_view, name="api-docente-resumen"),
    path("docente/asignaciones/<int:pk>/actas/generar/", api_views.docente_generar_acta_view, name="api-docente-generar-acta"),
    path("docente/actas/", api_views.docente_actas_view, name="api-docente-actas"),
    path("docente/actas/<int:acta_id>/", api_views.docente_acta_detalle_view, name="api-docente-acta-detalle"),
    path("docente/actas/<int:acta_id>/regenerar/", api_views.docente_regenerar_acta_view, name="api-docente-regenerar-acta"),
    path("docente/actas/<int:acta_id>/publicar/", api_views.docente_publicar_acta_view, name="api-docente-publicar-acta"),
    path("docente/actas/<int:acta_id>/remitir/", api_views.docente_remitir_acta_view, name="api-docente-remitir-acta"),
    path("discente/actas/", api_views.discente_actas_view, name="api-discente-actas"),
    path("discente/actas/<int:detalle_id>/", api_views.discente_acta_detalle_view, name="api-discente-acta-detalle"),
    path("discente/actas/<int:detalle_id>/conformidad/", api_views.discente_conformidad_view, name="api-discente-conformidad"),
    path("jefatura-carrera/actas/pendientes/", api_views.jefatura_carrera_actas_pendientes_view, name="api-jefatura-carrera-actas"),
    path("jefatura-carrera/actas/<int:acta_id>/", api_views.jefatura_carrera_acta_detalle_view, name="api-jefatura-carrera-acta-detalle"),
    path("jefatura-carrera/actas/<int:acta_id>/validar/", api_views.jefatura_carrera_validar_acta_view, name="api-jefatura-carrera-validar-acta"),
    path("jefatura-academica/actas/pendientes/", api_views.jefatura_academica_actas_pendientes_view, name="api-jefatura-academica-actas"),
    path("jefatura-academica/actas/<int:acta_id>/", api_views.jefatura_academica_acta_detalle_view, name="api-jefatura-academica-acta-detalle"),
    path("jefatura-academica/actas/<int:acta_id>/formalizar/", api_views.jefatura_academica_formalizar_acta_view, name="api-jefatura-academica-formalizar-acta"),
    path("estadistica/actas/", api_views.estadistica_actas_view, name="api-estadistica-actas"),
    path("estadistica/actas/<int:acta_id>/", api_views.estadistica_acta_detalle_view, name="api-estadistica-acta-detalle"),
]
