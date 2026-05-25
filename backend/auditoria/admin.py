from django.contrib import admin

from .models import BitacoraEventoCritico


@admin.register(BitacoraEventoCritico)
class BitacoraEventoCriticoAdmin(admin.ModelAdmin):
    list_display = (
        "creado_en",
        "usuario",
        "modulo",
        "evento_codigo",
        "severidad",
        "resultado",
        "objeto_tipo",
        "objeto_id",
        "ip_origen",
    )
    list_filter = ("modulo", "evento_codigo", "severidad", "resultado", "creado_en")
    search_fields = (
        "username_snapshot",
        "nombre_usuario_snapshot",
        "objeto_repr",
        "objeto_tipo",
        "objeto_id",
        "resumen",
        "request_id",
        "correlacion_id",
    )
    date_hierarchy = "creado_en"
    ordering = ("-creado_en", "-id")
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return {}
