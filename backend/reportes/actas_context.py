from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from statistics import multimode, pstdev

from django.db import models
from django.db.models import Prefetch
from django.utils import timezone

from evaluacion.models import Acta, CalificacionComponente, ComponenteEvaluacion, DetalleActa, ValidacionActa
from relaciones.models import AsignacionDocente, InscripcionMateria
from usuarios.models import AsignacionCargo

from .constantes import LUGAR_FECHA_INSTITUCIONAL, MESES_ES, NOMBRES_OFICIALES_CARRERA

CALIFICACION_APROBATORIA = Decimal("6.0")
DECIMAL_UN_DECIMAL = Decimal("0.1")


@dataclass(frozen=True)
class FirmaActa:
    etiqueta: str
    nombre: str = "Pendiente"
    cargo: str = ""
    estado: str = ""
    cedula: str = ""


@dataclass(frozen=True)
class ComponenteActa:
    id: int
    nombre: str
    porcentaje: Decimal
    es_examen: bool = False

    @property
    def encabezado(self):
        porcentaje = self.porcentaje.quantize(Decimal("0.01"))
        if porcentaje == porcentaje.to_integral_value():
            porcentaje_texto = str(int(porcentaje))
        else:
            porcentaje_texto = str(porcentaje).rstrip("0").rstrip(".")
        return f"{self.nombre} {porcentaje_texto}%"


@dataclass(frozen=True)
class FilaActaCorte:
    numero: int
    grado_empleo: str
    nombre: str
    componentes: list
    calificacion_final: Decimal | None
    firma_conformidad: str = ""


@dataclass(frozen=True)
class FilaActaCalificacionFinal:
    numero: int
    grado_empleo: str
    nombre: str
    parcial_1: Decimal | None
    parcial_2: Decimal | None
    parcial_3: Decimal | None
    evaluacion_final: Decimal | None
    calificacion_final: Decimal | None
    firma_conformidad: str = ""


@dataclass(frozen=True)
class EstadisticosActa:
    alumnos_reprobados: int | None = None
    media: Decimal | None = None
    moda: Decimal | None = None
    desviacion_estandar: Decimal | None = None


@dataclass(frozen=True)
class ContextoActa:
    titulo: str
    tipo_documento: str
    carrera: str
    unidad_aprendizaje: str
    docente: str
    grupo: str
    ciclo_escolar: str
    semestre: str
    evaluacion: str
    estado_documental: str
    marca_no_oficial: str
    lugar_fecha: str
    causas_reprobacion: str
    sugerencias: str
    firmas: list[FirmaActa]
    estadisticos: EstadisticosActa
    componentes: list[ComponenteActa] = field(default_factory=list)
    filas_corte: list[FilaActaCorte] = field(default_factory=list)
    filas_final: list[FilaActaCalificacionFinal] = field(default_factory=list)
    nota_exencion: str = ""

    @property
    def es_calificacion_final(self):
        return bool(self.filas_final)


def decimal_un_decimal(valor):
    if valor is None:
        return None
    return Decimal(valor).quantize(DECIMAL_UN_DECIMAL, rounding=ROUND_HALF_UP)


def decimal_a_texto(valor, default="N/A"):
    if valor is None:
        return default
    return f"{decimal_un_decimal(valor):.1f}"


def construir_lugar_fecha(fecha):
    fecha = timezone.localtime(fecha).date() if hasattr(fecha, "hour") else fecha
    if not fecha:
        fecha = timezone.localdate()
    mes = MESES_ES.get(fecha.month, str(fecha.month))
    return f"{LUGAR_FECHA_INSTITUCIONAL}, a {fecha.day} de {mes} de {fecha.year}."


def calcular_estadisticos(valores):
    valores_validos = [Decimal(valor) for valor in valores if valor is not None]
    if not valores_validos:
        return EstadisticosActa()

    reprobados = sum(1 for valor in valores_validos if valor < CALIFICACION_APROBATORIA)
    media = sum(valores_validos) / Decimal(len(valores_validos))
    modos = multimode(valores_validos)
    moda = modos[0] if modos else None
    desviacion = Decimal(str(pstdev([float(valor) for valor in valores_validos]))) if len(valores_validos) > 1 else Decimal("0")
    return EstadisticosActa(
        alumnos_reprobados=reprobados,
        media=decimal_un_decimal(media),
        moda=decimal_un_decimal(moda),
        desviacion_estandar=decimal_un_decimal(desviacion),
    )


def acta_queryset_base():
    return Acta.objects.select_related(
        "asignacion_docente__usuario_docente__grado_empleo",
        "asignacion_docente__grupo_academico__periodo",
        "asignacion_docente__programa_asignatura__materia",
        "asignacion_docente__programa_asignatura__plan_estudios__carrera",
        "esquema",
    ).prefetch_related(
        Prefetch(
            "detalles",
            queryset=DetalleActa.objects.select_related(
                "inscripcion_materia__discente__usuario__grado_empleo",
            ).prefetch_related(
                Prefetch(
                    "calificaciones_componentes",
                    queryset=CalificacionComponente.objects.select_related("componente").order_by(
                        "componente__orden",
                        "componente_id",
                    ),
                )
            ),
        ),
        "validaciones__usuario__grado_empleo",
        "validaciones__asignacion_cargo",
    )


def asignacion_queryset_base():
    return AsignacionDocente.objects.select_related(
        "usuario_docente__grado_empleo",
        "grupo_academico__periodo",
        "programa_asignatura__materia",
        "programa_asignatura__plan_estudios__carrera",
    ).prefetch_related(
        Prefetch(
            "inscripciones_materia",
            queryset=InscripcionMateria.objects.select_related("discente__usuario__grado_empleo"),
        ),
        Prefetch(
            "actas",
            queryset=acta_queryset_base().exclude(estado_acta=Acta.ESTADO_ARCHIVADO),
        ),
    )


def construir_contexto_acta_corte(acta: Acta) -> ContextoActa:
    asignacion = acta.asignacion_docente
    componentes = _componentes_del_acta(acta)
    filas = []
    nota_exencion = ""

    for numero, detalle in enumerate(_detalles_ordenados(acta.detalles.all()), start=1):
        valores_componentes = []
        calificaciones_por_componente = {cal.componente_id: cal for cal in detalle.calificaciones_componentes.all()}
        for componente in componentes:
            calificacion = calificaciones_por_componente.get(componente.id)
            valor = _valor_componente_visible(calificacion)
            if valor == "EXENTO":
                nota_exencion = "Valor aplicado por regla de exención conforme al promedio de parciales."
            valores_componentes.append(valor)

        usuario = detalle.inscripcion_materia.discente.usuario
        filas.append(
            FilaActaCorte(
                numero=numero,
                grado_empleo=_grado(usuario),
                nombre=usuario.nombre_visible,
                componentes=valores_componentes,
                calificacion_final=decimal_un_decimal(detalle.resultado_corte_visible),
            )
        )

    evaluacion = _evaluacion_acta(acta.corte_codigo)
    return ContextoActa(
        titulo="Acta de Evaluación Final" if acta.es_final else "Acta de Evaluación Parcial",
        tipo_documento="ACTA_EVALUACION_FINAL" if acta.es_final else "ACTA_EVALUACION_PARCIAL",
        carrera=_carrera(asignacion),
        unidad_aprendizaje=_materia(asignacion),
        docente=asignacion.usuario_docente.nombre_institucional,
        grupo=asignacion.grupo_academico.clave_grupo,
        ciclo_escolar=_ciclo(asignacion),
        semestre=f"{asignacion.grupo_academico.semestre_numero}/o. Semestre",
        evaluacion=evaluacion,
        estado_documental=acta.get_estado_acta_display(),
        marca_no_oficial=_marca_no_oficial_acta(acta),
        lugar_fecha=construir_lugar_fecha(acta.formalizada_en if _acta_formalizada(acta) else timezone.now()),
        causas_reprobacion=(acta.probables_causas_reprobacion or "N/A").strip() or "N/A",
        sugerencias=(acta.sugerencias_academicas or "N/A").strip() or "N/A",
        firmas=_firmas_acta(acta),
        estadisticos=calcular_estadisticos([fila.calificacion_final for fila in filas]),
        componentes=componentes,
        filas_corte=filas,
        nota_exencion=nota_exencion,
    )


def construir_contexto_calificacion_final(asignacion: AsignacionDocente) -> ContextoActa:
    actas_por_corte = {acta.corte_codigo: acta for acta in asignacion.actas.all() if acta.estado_acta != Acta.ESTADO_ARCHIVADO}
    detalles_por_corte = {
        corte: {detalle.inscripcion_materia_id: detalle for detalle in acta.detalles.all()}
        for corte, acta in actas_por_corte.items()
    }
    filas = []

    inscripciones = sorted(
        [inscripcion for inscripcion in asignacion.inscripciones_materia.all() if inscripcion.estado_inscripcion == InscripcionMateria.ESTADO_INSCRITA],
        key=lambda item: item.discente.matricula,
    )
    for numero, inscripcion in enumerate(inscripciones, start=1):
        usuario = inscripcion.discente.usuario
        detalle_final = detalles_por_corte.get(ComponenteEvaluacion.CORTE_FINAL, {}).get(inscripcion.id)
        calificacion_final = decimal_un_decimal(inscripcion.calificacion_final)
        if calificacion_final is None and detalle_final:
            calificacion_final = decimal_un_decimal(detalle_final.resultado_final_preliminar_visible)
        filas.append(
            FilaActaCalificacionFinal(
                numero=numero,
                grado_empleo=_grado(usuario),
                nombre=usuario.nombre_visible,
                parcial_1=_resultado_corte(detalles_por_corte, ComponenteEvaluacion.CORTE_P1, inscripcion.id),
                parcial_2=_resultado_corte(detalles_por_corte, ComponenteEvaluacion.CORTE_P2, inscripcion.id),
                parcial_3=_resultado_corte(detalles_por_corte, ComponenteEvaluacion.CORTE_P3, inscripcion.id),
                evaluacion_final=_resultado_corte(detalles_por_corte, ComponenteEvaluacion.CORTE_FINAL, inscripcion.id),
                calificacion_final=calificacion_final,
            )
        )

    acta_final = actas_por_corte.get(ComponenteEvaluacion.CORTE_FINAL)
    acta_referencia = acta_final or next(iter(actas_por_corte.values()), None)
    marca_no_oficial = ""
    if not acta_final or not _acta_formalizada(acta_final):
        marca_no_oficial = "DOCUMENTO NO OFICIAL / CONSOLIDADO PARA REVISION"

    return ContextoActa(
        titulo="Acta de Calificación Final",
        tipo_documento="ACTA_CALIFICACION_FINAL",
        carrera=_carrera(asignacion),
        unidad_aprendizaje=_materia(asignacion),
        docente=asignacion.usuario_docente.nombre_institucional,
        grupo=asignacion.grupo_academico.clave_grupo,
        ciclo_escolar=_ciclo(asignacion),
        semestre=f"{asignacion.grupo_academico.semestre_numero}/o. Semestre",
        evaluacion="Calificación Final",
        estado_documental=acta_final.get_estado_acta_display() if acta_final else "Sin acta final formalizada",
        marca_no_oficial=marca_no_oficial,
        lugar_fecha=construir_lugar_fecha(acta_final.formalizada_en if acta_final and _acta_formalizada(acta_final) else timezone.now()),
        causas_reprobacion=_texto_acta_referencia(acta_referencia, "probables_causas_reprobacion"),
        sugerencias=_texto_acta_referencia(acta_referencia, "sugerencias_academicas"),
        firmas=_firmas_acta(acta_final) if acta_final else _firmas_pendientes(asignacion),
        estadisticos=calcular_estadisticos([fila.calificacion_final for fila in filas]),
        filas_final=filas,
    )


def _componentes_del_acta(acta):
    componentes = {}
    for detalle in acta.detalles.all():
        for calificacion in detalle.calificaciones_componentes.all():
            componentes.setdefault(
                calificacion.componente_id,
                ComponenteActa(
                    id=calificacion.componente_id,
                    nombre=calificacion.componente_nombre_snapshot,
                    porcentaje=calificacion.componente_porcentaje_snapshot,
                    es_examen=calificacion.componente_es_examen_snapshot,
                ),
            )
    return list(componentes.values())


def _detalles_ordenados(detalles):
    return sorted(detalles, key=lambda item: item.inscripcion_materia.discente.matricula)


def _valor_componente_visible(calificacion):
    if not calificacion:
        return None
    if calificacion.sustituido_por_exencion and calificacion.componente_es_examen_snapshot:
        return "EXENTO"
    if calificacion.valor_calculado is not None:
        return decimal_un_decimal(calificacion.valor_calculado)
    if calificacion.valor_capturado is None:
        return None
    ponderado = Decimal(calificacion.valor_capturado) * calificacion.componente_porcentaje_snapshot / Decimal("100")
    return decimal_un_decimal(ponderado)


def _resultado_corte(detalles_por_corte, corte, inscripcion_id):
    detalle = detalles_por_corte.get(corte, {}).get(inscripcion_id)
    if not detalle:
        return None
    return decimal_un_decimal(detalle.resultado_corte_visible)


def _acta_formalizada(acta):
    return bool(acta and acta.estado_acta == Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA)


def _marca_no_oficial_acta(acta):
    if _acta_formalizada(acta):
        return ""
    if acta.estado_acta == Acta.ESTADO_BORRADOR_DOCENTE:
        return "BORRADOR / DOCUMENTO NO OFICIAL"
    return "DOCUMENTO NO OFICIAL / PARA REVISION O FIRMA FISICA"


def _evaluacion_acta(corte):
    if corte == ComponenteEvaluacion.CORTE_P1:
        return "1/a. Evaluación"
    if corte == ComponenteEvaluacion.CORTE_P2:
        return "2/a. Evaluación"
    if corte == ComponenteEvaluacion.CORTE_P3:
        return "3/a. Evaluación"
    return "Evaluación final"


def _grado(usuario):
    return usuario.grado_empleo.abreviatura if getattr(usuario, "grado_empleo_id", None) else ""


def _carrera(asignacion):
    carrera = asignacion.programa_asignatura.plan_estudios.carrera
    clave = (getattr(carrera, "clave", "") or "").strip().upper()
    codigo = (getattr(carrera, "codigo", "") or "").strip().upper()
    nombre = (carrera.nombre or "").strip()
    return NOMBRES_OFICIALES_CARRERA.get(clave) or NOMBRES_OFICIALES_CARRERA.get(codigo) or nombre


def _materia(asignacion):
    materia = asignacion.programa_asignatura.materia
    return materia.nombre


def _ciclo(asignacion):
    periodo = asignacion.grupo_academico.periodo
    return periodo.anio_escolar


def _texto_acta_referencia(acta, field_name):
    if not acta:
        return "N/A"
    return (getattr(acta, field_name, "") or "N/A").strip() or "N/A"


def _firmas_acta(acta):
    asignacion = acta.asignacion_docente
    reviso = _validacion_firma(
        acta,
        ValidacionActa.ETAPA_JEFATURA_CARRERA,
        ValidacionActa.ACCION_VALIDA,
        "Revisó",
    ) or _firma_jefatura_carrera(asignacion, "Revisó")
    vo_bo = _validacion_firma(
        acta,
        ValidacionActa.ETAPA_JEFATURA_ACADEMICA,
        ValidacionActa.ACCION_FORMALIZA,
        "Vo. Bo.",
    ) or _firma_jefatura_academica("Vo. Bo.")
    return [
        _firma_docente(asignacion),
        reviso,
        vo_bo,
    ]


def _firmas_pendientes(asignacion):
    return [
        _firma_docente(asignacion),
        _firma_jefatura_carrera(asignacion, "Revisó"),
        _firma_jefatura_academica("Vo. Bo."),
    ]


def _validacion_firma(acta, etapa, accion, etiqueta):
    validacion = next(
        (
            item
            for item in acta.validaciones.all()
            if item.etapa_validacion == etapa and item.accion == accion
        ),
        None,
    )
    if not validacion:
        return None
    cargo = validacion.asignacion_cargo.cargo_descripcion() if validacion.asignacion_cargo_id else ""
    estado = validacion.asignacion_cargo.get_tipo_designacion_display() if validacion.asignacion_cargo_id else ""
    return FirmaActa(
        etiqueta=etiqueta,
        nombre=validacion.usuario.nombre_institucional,
        cargo=cargo,
        estado=estado,
    )


def _firma_docente(asignacion):
    usuario = asignacion.usuario_docente
    cedula = (getattr(usuario, "cedula_profesional", "") or "").strip()
    return FirmaActa(
        etiqueta="Evaluó",
        nombre=usuario.nombre_institucional,
        cargo=(getattr(usuario, "titulo_profesional", "") or "").strip(),
        cedula=f"Cédula profesional: {cedula}" if cedula else "",
    )


def _firma_jefatura_carrera(asignacion, etiqueta):
    carrera_id = asignacion.programa_asignatura.plan_estudios.carrera_id
    cargo = _cargo_vigente(
        [
            AsignacionCargo.CARGO_JEFE_SUB_EJEC_CTR,
            AsignacionCargo.CARGO_JEFE_CARRERA,
        ],
        carrera_id=carrera_id,
    )
    return _firma_desde_cargo(etiqueta, cargo)


def _firma_jefatura_academica(etiqueta):
    cargo = _cargo_vigente([AsignacionCargo.CARGO_JEFE_ACADEMICO])
    return _firma_desde_cargo(etiqueta, cargo)


def _firma_desde_cargo(etiqueta, asignacion_cargo):
    if not asignacion_cargo:
        return FirmaActa(etiqueta=etiqueta)
    return FirmaActa(
        etiqueta=etiqueta,
        nombre=asignacion_cargo.usuario.nombre_institucional,
        cargo=asignacion_cargo.cargo_descripcion(),
        estado=asignacion_cargo.get_tipo_designacion_display(),
    )


def _cargo_vigente(codigos, *, carrera_id=None):
    hoy = timezone.localdate()
    qs = (
        AsignacionCargo.objects.select_related(
            "usuario__grado_empleo",
            "carrera",
            "unidad_organizacional__carrera",
        )
        .filter(
            models.Q(vigente_desde__isnull=True) | models.Q(vigente_desde__lte=hoy),
            models.Q(vigente_hasta__isnull=True) | models.Q(vigente_hasta__gte=hoy),
            activo=True,
            cargo_codigo__in=codigos,
        )
    )
    if carrera_id:
        qs = qs.filter(
            models.Q(carrera_id=carrera_id)
            | models.Q(unidad_organizacional__carrera_id=carrera_id)
        )
    cargos = list(qs)
    cargos.sort(
        key=lambda item: (
            item.tipo_designacion != AsignacionCargo.DESIGNACION_TITULAR,
            codigos.index(item.cargo_codigo) if item.cargo_codigo in codigos else 99,
            item.vigente_desde or date.min,
        )
    )
    return cargos[0] if cargos else None
