from relaciones.permisos import (
    usuario_es_admin_soporte,
    usuario_es_estadistica,
    usuario_es_jefatura_carrera,
)
from trayectoria.permisos import usuario_es_jefatura_academica


def puede_operar_cierre_apertura(user):
    return usuario_es_admin_soporte(user) or usuario_es_estadistica(user)


def puede_consultar_cierre_periodo(user):
    return puede_operar_cierre_apertura(user) or usuario_es_jefatura_academica(user)


def puede_consultar_pendientes_docente(user):
    return (
        usuario_es_admin_soporte(user)
        or usuario_es_estadistica(user)
        or usuario_es_jefatura_carrera(user)
    )
