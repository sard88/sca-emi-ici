from django.urls import path

from . import api_views

urlpatterns = [
    path("reportes/catalogo/", api_views.catalogo_reportes_view, name="api-reportes-catalogo"),
    path("exportaciones/", api_views.exportaciones_usuario_view, name="api-exportaciones"),
    path("exportaciones/registrar-evento-prueba/", api_views.registrar_evento_prueba_view, name="api-exportaciones-prueba"),
    path("auditoria/exportaciones/", api_views.auditoria_exportaciones_view, name="api-auditoria-exportaciones"),
]
