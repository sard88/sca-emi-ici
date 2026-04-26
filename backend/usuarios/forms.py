from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.db.models import Q

from .models import GradoEmpleo, Usuario


def rol_field():
    return forms.ModelChoiceField(
        queryset=Group.objects.none(),
        required=True,
        label="Rol",
        help_text="Seleccione un único rol para el usuario.",
        error_messages={
            "required": "Debe seleccionar un rol para el usuario.",
            "invalid_choice": "Seleccione un rol válido.",
        },
    )


class LoginFormulario(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Usuario o contraseña incorrectos.",
        "inactive": "Usuario o contraseña incorrectos.",
    }

    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={"autofocus": True}),
    )
    password = forms.CharField(
        label="Contrasena",
        strip=False,
        widget=forms.PasswordInput,
    )

    def confirm_login_allowed(self, user):
        estado_activo = getattr(user, "ESTADO_ACTIVO", "activo")
        estado_cuenta = getattr(user, "estado_cuenta", estado_activo)
        if not user.is_active or estado_cuenta != estado_activo:
            raise forms.ValidationError(
                self.error_messages["invalid_login"],
                code="invalid_login",
                params={"username": self.cleaned_data.get("username")},
            )


class UsuarioRolUnicoMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        groups_field = self.fields["groups"]
        groups_field.queryset = Group.objects.order_by("name")

        if "grado_empleo" in self.fields:
            grado_queryset = GradoEmpleo.objects.filter(activo=True)
            grado_actual_id = getattr(self.instance, "grado_empleo_id", None)
            if grado_actual_id:
                grado_queryset = GradoEmpleo.objects.filter(
                    Q(activo=True) | Q(pk=grado_actual_id)
                )
            self.fields["grado_empleo"].queryset = grado_queryset.order_by(
                "tipo",
                "abreviatura",
                "nombre",
            )

        if "user_permissions" in self.fields:
            self.fields["user_permissions"].label = "Permisos directos adicionales"
            self.fields["user_permissions"].help_text = (
                "Use este campo solo para excepciones puntuales. Los permisos del rol/grupo "
                "se heredan automaticamente y se consultan en la seccion informativa del usuario."
            )

        if self.instance and self.instance.pk:
            rol_actual = self.instance.groups.order_by("name").first()
            if rol_actual:
                self.initial["groups"] = rol_actual.pk

    def clean_groups(self):
        group = self.cleaned_data.get("groups")
        if not group:
            raise forms.ValidationError("Debe seleccionar un rol para el usuario.")

        return [group]


class UsuarioAdminForm(UsuarioRolUnicoMixin, UserChangeForm):
    groups = rol_field()

    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = "__all__"


class UsuarioAdminCreationForm(UsuarioRolUnicoMixin, UserCreationForm):
    groups = rol_field()

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = (
            "username",
            "estado_cuenta",
            "grado_empleo",
            "nombre_completo",
            "correo",
            "telefono",
            "groups",
        )
