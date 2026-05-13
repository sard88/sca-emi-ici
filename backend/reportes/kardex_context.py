from dataclasses import dataclass, field
from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from reportes.constantes import LUGAR_FECHA_INSTITUCIONAL, MESES_ES, NOMBRES_OFICIALES_CARRERA
from reportes.utils_calificaciones import calificacion_numerica_con_letra, redondear_un_decimal
from trayectoria.services import ServicioKardex
from usuarios.models import AsignacionCargo


ANIOS_FORMACION = {
    1: "Primer año",
    2: "Segundo año",
    3: "Tercer año",
    4: "Cuarto año",
    5: "Quinto año",
    6: "Sexto año",
}

RESULTADOS_NO_NUMERICOS = {
    "ACREDITADA": "ACREDITADA",
    "APROBADO": "APROBADO",
    "APROBADO_NO_NUMERICO": "APROBADO",
    "EXCEPTUADO": "EXCEPTUADO",
}


@dataclass(frozen=True)
class KardexMateriaDocumento:
    anio_formacion: int
    anio_label: str
    semestre_numero: int
    clave_materia: str
    nombre_materia: str
    calificacion: Decimal | None
    calificacion_display: str
    calificacion_letra_display: str
    resultado_display: str
    marca: str
    es_numerica: bool


@dataclass(frozen=True)
class KardexAnioDocumento:
    anio_formacion: int
    anio_label: str
    materias: list[KardexMateriaDocumento] = field(default_factory=list)
    promedio_anual: Decimal | None = None
    promedio_anual_display: str = "N/A"


@dataclass(frozen=True)
class KardexCertificacion:
    texto: str
    autoridad_nombre: str
    autoridad_cargo: str
    unidad_responsable: str


@dataclass(frozen=True)
class KardexDocumentoContexto:
    discente_id: int
    nombre_discente: str
    grado_empleo: str
    carrera_clave: str
    carrera_nombre: str
    carrera_oficial: str
    plan_estudios: str
    antiguedad: str
    situacion_actual: str
    fecha_emision: str
    lugar_fecha: str
    anios: list[KardexAnioDocumento]
    promedio_general: Decimal | None
    promedio_general_display: str
    certificacion: KardexCertificacion


def construir_contexto_kardex(discente, *, fecha_emision=None):
    fecha = fecha_emision or timezone.localdate()
    kardex = ServicioKardex.construir_por_discente(discente)
    anios = [_convertir_anio(anio) for anio in kardex.anios]
    promedio_general = _calcular_promedio_general(anios)
    certificacion = _resolver_certificacion()
    carrera_clave = getattr(kardex.carrera, "clave", "")

    return KardexDocumentoContexto(
        discente_id=discente.id,
        nombre_discente=discente.usuario.nombre_visible,
        grado_empleo=discente.usuario.grado_empleo.abreviatura if discente.usuario.grado_empleo_id else "",
        carrera_clave=carrera_clave,
        carrera_nombre=getattr(kardex.carrera, "nombre", ""),
        carrera_oficial=NOMBRES_OFICIALES_CARRERA.get(carrera_clave, getattr(kardex.carrera, "nombre", "")),
        plan_estudios=getattr(kardex.plan_estudios, "nombre", ""),
        antiguedad=getattr(kardex.antiguedad, "nombre", ""),
        situacion_actual=kardex.situacion_actual,
        fecha_emision=fecha.isoformat(),
        lugar_fecha=_lugar_fecha(fecha),
        anios=anios,
        promedio_general=promedio_general,
        promedio_general_display=_decimal_display(promedio_general),
        certificacion=certificacion,
    )


def _convertir_anio(anio):
    materias = [_convertir_materia(asignatura) for asignatura in anio.asignaturas]
    promedio = redondear_un_decimal(anio.promedio_anual)
    return KardexAnioDocumento(
        anio_formacion=anio.anio_formacion,
        anio_label=ANIOS_FORMACION.get(anio.anio_formacion, f"Año {anio.anio_formacion}"),
        materias=materias,
        promedio_anual=promedio,
        promedio_anual_display=_decimal_display(promedio),
    )


def _convertir_materia(asignatura):
    calificacion = redondear_un_decimal(asignatura.calificacion_visible or asignatura.calificacion)
    resultado_display = _resultado_display(asignatura.resultado_no_numerico or asignatura.codigo_resultado)
    return KardexMateriaDocumento(
        anio_formacion=asignatura.anio_formacion,
        anio_label=ANIOS_FORMACION.get(asignatura.anio_formacion, f"Año {asignatura.anio_formacion}"),
        semestre_numero=asignatura.semestre_numero,
        clave_materia=asignatura.clave_materia,
        nombre_materia=asignatura.nombre_materia,
        calificacion=calificacion,
        calificacion_display=_decimal_display(calificacion) if asignatura.es_numerica else resultado_display,
        calificacion_letra_display=calificacion_numerica_con_letra(calificacion) if asignatura.es_numerica else resultado_display,
        resultado_display=resultado_display,
        marca="EE" if asignatura.marca_ee else (asignatura.codigo_marca or ""),
        es_numerica=asignatura.es_numerica,
    )


def _calcular_promedio_general(anios):
    valores = [materia.calificacion for anio in anios for materia in anio.materias if materia.es_numerica and materia.calificacion is not None]
    if not valores:
        return None
    return redondear_un_decimal(sum(valores, Decimal("0.0")) / Decimal(len(valores)))


def _resolver_certificacion():
    hoy = timezone.localdate()
    cargos = (
        AsignacionCargo.objects.filter(
            Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
            Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
            activo=True,
            cargo_codigo__in=[
                AsignacionCargo.CARGO_JEFE_ACADEMICO,
                AsignacionCargo.CARGO_JEFE_PEDAGOGICA,
            ],
        )
        .select_related("usuario", "unidad_organizacional")
        .order_by("cargo_codigo")
    )
    cargo = cargos.first()
    autoridad_nombre = cargo.usuario.nombre_institucional if cargo else "Pendiente de designación"
    autoridad_cargo = cargo.get_cargo_codigo_display() if cargo else "Autoridad certificadora"
    unidad = cargo.unidad_organizacional.nombre if cargo and cargo.unidad_organizacional_id else "Sección Académica"
    texto = (
        "Se certifica que la presente relación de calificaciones se emite con base en la "
        "información académica consolidada en el Sistema de Control Académico."
    )
    return KardexCertificacion(
        texto=texto,
        autoridad_nombre=autoridad_nombre,
        autoridad_cargo=autoridad_cargo,
        unidad_responsable=unidad,
    )


def _resultado_display(codigo):
    if not codigo:
        return ""
    return RESULTADOS_NO_NUMERICOS.get(codigo, codigo.replace("_", " "))


def _decimal_display(valor):
    if valor is None:
        return "N/A"
    return f"{redondear_un_decimal(valor):.1f}"


def _lugar_fecha(fecha):
    mes = MESES_ES.get(fecha.month, str(fecha.month))
    return f'{LUGAR_FECHA_INSTITUCIONAL}, a {fecha.day} de {mes} de {fecha.year}.'
