from django.urls import path

from . import api_views

app_name = "core_api"

urlpatterns = [
    path("dashboard/resumen/", api_views.dashboard_resumen_view, name="dashboard-resumen"),
    path("dashboard/actividad-reciente/", api_views.actividad_reciente_view, name="actividad-reciente"),
    path("notificaciones/", api_views.notificaciones_view, name="notificaciones"),
    path("notificaciones/<int:pk>/leer/", api_views.notificacion_leer_view, name="notificacion-leer"),
    path("notificaciones/leer-todas/", api_views.notificaciones_leer_todas_view, name="notificaciones-leer-todas"),
    path("calendario/mes/", api_views.calendario_mes_view, name="calendario-mes"),
    path("calendario/proximos/", api_views.calendario_proximos_view, name="calendario-proximos"),
    path("busqueda/", api_views.busqueda_view, name="busqueda"),
    path("perfil/me/", api_views.perfil_me_view, name="perfil-me"),
    path("accesos-rapidos/", api_views.accesos_rapidos_view, name="accesos-rapidos"),
    path("accesos-rapidos/crear/", api_views.acceso_rapido_crear_view, name="acceso-rapido-crear"),
    path("accesos-rapidos/<int:pk>/", api_views.acceso_rapido_eliminar_view, name="acceso-rapido-eliminar"),
]
