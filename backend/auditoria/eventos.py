MODULO_AUTENTICACION = "AUTENTICACION"
MODULO_ADMINISTRACION = "ADMINISTRACION"
MODULO_CATALOGOS = "CATALOGOS"
MODULO_RELACIONES = "RELACIONES"
MODULO_EVALUACION = "EVALUACION"
MODULO_ACTAS = "ACTAS"
MODULO_CONFORMIDAD = "CONFORMIDAD"
MODULO_TRAYECTORIA = "TRAYECTORIA"
MODULO_MOVIMIENTOS = "MOVIMIENTOS"
MODULO_PERIODOS = "PERIODOS"
MODULO_REPORTES = "REPORTES"
MODULO_EXPORTACIONES = "EXPORTACIONES"
MODULO_SISTEMA = "SISTEMA"

MODULO_CHOICES = [
    (MODULO_AUTENTICACION, "Autenticacion"),
    (MODULO_ADMINISTRACION, "Administracion"),
    (MODULO_CATALOGOS, "Catalogos"),
    (MODULO_RELACIONES, "Relaciones"),
    (MODULO_EVALUACION, "Evaluacion"),
    (MODULO_ACTAS, "Actas"),
    (MODULO_CONFORMIDAD, "Conformidad"),
    (MODULO_TRAYECTORIA, "Trayectoria"),
    (MODULO_MOVIMIENTOS, "Movimientos"),
    (MODULO_PERIODOS, "Periodos"),
    (MODULO_REPORTES, "Reportes"),
    (MODULO_EXPORTACIONES, "Exportaciones"),
    (MODULO_SISTEMA, "Sistema"),
]

SEVERIDAD_INFO = "INFO"
SEVERIDAD_ADVERTENCIA = "ADVERTENCIA"
SEVERIDAD_CRITICO = "CRITICO"

SEVERIDAD_CHOICES = [
    (SEVERIDAD_INFO, "Info"),
    (SEVERIDAD_ADVERTENCIA, "Advertencia"),
    (SEVERIDAD_CRITICO, "Critico"),
]

RESULTADO_EXITOSO = "EXITOSO"
RESULTADO_FALLIDO = "FALLIDO"
RESULTADO_BLOQUEADO = "BLOQUEADO"

RESULTADO_CHOICES = [
    (RESULTADO_EXITOSO, "Exitoso"),
    (RESULTADO_FALLIDO, "Fallido"),
    (RESULTADO_BLOQUEADO, "Bloqueado"),
]


EVENTOS = {
    "LOGIN_EXITOSO": "Login exitoso",
    "LOGIN_FALLIDO": "Login fallido",
    "LOGOUT": "Logout",
    "ACCESO_DENEGADO": "Acceso denegado",
    "USUARIO_CREADO": "Usuario creado",
    "USUARIO_ACTUALIZADO": "Usuario actualizado",
    "USUARIO_ACTIVADO": "Usuario activado",
    "USUARIO_INACTIVADO": "Usuario inactivado",
    "GRADO_EMPLEO_CREADO": "Grado/empleo creado",
    "GRADO_EMPLEO_ACTUALIZADO": "Grado/empleo actualizado",
    "GRADO_EMPLEO_ACTIVADO": "Grado/empleo activado",
    "GRADO_EMPLEO_INACTIVADO": "Grado/empleo inactivado",
    "UNIDAD_ORGANIZACIONAL_CREADA": "Unidad organizacional creada",
    "UNIDAD_ORGANIZACIONAL_ACTUALIZADA": "Unidad organizacional actualizada",
    "UNIDAD_ORGANIZACIONAL_ACTIVADA": "Unidad organizacional activada",
    "UNIDAD_ORGANIZACIONAL_INACTIVADA": "Unidad organizacional inactivada",
    "ASIGNACION_CARGO_CREADA": "Asignacion de cargo creada",
    "ASIGNACION_CARGO_ACTUALIZADA": "Asignacion de cargo actualizada",
    "ASIGNACION_CARGO_CERRADA": "Asignacion de cargo cerrada",
    "ASIGNACION_CARGO_INACTIVADA": "Asignacion de cargo inactivada",
    "CATALOGO_CREADO": "Catalogo creado",
    "CATALOGO_ACTUALIZADO": "Catalogo actualizado",
    "CATALOGO_ACTIVADO": "Catalogo activado",
    "CATALOGO_INACTIVADO": "Catalogo inactivado",
    "ESQUEMA_EVALUACION_CREADO": "Esquema de evaluacion creado",
    "ESQUEMA_EVALUACION_ACTUALIZADO": "Esquema de evaluacion actualizado",
    "COMPONENTE_EVALUACION_CREADO": "Componente de evaluacion creado",
    "COMPONENTE_EVALUACION_ACTUALIZADO": "Componente de evaluacion actualizado",
    "CAPTURA_PRELIMINAR_GUARDADA": "Captura preliminar guardada",
    "CAPTURA_PRELIMINAR_ELIMINADA": "Captura preliminar eliminada",
    "CAPTURA_PRELIMINAR_BLOQUEADA": "Captura preliminar bloqueada",
    "ACTA_BORRADOR_GENERADA": "Acta borrador generada",
    "ACTA_BORRADOR_REGENERADA": "Acta borrador regenerada",
    "ACTA_PUBLICADA": "Acta publicada",
    "ACTA_REMITIDA": "Acta remitida",
    "ACTA_VALIDADA_JEFATURA_CARRERA": "Acta validada por jefatura de carrera",
    "ACTA_FORMALIZADA_JEFATURA_ACADEMICA": "Acta formalizada por jefatura academica",
    "ACTA_ACCION_BLOQUEADA": "Accion de acta bloqueada",
    "ACTA_EXPORTADA_REFERENCIA": "Acta exportada como referencia transversal",
    "CONFORMIDAD_ACUSE_REGISTRADO": "Acuse de conformidad registrado",
    "CONFORMIDAD_CONFORME_REGISTRADA": "Conformidad registrada",
    "CONFORMIDAD_INCONFORME_REGISTRADA": "Inconformidad registrada",
    "CONFORMIDAD_RECHAZADA_SIN_COMENTARIO": "Inconformidad rechazada sin comentario",
    "CONFORMIDAD_BLOQUEADA_POR_REMISION": "Conformidad bloqueada por remision",
    "EXTRAORDINARIO_REGISTRADO": "Extraordinario registrado",
    "EXTRAORDINARIO_RECHAZADO": "Extraordinario rechazado",
    "SITUACION_ACADEMICA_REGISTRADA": "Situacion academica registrada",
    "BAJA_TEMPORAL_REGISTRADA": "Baja temporal registrada",
    "BAJA_DEFINITIVA_REGISTRADA": "Baja definitiva registrada",
    "REINGRESO_REGISTRADO": "Reingreso registrado",
    "MOVIMIENTO_ACADEMICO_REGISTRADO": "Movimiento academico registrado",
    "CAMBIO_GRUPO_APLICADO": "Cambio de grupo aplicado",
    "CAMBIO_GRUPO_BLOQUEADO": "Cambio de grupo bloqueado",
    "ADSCRIPCION_ORIGEN_CERRADA": "Adscripcion origen cerrada",
    "ADSCRIPCION_DESTINO_CREADA": "Adscripcion destino creada",
    "INSCRIPCIONES_ORIGEN_DADAS_BAJA": "Inscripciones origen dadas de baja",
    "INSCRIPCIONES_DESTINO_CREADAS": "Inscripciones destino creadas",
    "DIAGNOSTICO_CIERRE_EJECUTADO": "Diagnostico de cierre ejecutado",
    "CIERRE_PERIODO_BLOQUEADO": "Cierre de periodo bloqueado",
    "CIERRE_PERIODO_EJECUTADO": "Cierre de periodo ejecutado",
    "APERTURA_PERIODO_EJECUTADA": "Apertura de periodo ejecutada",
    "APERTURA_PERIODO_BLOQUEADA": "Apertura de periodo bloqueada",
    "PENDIENTES_ASIGNACION_DOCENTE_CONSULTADOS": "Pendientes de asignacion docente consultados",
    "EXPORTACION_SOLICITADA": "Exportacion solicitada",
    "EXPORTACION_GENERADA": "Exportacion generada",
    "EXPORTACION_FALLIDA": "Exportacion fallida",
    "AUDITORIA_EVENTOS_EXPORTADA": "Auditoria de eventos exportada",
}

EVENTO_CHOICES = [(codigo, nombre) for codigo, nombre in sorted(EVENTOS.items())]


def nombre_evento(codigo):
    return EVENTOS.get(codigo, codigo or "")
