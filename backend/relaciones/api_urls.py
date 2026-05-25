from django.urls import path

from . import api_views

urlpatterns = [
    path("movimientos/", api_views.movimientos_list_create_view, name="api-movimientos-list-create"),
    path("movimientos/cambio-grupo/", api_views.cambio_grupo_create_view, name="api-cambio-grupo-create"),
    path("movimientos/<int:pk>/", api_views.movimiento_detail_view, name="api-movimiento-detail"),
]
