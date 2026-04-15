from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "estado_cuenta", "is_staff", "is_active")
    list_filter = ("estado_cuenta", "is_staff", "is_superuser", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Informacion adicional",
            {"fields": ("estado_cuenta", "nombre_completo", "telefono", "ultimo_acceso")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informacion adicional",
            {"fields": ("estado_cuenta", "nombre_completo", "telefono", "ultimo_acceso")},
        ),
    )
