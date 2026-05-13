import hashlib
from dataclasses import dataclass

from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from core.portal_services import portal_context
from evaluacion.models import Acta, ComponenteEvaluacion
from relaciones.models import AsignacionDocente

from .actas_context import (
    acta_queryset_base,
    asignacion_queryset_base,
    construir_contexto_acta_corte,
    construir_contexto_calificacion_final,
)
from .models import RegistroExportacion
from .services import ServicioExportacion, construir_nombre_archivo, normalizar_fragmento_archivo

PDF_MIME = "application/pdf"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@dataclass(frozen=True)
class ArchivoActaGenerado:
    contenido: bytes
    nombre_archivo: str
    content_type: str
    registro: RegistroExportacion


class ServicioPermisosActaExportacion:
    def __init__(self, user):
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Autenticación requerida para exportar actas.")
        self.user = user
        self.ctx = portal_context(user)

    def validar_acta(self, acta: Acta):
        if self._puede_soporte_o_consulta_amplia():
            return
        if self.ctx.is_discente:
            raise PermissionDenied("El perfil discente no puede exportar actas completas de grupo.")
        if self.ctx.is_docente and acta.asignacion_docente.usuario_docente_id == self.user.id:
            return
        if self.ctx.is_jefatura_carrera and self._en_ambito_carrera(acta.asignacion_docente):
            return
        raise PermissionDenied("No tienes permiso para exportar esta acta.")

    def validar_asignacion_calificacion_final(self, asignacion: AsignacionDocente):
        if self._puede_soporte_o_consulta_amplia():
            return
        if self.ctx.is_discente:
            raise PermissionDenied("El perfil discente no puede exportar actas completas de grupo.")
        if self.ctx.is_docente and asignacion.usuario_docente_id == self.user.id:
            return
        if self.ctx.is_jefatura_carrera and self._en_ambito_carrera(asignacion):
            return
        raise PermissionDenied("No tienes permiso para exportar la calificación final de esta asignación.")

    def _puede_soporte_o_consulta_amplia(self):
        return self.ctx.is_admin or self.ctx.is_estadistica or self.ctx.is_jefatura_academica or self.ctx.is_jefatura_pedagogica

    def _en_ambito_carrera(self, asignacion):
        if not self.ctx.carrera_ids:
            return True
        carrera_id = asignacion.programa_asignatura.plan_estudios.carrera_id
        return carrera_id in self.ctx.carrera_ids


class ServicioExportacionActa:
    def __init__(self, user, request=None):
        self.user = user
        self.request = request
        self.permisos = ServicioPermisosActaExportacion(user)
        self.servicio_exportacion = ServicioExportacion(user, request=request)

    def exportar_acta_corte(self, acta_id: int, formato: str) -> ArchivoActaGenerado:
        formato = self._validar_formato(formato)
        acta = get_object_or_404(acta_queryset_base(), pk=acta_id)
        self.permisos.validar_acta(acta)
        tipo_documento = self._tipo_documento_acta(acta)
        nombre_documento = "Acta de Evaluación Final" if acta.es_final else "Acta de Evaluación Parcial"
        objeto_repr = self._objeto_repr_acta(acta)
        nombre_archivo = self._nombre_archivo(tipo_documento, formato, objeto_repr)
        registro = self.servicio_exportacion.registrar_solicitud(
            tipo_documento=tipo_documento,
            formato=formato,
            nombre_documento=nombre_documento,
            nombre_archivo=nombre_archivo,
            objeto=acta,
            objeto_repr=objeto_repr,
            parametros={"corte": acta.corte_codigo, "estado_acta": acta.estado_acta},
            validar_disponible=True,
        )
        try:
            contexto = construir_contexto_acta_corte(acta)
            contenido = self._generar(contexto, formato)
        except Exception as exc:
            self.servicio_exportacion.marcar_fallida(registro, exc)
            raise
        self._marcar_generada(registro, contenido)
        return ArchivoActaGenerado(
            contenido=contenido,
            nombre_archivo=nombre_archivo,
            content_type=self._content_type(formato),
            registro=registro,
        )

    def exportar_calificacion_final(self, asignacion_docente_id: int, formato: str) -> ArchivoActaGenerado:
        formato = self._validar_formato(formato)
        asignacion = get_object_or_404(asignacion_queryset_base(), pk=asignacion_docente_id)
        self.permisos.validar_asignacion_calificacion_final(asignacion)
        tipo_documento = RegistroExportacion.TIPO_ACTA_CALIFICACION_FINAL
        nombre_documento = "Acta de Calificación Final"
        objeto_repr = self._objeto_repr_asignacion(asignacion)
        nombre_archivo = self._nombre_archivo(tipo_documento, formato, objeto_repr)
        registro = self.servicio_exportacion.registrar_solicitud(
            tipo_documento=tipo_documento,
            formato=formato,
            nombre_documento=nombre_documento,
            nombre_archivo=nombre_archivo,
            objeto=asignacion,
            objeto_repr=objeto_repr,
            parametros={"tipo": "calificacion_final"},
            validar_disponible=True,
        )
        try:
            contexto = construir_contexto_calificacion_final(asignacion)
            contenido = self._generar(contexto, formato)
        except Exception as exc:
            self.servicio_exportacion.marcar_fallida(registro, exc)
            raise
        self._marcar_generada(registro, contenido)
        return ArchivoActaGenerado(
            contenido=contenido,
            nombre_archivo=nombre_archivo,
            content_type=self._content_type(formato),
            registro=registro,
        )

    def _generar(self, contexto, formato):
        if formato == RegistroExportacion.FORMATO_PDF:
            from .exportadores.actas_pdf import ExportadorActaPDF

            return ExportadorActaPDF().generar(contexto)
        if formato == RegistroExportacion.FORMATO_XLSX:
            from .exportadores.actas_excel import ExportadorActaExcel

            return ExportadorActaExcel().generar(contexto)
        raise ValidationError({"formato": "Formato no soportado para actas."})

    def _marcar_generada(self, registro, contenido):
        self.servicio_exportacion.marcar_generada(
            registro,
            tamano_bytes=len(contenido),
            hash_archivo=hashlib.sha256(contenido).hexdigest(),
        )

    def _validar_formato(self, formato):
        formato = (formato or "").upper()
        if formato not in {RegistroExportacion.FORMATO_PDF, RegistroExportacion.FORMATO_XLSX}:
            raise ValidationError({"formato": "Las actas solo soportan PDF o XLSX."})
        return formato

    def _content_type(self, formato):
        return PDF_MIME if formato == RegistroExportacion.FORMATO_PDF else XLSX_MIME

    def _tipo_documento_acta(self, acta):
        if acta.corte_codigo == ComponenteEvaluacion.CORTE_FINAL:
            return RegistroExportacion.TIPO_ACTA_EVALUACION_FINAL
        return RegistroExportacion.TIPO_ACTA_EVALUACION_PARCIAL

    def _nombre_archivo(self, tipo_documento, formato, objeto_repr):
        return construir_nombre_archivo(tipo_documento, formato, objeto_repr=objeto_repr)

    def _objeto_repr_acta(self, acta):
        asignacion = acta.asignacion_docente
        partes = [
            asignacion.grupo_academico.periodo.clave,
            asignacion.programa_asignatura.plan_estudios.carrera.clave,
            asignacion.grupo_academico.clave_grupo,
            asignacion.programa_asignatura.materia.clave,
            acta.corte_codigo,
        ]
        return normalizar_fragmento_archivo(" ".join(filter(None, partes)), fallback="acta")

    def _objeto_repr_asignacion(self, asignacion):
        partes = [
            asignacion.grupo_academico.periodo.clave,
            asignacion.programa_asignatura.plan_estudios.carrera.clave,
            asignacion.grupo_academico.clave_grupo,
            asignacion.programa_asignatura.materia.clave,
            "calificacion-final",
        ]
        return normalizar_fragmento_archivo(" ".join(filter(None, partes)), fallback="calificacion-final")
