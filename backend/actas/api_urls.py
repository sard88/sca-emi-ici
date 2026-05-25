from django.urls import path

from . import api_views

urlpatterns = [
    path("periodos/", api_views.periodos_list_view, name="api-periodos-list"),
    path("periodos/<int:periodo_id>/diagnostico-cierre/", api_views.diagnostico_cierre_view, name="api-diagnostico-cierre"),
    path("periodos/<int:periodo_id>/cerrar/", api_views.cerrar_periodo_view, name="api-cerrar-periodo"),
    path("cierres/", api_views.cierres_list_view, name="api-cierres-list"),
    path("cierres/<int:pk>/", api_views.cierre_detail_view, name="api-cierre-detail"),
    path("aperturas/", api_views.aperturas_list_view, name="api-aperturas-list"),
    path("aperturas/crear/", api_views.apertura_create_view, name="api-apertura-create"),
    path("aperturas/<int:pk>/", api_views.apertura_detail_view, name="api-apertura-detail"),
    path("pendientes-asignacion-docente/", api_views.pendientes_asignacion_docente_view, name="api-pendientes-asignacion-docente"),
]
