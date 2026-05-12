from django.contrib import admin

from .models import (
    CatalogoResultadoAcademico,
    CatalogoSituacionAcademica,
    EventoSituacionAcademica,
    Extraordinario,
)


@admin.register(CatalogoSituacionAcademica)
class CatalogoSituacionAcademicaAdmin(admin.ModelAdmin):
    list_display = ("clave", "nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("clave", "nombre")


@admin.register(CatalogoResultadoAcademico)
class CatalogoResultadoAcademicoAdmin(admin.ModelAdmin):
    list_display = ("clave", "nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("clave", "nombre")


@admin.register(EventoSituacionAcademica)
class EventoSituacionAcademicaAdmin(admin.ModelAdmin):
    list_display = (
        "discente",
        "situacion",
        "fecha_inicio",
        "fecha_fin",
        "periodo",
        "registrado_por",
    )
    list_filter = ("situacion", "periodo")
    search_fields = (
        "discente__matricula",
        "discente__usuario__username",
        "discente__usuario__nombre_completo",
        "motivo",
    )
    readonly_fields = ("creado_en", "actualizado_en")


@admin.register(Extraordinario)
class ExtraordinarioAdmin(admin.ModelAdmin):
    readonly_fields = (
        "aprobado",
        "codigo_resultado_oficial",
        "codigo_marca",
        "calificacion_ordinaria",
        "codigo_resultado_ordinario",
        "codigo_marca_ordinaria",
        "creado_en",
        "actualizado_en",
    )
    list_display = (
        "inscripcion_materia",
        "fecha_aplicacion",
        "calificacion",
        "aprobado",
        "codigo_resultado_oficial",
        "codigo_marca",
        "registrado_por",
    )
    list_filter = ("aprobado", "codigo_resultado_oficial", "codigo_marca", "fecha_aplicacion")
    search_fields = (
        "inscripcion_materia__discente__matricula",
        "inscripcion_materia__discente__usuario__username",
        "inscripcion_materia__discente__usuario__nombre_completo",
        "inscripcion_materia__asignacion_docente__programa_asignatura__materia__clave",
        "inscripcion_materia__asignacion_docente__programa_asignatura__materia__nombre",
    )
