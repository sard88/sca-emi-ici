from django.contrib import admin

from .models import RegistroExportacion


@admin.register(RegistroExportacion)
class RegistroExportacionAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "tipo_documento",
        "formato",
        "nombre_archivo",
        "estado",
        "creado_en",
        "finalizado_en",
        "ip_origen",
        "rol_contexto",
        "cargo_contexto",
    )
    list_filter = ("tipo_documento", "formato", "estado", "creado_en", "usuario")
    search_fields = (
        "usuario__username",
        "usuario__nombre_completo",
        "nombre_archivo",
        "objeto_repr",
        "tipo_documento",
    )
    date_hierarchy = "creado_en"
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or super().has_view_permission(request, obj=obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions
