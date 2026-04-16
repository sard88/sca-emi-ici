from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import ComponenteEvaluacion, EsquemaEvaluacion


class ComponenteEvaluacionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        totales = {}
        componentes = []

        for form in self.forms:
            if form.cleaned_data.get("DELETE", False):
                continue
            if not form.cleaned_data:
                continue

            corte = form.cleaned_data.get("corte_codigo")
            porcentaje = form.cleaned_data.get("porcentaje")
            es_examen = form.cleaned_data.get("es_examen")

            if corte and porcentaje is not None:
                totales[corte] = totales.get(corte, 0) + porcentaje
                componentes.append((corte, es_examen))

        esquema = self.instance
        if esquema.pk:
            cortes_esperados = esquema.cortes_esperados()
            for corte in cortes_esperados:
                total = totales.get(corte, 0)
                if total != 100:
                    raise ValidationError(
                        f"La suma del corte {corte} debe ser 100 (actual: {total})."
                    )

            if esquema.num_parciales == EsquemaEvaluacion.PARCIALES_1:
                tiene_examen_final = any(corte == "FINAL" and es_examen for corte, es_examen in componentes)
                if not tiene_examen_final:
                    raise ValidationError(
                        "En materias de 1 parcial, el examen final es obligatorio."
                    )


class ComponenteEvaluacionInline(admin.TabularInline):
    model = ComponenteEvaluacion
    formset = ComponenteEvaluacionInlineFormSet
    extra = 1


@admin.register(EsquemaEvaluacion)
class EsquemaEvaluacionAdmin(admin.ModelAdmin):
    list_display = (
        "materia_plan",
        "version",
        "num_parciales",
        "permite_exencion",
        "peso_parciales",
        "peso_final",
        "activo",
    )
    list_filter = ("num_parciales", "permite_exencion", "activo")
    search_fields = (
        "materia_plan__plan_estudios__clave",
        "materia_plan__materia__clave",
        "materia_plan__materia__nombre",
        "version",
    )
    inlines = [ComponenteEvaluacionInline]


@admin.register(ComponenteEvaluacion)
class ComponenteEvaluacionAdmin(admin.ModelAdmin):
    list_display = ("esquema", "corte_codigo", "nombre", "porcentaje", "es_examen", "orden")
    list_filter = ("corte_codigo", "es_examen")
    search_fields = ("esquema__materia_plan__materia__clave", "nombre")
