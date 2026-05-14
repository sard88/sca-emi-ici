from django.urls import path

from . import api_views

urlpatterns = [
    path("mi-historial/", api_views.mi_historial_view, name="api-mi-historial"),
    path("historial/", api_views.historial_list_view, name="api-historial-list"),
    path("historial/<int:discente_id>/", api_views.historial_detail_view, name="api-historial-detail"),
    path("extraordinarios/", api_views.extraordinarios_list_view, name="api-extraordinarios-list"),
    path("extraordinarios/crear/", api_views.extraordinario_create_view, name="api-extraordinarios-create-alt"),
    path("extraordinarios/<int:pk>/", api_views.extraordinario_detail_view, name="api-extraordinarios-detail"),
    path("situaciones/", api_views.situaciones_list_view, name="api-situaciones-list"),
    path("situaciones/crear/", api_views.situacion_create_view, name="api-situaciones-create-alt"),
    path("situaciones/<int:pk>/", api_views.situacion_detail_view, name="api-situaciones-detail"),
]
