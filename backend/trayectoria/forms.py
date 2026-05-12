from django import forms

from relaciones.models import Discente

from .models import CatalogoSituacionAcademica
from .services import (
    inscripciones_elegibles_extraordinario,
    registrar_evento_situacion,
    registrar_extraordinario,
)


class ExtraordinarioForm(forms.Form):
    inscripcion_materia = forms.ModelChoiceField(
        queryset=inscripciones_elegibles_extraordinario(),
        label="Inscripción a asignatura",
    )
    fecha_aplicacion = forms.DateField(
        label="Fecha de aplicación",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    calificacion = forms.DecimalField(
        max_digits=4,
        decimal_places=1,
        min_value=0,
        max_value=10,
        label="Calificación",
        help_text="Captura la calificación del extraordinario en escala de 0.0 a 10.0.",
    )

    def __init__(self, *args, **kwargs):
        inscripcion_inicial = kwargs.pop("inscripcion_inicial", None)
        super().__init__(*args, **kwargs)
        self.fields["inscripcion_materia"].queryset = inscripciones_elegibles_extraordinario()
        if inscripcion_inicial:
            self.fields["inscripcion_materia"].initial = inscripcion_inicial

    def save(self, usuario):
        return registrar_extraordinario(
            inscripcion_materia=self.cleaned_data["inscripcion_materia"],
            calificacion=self.cleaned_data["calificacion"],
            fecha_aplicacion=self.cleaned_data["fecha_aplicacion"],
            registrado_por=usuario,
        )


class EventoSituacionAcademicaForm(forms.Form):
    discente = forms.ModelChoiceField(
        queryset=Discente.objects.select_related("usuario", "plan_estudios").order_by("matricula"),
        label="Discente",
    )
    situacion = forms.ModelChoiceField(
        queryset=CatalogoSituacionAcademica.objects.filter(activo=True).order_by("clave"),
        label="Situación",
    )
    fecha_inicio = forms.DateField(
        label="Fecha de inicio",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    fecha_fin = forms.DateField(
        required=False,
        label="Fecha de fin",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    motivo = forms.CharField(
        required=False,
        label="Motivo",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        discente_inicial = kwargs.pop("discente_inicial", None)
        super().__init__(*args, **kwargs)
        self.fields["situacion"].queryset = CatalogoSituacionAcademica.objects.filter(
            activo=True
        ).order_by("clave")
        if discente_inicial:
            self.fields["discente"].initial = discente_inicial

    def save(self, usuario):
        return registrar_evento_situacion(
            discente=self.cleaned_data["discente"],
            situacion=self.cleaned_data["situacion"],
            fecha_inicio=self.cleaned_data["fecha_inicio"],
            fecha_fin=self.cleaned_data["fecha_fin"],
            motivo=self.cleaned_data["motivo"],
            registrado_por=usuario,
        )
