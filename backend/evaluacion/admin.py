from decimal import Decimal

from django.contrib import admin
from django.forms.formsets import DELETION_FIELD_NAME
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .forms import EsquemaEvaluacionAdminForm
from .models import ComponenteEvaluacion, EsquemaEvaluacion


class ComponenteEvaluacionInlineFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if "es_examen" in form.fields:
            form.fields["es_examen"].label = "Es examen final"
        if DELETION_FIELD_NAME in form.fields:
            form.fields[DELETION_FIELD_NAME].label = "Eliminar completamente"

    @staticmethod
    def _build_cortes_esperados(num_parciales):
        esquema = EsquemaEvaluacion(num_parciales=num_parciales)
        return esquema.cortes_esperados()

    def _get_num_parciales_actual(self):
        raw_num_parciales = self.data.get("num_parciales")
        if raw_num_parciales not in (None, ""):
            try:
                return int(raw_num_parciales)
            except (TypeError, ValueError):
                return None

        return self.instance.num_parciales

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        num_parciales = self._get_num_parciales_actual()
        if num_parciales not in (
            EsquemaEvaluacion.PARCIALES_1,
            EsquemaEvaluacion.PARCIALES_2,
            EsquemaEvaluacion.PARCIALES_3,
        ):
            return

        totales = {}
        componentes = []

        for form in self.forms:
            if not getattr(form, "cleaned_data", None):
                continue
            if not form.instance.pk and not form.has_changed():
                continue
            if form.cleaned_data.get("DELETE", False):
                continue

            corte = form.cleaned_data.get("corte_codigo")
            porcentaje = form.cleaned_data.get("porcentaje")
            es_examen = form.cleaned_data.get("es_examen", False)

            if corte and porcentaje is not None:
                totales[corte] = totales.get(corte, Decimal("0.00")) + porcentaje
                componentes.append((corte, bool(es_examen)))

        errores = []
        cortes_esperados = self._build_cortes_esperados(num_parciales)
        for corte in cortes_esperados:
            total = totales.get(corte, Decimal("0.00"))
            if total != Decimal("100.00"):
                errores.append(f"La suma del corte {corte} debe ser 100 (actual: {total}).")

        if num_parciales == EsquemaEvaluacion.PARCIALES_1:
            tiene_examen_final = any(
                corte == ComponenteEvaluacion.CORTE_FINAL and es_examen
                for corte, es_examen in componentes
            )
            if not tiene_examen_final:
                errores.append("En materias de 1 parcial, el examen final es obligatorio.")

        if errores:
            raise ValidationError(errores)


class ComponenteEvaluacionInline(admin.TabularInline):
    model = ComponenteEvaluacion
    formset = ComponenteEvaluacionInlineFormSet
    extra = 1
    template = "admin/evaluacion/componenteevaluacion/tabular.html"


@admin.register(EsquemaEvaluacion)
class EsquemaEvaluacionAdmin(admin.ModelAdmin):
    form = EsquemaEvaluacionAdminForm
    list_display = (
        "programa_asignatura",
        "version",
        "num_parciales",
        "permite_exencion",
        "peso_parciales",
        "peso_final",
        "activo",
    )
    list_filter = ("num_parciales", "permite_exencion", "activo")
    search_fields = (
        "programa_asignatura__plan_estudios__clave",
        "programa_asignatura__materia__clave",
        "programa_asignatura__materia__nombre",
        "version",
    )
    inlines = [ComponenteEvaluacionInline]
