from django import forms

from catalogos.models import ESTADO_ACTIVO, ProgramaAsignatura

from .models import CapturaCalificacionPreliminar, EsquemaEvaluacion


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


class CapturaCalificacionesCorteForm(forms.Form):
    def __init__(self, *args, asignacion, esquema, corte_codigo, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        self.asignacion = asignacion
        self.esquema = esquema
        self.corte_codigo = corte_codigo
        self.usuario = usuario
        self.componentes = list(
            esquema.componentes.filter(corte_codigo=corte_codigo).order_by("orden", "pk")
        )
        self.inscripciones = list(
            asignacion.inscripciones_materia.select_related(
                "discente",
                "discente__usuario",
            ).order_by("discente__matricula")
        )
        self._field_map = {}
        capturas = {
            (captura.inscripcion_materia_id, captura.componente_id): captura
            for captura in CapturaCalificacionPreliminar.objects.filter(
                inscripcion_materia__in=self.inscripciones,
                componente__in=self.componentes,
            )
        }
        self._capturas_existentes = capturas
        self.deleted_count = 0

        for inscripcion in self.inscripciones:
            for componente in self.componentes:
                field_name = self.get_field_name(inscripcion.pk, componente.pk)
                captura = capturas.get((inscripcion.pk, componente.pk))
                self._field_map[field_name] = (inscripcion, componente)
                self.fields[field_name] = forms.DecimalField(
                    label=componente.nombre,
                    min_value=0,
                    max_value=10,
                    decimal_places=1,
                    max_digits=4,
                    required=False,
                    initial=captura.valor if captura else None,
                    widget=forms.NumberInput(
                        attrs={
                            "min": "0",
                            "max": "10",
                            "step": "0.1",
                            "inputmode": "decimal",
                        }
                    ),
                )

    @staticmethod
    def get_field_name(inscripcion_id, componente_id):
        return f"cal_{inscripcion_id}_{componente_id}"

    def save(self):
        capturas = []
        for field_name, (inscripcion, componente) in self._field_map.items():
            valor = self.cleaned_data.get(field_name)
            captura_existente = self._capturas_existentes.get(
                (inscripcion.pk, componente.pk)
            )
            if valor is None:
                if captura_existente:
                    captura_existente.delete()
                    self.deleted_count += 1
                continue

            if captura_existente:
                captura_existente.valor = valor
                captura_existente.capturado_por = self.usuario
                captura_existente.save()
                captura = captura_existente
            else:
                captura = CapturaCalificacionPreliminar.objects.create(
                    inscripcion_materia=inscripcion,
                    componente=componente,
                    valor=valor,
                    capturado_por=self.usuario,
                )
            capturas.append(captura)
        return capturas
