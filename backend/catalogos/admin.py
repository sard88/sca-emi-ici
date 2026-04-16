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
    list_display = (
        "clave",
        "anio_escolar",
        "semestre_operativo",
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
        "generacion",
        "periodo",
        "semestre_numero",
        "cupo_maximo",
        "estado",
    )
    list_filter = ("estado", "periodo", "generacion__plan_estudios")
    search_fields = ("clave_grupo", "generacion__clave", "periodo__clave")


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
        "semestre_numero",
        "anio_escolar_numero",
        "obligatoria",
    )
    list_filter = ("obligatoria", "plan_estudios", "anio_escolar_numero", "semestre_numero")
    search_fields = ("plan_estudios__clave", "materia__clave", "materia__nombre")
