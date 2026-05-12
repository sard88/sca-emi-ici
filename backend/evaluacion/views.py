from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from relaciones.models import AsignacionDocente, Discente
from relaciones.permisos import (
    puede_consultar_asignacion_docente,
    usuario_es_admin_soporte,
    usuario_es_docente,
    usuario_es_estadistica,
    usuario_es_jefatura_carrera,
    usuario_es_jefatura_planeacion,
)

from .forms import CapturaCalificacionesCorteForm, ConformidadDiscenteForm
from .models import Acta, ComponenteEvaluacion, DetalleActa
from .services import (
    ServicioCalculoAcademico,
    crear_o_regenerar_borrador_acta,
    formalizar_acta_jefatura_academica,
    obtener_cargo_jefatura_academica,
    obtener_cargo_jefatura_carrera_para_acta,
    obtener_cargo_jefatura_planeacion_para_acta,
    publicar_acta,
    registrar_conformidad_discente,
    remitir_acta,
    validar_acta_jefatura_carrera,
)


ROLES_CONSULTA_CALIFICACIONES = (
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
)


def usuario_es_jefatura_academica(user):
    return user.is_authenticated and user.groups.filter(
        name__in=ROLES_CONSULTA_CALIFICACIONES
    ).exists()


def puede_capturar_calificaciones(user, asignacion):
    if not user.is_authenticated:
        return False
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


def puede_consultar_estados_actas(user):
    return usuario_es_admin_soporte(user) or usuario_es_estadistica(user)


def puede_ver_actas_por_validar(user):
    return usuario_es_admin_soporte(user) or usuario_es_jefatura_carrera(user)


def puede_consultar_actas_planeacion(user):
    return usuario_es_admin_soporte(user) or usuario_es_jefatura_planeacion(user)


def puede_operar_acta_docente(user, acta):
    return puede_capturar_calificaciones(user, acta.asignacion_docente)


def puede_consultar_acta(user, acta):
    if not user.is_authenticated:
        return False
    return (
        usuario_es_admin_soporte(user)
        or (
            usuario_es_docente(user)
            and acta.asignacion_docente.usuario_docente_id == user.id
        )
        or usuario_es_estadistica(user)
        or obtener_cargo_jefatura_carrera_para_acta(user, acta) is not None
        or obtener_cargo_jefatura_planeacion_para_acta(user, acta) is not None
        or obtener_cargo_jefatura_academica(user) is not None
    )


def puede_validar_acta_carrera(user, acta):
    if not user.is_authenticated:
        return False
    return usuario_es_admin_soporte(user) or obtener_cargo_jefatura_carrera_para_acta(user, acta)


def puede_formalizar_acta_academica(user):
    if not user.is_authenticated:
        return False
    return usuario_es_admin_soporte(user) or obtener_cargo_jefatura_academica(user)


def mensajes_validation_error(error):
    if hasattr(error, "messages"):
        return error.messages
    return [str(error)]


def ip_origen_request(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def preparar_tabla_acta_corte(acta):
    detalles = list(
        acta.detalles.select_related(
            "inscripcion_materia",
            "inscripcion_materia__discente",
            "inscripcion_materia__discente__usuario",
            "inscripcion_materia__discente__usuario__grado_empleo",
        ).prefetch_related("calificaciones_componentes", "conformidades")
    )
    componentes = []
    vistos = set()
    for detalle in detalles:
        for calificacion in detalle.calificaciones_componentes.all():
            if calificacion.componente_id in vistos:
                continue
            vistos.add(calificacion.componente_id)
            componentes.append(calificacion)

    filas = []
    for index, detalle in enumerate(detalles, start=1):
        calificaciones_por_componente = {
            calificacion.componente_id: calificacion
            for calificacion in detalle.calificaciones_componentes.all()
        }
        conformidad = detalle.conformidades.filter(vigente=True).first()
        filas.append(
            {
                "numero": index,
                "detalle": detalle,
                "calificaciones": [
                    calificaciones_por_componente.get(componente.componente_id)
                    for componente in componentes
                ],
                "conformidad": conformidad,
            }
        )
    return componentes, filas


def obtener_acta_bloqueante_captura(asignacion, corte_codigo):
    return (
        Acta.objects.filter(
            asignacion_docente=asignacion,
            corte_codigo=corte_codigo,
            estado_acta__in=[
                Acta.ESTADO_PUBLICADO_DISCENTE,
                Acta.ESTADO_REMITIDO_JEFATURA_CARRERA,
                Acta.ESTADO_VALIDADO_JEFATURA_CARRERA,
                Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
                Acta.ESTADO_ARCHIVADO,
            ],
        )
        .order_by("-creado_en")
        .first()
    )


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
        if not request.user.is_authenticated:
            return self.handle_no_permission()
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
        acta_bloqueante = obtener_acta_bloqueante_captura(
            self.asignacion,
            self.get_corte_codigo(),
        )
        if acta_bloqueante:
            messages.error(
                request,
                (
                    "Este corte ya tiene un acta publicada, remitida o formalizada. "
                    "La captura preliminar quedó bloqueada para conservar la trazabilidad."
                ),
            )
            return redirect(
                "evaluacion:captura-calificaciones",
                pk=self.asignacion.pk,
                corte_codigo=self.get_corte_codigo(),
            )
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


class ActaQuerysetMixin(LoginRequiredMixin):
    login_url = reverse_lazy("usuarios:login")

    def get_queryset(self):
        return Acta.objects.select_related(
            "asignacion_docente",
            "asignacion_docente__usuario_docente",
            "asignacion_docente__grupo_academico",
            "asignacion_docente__grupo_academico__periodo",
            "asignacion_docente__programa_asignatura",
            "asignacion_docente__programa_asignatura__materia",
            "esquema",
            "creado_por",
        ).prefetch_related(
            "detalles",
            "detalles__inscripcion_materia",
            "detalles__inscripcion_materia__discente",
            "detalles__inscripcion_materia__discente__usuario",
            "validaciones",
        )


class DocenteActasListView(ActaQuerysetMixin, ListView):
    template_name = "evaluacion/docente_actas.html"
    context_object_name = "actas"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (usuario_es_docente(request.user) or usuario_es_admin_soporte(request.user)):
            raise PermissionDenied("No tienes permiso para consultar actas docentes.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if usuario_es_admin_soporte(self.request.user):
            return queryset
        return queryset.filter(asignacion_docente__usuario_docente=self.request.user)


class ActaDetalleView(ActaQuerysetMixin, DetailView):
    template_name = "evaluacion/acta_detalle.html"
    context_object_name = "acta"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.object = self.get_object()
        if not puede_consultar_acta(request.user, self.object):
            raise PermissionDenied("No tienes permiso para consultar esta acta.")
        return super().dispatch(request, *args, **kwargs)

    def enlace_regreso(self, acta):
        user = self.request.user
        if usuario_es_admin_soporte(user) or (
            usuario_es_docente(user) and acta.asignacion_docente.usuario_docente_id == user.id
        ):
            return {
                "texto": "Actas docentes",
                "url": reverse("evaluacion:docente-actas"),
            }
        if usuario_es_estadistica(user):
            return {
                "texto": "Consulta de actas de calificaciones",
                "url": reverse("evaluacion:estadistica-actas"),
            }
        if obtener_cargo_jefatura_carrera_para_acta(user, acta):
            return {
                "texto": "Actas por validar",
                "url": reverse("evaluacion:jefatura-carrera-actas"),
            }
        if obtener_cargo_jefatura_planeacion_para_acta(user, acta):
            return {
                "texto": "Consulta de actas de Planeación y Evaluación",
                "url": reverse("evaluacion:jefatura-planeacion-consulta-actas"),
            }
        if obtener_cargo_jefatura_academica(user):
            return {
                "texto": "Actas por formalizar",
                "url": reverse("evaluacion:jefatura-academica-actas"),
            }
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        acta = self.object
        componentes_acta, filas_acta = preparar_tabla_acta_corte(acta)
        context.update(
            {
                "componentes_acta": componentes_acta,
                "filas_acta": filas_acta,
                "comentarios_conformidad": [
                    fila
                    for fila in filas_acta
                    if fila["conformidad"] and fila["conformidad"].comentario
                ],
                "enlace_regreso_acta": self.enlace_regreso(acta),
                "puede_regenerar": acta.permite_regenerar
                and puede_operar_acta_docente(self.request.user, acta),
                "puede_publicar": acta.estado_acta == Acta.ESTADO_BORRADOR_DOCENTE
                and puede_operar_acta_docente(self.request.user, acta),
                "puede_remitir": acta.estado_acta == Acta.ESTADO_PUBLICADO_DISCENTE
                and puede_operar_acta_docente(self.request.user, acta),
                "puede_validar_carrera": acta.estado_acta
                == Acta.ESTADO_REMITIDO_JEFATURA_CARRERA
                and bool(puede_validar_acta_carrera(self.request.user, acta)),
                "puede_formalizar": acta.estado_acta
                == Acta.ESTADO_VALIDADO_JEFATURA_CARRERA
                and bool(puede_formalizar_acta_academica(self.request.user)),
            }
        )
        return context


class CrearBorradorActaView(AsignacionEvaluacionMixin, View):
    def tiene_permiso(self, user):
        return puede_capturar_calificaciones(user, self.asignacion)

    def post(self, request, *args, **kwargs):
        corte_codigo = kwargs["corte_codigo"].upper()
        try:
            acta = crear_o_regenerar_borrador_acta(self.asignacion, corte_codigo, request.user)
            messages.success(request, "Borrador de acta generado desde capturas preliminares.")
            return redirect("evaluacion:acta-detalle", pk=acta.pk)
        except ValidationError as error:
            for mensaje in mensajes_validation_error(error):
                messages.error(request, mensaje)
            return redirect("usuarios:docente-asignacion-detalle", pk=self.asignacion.pk)


class RegenerarActaView(ActaQuerysetMixin, View):
    def post(self, request, pk):
        acta = get_object_or_404(self.get_queryset(), pk=pk)
        if not puede_operar_acta_docente(request.user, acta):
            raise PermissionDenied("No tienes permiso para regenerar esta acta.")
        if acta.estado_acta != Acta.ESTADO_BORRADOR_DOCENTE:
            messages.error(
                request,
                "Solo se puede regenerar un acta en estado borrador docente.",
            )
            return redirect("evaluacion:acta-detalle", pk=acta.pk)
        try:
            acta = crear_o_regenerar_borrador_acta(
                acta.asignacion_docente,
                acta.corte_codigo,
                request.user,
            )
            messages.success(request, "Acta regenerada desde capturas preliminares.")
        except ValidationError as error:
            for mensaje in mensajes_validation_error(error):
                messages.error(request, mensaje)
        return redirect("evaluacion:acta-detalle", pk=acta.pk)


class PublicarActaView(ActaQuerysetMixin, View):
    def post(self, request, pk):
        acta = get_object_or_404(self.get_queryset(), pk=pk)
        if not puede_operar_acta_docente(request.user, acta):
            raise PermissionDenied("No tienes permiso para publicar esta acta.")
        try:
            publicar_acta(acta, request.user, ip_origen=ip_origen_request(request))
            messages.success(request, "Acta publicada para consulta de discentes.")
        except ValidationError as error:
            for mensaje in mensajes_validation_error(error):
                messages.error(request, mensaje)
        return redirect("evaluacion:acta-detalle", pk=acta.pk)


class RemitirActaView(ActaQuerysetMixin, View):
    def post(self, request, pk):
        acta = get_object_or_404(self.get_queryset(), pk=pk)
        if not puede_operar_acta_docente(request.user, acta):
            raise PermissionDenied("No tienes permiso para remitir esta acta.")
        try:
            remitir_acta(acta, request.user, ip_origen=ip_origen_request(request))
            messages.success(request, "Acta remitida a jefatura de carrera.")
        except ValidationError as error:
            for mensaje in mensajes_validation_error(error):
                messages.error(request, mensaje)
        return redirect("evaluacion:acta-detalle", pk=acta.pk)


class JefaturaCarreraActasPendientesView(ActaQuerysetMixin, ListView):
    template_name = "evaluacion/jefatura_carrera_actas.html"
    context_object_name = "actas"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not puede_ver_actas_por_validar(request.user):
            raise PermissionDenied("No tienes permiso para consultar actas.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            estado_acta=Acta.ESTADO_REMITIDO_JEFATURA_CARRERA
        )
        if usuario_es_admin_soporte(self.request.user):
            return queryset
        return [
            acta
            for acta in queryset
            if obtener_cargo_jefatura_carrera_para_acta(self.request.user, acta)
        ]


class JefaturaCarreraConsultaActasView(ActaQuerysetMixin, ListView):
    template_name = "evaluacion/consulta_actas.html"
    context_object_name = "actas"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not puede_ver_actas_por_validar(request.user):
            raise PermissionDenied("No tienes permiso para consultar actas.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if usuario_es_admin_soporte(self.request.user):
            return queryset
        return [
            acta
            for acta in queryset
            if obtener_cargo_jefatura_carrera_para_acta(self.request.user, acta)
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "titulo": "Consulta de actas de mi ámbito",
                "descripcion": (
                    "Consulta limitada a las actas de calificaciones correspondientes "
                    "a tu carrera o unidad organizacional."
                ),
            }
        )
        return context


class JefaturaPlaneacionConsultaActasView(ActaQuerysetMixin, ListView):
    template_name = "evaluacion/consulta_actas.html"
    context_object_name = "actas"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not puede_consultar_actas_planeacion(request.user):
            raise PermissionDenied("No tienes permiso para consultar actas.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if usuario_es_admin_soporte(self.request.user):
            return queryset
        return [
            acta
            for acta in queryset
            if obtener_cargo_jefatura_planeacion_para_acta(self.request.user, acta)
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "titulo": "Consulta de actas de Planeación y Evaluación",
                "descripcion": (
                    "Consulta solo lectura para jefatura de subsección de Planeación "
                    "y Evaluación. No valida, remite, formaliza ni modifica actas."
                ),
            }
        )
        return context


class ValidarActaCarreraView(ActaQuerysetMixin, View):
    def post(self, request, pk):
        acta = get_object_or_404(self.get_queryset(), pk=pk)
        if not puede_validar_acta_carrera(request.user, acta):
            raise PermissionDenied("No tienes permiso para validar esta acta.")
        try:
            validar_acta_jefatura_carrera(
                acta,
                request.user,
                ip_origen=ip_origen_request(request),
            )
            messages.success(request, "Acta validada por jefatura de carrera.")
        except ValidationError as error:
            for mensaje in mensajes_validation_error(error):
                messages.error(request, mensaje)
        return redirect("evaluacion:acta-detalle", pk=acta.pk)


class JefaturaAcademicaActasPendientesView(ActaQuerysetMixin, ListView):
    template_name = "evaluacion/jefatura_academica_actas.html"
    context_object_name = "actas"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not puede_formalizar_acta_academica(request.user):
            raise PermissionDenied("No tienes permiso para formalizar actas.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(estado_acta=Acta.ESTADO_VALIDADO_JEFATURA_CARRERA)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["actas_formalizadas"] = (
            super()
            .get_queryset()
            .filter(estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA)
        )
        return context


class FormalizarActaView(ActaQuerysetMixin, View):
    def post(self, request, pk):
        acta = get_object_or_404(self.get_queryset(), pk=pk)
        if not puede_formalizar_acta_academica(request.user):
            raise PermissionDenied("No tienes permiso para formalizar esta acta.")
        try:
            formalizar_acta_jefatura_academica(
                acta,
                request.user,
                ip_origen=ip_origen_request(request),
            )
            messages.success(request, "Acta formalizada por jefatura académica.")
        except ValidationError as error:
            for mensaje in mensajes_validation_error(error):
                messages.error(request, mensaje)
        return redirect("evaluacion:acta-detalle", pk=acta.pk)


class DiscenteActasPublicadasView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy("usuarios:login")
    template_name = "evaluacion/discente_actas.html"
    context_object_name = "detalles"

    def get_queryset(self):
        discente = Discente.objects.filter(usuario=self.request.user, activo=True).first()
        if not discente:
            return DetalleActa.objects.none()
        return DetalleActa.objects.filter(
            inscripcion_materia__discente=discente,
            acta__estado_acta__in=[
                Acta.ESTADO_PUBLICADO_DISCENTE,
                Acta.ESTADO_REMITIDO_JEFATURA_CARRERA,
                Acta.ESTADO_VALIDADO_JEFATURA_CARRERA,
                Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            ],
        ).select_related(
            "acta",
            "acta__asignacion_docente",
            "acta__asignacion_docente__programa_asignatura",
            "acta__asignacion_docente__programa_asignatura__materia",
        )


class DiscenteDetalleActaView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy("usuarios:login")
    model = DetalleActa
    template_name = "evaluacion/discente_acta_detalle.html"
    context_object_name = "detalle"

    def get_queryset(self):
        return DetalleActa.objects.select_related(
            "acta",
            "acta__asignacion_docente",
            "acta__asignacion_docente__programa_asignatura",
            "acta__asignacion_docente__programa_asignatura__materia",
            "inscripcion_materia",
            "inscripcion_materia__discente",
            "inscripcion_materia__discente__usuario",
        ).prefetch_related("calificaciones_componentes", "conformidades")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.object = self.get_object()
        if self.object.inscripcion_materia.discente.usuario_id != request.user.id:
            raise PermissionDenied("No tienes permiso para consultar este detalle.")
        if self.object.acta.estado_acta == Acta.ESTADO_BORRADOR_DOCENTE:
            raise PermissionDenied("El acta aún no está publicada.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form") or ConformidadDiscenteForm()
        context["conformidad_vigente"] = self.object.conformidades.filter(vigente=True).first()
        context["puede_registrar_conformidad"] = (
            self.object.acta.estado_acta == Acta.ESTADO_PUBLICADO_DISCENTE
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.inscripcion_materia.discente.usuario_id != request.user.id:
            raise PermissionDenied("No tienes permiso para registrar conformidad.")
        form = ConformidadDiscenteForm(request.POST)
        if form.is_valid():
            try:
                registrar_conformidad_discente(
                    self.object,
                    request.user,
                    form.cleaned_data["estado_conformidad"],
                    form.cleaned_data["comentario"],
                )
                messages.success(request, "Conformidad informativa registrada.")
                return redirect("evaluacion:discente-acta-detalle", pk=self.object.pk)
            except ValidationError as error:
                for mensaje in mensajes_validation_error(error):
                    messages.error(request, mensaje)
        return render(request, self.template_name, self.get_context_data(form=form))


class EstadisticaActasView(ActaQuerysetMixin, ListView):
    template_name = "evaluacion/consulta_actas.html"
    context_object_name = "actas"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not puede_consultar_estados_actas(request.user):
            raise PermissionDenied("No tienes permiso para consultar estados de actas.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "titulo": "Consulta de actas de calificaciones",
                "descripcion": (
                    "Consulta general de estados para Estadística. "
                    "Esta vista no firma ni formaliza actas."
                ),
            }
        )
        return context
