from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AsignacionCargo, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "correo", "estado_cuenta", "is_staff", "is_active")
    list_filter = ("estado_cuenta", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "correo", "nombre_completo")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Informacion adicional",
            {
                "fields": (
                    "estado_cuenta",
                    "nombre_completo",
                    "correo",
                    "telefono",
                    "ultimo_acceso",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informacion adicional",
            {
                "fields": (
                    "estado_cuenta",
                    "nombre_completo",
                    "correo",
                    "telefono",
                    "ultimo_acceso",
                )
            },
        ),
    )


@admin.register(AsignacionCargo)
class AsignacionCargoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "cargo_codigo",
        "tipo_designacion",
        "vigente_desde",
        "vigente_hasta",
        "activo",
    )
    list_filter = ("tipo_designacion", "activo", "cargo_codigo")
    search_fields = ("usuario__username", "usuario__nombre_completo", "cargo_codigo")
