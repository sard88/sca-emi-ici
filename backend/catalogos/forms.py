from django import forms
from django.utils import timezone

from .models import Generacion


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
