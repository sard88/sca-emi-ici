from django.db.models import Q
from django.utils import timezone

from usuarios.models import Usuario

from .models import AdscripcionGrupo, InscripcionMateria


def sincronizar_carga_academica(asignacion_docente):
    if not asignacion_docente.activo:
        return 0

    hoy = timezone.localdate()
    adscripciones = (
        AdscripcionGrupo.objects.filter(
            Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
            Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
            activo=True,
            grupo_academico=asignacion_docente.grupo_academico,
            discente__activo=True,
            discente__usuario__is_active=True,
            discente__usuario__estado_cuenta=Usuario.ESTADO_ACTIVO,
        )
        .select_related("discente", "discente__usuario")
        .order_by("discente__matricula")
    )

    creadas = 0
    for adscripcion in adscripciones:
        existe_activa = InscripcionMateria.objects.filter(
            discente=adscripcion.discente,
            asignacion_docente=asignacion_docente,
            estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
        ).exists()
        if existe_activa:
            continue

        InscripcionMateria.objects.create(
            discente=adscripcion.discente,
            asignacion_docente=asignacion_docente,
            estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
            intento_numero=1,
        )
        creadas += 1

    return creadas
