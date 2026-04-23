from django import forms
from django.utils import timezone

from .models import (
    Antiguedad,
    Carrera,
    ESTADO_ACTIVO,
    Materia,
    PlanEstudios,
    ProgramaAsignatura,
    MATERIA_PLAN_SEMESTRE_CHOICES,
    MATERIA_PLAN_SEMESTRE_MAX,
    MATERIA_PLAN_SEMESTRE_MIN,
)


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


class AntiguedadAdminForm(forms.ModelForm):
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
        model = Antiguedad
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


class ProgramaAsignaturaAdminForm(forms.ModelForm):
    semestre_numero = forms.TypedChoiceField(
        choices=MATERIA_PLAN_SEMESTRE_CHOICES,
        coerce=int,
        label="Semestre",
    )
    anio_formacion = forms.IntegerField(
        required=False,
        disabled=True,
        label="Año de formación",
    )
    obligatoria = forms.BooleanField(
        required=False,
        disabled=True,
        initial=True,
        label="Obligatoria",
    )

    class Meta:
        model = ProgramaAsignatura
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        plan_field = self.fields["plan_estudios"]
        plan_field.queryset = PlanEstudios.objects.filter(estado=ESTADO_ACTIVO).order_by(
            "carrera__clave", "clave"
        )

        materia_field = self.fields["materia"]
        materia_field.queryset = Materia.objects.filter(estado=ESTADO_ACTIVO).order_by(
            "clave", "nombre"
        )

        if self.instance.pk and self.instance.plan_estudios.estado != ESTADO_ACTIVO:
            plan_field.help_text = (
                "El plan de estudios actual está inactivo. Selecciona uno activo "
                "para guardar cambios."
            )
        if self.instance.pk and self.instance.materia.estado != ESTADO_ACTIVO:
            materia_field.help_text = (
                "La materia actual está inactiva. Selecciona una activa para guardar cambios."
            )

        self.initial["obligatoria"] = True
        self.fields["obligatoria"].initial = True
        self.fields["anio_formacion"].initial = self._build_anio_formacion_initial()

    def _build_anio_formacion_initial(self):
        semestre = self.data.get("semestre_numero") if self.is_bound else self.instance.semestre_numero

        try:
            semestre = int(semestre)
        except (TypeError, ValueError):
            semestre = None

        if semestre and MATERIA_PLAN_SEMESTRE_MIN <= semestre <= MATERIA_PLAN_SEMESTRE_MAX:
            return ProgramaAsignatura.calculate_anio_formacion(semestre)

        return self.instance.anio_formacion or ProgramaAsignatura.calculate_anio_formacion(1)

    def clean_semestre_numero(self):
        semestre_numero = self.cleaned_data.get("semestre_numero")
        if semestre_numero is None:
            raise forms.ValidationError("Este campo es obligatorio.")
        if not MATERIA_PLAN_SEMESTRE_MIN <= semestre_numero <= MATERIA_PLAN_SEMESTRE_MAX:
            raise forms.ValidationError(
                f"Debe estar entre {MATERIA_PLAN_SEMESTRE_MIN} y {MATERIA_PLAN_SEMESTRE_MAX}."
            )
        return semestre_numero

    def clean(self):
        cleaned_data = super().clean()
        semestre_numero = cleaned_data.get("semestre_numero")

        cleaned_data["obligatoria"] = True
        if semestre_numero is not None:
            cleaned_data["anio_formacion"] = ProgramaAsignatura.calculate_anio_formacion(semestre_numero)

        return cleaned_data
