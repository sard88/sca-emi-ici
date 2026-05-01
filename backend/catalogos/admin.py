from django.contrib import admin

from .forms import (
    AntiguedadAdminForm,
    MateriaAdminForm,
    ProgramaAsignaturaAdminForm,
    PlanEstudiosAdminForm,
)
from .models import (
    Antiguedad,
    Carrera,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
    ProgramaAsignaturaUbicacion,
)


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ("clave", "nombre", "estado", "vigente_desde", "vigente_hasta")
    list_filter = ("estado",)
    search_fields = ("clave", "nombre")


@admin.register(PlanEstudios)
class PlanEstudiosAdmin(admin.ModelAdmin):
    form = PlanEstudiosAdminForm
    list_display = (
        "clave",
        "nombre",
        "carrera",
        "version",
        "estado",
        "vigente_desde",
        "vigente_hasta",
    )
    list_filter = ("estado", "carrera")
    search_fields = ("clave", "nombre", "version", "carrera__nombre")


@admin.register(Antiguedad)
class AntiguedadAdmin(admin.ModelAdmin):
    form = AntiguedadAdminForm
    list_display = (
        "clave",
        "nombre",
        "plan_estudios",
        "anio_inicio",
        "anio_fin",
        "estado",
    )
    list_filter = ("estado", "plan_estudios__carrera")
    search_fields = ("clave", "nombre", "plan_estudios__clave")


@admin.register(PeriodoEscolar)
class PeriodoEscolarAdmin(admin.ModelAdmin):
    list_display = (
        "clave",
        "anio_escolar",
        "periodo_academico",
        "fecha_inicio",
        "fecha_fin",
        "estado",
    )
    list_filter = ("estado",)
    search_fields = ("clave", "anio_escolar")


@admin.register(GrupoAcademico)
class GrupoAcademicoAdmin(admin.ModelAdmin):
    list_display = (
        "clave_grupo",
        "antiguedad",
        "periodo",
        "semestre_numero",
        "cupo_maximo",
        "estado",
    )
    list_filter = ("estado", "periodo", "antiguedad__plan_estudios")
    search_fields = ("clave_grupo", "antiguedad__clave", "periodo__clave")


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    form = MateriaAdminForm
    readonly_fields = ("creditos",)
    fields = (
        "clave",
        "nombre",
        "horas_totales",
        "creditos",
        "estado",
        "vigente_desde",
        "vigente_hasta",
    )
    list_display = (
        "clave",
        "nombre",
        "creditos",
        "horas_totales",
        "estado",
        "vigente_desde",
        "vigente_hasta",
    )
    list_filter = ("estado",)
    search_fields = ("clave", "nombre")


class ProgramaAsignaturaUbicacionInline(admin.TabularInline):
    model = ProgramaAsignaturaUbicacion
    extra = 0
    fields = ("antiguedad", "semestre_numero", "activo")


@admin.register(ProgramaAsignatura)
class ProgramaAsignaturaAdmin(admin.ModelAdmin):
    form = ProgramaAsignaturaAdminForm
    inlines = (ProgramaAsignaturaUbicacionInline,)
    fields = (
        "plan_estudios",
        "materia",
        "semestre_numero",
        "anio_formacion",
        "obligatoria",
        "ubicacion_excepcional",
    )
    list_display = (
        "plan_estudios",
        "materia",
        "semestre_numero",
        "anio_formacion",
        "obligatoria",
        "ubicacion_excepcional",
    )
    list_filter = (
        "obligatoria",
        "ubicacion_excepcional",
        "plan_estudios",
        "anio_formacion",
        "semestre_numero",
    )
    search_fields = ("plan_estudios__clave", "materia__clave", "materia__nombre")
