from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from relaciones.models import InscripcionMateria
from relaciones.permisos import usuario_es_admin_soporte
from usuarios.models import AsignacionCargo

from .models import (
    Acta,
    CalificacionComponente,
    CapturaCalificacionPreliminar,
    ConformidadDiscente,
    DetalleActa,
    ComponenteEvaluacion,
    EsquemaEvaluacion,
    ValidacionActa,
)


CALIFICACION_APROBATORIA = Decimal("6.0")
UMBRAL_EXENCION_INSTITUCIONAL = Decimal("9.0")


def redondear_visualizacion_un_decimal(valor):
    if valor is None:
        return None
    return Decimal(valor).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def normalizar_decimal_6(valor):
    if valor is None:
        return None
    return Decimal(valor).quantize(Decimal("0.000001"))


class ServicioCalculoAcademico:
    def __init__(self, inscripcion_materia):
        self.inscripcion_materia = inscripcion_materia
        self.esquema = self.obtener_esquema_activo(inscripcion_materia.programa_asignatura)
        self.componentes = list(
            self.esquema.componentes.all().order_by("corte_codigo", "orden", "pk")
        )
        self.capturas = {
            captura.componente_id: captura
            for captura in CapturaCalificacionPreliminar.objects.filter(
                inscripcion_materia=inscripcion_materia,
                componente__esquema=self.esquema,
            )
        }

    @staticmethod
    def obtener_esquema_activo(programa_asignatura):
        esquema = (
            EsquemaEvaluacion.objects.filter(
                programa_asignatura=programa_asignatura,
                activo=True,
            )
            .prefetch_related("componentes")
            .order_by("-id")
            .first()
        )
        if not esquema:
            raise ValidationError(
                "No existe un esquema de evaluación activo para este programa de asignatura."
            )
        return esquema

    def _componentes_corte(self, corte_codigo):
        return [
            componente
            for componente in self.componentes
            if componente.corte_codigo == corte_codigo
        ]

    def _valor_componente(self, componente):
        captura = self.capturas.get(componente.id)
        if not captura:
            return None
        return captura.valor

    def calcular_resultado_corte(
        self,
        corte_codigo,
        promedio_parciales=None,
        sustituir_examen=False,
    ):
        componentes = self._componentes_corte(corte_codigo)
        detalle = []
        total = Decimal("0.00")
        completo = bool(componentes)

        for componente in componentes:
            valor_capturado = self._valor_componente(componente)
            sustituido_por_exencion = (
                sustituir_examen
                and componente.corte_codigo == ComponenteEvaluacion.CORTE_FINAL
                and componente.es_examen
            )
            valor = promedio_parciales if sustituido_por_exencion else valor_capturado
            if valor is None:
                completo = False
                ponderado = None
            else:
                ponderado = Decimal(valor) * componente.porcentaje / Decimal("100")
                total += ponderado

            detalle.append(
                {
                    "componente": componente,
                    "valor": valor,
                    "valor_capturado": valor_capturado,
                    "porcentaje": componente.porcentaje,
                    "ponderado": ponderado,
                    "sustituido_por_exencion": sustituido_por_exencion,
                }
            )

        return {
            "corte": corte_codigo,
            "componentes": detalle,
            "completo": completo,
            "resultado": total if completo else None,
            "resultado_visual": redondear_visualizacion_un_decimal(total) if completo else None,
        }

    def _cortes_parciales(self):
        cortes = [ComponenteEvaluacion.CORTE_P1]
        if self.esquema.num_parciales >= EsquemaEvaluacion.PARCIALES_2:
            cortes.append(ComponenteEvaluacion.CORTE_P2)
        if self.esquema.num_parciales >= EsquemaEvaluacion.PARCIALES_3:
            cortes.append(ComponenteEvaluacion.CORTE_P3)
        return cortes

    def _calcular_promedio_parciales(self, resultados_corte):
        resultados = []
        for corte in self._cortes_parciales():
            resultado = resultados_corte[corte]["resultado"]
            if resultado is None:
                return None
            resultados.append(resultado)
        return sum(resultados) / Decimal(len(resultados))

    def _exencion_aplica(self, promedio_parciales):
        if promedio_parciales is None:
            return False
        tiene_examen_final = any(
            componente.corte_codigo == ComponenteEvaluacion.CORTE_FINAL and componente.es_examen
            for componente in self.componentes
        )
        return (
            self.esquema.permite_exencion
            and self.esquema.num_parciales in (
                EsquemaEvaluacion.PARCIALES_2,
                EsquemaEvaluacion.PARCIALES_3,
            )
            and promedio_parciales
            >= (self.esquema.umbral_exencion or UMBRAL_EXENCION_INSTITUCIONAL)
            and tiene_examen_final
        )

    def calcular(self):
        resultados_corte = {}
        for corte in self._cortes_parciales():
            resultados_corte[corte] = self.calcular_resultado_corte(corte)

        promedio_parciales = self._calcular_promedio_parciales(resultados_corte)
        exencion_aplica = self._exencion_aplica(promedio_parciales)
        resultado_final = self.calcular_resultado_corte(
            ComponenteEvaluacion.CORTE_FINAL,
            promedio_parciales=promedio_parciales,
            sustituir_examen=exencion_aplica,
        )
        resultados_corte[ComponenteEvaluacion.CORTE_FINAL] = resultado_final

        calificacion_final_preliminar = None
        calificacion_final_preliminar_visual = None
        resultado_preliminar = "INCOMPLETO"
        if promedio_parciales is not None and resultado_final["resultado"] is not None:
            calificacion_final_preliminar = (
                promedio_parciales * self.esquema.peso_parciales
                + resultado_final["resultado"] * self.esquema.peso_final
            ) / Decimal("100")
            calificacion_final_preliminar_visual = redondear_visualizacion_un_decimal(
                calificacion_final_preliminar
            )
            resultado_preliminar = (
                "APROBATORIO"
                if calificacion_final_preliminar >= CALIFICACION_APROBATORIA
                else "REPROBATORIO"
            )

        return {
            "inscripcion": self.inscripcion_materia,
            "esquema": self.esquema,
            "cortes": resultados_corte,
            "promedio_parciales": promedio_parciales,
            "promedio_parciales_visual": redondear_visualizacion_un_decimal(promedio_parciales),
            "exencion_aplica": exencion_aplica,
            "resultado_final": resultado_final["resultado"],
            "resultado_final_visual": resultado_final["resultado_visual"],
            "calificacion_final_preliminar": calificacion_final_preliminar,
            "calificacion_final_preliminar_visual": calificacion_final_preliminar_visual,
            "resultado_preliminar": resultado_preliminar,
        }


def _inscripciones_activas(asignacion_docente):
    return asignacion_docente.inscripciones_materia.filter(
        estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA
    ).select_related("discente", "discente__usuario")


def _snapshot_acta(acta, esquema):
    acta.esquema = esquema
    acta.esquema_version_snapshot = esquema.version
    acta.peso_parciales_snapshot = esquema.peso_parciales
    acta.peso_final_snapshot = esquema.peso_final
    acta.umbral_exencion_snapshot = esquema.umbral_exencion


def obtener_acta_activa(asignacion_docente, corte_codigo):
    return (
        Acta.objects.filter(
            asignacion_docente=asignacion_docente,
            corte_codigo=corte_codigo,
        )
        .exclude(estado_acta=Acta.ESTADO_ARCHIVADO)
        .first()
    )


@transaction.atomic
def crear_o_regenerar_borrador_acta(asignacion_docente, corte_codigo, usuario):
    esquema = ServicioCalculoAcademico.obtener_esquema_activo(
        asignacion_docente.programa_asignatura
    )
    corte_codigo = corte_codigo.upper()
    if corte_codigo not in esquema.cortes_esperados():
        raise ValidationError("El corte solicitado no aplica al esquema activo.")

    inscripciones = list(_inscripciones_activas(asignacion_docente))
    if not inscripciones:
        raise ValidationError("No existen discentes inscritos para generar el acta.")

    acta = obtener_acta_activa(asignacion_docente, corte_codigo)
    if acta and acta.estado_acta != Acta.ESTADO_BORRADOR_DOCENTE:
        raise ValidationError("Solo se puede regenerar un acta en estado borrador docente.")

    if not acta:
        acta = Acta(
            asignacion_docente=asignacion_docente,
            corte_codigo=corte_codigo,
            creado_por=usuario,
        )
    _snapshot_acta(acta, esquema)
    acta.estado_acta = Acta.ESTADO_BORRADOR_DOCENTE
    acta.save()

    acta.detalles.all().delete()
    for inscripcion in inscripciones:
        resultado = ServicioCalculoAcademico(inscripcion).calcular()
        corte = resultado["cortes"][corte_codigo]
        detalle = DetalleActa.objects.create(
            acta=acta,
            inscripcion_materia=inscripcion,
            resultado_corte=normalizar_decimal_6(corte["resultado"]),
            resultado_corte_visible=corte["resultado_visual"],
            promedio_parciales=normalizar_decimal_6(resultado["promedio_parciales"]),
            promedio_parciales_visible=resultado["promedio_parciales_visual"],
            resultado_final_preliminar=normalizar_decimal_6(
                resultado["calificacion_final_preliminar"]
            ),
            resultado_final_preliminar_visible=resultado[
                "calificacion_final_preliminar_visual"
            ],
            resultado_preliminar=resultado["resultado_preliminar"],
            exencion_aplica=resultado["exencion_aplica"],
            completo=bool(corte["completo"]),
        )
        for componente_detalle in corte["componentes"]:
            componente = componente_detalle["componente"]
            CalificacionComponente.objects.create(
                detalle=detalle,
                componente=componente,
                componente_nombre_snapshot=componente.nombre,
                componente_porcentaje_snapshot=componente.porcentaje,
                componente_es_examen_snapshot=componente.es_examen,
                valor_capturado=componente_detalle["valor_capturado"],
                valor_calculado=normalizar_decimal_6(componente_detalle["ponderado"]),
                sustituido_por_exencion=componente_detalle["sustituido_por_exencion"],
            )
    return acta


def validar_acta_completa(acta):
    errores = []
    detalles = list(
        acta.detalles.prefetch_related("calificaciones_componentes").select_related(
            "inscripcion_materia", "inscripcion_materia__discente"
        )
    )
    if not detalles:
        errores.append("El acta no tiene detalles generados.")

    for detalle in detalles:
        if not detalle.completo:
            errores.append(
                f"Faltan capturas requeridas para {detalle.inscripcion_materia.discente}."
            )
        for calificacion in detalle.calificaciones_componentes.all():
            if calificacion.valor_capturado is not None and (
                calificacion.valor_capturado < Decimal("0.0")
                or calificacion.valor_capturado > Decimal("10.0")
            ):
                errores.append(
                    "Existe una calificación fuera del rango 0.0 a 10.0 "
                    f"en {detalle.inscripcion_materia.discente}."
                )
        if detalle.resultado_corte_visible is None:
            errores.append(
                f"No existe resultado visible calculado para {detalle.inscripcion_materia.discente}."
            )

    if errores:
        raise ValidationError(errores)


def registrar_validacion_acta(acta, usuario, etapa, accion, asignacion_cargo=None, ip_origen=None):
    return ValidacionActa.objects.create(
        acta=acta,
        usuario=usuario,
        asignacion_cargo=asignacion_cargo,
        etapa_validacion=etapa,
        accion=accion,
        ip_origen=ip_origen,
    )


@transaction.atomic
def publicar_acta(acta, usuario, ip_origen=None):
    if acta.estado_acta != Acta.ESTADO_BORRADOR_DOCENTE:
        raise ValidationError("Solo se puede publicar un acta en borrador docente.")
    validar_acta_completa(acta)
    acta.estado_acta = Acta.ESTADO_PUBLICADO_DISCENTE
    acta.publicada_en = timezone.now()
    acta.save(update_fields=["estado_acta", "publicada_en", "actualizado_en"])
    registrar_validacion_acta(
        acta,
        usuario,
        ValidacionActa.ETAPA_DOCENTE,
        ValidacionActa.ACCION_PUBLICA,
        ip_origen=ip_origen,
    )
    return acta


@transaction.atomic
def remitir_acta(acta, usuario, ip_origen=None):
    if acta.estado_acta != Acta.ESTADO_PUBLICADO_DISCENTE:
        raise ValidationError("Solo se puede remitir un acta publicada a discentes.")
    acta.estado_acta = Acta.ESTADO_REMITIDO_JEFATURA_CARRERA
    acta.remitida_en = timezone.now()
    acta.save(update_fields=["estado_acta", "remitida_en", "actualizado_en"])
    registrar_validacion_acta(
        acta,
        usuario,
        ValidacionActa.ETAPA_DOCENTE,
        ValidacionActa.ACCION_REMITE,
        ip_origen=ip_origen,
    )
    return acta


def _cargos_vigentes_usuario(usuario, codigos):
    hoy = timezone.localdate()
    return AsignacionCargo.objects.filter(
        Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
        Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
        usuario=usuario,
        activo=True,
        cargo_codigo__in=codigos,
    ).select_related("carrera", "unidad_organizacional")


def obtener_cargo_jefatura_carrera_para_acta(usuario, acta):
    carrera_id = acta.asignacion_docente.programa_asignatura.plan_estudios.carrera_id
    cargos = _cargos_vigentes_usuario(
        usuario,
        [AsignacionCargo.CARGO_JEFE_CARRERA, AsignacionCargo.CARGO_JEFE_SUB_EJEC_CTR],
    )
    for cargo in cargos:
        if cargo.carrera_id == carrera_id:
            return cargo
        if cargo.unidad_organizacional_id and cargo.unidad_organizacional.carrera_id == carrera_id:
            return cargo
    return None


def obtener_cargo_jefatura_planeacion_para_acta(usuario, acta):
    carrera_id = acta.asignacion_docente.programa_asignatura.plan_estudios.carrera_id
    cargos = _cargos_vigentes_usuario(
        usuario,
        [
            AsignacionCargo.CARGO_JEFE_SUBSECCION_PEDAGOGICA,
            AsignacionCargo.CARGO_JEFE_SUB_PLAN_EVAL,
        ],
    )
    for cargo in cargos:
        if cargo.carrera_id == carrera_id:
            return cargo
        if cargo.unidad_organizacional_id and cargo.unidad_organizacional.carrera_id == carrera_id:
            return cargo
    return None


def obtener_cargo_jefatura_academica(usuario):
    return _cargos_vigentes_usuario(
        usuario,
        [AsignacionCargo.CARGO_JEFE_ACADEMICO],
    ).first()


@transaction.atomic
def validar_acta_jefatura_carrera(acta, usuario, ip_origen=None):
    if acta.estado_acta != Acta.ESTADO_REMITIDO_JEFATURA_CARRERA:
        raise ValidationError("Solo se puede validar un acta remitida a jefatura de carrera.")

    cargo = None
    if not usuario_es_admin_soporte(usuario):
        cargo = obtener_cargo_jefatura_carrera_para_acta(usuario, acta)
        if not cargo:
            raise ValidationError("El usuario no tiene jefatura de carrera vigente para esta acta.")

    acta.estado_acta = Acta.ESTADO_VALIDADO_JEFATURA_CARRERA
    acta.save(update_fields=["estado_acta", "actualizado_en"])
    registrar_validacion_acta(
        acta,
        usuario,
        ValidacionActa.ETAPA_JEFATURA_CARRERA,
        ValidacionActa.ACCION_VALIDA,
        asignacion_cargo=cargo,
        ip_origen=ip_origen,
    )
    return acta


def _actualizar_campos_oficiales_final(acta):
    for detalle in acta.detalles.select_related("inscripcion_materia"):
        inscripcion = detalle.inscripcion_materia
        inscripcion.calificacion_final = detalle.resultado_final_preliminar_visible
        inscripcion.codigo_resultado_oficial = (
            "APROBADO"
            if detalle.resultado_preliminar == DetalleActa.RESULTADO_APROBATORIO
            else "REPROBADO"
        )
        inscripcion.codigo_marca = "EXENTO" if detalle.exencion_aplica else ""
        inscripcion.cerrado_en = timezone.now()
        inscripcion.save(
            update_fields=[
                "calificacion_final",
                "codigo_resultado_oficial",
                "codigo_marca",
                "cerrado_en",
            ]
        )


@transaction.atomic
def formalizar_acta_jefatura_academica(acta, usuario, ip_origen=None):
    if acta.estado_acta != Acta.ESTADO_VALIDADO_JEFATURA_CARRERA:
        raise ValidationError("Solo se puede formalizar un acta validada por jefatura de carrera.")
    if not acta.validaciones.filter(
        etapa_validacion=ValidacionActa.ETAPA_JEFATURA_CARRERA,
        accion=ValidacionActa.ACCION_VALIDA,
    ).exists():
        raise ValidationError("No se puede formalizar sin validación previa de jefatura de carrera.")

    cargo = None
    if not usuario_es_admin_soporte(usuario):
        cargo = obtener_cargo_jefatura_academica(usuario)
        if not cargo:
            raise ValidationError("El usuario no tiene jefatura académica vigente.")

    if acta.es_final:
        _actualizar_campos_oficiales_final(acta)

    acta.estado_acta = Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA
    acta.formalizada_en = timezone.now()
    acta.save(update_fields=["estado_acta", "formalizada_en", "actualizado_en"])
    registrar_validacion_acta(
        acta,
        usuario,
        ValidacionActa.ETAPA_JEFATURA_ACADEMICA,
        ValidacionActa.ACCION_FORMALIZA,
        asignacion_cargo=cargo,
        ip_origen=ip_origen,
    )
    return acta


@transaction.atomic
def registrar_conformidad_discente(detalle, usuario, estado_conformidad, comentario=""):
    if detalle.acta.estado_acta == Acta.ESTADO_BORRADOR_DOCENTE:
        raise ValidationError("El acta todavía no está publicada para discentes.")
    if detalle.acta.estado_acta != Acta.ESTADO_PUBLICADO_DISCENTE:
        raise ValidationError(
            "La conformidad quedó en solo lectura después de remitir el acta."
        )
    if detalle.inscripcion_materia.discente.usuario_id != usuario.id:
        raise ValidationError("Solo el discente titular puede registrar conformidad.")

    comentario = (comentario or "").strip()
    if estado_conformidad == ConformidadDiscente.ESTADO_INCONFORME and not comentario:
        raise ValidationError(
            "El comentario es obligatorio cuando se registra inconformidad."
        )

    ConformidadDiscente.objects.filter(
        detalle=detalle,
        discente=detalle.inscripcion_materia.discente,
        vigente=True,
    ).update(vigente=False, invalidado_en=timezone.now())

    return ConformidadDiscente.objects.create(
        detalle=detalle,
        discente=detalle.inscripcion_materia.discente,
        usuario=usuario,
        estado_conformidad=estado_conformidad,
        comentario=comentario,
    )
