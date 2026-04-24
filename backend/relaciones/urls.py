from django.urls import path

from .views import (
    AsignacionDocenteCreateView,
    AsignacionDocenteListView,
    InscripcionMateriaListView,
    MovimientoAcademicoCreateView,
    MovimientoAcademicoListView,
)

app_name = "relaciones"

urlpatterns = [
    path(
        "asignaciones-docentes/",
        AsignacionDocenteListView.as_view(),
        name="asignacion-docente-list",
    ),
    path(
        "asignaciones-docentes/crear/",
        AsignacionDocenteCreateView.as_view(),
        name="asignacion-docente-create",
    ),
    path(
        "inscripciones-materia/",
        InscripcionMateriaListView.as_view(),
        name="inscripcion-materia-list",
    ),
    path(
        "movimientos-academicos/",
        MovimientoAcademicoListView.as_view(),
        name="movimiento-academico-list",
    ),
    path(
        "movimientos-academicos/crear/",
        MovimientoAcademicoCreateView.as_view(),
        name="movimiento-academico-create",
    ),
]
