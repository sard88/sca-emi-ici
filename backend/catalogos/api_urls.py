from django.urls import path

from . import api_views


urlpatterns = [
    path("<slug:slug>/", api_views.collection_view, name="api-catalogos-collection"),
    path("<slug:slug>/<int:pk>/", api_views.detail_view, name="api-catalogos-detail"),
    path("<slug:slug>/<int:pk>/activar/", api_views.activar_view, name="api-catalogos-activar"),
    path("<slug:slug>/<int:pk>/inactivar/", api_views.inactivar_view, name="api-catalogos-inactivar"),
    path(
        "esquemas-evaluacion/<int:esquema_id>/componentes/",
        api_views.componentes_collection_view,
        name="api-catalogos-esquema-componentes",
    ),
    path(
        "esquemas-evaluacion/<int:esquema_id>/componentes/<int:componente_id>/",
        api_views.componente_detail_view,
        name="api-catalogos-esquema-componente-detail",
    ),
]
