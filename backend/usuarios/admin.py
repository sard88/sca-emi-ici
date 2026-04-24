from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html, format_html_join

from .forms import UsuarioAdminCreationForm, UsuarioAdminForm
from .models import AsignacionCargo, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioAdminForm
    add_form = UsuarioAdminCreationForm
    list_display = ("username", "correo", "estado_cuenta", "is_staff", "is_active")
    list_filter = ("estado_cuenta", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "correo", "nombre_completo")
    readonly_fields = tuple(
        dict.fromkeys(
            (
                *UserAdmin.readonly_fields,
                "last_login",
                "date_joined",
                "ultimo_acceso",
                "permisos_heredados_por_rol",
            )
        )
    )

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
        (
            "Permisos efectivos heredados por rol",
            {
                "fields": ("permisos_heredados_por_rol",),
                "description": (
                    "Consulta informativa de los permisos que el usuario obtiene "
                    "por pertenecer a su rol/grupo. No duplica permisos directos."
                ),
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
                )
            },
        ),
        (
            "Roles y permisos",
            {
                "fields": (
                    "groups",
                )
            },
        ),
    )

    @admin.display(description="Permisos heredados por rol")
    def permisos_heredados_por_rol(self, obj):
        if not obj or not obj.pk:
            return "Guarde el usuario para consultar los permisos heredados."

        bloques = []

        if obj.is_superuser:
            bloques.append(
                format_html(
                    "<p><strong>Superusuario:</strong> acceso total sin requerir permisos "
                    "asignados de forma explicita.</p>"
                )
            )

        grupos = obj.groups.prefetch_related("permissions__content_type").order_by("name")
        if not grupos.exists():
            if bloques:
                return format_html_join("", "{}", ((bloque,) for bloque in bloques))
            return "Sin rol/grupo asignado."

        for grupo in grupos:
            permisos = grupo.permissions.select_related("content_type").order_by(
                "content_type__app_label",
                "content_type__model",
                "codename",
            )

            if not permisos.exists():
                bloques.append(
                    format_html(
                        "<p><strong>{}</strong>: sin permisos asignados.</p>",
                        grupo.name,
                    )
                )
                continue

            lista_permisos = format_html_join(
                "",
                "<li>{} <code>{}.{}</code></li>",
                (
                    (
                        permiso.name,
                        permiso.content_type.app_label,
                        permiso.codename,
                    )
                    for permiso in permisos
                ),
            )
            bloques.append(
                format_html(
                    "<div><strong>{}</strong><ul>{}</ul></div>",
                    grupo.name,
                    lista_permisos,
                )
            )

        return format_html_join("", "{}", ((bloque,) for bloque in bloques))


@admin.register(AsignacionCargo)
class AsignacionCargoAdmin(admin.ModelAdmin):
    fields = (
        "usuario",
        "cargo_codigo",
        "carrera",
        "tipo_designacion",
        "vigente_desde",
        "vigente_hasta",
        "activo",
    )
    list_display = (
        "usuario",
        "cargo",
        "carrera",
        "tipo_designacion",
        "vigente_desde",
        "vigente_hasta",
        "activo",
    )
    list_filter = ("tipo_designacion", "activo", "cargo_codigo", "carrera")
    search_fields = (
        "usuario__username",
        "usuario__nombre_completo",
        "cargo_codigo",
        "carrera__clave",
        "carrera__nombre",
    )

    @admin.display(description="Cargo", ordering="cargo_codigo")
    def cargo(self, obj):
        return obj.cargo_descripcion()
