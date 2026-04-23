from django import forms

from catalogos.models import ESTADO_ACTIVO, ProgramaAsignatura

from .models import EsquemaEvaluacion


class EsquemaEvaluacionAdminForm(forms.ModelForm):
    class Meta:
        model = EsquemaEvaluacion
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        programa_field = self.fields["programa_asignatura"]
        umbral_field = self.fields["umbral_exencion"]
        programa_field.queryset = (
            ProgramaAsignatura.objects.filter(
                plan_estudios__estado=ESTADO_ACTIVO,
                materia__estado=ESTADO_ACTIVO,
            )
            .select_related("plan_estudios", "materia", "plan_estudios__carrera")
            .order_by("plan_estudios__clave", "materia__clave")
        )
        umbral_field.help_text = (
            "Captura la calificación mínima para exentar el examen final en escala de 0 a 10."
        )

        if self.instance.pk and not self.instance.programa_asignatura_activo():
            programa_field.help_text = (
                "El programa de asignatura actual est\u00e1 inactivo. "
                "Selecciona uno activo para guardar cambios."
            )
