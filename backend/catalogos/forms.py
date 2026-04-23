from django import forms
from django.utils import timezone

from .models import Carrera, ESTADO_ACTIVO, Generacion, Materia, PlanEstudios


def _available_year_choices():
    current_year = timezone.localdate().year
    start_year = current_year - 20
    end_year = current_year + 10
    return [(year, str(year)) for year in range(start_year, end_year + 1)]


def build_year_choices(extra_value=None):
    base_choices = _available_year_choices()
    choice_values = {value for value, _ in base_choices}
    choices = [("", "---------")]

    if extra_value is not None and extra_value not in choice_values:
        choices.append((extra_value, str(extra_value)))

    choices.extend(base_choices)
    return choices


class GeneracionAdminForm(forms.ModelForm):
    anio_inicio = forms.TypedChoiceField(
        choices=(),
        coerce=int,
        empty_value=None,
        required=False,
        label="Año de inicio",
    )
    anio_fin = forms.TypedChoiceField(
        choices=(),
        coerce=int,
        empty_value=None,
        required=False,
        label="Año de fin",
    )

    class Meta:
        model = Generacion
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["anio_inicio"].choices = build_year_choices(self.instance.anio_inicio)
        self.fields["anio_fin"].choices = build_year_choices(self.instance.anio_fin)


class PlanEstudiosAdminForm(forms.ModelForm):
    class Meta:
        model = PlanEstudios
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        carrera_field = self.fields["carrera"]
        carrera_field.queryset = Carrera.objects.filter(estado=ESTADO_ACTIVO).order_by(
            "clave", "nombre"
        )

        if self.instance.pk and self.instance.carrera.estado != ESTADO_ACTIVO:
            carrera_field.help_text = (
                "La carrera actual est\u00e1 inactiva. Selecciona una carrera activa "
                "para guardar cambios."
            )


class MateriaAdminForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = "__all__"

    def clean_horas_totales(self):
        horas_totales = self.cleaned_data.get("horas_totales")
        if horas_totales is None or horas_totales <= 0:
            raise forms.ValidationError("Debe ser mayor a 0.")
        return horas_totales
