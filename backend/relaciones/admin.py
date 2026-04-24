from django.contrib import admin

from .forms import (
    AdscripcionGrupoForm,
    AsignacionDocenteForm,
    DiscenteAdminForm,
    InscripcionMateriaForm,
    MovimientoAcademicoForm,
)
from .models import AdscripcionGrupo, Discente, AsignacionDocente, InscripcionMateria, MovimientoAcademico
from .services import sincronizar_carga_academica as sincronizar_carga_academica_service


@admin.register(Discente)
class DiscenteAdmin(admin.ModelAdmin):
    form = DiscenteAdminForm
    list_display = (
        "matricula",
        "usuario",
        "plan_estudios",
        "antiguedad",
        "situacion_actual",
        "activo",
    )
    list_filter = ("activo", "situacion_actual", "plan_estudios", "antiguedad")
    search_fields = (
        "matricula",
        "usuario__username",
        "usuario__nombre_completo",
        "plan_estudios__clave",
        "antiguedad__clave",
    )


@admin.register(AdscripcionGrupo)
class AdscripcionGrupoAdmin(admin.ModelAdmin):
    form = AdscripcionGrupoForm
    list_display = (
        "discente",
        "grupo_academico",
        "vigente_desde",
        "vigente_hasta",
        "activo",
    )
    list_filter = ("activo", "grupo_academico__periodo", "grupo_academico")
    search_fields = (
        "discente__matricula",
        "discente__usuario__username",
        "discente__usuario__nombre_completo",
        "grupo_academico__clave_grupo",
    )


@admin.register(AsignacionDocente)
class AsignacionDocenteAdmin(admin.ModelAdmin):
    form = AsignacionDocenteForm
    actions = ("sincronizar_carga_academica",)
    list_display = (
        "usuario_docente",
        "grupo_academico",
        "programa_asignatura",
        "periodo",
        "vigente_desde",
        "vigente_hasta",
        "activo",
    )
    list_filter = (
        "activo",
        "grupo_academico__periodo",
        "grupo_academico",
        "programa_asignatura__plan_estudios",
    )
    search_fields = (
        "usuario_docente__username",
        "usuario_docente__nombre_completo",
        "grupo_academico__clave_grupo",
        "programa_asignatura__materia__clave",
        "programa_asignatura__materia__nombre",
    )

    @admin.action(description="Sincronizar carga académica del grupo")
    def sincronizar_carga_academica(self, request, queryset):
        total = 0
        for asignacion in queryset:
            total += sincronizar_carga_academica_service(asignacion)
        self.message_user(
            request,
            f"Sincronización completada. Inscripciones a asignatura creadas: {total}.",
        )


@admin.register(InscripcionMateria)
class InscripcionMateriaAdmin(admin.ModelAdmin):
    form = InscripcionMateriaForm
    readonly_fields = (
        "calificacion_final",
        "codigo_resultado_oficial",
        "codigo_marca",
        "cerrado_en",
    )
    list_display = (
        "discente",
        "asignacion_docente",
        "estado_inscripcion",
        "intento_numero",
        "calificacion_final",
        "codigo_resultado_oficial",
        "codigo_marca",
        "cerrado_en",
    )
    list_filter = (
        "estado_inscripcion",
        "asignacion_docente__grupo_academico__periodo",
        "asignacion_docente__grupo_academico",
        "asignacion_docente__programa_asignatura",
    )
    search_fields = (
        "discente__matricula",
        "discente__usuario__username",
        "discente__usuario__nombre_completo",
        "asignacion_docente__programa_asignatura__materia__clave",
        "asignacion_docente__programa_asignatura__materia__nombre",
    )

    def has_add_permission(self, request):
        return False


@admin.register(MovimientoAcademico)
class MovimientoAcademicoAdmin(admin.ModelAdmin):
    form = MovimientoAcademicoForm
    list_display = (
        "discente",
        "periodo",
        "tipo_movimiento",
        "grupo_origen",
        "grupo_destino",
        "fecha_movimiento",
    )
    list_filter = ("tipo_movimiento", "periodo", "grupo_origen", "grupo_destino")
    search_fields = (
        "discente__matricula",
        "discente__usuario__username",
        "discente__usuario__nombre_completo",
        "observaciones",
    )
