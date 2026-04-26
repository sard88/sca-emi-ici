from decimal import Decimal

from django.contrib import admin
from django.forms.formsets import DELETION_FIELD_NAME
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .forms import EsquemaEvaluacionAdminForm
from .models import CapturaCalificacionPreliminar, ComponenteEvaluacion, EsquemaEvaluacion


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

    def _get_activo_actual(self):
        if self.is_bound:
            return self.data.get("activo") in {"1", "true", "True", "on"}

        return getattr(self.instance, "activo", True)

    def _tiene_cambios_en_componentes(self):
        for form in self.forms:
            if getattr(form, "cleaned_data", None) and form.cleaned_data.get("DELETE", False):
                return True
            if form.has_changed():
                return True

        return False

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        if not self._get_activo_actual():
            if self._tiene_cambios_en_componentes():
                raise ValidationError(
                    "Los componentes no se pueden modificar si el esquema no está "
                    "disponible para evaluación."
                )
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

    class Media:
        js = ("evaluacion/admin/esquema_evaluacion.js",)


@admin.register(CapturaCalificacionPreliminar)
class CapturaCalificacionPreliminarAdmin(admin.ModelAdmin):
    readonly_fields = ("corte_codigo", "creado_en", "actualizado_en")
    list_display = (
        "inscripcion_materia",
        "componente",
        "corte_codigo",
        "valor",
        "capturado_por",
        "actualizado_en",
    )
    list_filter = (
        "corte_codigo",
        "componente__esquema",
        "inscripcion_materia__asignacion_docente__grupo_academico__periodo",
    )
    search_fields = (
        "inscripcion_materia__discente__matricula",
        "inscripcion_materia__discente__usuario__username",
        "inscripcion_materia__discente__usuario__nombre_completo",
        "componente__nombre",
        "capturado_por__username",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "inscripcion_materia",
                "inscripcion_materia__discente",
                "inscripcion_materia__discente__usuario",
                "inscripcion_materia__asignacion_docente",
                "componente",
                "componente__esquema",
                "capturado_por",
            )
        )

    def save_model(self, request, obj, form, change):
        if not obj.capturado_por_id:
            obj.capturado_por = request.user
        super().save_model(request, obj, form, change)
