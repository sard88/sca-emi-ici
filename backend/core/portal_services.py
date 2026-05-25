from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable

from django.db.models import Count, Q
from django.utils import timezone

from actas.models import ProcesoAperturaPeriodo, ProcesoCierrePeriodo
from catalogos.models import Carrera, GrupoAcademico, PeriodoEscolar, ProgramaAsignatura
from evaluacion.models import (
    Acta,
    CapturaCalificacionPreliminar,
    ConformidadDiscente,
    DetalleActa,
)
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria, MovimientoAcademico
from trayectoria.models import EventoSituacionAcademica, Extraordinario
from usuarios.models import AsignacionCargo, Usuario

from .models import AccesoRapidoUsuario, EventoCalendarioInstitucional, NotificacionUsuario


PERFIL_PRIORIDAD = (
    "ADMIN",
    "ADMIN_SISTEMA",
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "DOCENTE",
    "DISCENTE",
)

ROLES_ESTADISTICA = {"ENCARGADO_ESTADISTICA", "ESTADISTICA"}
ROLES_JEFATURA_CARRERA = {"JEFE_CARRERA", "JEFATURA_CARRERA", "JEFE_SUB_EJEC_CTR"}
ROLES_JEFATURA_ACADEMICA = {"JEFE_ACADEMICO", "JEFATURA_ACADEMICA"}
ROLES_JEFATURA_PEDAGOGICA = {"JEFE_PEDAGOGICA", "JEFE_SUB_PLAN_EVAL"}
ROLES_CONSULTA_AMPLIA = ROLES_ESTADISTICA | ROLES_JEFATURA_ACADEMICA | ROLES_JEFATURA_PEDAGOGICA


@dataclass
class PortalContext:
    user: Usuario
    roles: set[str]
    cargos: list[AsignacionCargo]
    perfil: str | None
    carrera_ids: set[int]
    grupo_ids: set[int]
    discente_ids: set[int]

    @property
    def is_admin(self) -> bool:
        return bool(self.user.is_superuser or self.roles.intersection({"ADMIN", "ADMIN_SISTEMA"}) or self.perfil == "ADMIN")

    @property
    def is_discente(self) -> bool:
        return "DISCENTE" in self.roles or self.perfil == "DISCENTE"

    @property
    def is_docente(self) -> bool:
        return "DOCENTE" in self.roles or self.perfil == "DOCENTE"

    @property
    def is_estadistica(self) -> bool:
        return bool(self.roles.intersection(ROLES_ESTADISTICA) or self.perfil in ROLES_ESTADISTICA)

    @property
    def is_jefatura_carrera(self) -> bool:
        return bool(self.roles.intersection(ROLES_JEFATURA_CARRERA) or self.perfil in ROLES_JEFATURA_CARRERA)

    @property
    def is_jefatura_academica(self) -> bool:
        return bool(self.roles.intersection(ROLES_JEFATURA_ACADEMICA) or self.perfil in ROLES_JEFATURA_ACADEMICA)

    @property
    def is_jefatura_pedagogica(self) -> bool:
        return bool(self.roles.intersection(ROLES_JEFATURA_PEDAGOGICA) or self.perfil in ROLES_JEFATURA_PEDAGOGICA)

    @property
    def has_consulta_amplia(self) -> bool:
        return self.is_admin or self.is_estadistica or self.is_jefatura_academica or self.is_jefatura_pedagogica

    def has_any(self, valores: Iterable[str]) -> bool:
        valores_set = set(valores)
        return bool(self.roles.intersection(valores_set) or (self.perfil in valores_set if self.perfil else False))


def portal_context(user: Usuario) -> PortalContext:
    roles = set(user.groups.values_list("name", flat=True))
    cargos = list(_cargos_vigentes(user))
    codigos_cargo = {cargo.cargo_codigo for cargo in cargos}
    perfil = _perfil_principal(user, roles, codigos_cargo)

    carrera_ids = set()
    for cargo in cargos:
        carrera = cargo.carrera or (cargo.unidad_organizacional.carrera if cargo.unidad_organizacional_id else None)
        if carrera:
            carrera_ids.add(carrera.id)

    discentes = list(user.perfiles_discente.select_related("plan_estudios__carrera").filter(activo=True))
    discente_ids = {discente.id for discente in discentes}
    for discente in discentes:
        carrera_ids.add(discente.plan_estudios.carrera_id)

    grupo_ids = set(
        AdscripcionGrupo.objects.filter(discente_id__in=discente_ids, activo=True).values_list("grupo_academico_id", flat=True)
    )
    grupo_ids.update(
        AsignacionDocente.objects.filter(usuario_docente=user, activo=True).values_list("grupo_academico_id", flat=True)
    )

    return PortalContext(
        user=user,
        roles=roles | codigos_cargo,
        cargos=cargos,
        perfil=perfil,
        carrera_ids=carrera_ids,
        grupo_ids=grupo_ids,
        discente_ids=discente_ids,
    )


def _cargos_vigentes(user):
    hoy = timezone.localdate()
    return (
        AsignacionCargo.objects.filter(
            Q(vigente_desde__isnull=True) | Q(vigente_desde__lte=hoy),
            Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy),
            usuario=user,
            activo=True,
        )
        .select_related("carrera", "unidad_organizacional", "unidad_organizacional__carrera")
        .distinct()
    )


def _perfil_principal(user, roles, codigos_cargo):
    if user.is_superuser:
        return "ADMIN"
    disponibles = set(roles) | set(codigos_cargo)
    for perfil in PERFIL_PRIORIDAD:
        if perfil in disponibles:
            return perfil
    return sorted(roles)[0] if roles else None


def visible_actas_queryset(ctx: PortalContext):
    qs = Acta.objects.select_related(
        "asignacion_docente__usuario_docente",
        "asignacion_docente__grupo_academico__periodo",
        "asignacion_docente__programa_asignatura__materia",
        "asignacion_docente__programa_asignatura__plan_estudios__carrera",
    )
    if ctx.has_consulta_amplia:
        return qs
    if ctx.is_docente:
        return qs.filter(asignacion_docente__usuario_docente=ctx.user)
    if ctx.is_discente and ctx.discente_ids:
        return qs.filter(detalles__inscripcion_materia__discente_id__in=ctx.discente_ids).distinct()
    if ctx.is_jefatura_carrera:
        if ctx.carrera_ids:
            return qs.filter(asignacion_docente__programa_asignatura__plan_estudios__carrera_id__in=ctx.carrera_ids)
        return qs
    return qs.none()


def visible_asignaciones_queryset(ctx: PortalContext):
    qs = AsignacionDocente.objects.select_related(
        "usuario_docente",
        "grupo_academico__periodo",
        "programa_asignatura__materia",
        "programa_asignatura__plan_estudios__carrera",
    )
    if ctx.has_consulta_amplia:
        return qs
    if ctx.is_docente:
        return qs.filter(usuario_docente=ctx.user)
    if ctx.is_jefatura_carrera:
        if ctx.carrera_ids:
            return qs.filter(programa_asignatura__plan_estudios__carrera_id__in=ctx.carrera_ids)
        return qs
    if ctx.is_discente and ctx.grupo_ids:
        return qs.filter(grupo_academico_id__in=ctx.grupo_ids)
    return qs.none()


def visible_inscripciones_queryset(ctx: PortalContext):
    qs = InscripcionMateria.objects.select_related(
        "discente__usuario",
        "asignacion_docente__usuario_docente",
        "asignacion_docente__grupo_academico__periodo",
        "asignacion_docente__programa_asignatura__materia",
        "asignacion_docente__programa_asignatura__plan_estudios__carrera",
    )
    if ctx.has_consulta_amplia:
        return qs
    if ctx.is_discente and ctx.discente_ids:
        return qs.filter(discente_id__in=ctx.discente_ids)
    if ctx.is_docente:
        return qs.filter(asignacion_docente__usuario_docente=ctx.user)
    if ctx.is_jefatura_carrera:
        if ctx.carrera_ids:
            return qs.filter(asignacion_docente__programa_asignatura__plan_estudios__carrera_id__in=ctx.carrera_ids)
        return qs
    return qs.none()


def visible_grupos_queryset(ctx: PortalContext):
    qs = GrupoAcademico.objects.select_related("periodo", "antiguedad__plan_estudios__carrera")
    if ctx.has_consulta_amplia:
        return qs
    if ctx.grupo_ids:
        return qs.filter(id__in=ctx.grupo_ids)
    if ctx.is_jefatura_carrera:
        if ctx.carrera_ids:
            return qs.filter(antiguedad__plan_estudios__carrera_id__in=ctx.carrera_ids)
        return qs
    return qs.none()


def visible_programas_queryset(ctx: PortalContext):
    qs = ProgramaAsignatura.objects.select_related("materia", "plan_estudios__carrera")
    if ctx.has_consulta_amplia:
        return qs
    if ctx.is_docente or ctx.is_discente:
        programa_ids = visible_asignaciones_queryset(ctx).values_list("programa_asignatura_id", flat=True)
        return qs.filter(id__in=programa_ids)
    if ctx.is_jefatura_carrera:
        if ctx.carrera_ids:
            return qs.filter(plan_estudios__carrera_id__in=ctx.carrera_ids)
        return qs
    return qs.none()


def dashboard_resumen(user: Usuario):
    ctx = portal_context(user)
    cards = []
    alertas = []

    def add_card(title, value, description, href=None, backend=True, tone="neutral"):
        cards.append(
            {
                "title": title,
                "value": int(value),
                "description": description,
                "href": href,
                "backend": backend,
                "tone": tone,
            }
        )

    if ctx.is_admin:
        add_card("Usuarios activos", Usuario.objects.filter(is_active=True, estado_cuenta=Usuario.ESTADO_ACTIVO).count(), "Cuentas activas del sistema.", "/admin/usuarios/usuario/", True, "guinda")
        add_card("Cargos vigentes", AsignacionCargo.objects.filter(activo=True).count(), "Asignaciones de cargo activas.", "/admin/usuarios/asignacioncargo/", True, "dorado")
        add_card("Periodos activos", PeriodoEscolar.objects.filter(estado="activo").count(), "Periodos académicos abiertos.", "/actas/periodos/", True, "verde")
        add_card("Notificaciones", NotificacionUsuario.objects.filter(usuario=user, leida=False).count(), "Avisos no leídos.", None, False, "guinda")
    elif ctx.is_docente:
        actas = visible_actas_queryset(ctx)
        add_card("Asignaciones activas", visible_asignaciones_queryset(ctx).filter(activo=True).count(), "Grupos y programas asignados.", "/validacion/docente/asignaciones/", True, "verde")
        add_card("Actas en borrador", actas.filter(estado_acta=Acta.ESTADO_BORRADOR_DOCENTE).count(), "Actas pendientes de publicar.", "/evaluacion/actas/docente/", True, "dorado")
        add_card("Actas publicadas", actas.filter(estado_acta=Acta.ESTADO_PUBLICADO_DISCENTE).count(), "Actas publicadas a discentes.", "/evaluacion/actas/docente/", True, "guinda")
        add_card("Actas remitidas", actas.filter(estado_acta=Acta.ESTADO_REMITIDO_JEFATURA_CARRERA).count(), "Actas enviadas a validación.", "/evaluacion/actas/docente/", True, "verde")
    elif ctx.is_discente:
        inscripciones = visible_inscripciones_queryset(ctx)
        detalles_publicados = DetalleActa.objects.filter(
            inscripcion_materia__in=inscripciones,
            acta__estado_acta=Acta.ESTADO_PUBLICADO_DISCENTE,
        )
        pendientes_conformidad = detalles_publicados.exclude(conformidades__discente_id__in=ctx.discente_ids, conformidades__vigente=True)
        add_card("Asignaturas activas", inscripciones.filter(estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA).count(), "Carga académica vigente.", "/validacion/discente/carga/", True, "verde")
        add_card("Actas publicadas", detalles_publicados.count(), "Actas disponibles para consulta.", "/evaluacion/actas/discente/", True, "guinda")
        add_card("Conformidad pendiente", pendientes_conformidad.count(), "Actas pendientes de acuse o conformidad.", "/evaluacion/actas/discente/", True, "dorado")
        add_card("Historial", EventoSituacionAcademica.objects.filter(discente_id__in=ctx.discente_ids).count(), "Eventos de situación académica propios.", "/trayectoria/mi-historial/", True, "verde")
    elif ctx.is_jefatura_carrera:
        actas = visible_actas_queryset(ctx)
        grupos = visible_grupos_queryset(ctx)
        add_card("Actas por validar", actas.filter(estado_acta=Acta.ESTADO_REMITIDO_JEFATURA_CARRERA).count(), "Pendientes de validación por jefatura.", "/evaluacion/actas/jefatura-carrera/pendientes/", True, "guinda")
        add_card("Grupos activos", grupos.filter(estado="activo").count(), "Grupos académicos del ámbito.", "/admin/catalogos/grupoacademico/", True, "verde")
        add_card("Asignaciones docentes", visible_asignaciones_queryset(ctx).filter(activo=True).count(), "Docentes asignados a grupo y programa.", "/validacion/jefatura/asignaciones-docentes/", True, "dorado")
        add_card("Periodos activos", PeriodoEscolar.objects.filter(estado="activo").count(), "Periodos operativos.", "/actas/periodos/", True, "verde")
    elif ctx.is_jefatura_academica:
        actas = visible_actas_queryset(ctx)
        add_card("Actas por formalizar", actas.filter(estado_acta=Acta.ESTADO_VALIDADO_JEFATURA_CARRERA).count(), "Pendientes de formalización.", "/evaluacion/actas/jefatura-academica/pendientes/", True, "guinda")
        add_card("Formalizadas recientes", actas.filter(estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA).count(), "Actas formalizadas.", "/evaluacion/actas/estadistica/", True, "verde")
        add_card("Periodos activos", PeriodoEscolar.objects.filter(estado="activo").count(), "Periodos en operación.", "/actas/periodos/", True, "dorado")
    elif ctx.is_estadistica:
        actas = visible_actas_queryset(ctx)
        add_card("Periodos activos", PeriodoEscolar.objects.filter(estado="activo").count(), "Periodos abiertos.", "/actas/periodos/", True, "verde")
        add_card("Actas vivas", actas.exclude(estado_acta=Acta.ESTADO_ARCHIVADO).count(), "Actas en flujo operativo.", "/evaluacion/actas/estadistica/", True, "guinda")
        add_card("Cierres registrados", ProcesoCierrePeriodo.objects.count(), "Procesos de cierre ejecutados.", "/actas/periodos/", True, "dorado")
        add_card("Kárdex institucional", DetalleActa.objects.filter(acta__estado_acta=Acta.ESTADO_FORMALIZADO_JEFATURA_ACADEMICA).count(), "Resultados formalizados disponibles.", "/trayectoria/kardex/", True, "verde")
    else:
        add_card("Accesos disponibles", len(accesos_rapidos(user)["items"]), "Accesos configurados para el usuario.", None, False, "verde")

    for card in cards:
        if card["value"] > 0 and any(word in card["title"].lower() for word in ["pendiente", "borrador", "notificaciones"]):
            alertas.append({"titulo": card["title"], "mensaje": card["description"], "prioridad": "NORMAL"})

    return {
        "perfil": ctx.perfil,
        "generado_en": timezone.now().isoformat(),
        "cards": cards,
        "alertas": alertas,
        "quick_accesses": accesos_rapidos(user)["items"],
    }


def accesos_rapidos(user: Usuario):
    ctx = portal_context(user)
    favoritos = list(
        AccesoRapidoUsuario.objects.filter(usuario=user, activo=True).order_by("orden", "etiqueta")[:12]
    )
    if favoritos:
        items = [serialize_acceso_rapido(favorito) for favorito in favoritos]
        return {"persisted": True, "items": items}

    items = []

    def add(label, url, description="", backend=True, icono=""):
        if any(item["label"] == label and item["url"] == url for item in items):
            return
        items.append({"id": None, "label": label, "url": url, "description": description, "backend": backend, "icono": icono})

    if ctx.is_admin:
        add("Usuarios", "/admin/usuarios/usuario/", "Gestión técnica de usuarios.")
        add("Roles y cargos", "/admin/usuarios/asignacioncargo/", "Cargos y unidades.")
        add("Reportes y exportaciones", "/reportes", "Catálogo documental del portal.", False)
        add("Auditoría exportaciones", "/reportes/auditoria", "Trazabilidad institucional.", False)
        add("Django Admin", "/admin/", "Administración técnica.")
    if ctx.is_estadistica or ctx.is_admin:
        add("Periodos", "/actas/periodos/", "Cierre y apertura.")
        add("Kárdex institucional", "/trayectoria/kardex/", "Consulta institucional.")
        add("Reportes y exportaciones", "/reportes", "Actas PDF/XLSX e historial.", False)
    if ctx.is_docente:
        add("Mis asignaciones", "/validacion/docente/asignaciones/", "Carga docente asignada.")
        add("Actas docente", "/evaluacion/actas/docente/", "Actas asociadas.")
        add("Exportar mis actas", "/reportes/actas", "Descarga PDF/XLSX autorizada.", False)
    if ctx.is_discente:
        add("Mi carga académica", "/validacion/discente/carga/", "Asignaturas vigentes.")
        add("Mis actas", "/evaluacion/actas/discente/", "Actas publicadas.")
        add("Mi historial", "/trayectoria/mi-historial/", "Trayectoria propia.")
    if ctx.is_jefatura_carrera:
        add("Asignaciones docentes", "/validacion/jefatura/asignaciones-docentes/", "Asignaciones por grupo.")
        add("Actas por validar", "/evaluacion/actas/jefatura-carrera/pendientes/", "Validación de carrera.")
        add("Actas exportables", "/reportes/actas", "Descarga documental autorizada.", False)
    if ctx.is_jefatura_academica:
        add("Actas por formalizar", "/evaluacion/actas/jefatura-academica/pendientes/", "Formalización académica.")
        add("Reportes y exportaciones", "/reportes", "Catálogo documental.", False)
    if ctx.is_jefatura_pedagogica:
        add("Consulta académica", "/evaluacion/actas/planeacion-evaluacion/consulta/", "Seguimiento académico.")
        add("Reportes y exportaciones", "/reportes", "Catálogo documental.", False)

    return {"persisted": False, "items": items[:12]}


def actividad_reciente(user: Usuario, limit=8):
    ctx = portal_context(user)
    items = []

    for acta in visible_actas_queryset(ctx).order_by("-actualizado_en")[:limit]:
        fecha = acta.formalizada_en or acta.remitida_en or acta.publicada_en or acta.actualizado_en or acta.creado_en
        items.append(
            {
                "id": f"acta-{acta.id}",
                "tipo": "ACTA",
                "titulo": f"Acta {acta.get_estado_acta_display()}",
                "descripcion": f"{acta.asignacion_docente.grupo_academico.clave_grupo} - {acta.asignacion_docente.programa_asignatura.materia.nombre}",
                "fecha": fecha.isoformat() if fecha else None,
                "url": f"/evaluacion/actas/{acta.id}/",
                "backend": True,
            }
        )

    capturas = CapturaCalificacionPreliminar.objects.select_related(
        "inscripcion_materia__discente__usuario",
        "inscripcion_materia__asignacion_docente__usuario_docente",
        "inscripcion_materia__asignacion_docente__programa_asignatura__materia",
    )
    if ctx.is_docente and not ctx.has_consulta_amplia:
        capturas = capturas.filter(inscripcion_materia__asignacion_docente__usuario_docente=user)
    elif ctx.is_discente:
        capturas = capturas.filter(inscripcion_materia__discente_id__in=ctx.discente_ids)
    elif ctx.is_jefatura_carrera and ctx.carrera_ids:
        capturas = capturas.filter(
            inscripcion_materia__asignacion_docente__programa_asignatura__plan_estudios__carrera_id__in=ctx.carrera_ids
        )
    elif not (ctx.has_consulta_amplia or ctx.is_jefatura_carrera):
        capturas = capturas.none()

    for captura in capturas.order_by("-actualizado_en")[:limit]:
        items.append(
            {
                "id": f"captura-{captura.id}",
                "tipo": "CAPTURA",
                "titulo": "Captura preliminar actualizada",
                "descripcion": str(captura.inscripcion_materia.asignacion_docente.programa_asignatura.materia),
                "fecha": captura.actualizado_en.isoformat() if captura.actualizado_en else None,
                "url": "/validacion/docente/asignaciones/",
                "backend": True,
            }
        )

    movimientos = MovimientoAcademico.objects.select_related("discente__usuario", "periodo")
    if ctx.is_discente:
        movimientos = movimientos.filter(discente_id__in=ctx.discente_ids)
    elif ctx.is_jefatura_carrera and ctx.carrera_ids:
        movimientos = movimientos.filter(discente__plan_estudios__carrera_id__in=ctx.carrera_ids)
    elif not ctx.has_consulta_amplia:
        movimientos = movimientos.none()

    for movimiento in movimientos.order_by("-fecha_movimiento")[:limit]:
        items.append(
            {
                "id": f"mov-{movimiento.id}",
                "tipo": "MOVIMIENTO",
                "titulo": movimiento.get_tipo_movimiento_display(),
                "descripcion": f"{movimiento.discente.matricula} - {movimiento.periodo.clave}",
                "fecha": movimiento.fecha_movimiento.isoformat(),
                "url": "/validacion/estadistica/movimientos/",
                "backend": True,
            }
        )

    return sorted(items, key=lambda item: item["fecha"] or "", reverse=True)[:limit]


def eventos_visibles_queryset(user: Usuario):
    ctx = portal_context(user)
    qs = EventoCalendarioInstitucional.objects.filter(visible=True).select_related("periodo", "carrera", "grupo")
    if ctx.is_admin or ctx.is_estadistica or ctx.is_jefatura_academica or ctx.is_jefatura_pedagogica:
        return qs

    candidatos = list(qs)
    visibles = [evento.id for evento in candidatos if _evento_aplica_contexto(evento, ctx)]
    return qs.filter(id__in=visibles)


def eventos_mes(user: Usuario, year: int, month: int):
    start = timezone.datetime(year, month, 1).date()
    end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    qs = eventos_visibles_queryset(user).filter(fecha_inicio__lte=end).filter(Q(fecha_fin__isnull=True, fecha_inicio__gte=start) | Q(fecha_fin__gte=start))
    eventos = [serialize_evento(evento) for evento in qs.order_by("fecha_inicio", "titulo")]
    dias = sorted({evento["fecha_inicio"] for evento in eventos})
    return {"year": year, "month": month, "dias_con_eventos": dias, "eventos": eventos}


def eventos_proximos(user: Usuario, limit=6):
    hoy = timezone.localdate()
    qs = eventos_visibles_queryset(user).filter(Q(fecha_fin__isnull=True, fecha_inicio__gte=hoy) | Q(fecha_fin__gte=hoy))
    return [serialize_evento(evento) for evento in qs.order_by("fecha_inicio", "titulo")[:limit]]


def _evento_aplica_contexto(evento, ctx: PortalContext):
    roles_destino = set(evento.roles_destino or [])
    if roles_destino and not ctx.roles.intersection(roles_destino) and ctx.perfil not in roles_destino:
        return False
    if evento.carrera_id and ctx.carrera_ids and evento.carrera_id not in ctx.carrera_ids:
        return False
    if evento.carrera_id and not ctx.carrera_ids and (ctx.is_discente or ctx.is_docente or ctx.is_jefatura_carrera):
        return False
    if evento.grupo_id and ctx.grupo_ids and evento.grupo_id not in ctx.grupo_ids:
        return False
    if evento.grupo_id and not ctx.grupo_ids and (ctx.is_discente or ctx.is_docente):
        return False
    return True


def busqueda(user: Usuario, query: str):
    ctx = portal_context(user)
    q = (query or "").strip()
    if len(q) < 2:
        return {"query": q, "min_chars": 2, "groups": []}

    groups = []

    def add_group(label, items):
        if items:
            groups.append({"label": label, "items": items[:8]})

    if ctx.has_consulta_amplia or ctx.is_jefatura_carrera:
        usuarios = Usuario.objects.filter(Q(username__icontains=q) | Q(nombre_completo__icontains=q) | Q(correo__icontains=q)).order_by("username")[:8]
        add_group("Usuarios", [serialize_resultado("usuario", u.nombre_visible, u.username, f"/admin/usuarios/usuario/{u.id}/change/", True) for u in usuarios])
    elif ctx.is_discente:
        add_group("Mi perfil", [serialize_resultado("usuario", user.nombre_visible, user.username, "/perfil", False)])

    discentes = Discente.objects.select_related("usuario", "plan_estudios__carrera").filter(
        Q(matricula__icontains=q) | Q(usuario__nombre_completo__icontains=q) | Q(usuario__username__icontains=q)
    )
    if ctx.is_discente:
        discentes = discentes.filter(id__in=ctx.discente_ids)
    elif ctx.is_docente:
        discentes = discentes.filter(inscripciones_materia__asignacion_docente__usuario_docente=user).distinct()
    elif ctx.is_jefatura_carrera and ctx.carrera_ids:
        discentes = discentes.filter(plan_estudios__carrera_id__in=ctx.carrera_ids)
    elif not ctx.has_consulta_amplia and not ctx.is_jefatura_carrera:
        discentes = discentes.none()
    add_group("Discentes", [serialize_resultado("discente", d.usuario.nombre_visible, d.matricula, "/validacion/estadistica/carga/", True) for d in discentes[:8]])

    grupos = visible_grupos_queryset(ctx).filter(Q(clave_grupo__icontains=q) | Q(periodo__clave__icontains=q)).order_by("clave_grupo")[:8]
    add_group("Grupos", [serialize_resultado("grupo", g.clave_grupo, str(g.periodo), "/admin/catalogos/grupoacademico/", True) for g in grupos])

    programas = visible_programas_queryset(ctx).filter(Q(materia__clave__icontains=q) | Q(materia__nombre__icontains=q)).order_by("materia__clave")[:8]
    add_group("Programas de asignatura", [serialize_resultado("programa", p.materia.nombre, p.materia.clave, "/admin/catalogos/programaasignatura/", True) for p in programas])

    actas = visible_actas_queryset(ctx).filter(
        Q(asignacion_docente__programa_asignatura__materia__nombre__icontains=q)
        | Q(asignacion_docente__programa_asignatura__materia__clave__icontains=q)
        | Q(asignacion_docente__grupo_academico__clave_grupo__icontains=q)
    ).order_by("-actualizado_en")[:8]
    add_group("Actas", [serialize_resultado("acta", f"Acta {a.get_corte_codigo_display()}", a.asignacion_docente.programa_asignatura.materia.nombre, f"/evaluacion/actas/{a.id}/", True) for a in actas])

    periodos = PeriodoEscolar.objects.filter(Q(clave__icontains=q) | Q(anio_escolar__icontains=q)).order_by("-anio_escolar")[:8]
    if ctx.has_consulta_amplia or ctx.is_jefatura_carrera:
        add_group("Periodos", [serialize_resultado("periodo", p.clave, p.get_estado_display(), "/actas/periodos/", True) for p in periodos])

    if not ctx.is_discente and (ctx.has_consulta_amplia or ctx.is_jefatura_carrera):
        add_group("Kárdex institucional", [serialize_resultado("kardex", "Kárdex institucional", "Vista oficial derivada", "/trayectoria/kardex/", True)])

    return {"query": q, "min_chars": 2, "groups": groups}


def serialize_resultado(tipo, title, subtitle, url, backend):
    return {"type": tipo, "title": title, "subtitle": subtitle, "url": url, "backend": backend}


def serialize_notificacion(notificacion: NotificacionUsuario):
    return {
        "id": notificacion.id,
        "tipo": notificacion.tipo,
        "tipo_label": notificacion.get_tipo_display(),
        "titulo": notificacion.titulo,
        "mensaje": notificacion.mensaje,
        "url_destino": notificacion.url_destino,
        "prioridad": notificacion.prioridad,
        "prioridad_label": notificacion.get_prioridad_display(),
        "leida": notificacion.leida,
        "creada_en": notificacion.creada_en.isoformat() if notificacion.creada_en else None,
        "leida_en": notificacion.leida_en.isoformat() if notificacion.leida_en else None,
    }


def serialize_evento(evento: EventoCalendarioInstitucional):
    return {
        "id": evento.id,
        "titulo": evento.titulo,
        "descripcion": evento.descripcion,
        "tipo_evento": evento.tipo_evento,
        "tipo_evento_label": evento.get_tipo_evento_display(),
        "fecha_inicio": evento.fecha_inicio.isoformat(),
        "fecha_fin": evento.fecha_fin.isoformat() if evento.fecha_fin else None,
        "periodo": evento.periodo.clave if evento.periodo_id else None,
        "carrera": evento.carrera.clave if evento.carrera_id else None,
        "grupo": evento.grupo.clave_grupo if evento.grupo_id else None,
        "roles_destino": evento.roles_destino or [],
        "url_destino": evento.url_destino,
    }


def serialize_acceso_rapido(acceso: AccesoRapidoUsuario):
    return {
        "id": acceso.id,
        "label": acceso.etiqueta,
        "url": acceso.url,
        "description": "Acceso guardado por el usuario.",
        "backend": acceso.url.startswith("/admin") or acceso.url.startswith("/evaluacion") or acceso.url.startswith("/trayectoria") or acceso.url.startswith("/actas") or acceso.url.startswith("/validacion"),
        "icono": acceso.icono,
    }


def estado_basico_sistema():
    return {
        "usuarios_activos": Usuario.objects.filter(is_active=True, estado_cuenta=Usuario.ESTADO_ACTIVO).count(),
        "periodos_activos": PeriodoEscolar.objects.filter(estado="activo").count(),
        "notificaciones_pendientes": NotificacionUsuario.objects.filter(leida=False).count(),
    }
