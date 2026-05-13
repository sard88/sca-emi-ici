import re

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from catalogos.models import (
    ESTADO_ACTIVO,
    ESTADO_CERRADO,
    ESTADO_PLANIFICADO,
    GrupoAcademico,
    PeriodoEscolar,
    ProgramaAsignatura,
)
from evaluacion.models import Acta, ComponenteEvaluacion
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria
from relaciones.permisos import usuario_es_admin_soporte, usuario_es_estadistica
from trayectoria.models import CALIFICACION_APROBATORIA, Extraordinario
from trayectoria.permisos import carreras_ambito_usuario

from .models import (
    DetalleCierrePeriodoDiscente,
    ProcesoAperturaPeriodo,
    ProcesoCierrePeriodo,
)


ACTAS_VIVAS_BLOQUEANTES = [
    Acta.ESTADO_BORRADOR_DOCENTE,
    Acta.ESTADO_PUBLICADO_DISCENTE,
    Acta.ESTADO_REMITIDO_JEFATURA_CARRERA,
    Acta.ESTADO_VALIDADO_JEFATURA_CARRERA,
]

ACTAS_FINALES_CONSOLIDADAS = [
    Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA,
    Acta.ESTADO_ARCHIVADO,
]


def _resumen_vacio(periodo):
    return {
        "periodo": periodo.clave,
        "bloqueantes": [],
        "advertencias": [],
        "discentes_promovibles": [],
        "discentes_pendientes_extraordinario": [],
        "discentes_baja_temporal": [],
        "discentes_baja_definitiva": [],
        "discentes_egresables": [],
        "resumen_por_grupo": {},
    }


def _datos_discente(discente, grupo=None, motivo=""):
    return {
        "discente_id": discente.pk,
        "matricula": discente.matricula,
        "nombre": discente.usuario.nombre_completo or discente.usuario.username,
        "grupo": grupo.clave_grupo if grupo else "",
        "motivo": motivo,
    }


def _agregar_resumen_grupo(resumen, grupo, clave):
    grupo_key = grupo.clave_grupo if grupo else "SIN_GRUPO"
    resumen_grupo = resumen["resumen_por_grupo"].setdefault(
        grupo_key,
        {
            "grupo": grupo_key,
            "promovibles": 0,
            "pendientes_extraordinario": 0,
            "baja_temporal": 0,
            "baja_definitiva": 0,
            "egresables": 0,
            "no_promovibles": 0,
        },
    )
    resumen_grupo[clave] += 1


class ServicioDiagnosticoCierrePeriodo:
    def __init__(self, periodo):
        self.periodo = periodo

    def diagnosticar(self):
        resumen = _resumen_vacio(self.periodo)
        grupos = GrupoAcademico.objects.filter(periodo=self.periodo).select_related(
            "antiguedad",
            "antiguedad__plan_estudios",
        )
        asignaciones = AsignacionDocente.objects.filter(
            grupo_academico__periodo=self.periodo,
            activo=True,
        ).select_related(
            "grupo_academico",
            "programa_asignatura",
            "programa_asignatura__materia",
        )

        self._diagnosticar_actas(asignaciones, resumen)
        self._diagnosticar_inscripciones(resumen)
        self._diagnosticar_adscripciones(resumen)
        self._clasificar_discentes(grupos, resumen)

        if not grupos.exists():
            resumen["advertencias"].append("El periodo no tiene grupos académicos registrados.")
        if not asignaciones.exists():
            resumen["advertencias"].append("El periodo no tiene asignaciones docentes activas.")

        return resumen

    def _diagnosticar_actas(self, asignaciones, resumen):
        for asignacion in asignaciones:
            tiene_inscripciones = asignacion.inscripciones_materia.exists()
            if not tiene_inscripciones:
                resumen["advertencias"].append(
                    f"La asignación {asignacion} no tiene inscripciones a asignatura."
                )
                continue

            actas_finales = Acta.objects.filter(
                asignacion_docente=asignacion,
                corte_codigo=ComponenteEvaluacion.CORTE_FINAL,
            )
            if actas_finales.filter(estado_acta__in=ACTAS_VIVAS_BLOQUEANTES).exists():
                resumen["bloqueantes"].append(
                    f"Existe acta FINAL viva pendiente para {asignacion}."
                )
            if not actas_finales.filter(estado_acta__in=ACTAS_FINALES_CONSOLIDADAS).exists():
                resumen["bloqueantes"].append(
                    f"Falta acta FINAL formalizada para {asignacion}."
                )

        actas_vivas = Acta.objects.filter(
            asignacion_docente__grupo_academico__periodo=self.periodo,
            estado_acta__in=ACTAS_VIVAS_BLOQUEANTES,
        )
        for acta in actas_vivas:
            resumen["bloqueantes"].append(
                f"Acta viva pendiente: {acta.asignacion_docente} - {acta.get_corte_codigo_display()}."
            )

    def _diagnosticar_inscripciones(self, resumen):
        inscripciones = InscripcionMateria.objects.filter(
            asignacion_docente__grupo_academico__periodo=self.periodo,
        ).select_related("discente", "discente__usuario", "asignacion_docente")

        for inscripcion in inscripciones:
            if inscripcion.cerrado_en is None or inscripcion.calificacion_final is None:
                resumen["bloqueantes"].append(
                    "Existe inscripción sin resultado oficial consolidado: "
                    f"{inscripcion.discente.usuario.nombre_visible} - "
                    f"{inscripcion.asignacion_docente.programa_asignatura.materia.nombre}."
                )
            elif (
                inscripcion.calificacion_final < CALIFICACION_APROBATORIA
                and not Extraordinario.objects.filter(inscripcion_materia=inscripcion).exists()
            ):
                resumen["bloqueantes"].append(
                    "Existe extraordinario pendiente o no resuelto para "
                    f"{inscripcion.discente.usuario.nombre_visible} - "
                    f"{inscripcion.asignacion_docente.programa_asignatura.materia.nombre}."
                )

    def _diagnosticar_adscripciones(self, resumen):
        duplicadas = (
            AdscripcionGrupo.objects.filter(
                grupo_academico__periodo=self.periodo,
                activo=True,
            )
            .values("discente_id")
            .annotate(total=models_count("id"))
            .filter(total__gt=1)
        )
        for item in duplicadas:
            resumen["bloqueantes"].append(
                f"El discente {item['discente_id']} tiene más de una adscripción activa en el periodo."
            )

    def _clasificar_discentes(self, grupos, resumen):
        adscripciones = (
            AdscripcionGrupo.objects.filter(
                grupo_academico__periodo=self.periodo,
                activo=True,
            )
            .select_related(
                "discente",
                "discente__usuario",
                "grupo_academico",
            )
            .order_by("grupo_academico__clave_grupo", "discente__matricula")
        )
        for adscripcion in adscripciones:
            discente = adscripcion.discente
            grupo = adscripcion.grupo_academico
            if discente.situacion_actual == Discente.SITUACION_BAJA_TEMPORAL:
                resumen["discentes_baja_temporal"].append(
                    _datos_discente(discente, grupo, "Discente en baja temporal.")
                )
                _agregar_resumen_grupo(resumen, grupo, "baja_temporal")
                continue
            if discente.situacion_actual == Discente.SITUACION_BAJA_DEFINITIVA:
                resumen["discentes_baja_definitiva"].append(
                    _datos_discente(discente, grupo, "Discente en baja definitiva.")
                )
                _agregar_resumen_grupo(resumen, grupo, "baja_definitiva")
                continue
            if grupo.semestre_numero >= 12:
                resumen["discentes_egresables"].append(
                    _datos_discente(discente, grupo, "Semestre institucional final.")
                )
                _agregar_resumen_grupo(resumen, grupo, "egresables")
                continue

            inscripciones = InscripcionMateria.objects.filter(
                discente=discente,
                asignacion_docente__grupo_academico__periodo=self.periodo,
            )
            tiene_extra_pendiente = inscripciones.filter(
                calificacion_final__lt=CALIFICACION_APROBATORIA,
                extraordinario__isnull=True,
            ).exists()
            incompletas = inscripciones.filter(
                Q(cerrado_en__isnull=True) | Q(calificacion_final__isnull=True)
            ).exists()

            if tiene_extra_pendiente:
                resumen["discentes_pendientes_extraordinario"].append(
                    _datos_discente(discente, grupo, "Tiene extraordinario pendiente.")
                )
                _agregar_resumen_grupo(resumen, grupo, "pendientes_extraordinario")
            elif incompletas:
                _agregar_resumen_grupo(resumen, grupo, "no_promovibles")
            else:
                resumen["discentes_promovibles"].append(
                    _datos_discente(discente, grupo, "Resultados oficiales completos.")
                )
                _agregar_resumen_grupo(resumen, grupo, "promovibles")


def models_count(field):
    from django.db.models import Count

    return Count(field)


class ServicioCierrePeriodo:
    def __init__(self, periodo, usuario, observaciones=""):
        self.periodo = periodo
        self.usuario = usuario
        self.observaciones = observaciones

    @transaction.atomic
    def cerrar(self):
        periodo = PeriodoEscolar.objects.select_for_update().get(pk=self.periodo.pk)
        diagnostico = ServicioDiagnosticoCierrePeriodo(periodo).diagnosticar()
        if diagnostico["bloqueantes"]:
            raise ValidationError(
                "No se puede cerrar el periodo porque existen bloqueantes críticos."
            )

        proceso = ProcesoCierrePeriodo.objects.create(
            periodo=periodo,
            estado=ProcesoCierrePeriodo.ESTADO_CERRADO,
            ejecutado_por=self.usuario,
            resumen_json=diagnostico,
            observaciones=self.observaciones,
        )
        self._crear_detalles(proceso, diagnostico)
        periodo.estado = ESTADO_CERRADO
        periodo.save(update_fields=["estado"])
        return proceso

    def _crear_detalles(self, proceso, diagnostico):
        grupos = {
            grupo.clave_grupo: grupo
            for grupo in GrupoAcademico.objects.filter(periodo=proceso.periodo)
        }
        clasificaciones = [
            (
                "discentes_promovibles",
                DetalleCierrePeriodoDiscente.CLASIFICACION_PROMOVIBLE,
                True,
                False,
            ),
            (
                "discentes_pendientes_extraordinario",
                DetalleCierrePeriodoDiscente.CLASIFICACION_EXTRAORDINARIO_PENDIENTE,
                False,
                True,
            ),
            (
                "discentes_baja_temporal",
                DetalleCierrePeriodoDiscente.CLASIFICACION_BAJA_TEMPORAL,
                False,
                False,
            ),
            (
                "discentes_baja_definitiva",
                DetalleCierrePeriodoDiscente.CLASIFICACION_BAJA_DEFINITIVA,
                False,
                False,
            ),
            (
                "discentes_egresables",
                DetalleCierrePeriodoDiscente.CLASIFICACION_EGRESABLE,
                False,
                False,
            ),
        ]
        for clave_resumen, clasificacion, promovible, requiere_extraordinario in clasificaciones:
            for item in diagnostico.get(clave_resumen, []):
                discente = Discente.objects.get(pk=item["discente_id"])
                grupo = grupos.get(item.get("grupo"))
                DetalleCierrePeriodoDiscente.objects.create(
                    proceso_cierre=proceso,
                    discente=discente,
                    grupo_origen=grupo,
                    clasificacion=clasificacion,
                    motivo=item.get("motivo", ""),
                    promovible=promovible,
                    requiere_extraordinario=requiere_extraordinario,
                    situacion_detectada=discente.get_situacion_actual_display(),
                )


def sugerir_clave_grupo_destino(clave_origen, semestre_destino):
    match = re.search(r"\d+", clave_origen or "")
    if match:
        return f"{clave_origen[:match.start()]}{semestre_destino}{clave_origen[match.end():]}"
    clave = f"{clave_origen}-S{semestre_destino}"
    return clave[:20]


class ServicioAperturaPeriodo:
    def __init__(self, periodo_origen, periodo_destino, usuario, observaciones=""):
        self.periodo_origen = periodo_origen
        self.periodo_destino = periodo_destino
        self.usuario = usuario
        self.observaciones = observaciones

    @transaction.atomic
    def abrir(self):
        origen = PeriodoEscolar.objects.select_for_update().get(pk=self.periodo_origen.pk)
        destino = PeriodoEscolar.objects.select_for_update().get(pk=self.periodo_destino.pk)
        if origen.estado != ESTADO_CERRADO:
            raise ValidationError("El periodo origen debe estar cerrado antes de abrir el siguiente.")
        if destino.estado not in {ESTADO_PLANIFICADO, ESTADO_ACTIVO}:
            raise ValidationError("El periodo destino debe estar planificado o abierto.")

        cierre = (
            ProcesoCierrePeriodo.objects.filter(
                periodo=origen,
                estado=ProcesoCierrePeriodo.ESTADO_CERRADO,
            )
            .order_by("-ejecutado_en")
            .first()
        )
        if not cierre:
            raise ValidationError("No existe un proceso de cierre válido para el periodo origen.")

        resumen = {
            "grupos_creados": [],
            "grupos_existentes": [],
            "adscripciones_creadas": 0,
            "adscripciones_cerradas": 0,
            "egresables": [],
            "omitidos": [],
        }

        if destino.estado == ESTADO_PLANIFICADO:
            destino.estado = ESTADO_ACTIVO
            destino.save(update_fields=["estado"])

        detalles = cierre.detalles_discente.select_related("discente", "grupo_origen")
        for detalle in detalles:
            if detalle.clasificacion == DetalleCierrePeriodoDiscente.CLASIFICACION_EGRESABLE:
                resumen["egresables"].append(detalle.discente.matricula)
                continue
            if not detalle.promovible or not detalle.grupo_origen_id:
                resumen["omitidos"].append(
                    {
                        "discente": detalle.discente.matricula,
                        "motivo": detalle.get_clasificacion_display(),
                    }
                )
                continue

            grupo_destino = self._obtener_o_crear_grupo_destino(detalle.grupo_origen, destino, resumen)
            cerradas = AdscripcionGrupo.objects.filter(
                discente=detalle.discente,
                grupo_academico=detalle.grupo_origen,
                activo=True,
            ).update(activo=False, vigente_hasta=timezone.localdate())
            resumen["adscripciones_cerradas"] += cerradas

            _, creada = AdscripcionGrupo.objects.get_or_create(
                discente=detalle.discente,
                grupo_academico=grupo_destino,
                activo=True,
                defaults={"vigente_desde": timezone.localdate()},
            )
            if creada:
                resumen["adscripciones_creadas"] += 1

        proceso = ProcesoAperturaPeriodo.objects.create(
            periodo_origen=origen,
            periodo_destino=destino,
            ejecutado_por=self.usuario,
            estado=ProcesoAperturaPeriodo.ESTADO_EJECUTADO,
            resumen_json=resumen,
            observaciones=self.observaciones,
        )
        return proceso

    def _obtener_o_crear_grupo_destino(self, grupo_origen, periodo_destino, resumen):
        semestre_destino = grupo_origen.semestre_numero + 1
        if semestre_destino > 12:
            raise ValidationError("No se puede crear grupo destino para semestre mayor a 12.")
        clave_destino = sugerir_clave_grupo_destino(grupo_origen.clave_grupo, semestre_destino)
        grupo, creado = GrupoAcademico.objects.get_or_create(
            antiguedad=grupo_origen.antiguedad,
            periodo=periodo_destino,
            clave_grupo=clave_destino,
            defaults={
                "semestre_numero": semestre_destino,
                "estado": ESTADO_ACTIVO,
                "cupo_maximo": grupo_origen.cupo_maximo,
            },
        )
        if creado:
            resumen["grupos_creados"].append(grupo.clave_grupo)
        else:
            resumen["grupos_existentes"].append(grupo.clave_grupo)
        return grupo


def listar_pendientes_asignacion_docente(periodo, user=None):
    grupos = GrupoAcademico.objects.filter(periodo=periodo).select_related(
        "antiguedad",
        "antiguedad__plan_estudios",
        "antiguedad__plan_estudios__carrera",
    )
    if user is not None:
        if not (usuario_es_admin_soporte(user) or usuario_es_estadistica(user)):
            carrera_ids = carreras_ambito_usuario(user)
            if carrera_ids:
                grupos = grupos.filter(antiguedad__plan_estudios__carrera_id__in=carrera_ids)
            else:
                grupos = grupos.none()

    pendientes = []
    for grupo in grupos.order_by("clave_grupo"):
        programas = ProgramaAsignatura.objects.filter(
            plan_estudios=grupo.antiguedad.plan_estudios,
            plan_estudios__estado=ESTADO_ACTIVO,
            materia__estado=ESTADO_ACTIVO,
        ).select_related("materia", "plan_estudios")
        for programa in programas:
            if not programa.aplica_para_grupo(grupo):
                continue
            tiene_asignacion = AsignacionDocente.objects.filter(
                grupo_academico=grupo,
                programa_asignatura=programa,
                activo=True,
            ).exists()
            if not tiene_asignacion:
                pendientes.append({"grupo": grupo, "programa": programa})
    return pendientes
