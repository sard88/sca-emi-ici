from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView

from relaciones.models import AsignacionDocente
from relaciones.permisos import (
    puede_consultar_asignacion_docente,
    usuario_es_admin_soporte,
    usuario_es_docente,
    usuario_es_estadistica,
)

from .forms import CapturaCalificacionesCorteForm
from .models import ComponenteEvaluacion
from .services import ServicioCalculoAcademico


ROLES_CONSULTA_CALIFICACIONES = (
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
)


def usuario_es_jefatura_academica(user):
    return user.is_authenticated and user.groups.filter(
        name__in=ROLES_CONSULTA_CALIFICACIONES
    ).exists()


def puede_capturar_calificaciones(user, asignacion):
    return usuario_es_admin_soporte(user) or (
        usuario_es_docente(user) and asignacion.usuario_docente_id == user.id
    )


def puede_consultar_calificaciones(user, asignacion):
    return (
        puede_capturar_calificaciones(user, asignacion)
        or puede_consultar_asignacion_docente(user)
        or usuario_es_estadistica(user)
        or usuario_es_jefatura_academica(user)
    )


def mensajes_validation_error(error):
    if hasattr(error, "messages"):
        return error.messages
    return [str(error)]


class AsignacionEvaluacionMixin(LoginRequiredMixin):
    login_url = reverse_lazy("usuarios:login")
    asignacion = None

    def get_asignaciones_queryset(self):
        return AsignacionDocente.objects.select_related(
            "usuario_docente",
            "grupo_academico",
            "grupo_academico__periodo",
            "programa_asignatura",
            "programa_asignatura__materia",
        )

    def dispatch(self, request, *args, **kwargs):
        self.asignacion = get_object_or_404(
            self.get_asignaciones_queryset(),
            pk=kwargs["pk"],
        )
        if not self.tiene_permiso(request.user):
            raise PermissionDenied("No tienes permiso para acceder a esta captura.")
        return super().dispatch(request, *args, **kwargs)

    def tiene_permiso(self, user):
        raise NotImplementedError

    def get_esquema(self):
        return ServicioCalculoAcademico.obtener_esquema_activo(
            self.asignacion.programa_asignatura
        )

    def get_inscripciones(self):
        return self.asignacion.inscripciones_materia.select_related(
            "discente",
            "discente__usuario",
        ).order_by("discente__matricula")

    def calcular_resultados(self):
        resultados = []
        errores = []
        for inscripcion in self.get_inscripciones():
            try:
                resultados.append(ServicioCalculoAcademico(inscripcion).calcular())
            except ValidationError as error:
                errores.extend(mensajes_validation_error(error))
        return resultados, errores


class CapturaCalificacionesCorteView(AsignacionEvaluacionMixin, View):
    template_name = "evaluacion/captura_calificaciones.html"

    def tiene_permiso(self, user):
        return puede_capturar_calificaciones(user, self.asignacion)

    def get_corte_codigo(self):
        return self.kwargs["corte_codigo"].upper()

    def get_form(self, data=None):
        esquema = self.get_esquema()
        corte_codigo = self.get_corte_codigo()
        if corte_codigo not in esquema.cortes_esperados():
            raise Http404("El corte solicitado no aplica a este esquema de evaluación.")
        return CapturaCalificacionesCorteForm(
            data=data,
            asignacion=self.asignacion,
            esquema=esquema,
            corte_codigo=corte_codigo,
            usuario=self.request.user,
        )

    def get_context_data(self, form):
        resultados, errores = self.calcular_resultados()
        corte_codigo = self.get_corte_codigo()
        captura_filas = []
        for inscripcion in form.inscripciones:
            captura_filas.append(
                {
                    "inscripcion": inscripcion,
                    "campos": [
                        form[
                            CapturaCalificacionesCorteForm.get_field_name(
                                inscripcion.pk,
                                componente.pk,
                            )
                        ]
                        for componente in form.componentes
                    ],
                }
            )
        return {
            "asignacion": self.asignacion,
            "esquema": self.get_esquema(),
            "cortes": self.get_esquema().cortes_esperados(),
            "corte_actual": corte_codigo,
            "form": form,
            "inscripciones": form.inscripciones,
            "componentes": form.componentes,
            "captura_filas": captura_filas,
            "resultados": resultados,
            "resultados_corte": [
                {
                    "inscripcion": resultado["inscripcion"],
                    "corte": resultado["cortes"].get(corte_codigo),
                    "exencion_aplica": resultado["exencion_aplica"],
                }
                for resultado in resultados
            ],
            "errores_calculo": errores,
        }

    def get(self, request, *args, **kwargs):
        try:
            form = self.get_form()
        except ValidationError as error:
            return render(
                request,
                self.template_name,
                {
                    "asignacion": self.asignacion,
                    "errores_calculo": mensajes_validation_error(error),
                },
            )
        return render(request, self.template_name, self.get_context_data(form))

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST)
        if form.is_valid():
            capturas = form.save()
            messages.success(
                request,
                (
                    "Captura preliminar guardada. "
                    f"Registros actualizados: {len(capturas)}. "
                    f"Registros limpiados: {form.deleted_count}."
                ),
            )
            return redirect(
                "evaluacion:captura-calificaciones",
                pk=self.asignacion.pk,
                corte_codigo=self.get_corte_codigo(),
            )
        return render(request, self.template_name, self.get_context_data(form))


class ResumenCalculoAsignacionView(AsignacionEvaluacionMixin, TemplateView):
    template_name = "evaluacion/resumen_calculo.html"

    def tiene_permiso(self, user):
        return puede_consultar_calificaciones(user, self.asignacion)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resultados, errores = self.calcular_resultados()
        esquema = None
        try:
            esquema = self.get_esquema()
        except ValidationError as error:
            errores.extend(mensajes_validation_error(error))

        context.update(
            {
                "asignacion": self.asignacion,
                "esquema": esquema,
                "resultados": resultados,
                "errores_calculo": errores,
            }
        )
        return context
