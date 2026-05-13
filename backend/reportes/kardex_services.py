import hashlib
from dataclasses import dataclass

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from relaciones.models import Discente
from trayectoria.permisos import puede_consultar_kardex_discente

from .kardex_context import construir_contexto_kardex
from .models import RegistroExportacion
from .services import ServicioExportacion, construir_nombre_archivo, normalizar_fragmento_archivo

PDF_MIME = "application/pdf"


@dataclass(frozen=True)
class ArchivoKardexGenerado:
    contenido: bytes
    nombre_archivo: str
    content_type: str
    registro: RegistroExportacion


class ServicioPermisosKardexExportacion:
    def __init__(self, user):
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Autenticación requerida para exportar kárdex.")
        self.user = user

    def validar_discente(self, discente: Discente):
        if discente.usuario_id == self.user.id:
            raise PermissionDenied("El perfil discente no puede exportar el kárdex oficial.")
        if not puede_consultar_kardex_discente(self.user, discente):
            raise PermissionDenied("No tienes permiso para exportar el kárdex de este discente.")


class ServicioExportacionKardex:
    def __init__(self, user, request=None):
        self.user = user
        self.request = request
        self.permisos = ServicioPermisosKardexExportacion(user)
        self.servicio_exportacion = ServicioExportacion(user, request=request)

    def exportar_kardex_pdf(self, discente_id: int) -> ArchivoKardexGenerado:
        discente = get_object_or_404(
            Discente.objects.select_related(
                "usuario",
                "usuario__grado_empleo",
                "plan_estudios",
                "plan_estudios__carrera",
                "antiguedad",
            ),
            pk=discente_id,
        )
        self.permisos.validar_discente(discente)
        objeto_repr = self._objeto_repr(discente)
        nombre_archivo = self._nombre_archivo(discente)
        registro = self.servicio_exportacion.registrar_solicitud(
            tipo_documento=RegistroExportacion.TIPO_KARDEX_OFICIAL,
            formato=RegistroExportacion.FORMATO_PDF,
            nombre_documento="Kárdex oficial",
            nombre_archivo=nombre_archivo,
            objeto=discente,
            objeto_repr=objeto_repr,
            parametros={"discente_id": discente.id},
            validar_disponible=True,
        )
        try:
            contexto = construir_contexto_kardex(discente)
            contenido = self._generar_pdf(contexto)
        except Exception as exc:
            self.servicio_exportacion.marcar_fallida(registro, exc)
            raise
        self.servicio_exportacion.marcar_generada(
            registro,
            tamano_bytes=len(contenido),
            hash_archivo=hashlib.sha256(contenido).hexdigest(),
        )
        return ArchivoKardexGenerado(
            contenido=contenido,
            nombre_archivo=nombre_archivo,
            content_type=PDF_MIME,
            registro=registro,
        )

    def _generar_pdf(self, contexto):
        from .exportadores.kardex_pdf import ExportadorKardexPDF

        return ExportadorKardexPDF().generar(contexto)

    def _nombre_archivo(self, discente):
        carrera = discente.plan_estudios.carrera.clave if discente.plan_estudios_id else "carrera"
        objeto_repr = f"{normalizar_fragmento_archivo(carrera)}-discente-{discente.id}"
        return construir_nombre_archivo(
            RegistroExportacion.TIPO_KARDEX_OFICIAL,
            RegistroExportacion.FORMATO_PDF,
            objeto_repr=objeto_repr,
        )

    def _objeto_repr(self, discente):
        carrera = discente.plan_estudios.carrera.clave if discente.plan_estudios_id else "SIN-CARRERA"
        return f"{carrera} - Discente {discente.id}"
