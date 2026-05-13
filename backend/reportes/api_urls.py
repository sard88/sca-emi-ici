from django.urls import path

from . import api_views

urlpatterns = [
    path("reportes/catalogo/", api_views.catalogo_reportes_view, name="api-reportes-catalogo"),
    path("exportaciones/", api_views.exportaciones_usuario_view, name="api-exportaciones"),
    path("exportaciones/actas/<int:acta_id>/pdf/", api_views.exportar_acta_pdf_view, name="api-exportaciones-acta-pdf"),
    path("exportaciones/actas/<int:acta_id>/xlsx/", api_views.exportar_acta_xlsx_view, name="api-exportaciones-acta-xlsx"),
    path(
        "exportaciones/asignaciones/<int:asignacion_docente_id>/calificacion-final/pdf/",
        api_views.exportar_calificacion_final_pdf_view,
        name="api-exportaciones-calificacion-final-pdf",
    ),
    path(
        "exportaciones/asignaciones/<int:asignacion_docente_id>/calificacion-final/xlsx/",
        api_views.exportar_calificacion_final_xlsx_view,
        name="api-exportaciones-calificacion-final-xlsx",
    ),
    path("exportaciones/registrar-evento-prueba/", api_views.registrar_evento_prueba_view, name="api-exportaciones-prueba"),
    path("auditoria/exportaciones/", api_views.auditoria_exportaciones_view, name="api-auditoria-exportaciones"),
]
