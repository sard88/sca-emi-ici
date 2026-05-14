from django.urls import path

from . import api_views


urlpatterns = [
    path("auditoria/eventos/", api_views.eventos_list_view, name="api-auditoria-eventos"),
    path("auditoria/eventos/resumen/", api_views.eventos_resumen_view, name="api-auditoria-eventos-resumen"),
    path("auditoria/eventos/<int:pk>/", api_views.eventos_detail_view, name="api-auditoria-eventos-detail"),
    path("exportaciones/auditoria/eventos/xlsx/", api_views.exportar_eventos_xlsx_view, name="api-exportaciones-auditoria-eventos-xlsx"),
]
