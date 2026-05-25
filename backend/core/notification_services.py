from django.db import transaction

from evaluacion.models import Acta
from usuarios.models import Usuario

from .models import NotificacionUsuario


def crear_notificacion_usuario(
    usuario: Usuario,
    *,
    tipo: str = NotificacionUsuario.TIPO_INFO,
    titulo: str,
    mensaje: str,
    url_destino: str = "",
    prioridad: str = NotificacionUsuario.PRIORIDAD_NORMAL,
) -> NotificacionUsuario:
    """Crea una notificacion del portal sin acoplar reglas de negocio al frontend."""
    return NotificacionUsuario.objects.create(
        usuario=usuario,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        url_destino=url_destino,
        prioridad=prioridad,
    )


@transaction.atomic
def notificar_acta_publicada_para_discentes(acta: Acta) -> int:
    """Genera avisos para discentes cuando un acta ya esta publicada.

    El servicio es idempotente por usuario, titulo y URL para evitar duplicados si se
    ejecuta manualmente mas de una vez desde una accion administrativa o tarea futura.
    """
    if acta.estado_acta != Acta.ESTADO_PUBLICADO_DISCENTE:
        return 0

    usuarios = Usuario.objects.filter(
        perfiles_discente__inscripciones_materia__detalles_acta__acta=acta,
        is_active=True,
    ).distinct()
    url = f"/evaluacion/actas/{acta.id}/"
    creadas = 0

    for usuario in usuarios:
        _, created = NotificacionUsuario.objects.get_or_create(
            usuario=usuario,
            tipo=NotificacionUsuario.TIPO_ACTA,
            titulo="Acta publicada",
            url_destino=url,
            defaults={
                "mensaje": "Tienes un acta publicada disponible para consulta y conformidad.",
                "prioridad": NotificacionUsuario.PRIORIDAD_NORMAL,
            },
        )
        if created:
            creadas += 1

    return creadas
