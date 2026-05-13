from django.contrib import admin

from .models import (
    DetalleCierrePeriodoDiscente,
    ProcesoAperturaPeriodo,
    ProcesoCierrePeriodo,
)


class DetalleCierrePeriodoDiscenteInline(admin.TabularInline):
    model = DetalleCierrePeriodoDiscente
    extra = 0
    readonly_fields = (
        "discente",
        "grupo_origen",
        "clasificacion",
        "promovible",
        "requiere_extraordinario",
        "situacion_detectada",
        "motivo",
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProcesoCierrePeriodo)
class ProcesoCierrePeriodoAdmin(admin.ModelAdmin):
    list_display = ("periodo", "estado", "ejecutado_por", "ejecutado_en")
    list_filter = ("estado", "periodo")
    search_fields = ("periodo__clave", "ejecutado_por__username")
    readonly_fields = ("ejecutado_en", "resumen_json")
    inlines = [DetalleCierrePeriodoDiscenteInline]


@admin.register(DetalleCierrePeriodoDiscente)
class DetalleCierrePeriodoDiscenteAdmin(admin.ModelAdmin):
    list_display = (
        "proceso_cierre",
        "discente",
        "grupo_origen",
        "clasificacion",
        "promovible",
        "requiere_extraordinario",
    )
    list_filter = ("clasificacion", "promovible", "requiere_extraordinario")
    search_fields = (
        "discente__matricula",
        "discente__usuario__nombre_completo",
        "grupo_origen__clave_grupo",
    )
    readonly_fields = (
        "proceso_cierre",
        "discente",
        "grupo_origen",
        "clasificacion",
        "motivo",
        "promovible",
        "requiere_extraordinario",
        "situacion_detectada",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProcesoAperturaPeriodo)
class ProcesoAperturaPeriodoAdmin(admin.ModelAdmin):
    list_display = ("periodo_origen", "periodo_destino", "estado", "ejecutado_por", "ejecutado_en")
    list_filter = ("estado", "periodo_origen", "periodo_destino")
    search_fields = ("periodo_origen__clave", "periodo_destino__clave", "ejecutado_por__username")
    readonly_fields = ("ejecutado_en", "resumen_json")
