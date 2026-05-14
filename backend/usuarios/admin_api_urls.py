from django.urls import path

from . import admin_api_views


urlpatterns = [
    path("roles/", admin_api_views.roles_view, name="api-admin-roles"),
    path("usuarios/", admin_api_views.usuarios_collection_view, name="api-admin-usuarios"),
    path("usuarios/<int:pk>/", admin_api_views.usuarios_detail_view, name="api-admin-usuario-detail"),
    path("usuarios/<int:pk>/activar/", lambda request, pk: admin_api_views.usuario_estado_view(request, pk, True), name="api-admin-usuario-activar"),
    path("usuarios/<int:pk>/inactivar/", lambda request, pk: admin_api_views.usuario_estado_view(request, pk, False), name="api-admin-usuario-inactivar"),
    path("grados-empleos/", admin_api_views.grados_collection_view, name="api-admin-grados"),
    path("grados-empleos/<int:pk>/", admin_api_views.grados_detail_view, name="api-admin-grado-detail"),
    path("grados-empleos/<int:pk>/activar/", lambda request, pk: admin_api_views.simple_estado_view(request, "grados-empleos", pk, True), name="api-admin-grado-activar"),
    path("grados-empleos/<int:pk>/inactivar/", lambda request, pk: admin_api_views.simple_estado_view(request, "grados-empleos", pk, False), name="api-admin-grado-inactivar"),
    path("unidades-organizacionales/", admin_api_views.unidades_collection_view, name="api-admin-unidades"),
    path("unidades-organizacionales/<int:pk>/", admin_api_views.unidades_detail_view, name="api-admin-unidad-detail"),
    path("unidades-organizacionales/<int:pk>/activar/", lambda request, pk: admin_api_views.simple_estado_view(request, "unidades-organizacionales", pk, True), name="api-admin-unidad-activar"),
    path("unidades-organizacionales/<int:pk>/inactivar/", lambda request, pk: admin_api_views.simple_estado_view(request, "unidades-organizacionales", pk, False), name="api-admin-unidad-inactivar"),
    path("asignaciones-cargo/", admin_api_views.cargos_collection_view, name="api-admin-cargos"),
    path("asignaciones-cargo/<int:pk>/", admin_api_views.cargos_detail_view, name="api-admin-cargo-detail"),
    path("asignaciones-cargo/<int:pk>/cerrar/", admin_api_views.cargo_cerrar_view, name="api-admin-cargo-cerrar"),
    path("asignaciones-cargo/<int:pk>/activar/", lambda request, pk: admin_api_views.simple_estado_view(request, "asignaciones-cargo", pk, True), name="api-admin-cargo-activar"),
    path("asignaciones-cargo/<int:pk>/inactivar/", lambda request, pk: admin_api_views.simple_estado_view(request, "asignaciones-cargo", pk, False), name="api-admin-cargo-inactivar"),
]
