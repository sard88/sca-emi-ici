from django import forms

from catalogos.models import ESTADO_ACTIVO, ESTADO_CERRADO, ESTADO_PLANIFICADO, PeriodoEscolar


class CierrePeriodoForm(forms.Form):
    observaciones = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class AperturaPeriodoForm(forms.Form):
    periodo_origen = forms.ModelChoiceField(
        label="Periodo origen",
        queryset=PeriodoEscolar.objects.none(),
    )
    periodo_destino = forms.ModelChoiceField(
        label="Periodo destino",
        queryset=PeriodoEscolar.objects.none(),
    )
    observaciones = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["periodo_origen"].queryset = PeriodoEscolar.objects.filter(
            estado=ESTADO_CERRADO
        ).order_by("-anio_escolar", "-periodo_academico")
        self.fields["periodo_destino"].queryset = PeriodoEscolar.objects.filter(
            estado__in=[ESTADO_PLANIFICADO, ESTADO_ACTIVO]
        ).order_by("-anio_escolar", "-periodo_academico")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("periodo_origen") == cleaned_data.get("periodo_destino"):
            raise forms.ValidationError("El periodo origen y destino deben ser distintos.")
        return cleaned_data
