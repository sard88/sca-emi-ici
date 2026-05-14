from django.urls import path

from . import api_views

urlpatterns = [
    path("reportes/catalogo/", api_views.catalogo_reportes_view, name="api-reportes-catalogo"),
    path("exportaciones/", api_views.exportaciones_usuario_view, name="api-exportaciones"),
    path("exportaciones/actas-disponibles/", api_views.actas_disponibles_view, name="api-exportaciones-actas-disponibles"),
    path("exportaciones/kardex-disponibles/", api_views.kardex_disponibles_view, name="api-exportaciones-kardex-disponibles"),
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
    path("exportaciones/kardex/<int:discente_id>/pdf/", api_views.exportar_kardex_pdf_view, name="api-exportaciones-kardex-pdf"),
    path("reportes/operativos/actas-estado/", api_views.reporte_actas_estado_view, name="api-reportes-operativos-actas-estado"),
    path("reportes/operativos/actas-pendientes/", api_views.reporte_actas_pendientes_view, name="api-reportes-operativos-actas-pendientes"),
    path("reportes/operativos/inconformidades/", api_views.reporte_inconformidades_view, name="api-reportes-operativos-inconformidades"),
    path("reportes/operativos/sin-conformidad/", api_views.reporte_sin_conformidad_view, name="api-reportes-operativos-sin-conformidad"),
    path("reportes/operativos/actas-formalizadas/", api_views.reporte_actas_formalizadas_view, name="api-reportes-operativos-actas-formalizadas"),
    path("reportes/operativos/validaciones-acta/", api_views.reporte_validaciones_acta_view, name="api-reportes-operativos-validaciones-acta"),
    path("reportes/operativos/exportaciones-realizadas/", api_views.reporte_exportaciones_realizadas_view, name="api-reportes-operativos-exportaciones-realizadas"),
    path("exportaciones/reportes/actas-estado/xlsx/", api_views.exportar_reporte_actas_estado_xlsx_view, name="api-exportaciones-reportes-actas-estado-xlsx"),
    path("exportaciones/reportes/actas-pendientes/xlsx/", api_views.exportar_reporte_actas_pendientes_xlsx_view, name="api-exportaciones-reportes-actas-pendientes-xlsx"),
    path("exportaciones/reportes/inconformidades/xlsx/", api_views.exportar_reporte_inconformidades_xlsx_view, name="api-exportaciones-reportes-inconformidades-xlsx"),
    path("exportaciones/reportes/sin-conformidad/xlsx/", api_views.exportar_reporte_sin_conformidad_xlsx_view, name="api-exportaciones-reportes-sin-conformidad-xlsx"),
    path("exportaciones/reportes/actas-formalizadas/xlsx/", api_views.exportar_reporte_actas_formalizadas_xlsx_view, name="api-exportaciones-reportes-actas-formalizadas-xlsx"),
    path("exportaciones/reportes/validaciones-acta/xlsx/", api_views.exportar_reporte_validaciones_acta_xlsx_view, name="api-exportaciones-reportes-validaciones-acta-xlsx"),
    path("exportaciones/reportes/exportaciones-realizadas/xlsx/", api_views.exportar_reporte_exportaciones_realizadas_xlsx_view, name="api-exportaciones-reportes-exportaciones-realizadas-xlsx"),
    path("exportaciones/registrar-evento-prueba/", api_views.registrar_evento_prueba_view, name="api-exportaciones-prueba"),
    path("auditoria/exportaciones/", api_views.auditoria_exportaciones_view, name="api-auditoria-exportaciones"),
]
