from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from evaluacion.models import Acta, ComponenteEvaluacion, DetalleActa
from catalogos.models import ProgramaAsignatura
from relaciones.models import Discente, InscripcionMateria

from .models import (
    CALIFICACION_APROBATORIA,
    CatalogoResultadoAcademico,
    CatalogoSituacionAcademica,
    EventoSituacionAcademica,
    Extraordinario,
)


SITUACIONES_BASE = {
    CatalogoSituacionAcademica.CLAVE_ACTIVO: "Activo",
    CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL: "Baja temporal",
    CatalogoSituacionAcademica.CLAVE_BAJA_DEFINITIVA: "Baja definitiva",
    CatalogoSituacionAcademica.CLAVE_REINGRESO: "Reingreso",
    CatalogoSituacionAcademica.CLAVE_EGRESADO: "Egresado",
}

RESULTADOS_BASE = {
    CatalogoResultadoAcademico.CLAVE_APROBADO: "Aprobado",
    CatalogoResultadoAcademico.CLAVE_REPROBADO: "Reprobado",
    CatalogoResultadoAcademico.CLAVE_APROBADO_EXTRAORDINARIO: "Aprobado por extraordinario",
    CatalogoResultadoAcademico.CLAVE_EE: "Marca EE",
    CatalogoResultadoAcademico.CLAVE_ACREDITADA: "Acreditada",
    CatalogoResultadoAcademico.CLAVE_APROBADO_NO_NUMERICO: "Aprobado no numérico",
    CatalogoResultadoAcademico.CLAVE_EXCEPTUADO: "Exceptuado",
}


@dataclass
class ResultadoHistorial:
    inscripcion: InscripcionMateria
    tipo_resultado: str
    calificacion: Decimal | None
    codigo_resultado: str
    codigo_marca: str
    calificacion_ordinaria: Decimal | None = None
    codigo_resultado_ordinario: str = ""
    extraordinario: Extraordinario | None = None


@dataclass
class KardexAsignatura:
    inscripcion: InscripcionMateria
    anio_formacion: int
    semestre_numero: int
    clave_materia: str
    nombre_materia: str
    calificacion: Decimal | None
    calificacion_visible: Decimal | None
    calificacion_letra: str
    codigo_resultado: str
    resultado_no_numerico: str
    codigo_marca: str
    marca_ee: bool
    es_numerica: bool


@dataclass
class KardexAnio:
    anio_formacion: int
    asignaturas: list[KardexAsignatura] = field(default_factory=list)
    promedio_anual: Decimal | None = None


@dataclass
class KardexOficial:
    discente: Discente
    carrera: object
    plan_estudios: object
    antiguedad: object
    situacion_actual: str
    anios: list[KardexAnio]


def asegurar_catalogos_base():
    for clave, nombre in SITUACIONES_BASE.items():
        CatalogoSituacionAcademica.objects.get_or_create(
            clave=clave,
            defaults={"nombre": nombre, "activo": True},
        )
    for clave, nombre in RESULTADOS_BASE.items():
        CatalogoResultadoAcademico.objects.get_or_create(
            clave=clave,
            defaults={"nombre": nombre, "activo": True},
        )


def obtener_situacion(clave):
    asegurar_catalogos_base()
    return CatalogoSituacionAcademica.objects.get(clave=clave)


def actualizar_situacion_actual_discente(discente, situacion_clave):
    if situacion_clave == CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL:
        discente.situacion_actual = Discente.SITUACION_BAJA_TEMPORAL
    elif situacion_clave == CatalogoSituacionAcademica.CLAVE_BAJA_DEFINITIVA:
        discente.situacion_actual = Discente.SITUACION_BAJA_DEFINITIVA
    elif situacion_clave in (
        CatalogoSituacionAcademica.CLAVE_ACTIVO,
        CatalogoSituacionAcademica.CLAVE_REINGRESO,
    ):
        discente.situacion_actual = Discente.SITUACION_REGULAR
    elif situacion_clave == CatalogoSituacionAcademica.CLAVE_EGRESADO:
        discente.situacion_actual = Discente.SITUACION_EGRESADO
    discente.save(update_fields=["situacion_actual"])


@transaction.atomic
def registrar_baja_temporal(
    discente,
    fecha_inicio=None,
    periodo=None,
    motivo="",
    registrado_por=None,
    inscripcion_materia=None,
):
    evento = EventoSituacionAcademica.objects.create(
        discente=discente,
        situacion=obtener_situacion(CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL),
        fecha_inicio=fecha_inicio or timezone.localdate(),
        periodo=periodo,
        motivo=motivo,
        registrado_por=registrado_por,
        inscripcion_materia=inscripcion_materia,
    )
    actualizar_situacion_actual_discente(discente, CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL)
    return evento


@transaction.atomic
def registrar_reingreso(discente, fecha_inicio=None, periodo=None, motivo="", registrado_por=None):
    fecha_inicio = fecha_inicio or timezone.localdate()
    baja_abierta = (
        EventoSituacionAcademica.objects.select_for_update()
        .filter(
            discente=discente,
            situacion__clave=CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL,
            fecha_fin__isnull=True,
        )
        .order_by("-fecha_inicio", "-creado_en")
        .first()
    )
    if baja_abierta:
        baja_abierta.fecha_fin = fecha_inicio
        baja_abierta.save(update_fields=["fecha_fin", "actualizado_en"])

    evento = EventoSituacionAcademica.objects.create(
        discente=discente,
        situacion=obtener_situacion(CatalogoSituacionAcademica.CLAVE_REINGRESO),
        fecha_inicio=fecha_inicio,
        periodo=periodo,
        motivo=motivo,
        registrado_por=registrado_por,
    )
    actualizar_situacion_actual_discente(discente, CatalogoSituacionAcademica.CLAVE_REINGRESO)
    return evento


@transaction.atomic
def registrar_evento_situacion(
    discente,
    situacion,
    fecha_inicio=None,
    fecha_fin=None,
    periodo=None,
    motivo="",
    registrado_por=None,
    inscripcion_materia=None,
):
    if situacion.clave == CatalogoSituacionAcademica.CLAVE_BAJA_TEMPORAL:
        return registrar_baja_temporal(
            discente=discente,
            fecha_inicio=fecha_inicio,
            periodo=periodo,
            motivo=motivo,
            registrado_por=registrado_por,
            inscripcion_materia=inscripcion_materia,
        )
    if situacion.clave == CatalogoSituacionAcademica.CLAVE_REINGRESO:
        return registrar_reingreso(
            discente=discente,
            fecha_inicio=fecha_inicio,
            periodo=periodo,
            motivo=motivo,
            registrado_por=registrado_por,
        )

    evento = EventoSituacionAcademica.objects.create(
        discente=discente,
        situacion=situacion,
        fecha_inicio=fecha_inicio or timezone.localdate(),
        fecha_fin=fecha_fin,
        periodo=periodo,
        motivo=motivo,
        registrado_por=registrado_por,
        inscripcion_materia=inscripcion_materia,
    )
    actualizar_situacion_actual_discente(discente, situacion.clave)
    return evento


def inscripciones_con_acta_final_formalizada():
    return (
        InscripcionMateria.objects.filter(
            detalles_acta__acta__corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
            detalles_acta__acta__estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
            cerrado_en__isnull=False,
        )
        .select_related(
            "discente",
            "discente__usuario",
            "asignacion_docente",
            "asignacion_docente__grupo_academico",
            "asignacion_docente__grupo_academico__periodo",
            "asignacion_docente__programa_asignatura",
            "asignacion_docente__programa_asignatura__materia",
            "asignacion_docente__programa_asignatura__plan_estudios",
        )
        .distinct()
    )


def inscripciones_elegibles_extraordinario():
    return inscripciones_con_acta_final_formalizada().filter(
        calificacion_final__lt=CALIFICACION_APROBATORIA
    ).exclude(extraordinario__isnull=False)


@transaction.atomic
def registrar_extraordinario(
    inscripcion_materia,
    calificacion,
    fecha_aplicacion=None,
    registrado_por=None,
):
    if not registrado_por:
        raise ValidationError("El usuario registrador es obligatorio.")

    extraordinario = Extraordinario.objects.create(
        inscripcion_materia=inscripcion_materia,
        fecha_aplicacion=fecha_aplicacion or timezone.localdate(),
        calificacion=calificacion,
        registrado_por=registrado_por,
    )

    inscripcion_materia.calificacion_final = extraordinario.calificacion
    inscripcion_materia.codigo_resultado_oficial = (
        CatalogoResultadoAcademico.CLAVE_APROBADO
        if extraordinario.aprobado
        else CatalogoResultadoAcademico.CLAVE_REPROBADO
    )
    inscripcion_materia.codigo_marca = extraordinario.codigo_marca
    inscripcion_materia.save(
        update_fields=[
            "calificacion_final",
            "codigo_resultado_oficial",
            "codigo_marca",
        ]
    )

    if not extraordinario.aprobado:
        registrar_baja_temporal(
            discente=inscripcion_materia.discente,
            fecha_inicio=extraordinario.fecha_aplicacion,
            periodo=inscripcion_materia.asignacion_docente.periodo,
            motivo="Extraordinario no aprobado.",
            registrado_por=registrado_por,
            inscripcion_materia=inscripcion_materia,
        )

    return extraordinario


def construir_historial_discente(discente):
    inscripciones = inscripciones_con_acta_final_formalizada().filter(discente=discente)
    resultados = []

    for inscripcion in inscripciones:
        extraordinario = getattr(inscripcion, "extraordinario", None)
        if extraordinario:
            resultados.append(
                ResultadoHistorial(
                    inscripcion=inscripcion,
                    tipo_resultado="EXTRAORDINARIO",
                    calificacion=inscripcion.calificacion_final,
                    codigo_resultado=inscripcion.codigo_resultado_oficial or "",
                    codigo_marca=inscripcion.codigo_marca or "",
                    calificacion_ordinaria=extraordinario.calificacion_ordinaria,
                    codigo_resultado_ordinario=extraordinario.codigo_resultado_ordinario,
                    extraordinario=extraordinario,
                )
            )
        else:
            resultados.append(
                ResultadoHistorial(
                    inscripcion=inscripcion,
                    tipo_resultado="ORDINARIO",
                    calificacion=inscripcion.calificacion_final,
                    codigo_resultado=inscripcion.codigo_resultado_oficial or "",
                    codigo_marca=inscripcion.codigo_marca or "",
                )
            )

    eventos = (
        EventoSituacionAcademica.objects.filter(discente=discente)
        .select_related("situacion", "periodo", "inscripcion_materia")
        .order_by("-fecha_inicio", "-creado_en")
    )

    return {
        "discente": discente,
        "resultados": resultados,
        "eventos": eventos,
    }


def redondear_visual_un_decimal(valor):
    if valor is None:
        return None
    return Decimal(valor).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def calificacion_a_letra(calificacion):
    if calificacion is None:
        return ""

    valor = redondear_visual_un_decimal(calificacion)
    entero = int(valor)
    decimal = int((valor - Decimal(entero)) * Decimal("10"))
    numeros = {
        0: "CERO",
        1: "UNO",
        2: "DOS",
        3: "TRES",
        4: "CUATRO",
        5: "CINCO",
        6: "SEIS",
        7: "SIETE",
        8: "OCHO",
        9: "NUEVE",
        10: "DIEZ",
    }

    if decimal == 0:
        return numeros.get(entero, str(entero))
    return f"{numeros.get(entero, str(entero))} PUNTO {numeros.get(decimal, str(decimal))}"


def _resultado_no_numerico(codigo_resultado, calificacion):
    if calificacion is not None:
        return ""

    resultados_no_numericos = {
        CatalogoResultadoAcademico.CLAVE_ACREDITADA,
        CatalogoResultadoAcademico.CLAVE_APROBADO,
        CatalogoResultadoAcademico.CLAVE_APROBADO_NO_NUMERICO,
        CatalogoResultadoAcademico.CLAVE_EXCEPTUADO,
    }
    return codigo_resultado if codigo_resultado in resultados_no_numericos else ""


def _asignatura_kardex_desde_resultado(resultado):
    inscripcion = resultado.inscripcion
    asignacion = inscripcion.asignacion_docente
    programa = asignacion.programa_asignatura
    materia = programa.materia
    semestre_numero = asignacion.grupo_academico.semestre_numero or programa.semestre_numero
    anio_formacion = ProgramaAsignatura.calculate_anio_formacion(semestre_numero)
    calificacion = resultado.calificacion
    codigo_resultado = resultado.codigo_resultado or ""
    codigo_marca = resultado.codigo_marca or ""
    resultado_no_numerico = _resultado_no_numerico(codigo_resultado, calificacion)
    calificacion_visible = redondear_visual_un_decimal(calificacion)

    return KardexAsignatura(
        inscripcion=inscripcion,
        anio_formacion=anio_formacion,
        semestre_numero=semestre_numero,
        clave_materia=materia.clave,
        nombre_materia=materia.nombre,
        calificacion=calificacion,
        calificacion_visible=calificacion_visible,
        calificacion_letra=calificacion_a_letra(calificacion),
        codigo_resultado=codigo_resultado,
        resultado_no_numerico=resultado_no_numerico,
        codigo_marca=codigo_marca,
        marca_ee=codigo_marca == CatalogoResultadoAcademico.CLAVE_EE,
        es_numerica=calificacion is not None,
    )


def _calcular_promedio_anual(asignaturas):
    numericas = [asignatura.calificacion for asignatura in asignaturas if asignatura.es_numerica]
    if not numericas:
        return None
    promedio = sum(numericas, Decimal("0.0")) / Decimal(len(numericas))
    return redondear_visual_un_decimal(promedio)


def construir_kardex_discente(discente):
    historial = construir_historial_discente(discente)
    asignaturas = [
        _asignatura_kardex_desde_resultado(resultado)
        for resultado in historial["resultados"]
    ]
    asignaturas.sort(
        key=lambda item: (
            item.anio_formacion,
            item.semestre_numero,
            item.clave_materia,
            item.nombre_materia,
        )
    )

    anios_por_numero = {}
    for asignatura in asignaturas:
        anio = anios_por_numero.setdefault(
            asignatura.anio_formacion,
            KardexAnio(anio_formacion=asignatura.anio_formacion),
        )
        anio.asignaturas.append(asignatura)

    anios = []
    for anio in sorted(anios_por_numero.values(), key=lambda item: item.anio_formacion):
        anio.promedio_anual = _calcular_promedio_anual(anio.asignaturas)
        anios.append(anio)

    return KardexOficial(
        discente=discente,
        carrera=discente.plan_estudios.carrera,
        plan_estudios=discente.plan_estudios,
        antiguedad=discente.antiguedad,
        situacion_actual=discente.get_situacion_actual_display(),
        anios=anios,
    )


class ServicioKardex:
    @staticmethod
    def construir_por_discente(discente):
        return construir_kardex_discente(discente)
