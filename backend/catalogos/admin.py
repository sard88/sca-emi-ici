from django.contrib import admin

from .models import (
    Carrera,
    Generacion,
    GrupoAcademico,
    Materia,
    MateriaPlan,
    PeriodoEscolar,
    PlanEstudios,
)


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ("clave", "nombre", "estado", "vigente_desde", "vigente_hasta")
    list_filter = ("estado",)
    search_fields = ("clave", "nombre")


@admin.register(PlanEstudios)
class PlanEstudiosAdmin(admin.ModelAdmin):
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


@admin.register(Generacion)
class GeneracionAdmin(admin.ModelAdmin):
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
    list_display = ("clave", "nombre", "estado", "vigente_desde", "vigente_hasta")
    list_filter = ("estado",)
    search_fields = ("clave", "nombre")


@admin.register(GrupoAcademico)
class GrupoAcademicoAdmin(admin.ModelAdmin):
    list_display = (
        "clave",
        "nombre",
        "generacion",
        "periodo_escolar",
        "turno",
        "cupo_maximo",
        "estado",
    )
    list_filter = ("estado", "turno", "periodo_escolar", "generacion__plan_estudios")
    search_fields = ("clave", "nombre", "generacion__clave", "periodo_escolar__clave")


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
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


@admin.register(MateriaPlan)
class MateriaPlanAdmin(admin.ModelAdmin):
    list_display = (
        "plan_estudios",
        "materia",
        "semestre",
        "orden_malla",
        "obligatoria",
        "estado",
    )
    list_filter = ("estado", "obligatoria", "plan_estudios")
    search_fields = ("plan_estudios__clave", "materia__clave", "materia__nombre")
