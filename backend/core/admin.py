from django.contrib import admin

from .models import AccesoRapidoUsuario, EventoCalendarioInstitucional, NotificacionUsuario


@admin.register(NotificacionUsuario)
class NotificacionUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo", "titulo", "prioridad", "leida", "creada_en")
    list_filter = ("tipo", "prioridad", "leida", "creada_en")
    search_fields = ("usuario__username", "usuario__nombre_completo", "titulo", "mensaje")
    readonly_fields = ("creada_en", "leida_en")


@admin.register(EventoCalendarioInstitucional)
class EventoCalendarioInstitucionalAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo_evento", "fecha_inicio", "fecha_fin", "periodo", "carrera", "grupo", "visible")
    list_filter = ("tipo_evento", "visible", "fecha_inicio", "periodo", "carrera")
    search_fields = ("titulo", "descripcion", "periodo__clave", "carrera__clave", "grupo__clave_grupo")
    readonly_fields = ("creado_en",)

    def save_model(self, request, obj, form, change):
        if not obj.creado_por_id:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(AccesoRapidoUsuario)
class AccesoRapidoUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "etiqueta", "url", "orden", "activo", "creado_en")
    list_filter = ("activo", "creado_en")
    search_fields = ("usuario__username", "usuario__nombre_completo", "etiqueta", "url")
    readonly_fields = ("creado_en",)
