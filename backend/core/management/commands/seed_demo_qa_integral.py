import os
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from auditoria.eventos import MODULO_AUTENTICACION, RESULTADO_EXITOSO, SEVERIDAD_INFO
from auditoria.models import BitacoraEventoCritico
from catalogos.models import (
    ESTADO_ACTIVO,
    ESTADO_CERRADO,
    ESTADO_PLANIFICADO,
    Antiguedad,
    Carrera,
    GrupoAcademico,
    Materia,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
)
from evaluacion.models import Acta, CapturaCalificacionPreliminar, ComponenteEvaluacion, ConformidadDiscente, EsquemaEvaluacion
from evaluacion.services import (
    crear_o_regenerar_borrador_acta,
    formalizar_acta_jefatura_academica,
    publicar_acta,
    registrar_conformidad_discente,
    remitir_acta,
    validar_acta_jefatura_carrera,
)
from relaciones.models import AdscripcionGrupo, AsignacionDocente, Discente, InscripcionMateria, MovimientoAcademico
from trayectoria.models import CatalogoResultadoAcademico, CatalogoSituacionAcademica, EventoSituacionAcademica, Extraordinario
from usuarios.models import AsignacionCargo, GradoEmpleo, UnidadOrganizacional, Usuario


QA_CAREERS = {
    "ICI": "Ingeniería en Computación e Informática",
    "ICE": "Ingeniería en Comunicaciones y Electrónica",
    "IC": "Ingeniería Civil",
    "II": "Ingeniería Industrial",
}

SIZE_CONFIG = {
    "small": {"antiguedades": 2, "semestres": 4, "grupos": 1, "discentes": 3, "materias": 2, "docentes": 2},
    "medium": {"antiguedades": 3, "semestres": 8, "grupos": 2, "discentes": 5, "materias": 3, "docentes": 3},
    "full": {"antiguedades": 5, "semestres": 12, "grupos": 2, "discentes": 5, "materias": 5, "docentes": 3},
}


@dataclass
class SeedStats:
    created: int = 0
    reused: int = 0
    updated: int = 0
    omitted: int = 0
    errors: list[str] = field(default_factory=list)
    credentials: list[tuple[str, str]] = field(default_factory=list)

    def add(self, created: bool):
        if created:
            self.created += 1
        else:
            self.reused += 1


class Command(BaseCommand):
    help = "Crea un dataset QA integral, idempotente y ficticio para demo/E2E por rol."

    def add_arguments(self, parser):
        parser.add_argument("--size", choices=SIZE_CONFIG.keys(), default="medium")
        parser.add_argument("--reset-qa", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--print-credentials", action="store_true")

    def handle(self, *args, **options):
        self.size = options["size"]
        self.config = SIZE_CONFIG[self.size]
        self.dry_run = options["dry_run"]
        self.password = os.environ.get("DEMO_QA_PASSWORD", "DemoQA2026!")
        self.stats = SeedStats()

        self.stdout.write("Contraseña demo solo para ambiente local. No usar en producción.")
        if self.dry_run:
            self._print_plan()
            return

        with transaction.atomic():
            if options["reset_qa"]:
                self._reset_qa()
            self._seed()

        self._print_summary(options["print_credentials"])

    def _print_plan(self):
        c = self.config
        grupos = len(QA_CAREERS) * c["semestres"] * c["grupos"]
        discentes = grupos * c["discentes"]
        materias = len(QA_CAREERS) * c["semestres"] * c["materias"]
        self.stdout.write(f"DRY-RUN Bloque 11A size={self.size}")
        self.stdout.write(f"Carreras QA: {len(QA_CAREERS)}")
        self.stdout.write(f"Grupos QA estimados: {grupos}")
        self.stdout.write(f"Discentes QA estimados: {discentes}")
        self.stdout.write(f"Materias/programas QA estimados: {materias}")
        self.stdout.write("No se escribió información en base de datos.")

    def _reset_qa(self):
        # El reset borra o inactiva únicamente objetos QA por prefijo. Se ordena de hojas a raíces.
        qs_prefix = {
            Usuario: {"username__startswith": "qa_"},
            Carrera: {"clave__startswith": "QA_"},
            Materia: {"clave__startswith": "QA_"},
            PeriodoEscolar: {"clave__startswith": "QA_"},
            GradoEmpleo: {"clave__startswith": "QA_"},
            UnidadOrganizacional: {"clave__startswith": "QA_"},
            CatalogoSituacionAcademica: {"clave__startswith": "QA_"},
            CatalogoResultadoAcademico: {"clave__startswith": "QA_"},
        }
        actas = Acta.objects.filter(asignacion_docente__grupo_academico__clave_grupo__startswith="QA_")
        self.stats.omitted += actas.update(estado_acta=Acta.ESTADO_ARCHIVADO, archivada_en=timezone.now())
        for model, lookup in qs_prefix.items():
            if hasattr(model, "activo"):
                self.stats.omitted += model.objects.filter(**lookup).update(activo=False)
            elif model is Usuario:
                self.stats.omitted += model.objects.filter(**lookup).update(is_active=False, estado_cuenta=Usuario.ESTADO_INACTIVO)

    def _seed(self):
        self._ensure_groups()
        self._ensure_catalogs()
        self._ensure_grades()
        self._ensure_users()
        self._ensure_units_and_positions()
        self._ensure_academic_structure()
        self._ensure_operational_data()
        self._ensure_trajectory_and_audit()

    def _ensure_groups(self):
        for name in ["ADMIN", "ADMINISTRADOR", "ESTADISTICA", "DOCENTE", "DISCENTE", "JEFE_CARRERA", "JEFATURA_CARRERA", "JEFE_ACADEMICO", "JEFATURA_ACADEMICA", "JEFE_PEDAGOGICA"]:
            _, created = Group.objects.get_or_create(name=name)
            self.stats.add(created)

    def _ensure_catalogs(self):
        for clave, nombre in {
            "QA_ACTIVO": "QA Activo",
            "QA_BAJA_TEMPORAL": "QA Baja temporal",
            "QA_REINGRESO": "QA Reingreso",
        }.items():
            _, created = CatalogoSituacionAcademica.objects.update_or_create(clave=clave, defaults={"nombre": nombre, "activo": True})
            self.stats.add(created)
        for clave, nombre in {
            "QA_APROBADO": "QA Aprobado",
            "QA_REPROBADO": "QA Reprobado",
            "QA_EE": "QA Aprobado por extraordinario",
        }.items():
            _, created = CatalogoResultadoAcademico.objects.update_or_create(clave=clave, defaults={"nombre": nombre, "activo": True})
            self.stats.add(created)

    def _ensure_grades(self):
        data = [
            ("QA_SBTTE_PAS_ICI", "Sbtte. Pas. I.C.I.", "Subteniente pasante ICI", GradoEmpleo.TIPO_MILITAR_ACTIVO),
            ("QA_SBTTE_PAS_ICE", "Sbtte. Pas. I.C.E.", "Subteniente pasante ICE", GradoEmpleo.TIPO_MILITAR_ACTIVO),
            ("QA_SBTTE_PAS_IC", "Sbtte. Pas. I.C.", "Subteniente pasante IC", GradoEmpleo.TIPO_MILITAR_ACTIVO),
            ("QA_SBTTE_PAS_II", "Sbtte. Pas. I.I.", "Subteniente pasante II", GradoEmpleo.TIPO_MILITAR_ACTIVO),
            ("QA_TTE_DOC", "Tte.", "Teniente docente QA", GradoEmpleo.TIPO_MILITAR_ACTIVO),
            ("QA_CAP_DOC", "Cap.", "Capitán docente QA", GradoEmpleo.TIPO_MILITAR_ACTIVO),
            ("QA_CIVIL_DOCENTE", "Civil", "Docente civil QA", GradoEmpleo.TIPO_CIVIL),
        ]
        self.grades = {}
        for clave, abreviatura, nombre, tipo in data:
            obj, created = GradoEmpleo.objects.update_or_create(clave=clave, defaults={"abreviatura": abreviatura, "nombre": nombre, "tipo": tipo, "activo": True})
            self.grades[clave] = obj
            self.stats.add(created)

    def _user(self, username, group_names, full_name, grade=None, superuser=False):
        user, created = Usuario.objects.get_or_create(username=username, defaults={"nombre_completo": full_name, "correo": f"{username}@qa.local", "email": f"{username}@qa.local"})
        user.nombre_completo = full_name
        user.correo = f"{username}@qa.local"
        user.email = user.correo
        user.estado_cuenta = Usuario.ESTADO_ACTIVO
        user.is_active = True
        user.is_staff = superuser
        user.is_superuser = superuser
        if grade:
            user.grado_empleo = grade
        user.set_password(self.password)
        user.save()
        user.groups.set([Group.objects.get(name=name) for name in group_names])
        self.stats.add(created)
        self.stats.credentials.append((username, ", ".join(group_names)))
        return user

    def _ensure_users(self):
        self.users = {
            "admin": self._user("qa_admin", ["ADMIN", "ADMINISTRADOR"], "QA Administrador General", self.grades["QA_CAP_DOC"], True),
            "estadistica": self._user("qa_estadistica", ["ESTADISTICA"], "QA Estadística Institucional", self.grades["QA_CIVIL_DOCENTE"]),
            "jefatura_academica": self._user("qa_jefatura_academica", ["JEFE_ACADEMICO", "JEFATURA_ACADEMICA"], "QA Jefatura Académica", self.grades["QA_CAP_DOC"]),
            "jefatura_pedagogica": self._user("qa_jefatura_pedagogica", ["JEFE_PEDAGOGICA"], "QA Jefatura Pedagógica", self.grades["QA_CAP_DOC"]),
        }
        self.users["jefes_carrera"] = {}
        self.users["docentes"] = {}
        for code in QA_CAREERS:
            self.users["jefes_carrera"][code] = self._user(f"qa_jefe_carrera_{code.lower()}", ["JEFE_CARRERA", "JEFATURA_CARRERA"], f"QA Jefe Carrera {code}", self.grades["QA_CAP_DOC"])
            self.users["docentes"][code] = [
                self._user(f"qa_docente_{code.lower()}_{i:02d}", ["DOCENTE"], f"QA Docente {code} {i:02d}", self.grades["QA_TTE_DOC" if i % 2 else "QA_CIVIL_DOCENTE"])
                for i in range(1, self.config["docentes"] + 1)
            ]

    def _ensure_units_and_positions(self):
        sec_acad, created = UnidadOrganizacional.objects.get_or_create(
            clave=UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
            defaults={
                "nombre": "Sección Académica",
                "tipo_unidad": UnidadOrganizacional.TIPO_SECCION,
                "padre": None,
                "carrera": None,
                "activo": True,
                "orden": 10,
            },
        )
        self.stats.add(created)
        sec_ped, created = UnidadOrganizacional.objects.get_or_create(
            clave=UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA,
            defaults={
                "nombre": "Sección Pedagógica",
                "tipo_unidad": UnidadOrganizacional.TIPO_SECCION,
                "padre": None,
                "carrera": None,
                "activo": True,
                "orden": 20,
            },
        )
        self.stats.add(created)
        self.units = {"acad": sec_acad, "ped": sec_ped, "career": {}}
        self._cargo(self.users["jefatura_academica"], AsignacionCargo.CARGO_JEFE_ACADEMICO, sec_acad, tipo=AsignacionCargo.DESIGNACION_ACCIDENTAL)
        self._cargo(self.users["jefatura_pedagogica"], AsignacionCargo.CARGO_JEFE_PEDAGOGICA, sec_ped, tipo=AsignacionCargo.DESIGNACION_ACCIDENTAL)

    def _cargo(self, user, cargo, unidad, carrera=None, tipo=AsignacionCargo.DESIGNACION_TITULAR):
        obj, created = AsignacionCargo.objects.update_or_create(
            usuario=user,
            cargo_codigo=cargo,
            unidad_organizacional=unidad,
            defaults={
                "carrera": carrera,
                "tipo_designacion": tipo,
                "activo": True,
                "vigente_desde": timezone.localdate(),
                "vigente_hasta": date(2027, 12, 31) if tipo == AsignacionCargo.DESIGNACION_ACCIDENTAL else None,
            },
        )
        self.stats.add(created)
        return obj

    def _ensure_academic_structure(self):
        self.careers = {}
        self.plans = {}
        self.antiguedades = {}
        self.periods = {}
        for clave, year, acad, start, end, estado in [
            ("QA_2025_2", "2025-2026", 2, date(2026, 1, 15), date(2026, 7, 15), ESTADO_CERRADO),
            ("QA_2026_1", "2026-2027", 1, date(2026, 8, 1), date(2026, 12, 15), ESTADO_ACTIVO),
            ("QA_2026_2", "2026-2027", 2, date(2027, 1, 15), date(2027, 7, 15), ESTADO_PLANIFICADO),
        ]:
            p, created = PeriodoEscolar.objects.update_or_create(clave=clave, defaults={"anio_escolar": year, "periodo_academico": acad, "fecha_inicio": start, "fecha_fin": end, "estado": estado})
            self.periods[clave] = p
            self.stats.add(created)

        self.groups = []
        self.programs = {}
        for code, name in QA_CAREERS.items():
            career, created = Carrera.objects.update_or_create(clave=f"QA_{code}", defaults={"nombre": name, "estado": ESTADO_ACTIVO})
            self.careers[code] = career
            self.stats.add(created)
            plan, created = PlanEstudios.objects.update_or_create(carrera=career, clave=f"QA_PLAN_{code}_2026", defaults={"nombre": f"Plan QA {code} 2026", "version": "2026", "estado": ESTADO_ACTIVO})
            self.plans[code] = plan
            self.stats.add(created)
            self.antiguedades[code] = []
            for idx in range(self.config["antiguedades"]):
                year = 2026 - idx
                ant, created = Antiguedad.objects.update_or_create(plan_estudios=plan, clave=f"QA_ANT_{code}_{year}", defaults={"nombre": f"QA Antigüedad {code} {year}", "anio_inicio": year, "anio_fin": year + 4, "estado": ESTADO_ACTIVO})
                self.antiguedades[code].append(ant)
                self.stats.add(created)
            unidad, created = UnidadOrganizacional.objects.update_or_create(clave=f"QA_SUB_EJEC_CTRL_{code}", defaults={"nombre": f"QA Subsección Ejecución y Control {code}", "tipo_unidad": UnidadOrganizacional.TIPO_SUBSECCION, "padre": self.units["acad"], "carrera": career, "activo": True, "orden": 30})
            self.units["career"][code] = unidad
            self.stats.add(created)
            self._cargo(self.users["jefes_carrera"][code], AsignacionCargo.CARGO_JEFE_CARRERA, unidad, career)
            self._create_programs_and_groups(code, plan)

    def _create_programs_and_groups(self, code, plan):
        self.programs[code] = {}
        for sem in range(1, self.config["semestres"] + 1):
            self.programs[code][sem] = []
            for num in range(1, self.config["materias"] + 1):
                mat, created = Materia.objects.update_or_create(clave=f"QA_{code}_S{sem:02d}_M{num:02d}", defaults={"nombre": f"QA {code} Semestre {sem} Asignatura {num}", "estado": ESTADO_ACTIVO, "horas_totales": 64})
                self.stats.add(created)
                prog, created = ProgramaAsignatura.objects.update_or_create(plan_estudios=plan, materia=mat, defaults={"semestre_numero": sem, "obligatoria": True, "ubicacion_excepcional": False})
                self.programs[code][sem].append(prog)
                self.stats.add(created)
                self._ensure_scheme(prog, sem, num)
            for gidx in range(self.config["grupos"]):
                suffix = chr(ord("A") + gidx)
                ant = self.antiguedades[code][min(gidx, len(self.antiguedades[code]) - 1)]
                grupo, created = GrupoAcademico.objects.update_or_create(antiguedad=ant, periodo=self.periods["QA_2026_1"], clave_grupo=f"QA_{code}_{sem}{suffix}", defaults={"semestre_numero": sem, "estado": ESTADO_ACTIVO, "cupo_maximo": 40})
                self.groups.append((code, grupo))
                self.stats.add(created)

    def _ensure_scheme(self, programa, sem, num):
        parciales = [3, 2, 1, 3][(sem + num) % 4]
        esquema, created = EsquemaEvaluacion.objects.update_or_create(
            programa_asignatura=programa,
            version="QA_V1",
            defaults={"num_parciales": parciales, "permite_exencion": parciales in (2, 3) and num % 2 == 1, "peso_parciales": Decimal("45.00"), "peso_final": Decimal("55.00"), "umbral_exencion": Decimal("9.00"), "activo": True},
        )
        self.stats.add(created)
        components = {
            "P1": [("Participación", 10), ("Tareas", 20), ("Proyecto", 20), ("Examen parcial", 50)],
            "P2": [("Participación", 10), ("Trabajo extraclase", 20), ("Proyecto", 20), ("Examen parcial", 50)],
            "P3": [("Participación", 10), ("Portafolio", 10), ("Proyecto investigación", 15), ("Examen parcial", 65)],
            "FINAL": [("Trabajo extraclase", 15), ("Proyecto investigación", 15), ("Examen final", 70)],
        }
        for corte in esquema.cortes_esperados():
            for order, (name, pct) in enumerate(components[corte], start=1):
                _, created = ComponenteEvaluacion.objects.update_or_create(esquema=esquema, corte_codigo=corte, orden=order, defaults={"nombre": name, "porcentaje": Decimal(str(pct)), "es_examen": corte == "FINAL" and "Examen" in name})
                self.stats.add(created)

    def _ensure_operational_data(self):
        self.discentes_by_group = {}
        self.assignments = []
        for code, grupo in self.groups:
            discentes = []
            for idx in range(1, self.config["discentes"] + 1):
                uname = f"qa_discente_{code.lower()}_{grupo.semestre_numero}{grupo.clave_grupo[-1].lower()}_{idx:02d}"
                user = self._user(uname, ["DISCENTE"], f"QA Discente {code} {grupo.semestre_numero}{grupo.clave_grupo[-1]} {idx:02d}", self.grades[f"QA_SBTTE_PAS_{code}"])
                discente, created = Discente.objects.update_or_create(usuario=user, defaults={"matricula": f"QA-MAT-{code}-{grupo.semestre_numero}{grupo.clave_grupo[-1]}-{idx:03d}", "plan_estudios": grupo.antiguedad.plan_estudios, "antiguedad": grupo.antiguedad, "situacion_actual": Discente.SITUACION_REGULAR, "activo": True})
                discentes.append(discente)
                self.stats.add(created)
                _, created = AdscripcionGrupo.objects.update_or_create(discente=discente, grupo_academico=grupo, defaults={"activo": True})
                self.stats.add(created)
            self.discentes_by_group[grupo.id] = discentes
            for pidx, programa in enumerate(self.programs[code][grupo.semestre_numero], start=1):
                docente = self.users["docentes"][code][(pidx - 1) % len(self.users["docentes"][code])]
                asignacion, created = AsignacionDocente.objects.update_or_create(grupo_academico=grupo, programa_asignatura=programa, defaults={"usuario_docente": docente, "activo": True})
                self.assignments.append(asignacion)
                self.stats.add(created)
        self._ensure_grades_and_actas()

    def _ensure_grades_and_actas(self):
        if not self.assignments:
            return
        jefatura = self.users["jefatura_academica"]
        for idx, asignacion in enumerate(self.assignments[:12]):
            self._capture_assignment(asignacion, exento=idx % 5 == 1, reprobado=idx % 5 == 2, incompleto=idx % 5 == 3)
            corte = "FINAL" if idx % 2 == 0 else "P1"
            try:
                existente = Acta.objects.filter(asignacion_docente=asignacion, corte_codigo=corte).exclude(estado_acta=Acta.ESTADO_ARCHIVADO).first()
                if existente and existente.estado_acta != Acta.ESTADO_BORRADOR_DOCENTE:
                    self.stats.reused += 1
                    continue
                acta = crear_o_regenerar_borrador_acta(asignacion, corte, asignacion.usuario_docente)
                if idx % 5 == 3:
                    continue
                if idx % 5 >= 0:
                    publicar_acta(acta, asignacion.usuario_docente)
                if idx % 5 == 0:
                    first = acta.detalles.select_related("inscripcion_materia__discente__usuario").first()
                    registrar_conformidad_discente(first, first.inscripcion_materia.discente.usuario, ConformidadDiscente.ESTADO_INCONFORME, "QA solicita revisión de la calificación publicada.")
                if idx % 5 in (0, 1, 2):
                    remitir_acta(acta, asignacion.usuario_docente)
                    validar_acta_jefatura_carrera(acta, self.users["jefes_carrera"][asignacion.programa_asignatura.plan_estudios.carrera.clave.replace("QA_", "")])
                if idx % 5 in (1, 2):
                    formalizar_acta_jefatura_academica(acta, jefatura)
                    if acta.es_final:
                        self._maybe_extraordinario(acta)
            except Exception as exc:  # noqa: BLE001 - seed QA debe reportar y continuar.
                self.stats.errors.append(f"Acta {asignacion.id}-{corte}: {exc}")

    def _capture_assignment(self, asignacion, exento=False, reprobado=False, incompleto=False):
        esquema = EsquemaEvaluacion.objects.filter(programa_asignatura=asignacion.programa_asignatura, activo=True).first()
        componentes = list(esquema.componentes.all())
        for insc in asignacion.inscripciones_materia.filter(estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA):
            for comp in componentes:
                if incompleto and comp.corte_codigo == "FINAL" and comp.orden == 3:
                    continue
                base = Decimal("9.4") if exento else Decimal("5.2") if reprobado else Decimal("8.1")
                valor = min(Decimal("10.0"), base + Decimal(str((insc.id + comp.orden) % 4)) / Decimal("10"))
                _, created = CapturaCalificacionPreliminar.objects.update_or_create(inscripcion_materia=insc, componente=comp, defaults={"valor": valor, "capturado_por": asignacion.usuario_docente})
                self.stats.add(created)

    def _maybe_extraordinario(self, acta):
        detalle = acta.detalles.select_related("inscripcion_materia").filter(inscripcion_materia__calificacion_final__lt=Decimal("6.0")).first()
        if not detalle:
            return
        _, created = Extraordinario.objects.update_or_create(inscripcion_materia=detalle.inscripcion_materia, defaults={"calificacion": Decimal("7.0"), "registrado_por": self.users["estadistica"]})
        self.stats.add(created)

    def _ensure_trajectory_and_audit(self):
        situacion = CatalogoSituacionAcademica.objects.get(clave="QA_BAJA_TEMPORAL")
        for discente in Discente.objects.filter(matricula__startswith="QA-MAT-")[:6]:
            _, created = EventoSituacionAcademica.objects.update_or_create(discente=discente, situacion=situacion, periodo=self.periods["QA_2026_1"], defaults={"motivo": "QA evento de trayectoria ficticio.", "registrado_por": self.users["estadistica"]})
            self.stats.add(created)
        groups = list(GrupoAcademico.objects.filter(clave_grupo__in=["QA_ICI_4A", "QA_ICI_4B"]))
        if len(groups) == 2:
            discente = self.discentes_by_group.get(groups[0].id, [None])[0]
            if discente:
                MovimientoAcademico.objects.get_or_create(discente=discente, periodo=self.periods["QA_2026_1"], tipo_movimiento=MovimientoAcademico.CAMBIO_GRUPO, grupo_origen=groups[0], grupo_destino=groups[1], defaults={"observaciones": "QA cambio de grupo controlado."})
        BitacoraEventoCritico.objects.get_or_create(
            modulo=MODULO_AUTENTICACION,
            evento_codigo="LOGIN_EXITOSO",
            usuario=self.users["admin"],
            objeto_tipo="QA_SEED",
            objeto_id="BLOQUE_11A",
            defaults={
                "username_snapshot": self.users["admin"].username,
                "nombre_usuario_snapshot": self.users["admin"].nombre_visible,
                "evento_nombre": "Login exitoso",
                "severidad": SEVERIDAD_INFO,
                "resultado": RESULTADO_EXITOSO,
                "resumen": "Evento QA generado por seed integral.",
                "metadatos_json": {"qa": True, "bloque": "11A"},
            },
        )

    def _print_summary(self, print_credentials):
        self.stdout.write(self.style.SUCCESS("Dataset QA integral preparado."))
        self.stdout.write(f"size={self.size}")
        self.stdout.write(f"creados={self.stats.created} reutilizados={self.stats.reused} actualizados={self.stats.updated} omitidos={self.stats.omitted} errores={len(self.stats.errors)}")
        if self.stats.errors:
            for error in self.stats.errors[:20]:
                self.stdout.write(self.style.WARNING(error))
        self.stdout.write("Usuarios demo:")
        for username, roles in sorted(set(self.stats.credentials)):
            self.stdout.write(f"- {username}: {roles}")
        if print_credentials:
            self.stdout.write("Password demo local: usar DEMO_QA_PASSWORD o fallback local documentado.")
