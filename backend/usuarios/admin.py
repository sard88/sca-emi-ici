from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html, format_html_join

from .forms import UsuarioAdminCreationForm, UsuarioAdminForm
from .models import AsignacionCargo, GradoEmpleo, UnidadOrganizacional, Usuario


@admin.register(GradoEmpleo)
class GradoEmpleoAdmin(admin.ModelAdmin):
    list_display = ("clave", "abreviatura", "nombre", "tipo", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("clave", "abreviatura", "nombre")
    ordering = ("tipo", "abreviatura", "nombre")


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioAdminForm
    add_form = UsuarioAdminCreationForm
    list_display = (
        "username",
        "grado_empleo",
        "correo",
        "estado_cuenta",
        "is_staff",
        "is_active",
    )
    list_filter = ("estado_cuenta", "grado_empleo", "is_staff", "is_superuser", "is_active")
    search_fields = (
        "username",
        "correo",
        "nombre_completo",
        "grado_empleo__clave",
        "grado_empleo__abreviatura",
        "grado_empleo__nombre",
    )
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
                    "grado_empleo",
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
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
        (
            "Informacion adicional",
            {
                "fields": (
                    "estado_cuenta",
                    "grado_empleo",
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


@admin.register(UnidadOrganizacional)
class UnidadOrganizacionalAdmin(admin.ModelAdmin):
    list_display = (
        "clave",
        "nombre",
        "tipo_unidad",
        "padre",
        "carrera",
        "activo",
        "orden",
    )
    list_filter = ("tipo_unidad", "activo", "carrera")
    search_fields = ("clave", "nombre", "padre__nombre", "carrera__clave", "carrera__nombre")
    ordering = ("orden", "tipo_unidad", "nombre")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "padre":
            kwargs["label"] = "Depende de (Sección)"
            kwargs["queryset"] = UnidadOrganizacional.objects.filter(
                tipo_unidad=UnidadOrganizacional.TIPO_SECCION
            ).order_by("orden", "nombre")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AsignacionCargo)
class AsignacionCargoAdmin(admin.ModelAdmin):
    fields = (
        "usuario",
        "cargo_codigo",
        "carrera",
        "unidad_organizacional",
        "tipo_designacion",
        "vigente_desde",
        "vigente_hasta",
        "activo",
    )
    list_display = (
        "usuario",
        "cargo",
        "carrera",
        "unidad_organizacional",
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
        "unidad_organizacional__clave",
        "unidad_organizacional__nombre",
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        cargo_field = form.base_fields.get("cargo_codigo")
        if cargo_field:
            choices = list(AsignacionCargo.CARGO_CHOICES_ADMIN)
            valores_visibles = {value for value, _ in choices}
            if obj and obj.cargo_codigo not in valores_visibles:
                choices.append((obj.cargo_codigo, f"{obj.get_cargo_codigo_display()} (registro existente)"))
            cargo_field.choices = choices
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "unidad_organizacional":
            formfield.label_from_instance = self.unidad_organizacional_label
        return formfield

    @admin.display(description="Cargo", ordering="cargo_codigo")
    def cargo(self, obj):
        return obj.cargo_descripcion()

    def unidad_organizacional_label(self, obj):
        if obj.tipo_unidad == UnidadOrganizacional.TIPO_SUBSECCION and obj.padre_id:
            return f"{obj.padre.nombre} -> {obj.nombre}"
        return obj.nombre

    class Media:
        js = ("usuarios/admin/asignacion_cargo.js",)
