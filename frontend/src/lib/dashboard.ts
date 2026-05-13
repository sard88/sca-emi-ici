import type { AuthenticatedUser } from "./types";

export type DashboardCardItem = {
  title: string;
  description: string;
  href?: string;
  backend?: boolean;
  badge?: string;
  value?: number;
  tone?: "neutral" | "guinda" | "dorado" | "verde";
};

export type DashboardProfile = {
  key: string;
  title: string;
  description: string;
  allowed: string[];
  cards: DashboardCardItem[];
};

export const dashboardProfiles: Record<string, DashboardProfile> = {
  admin: {
    key: "ADMIN",
    title: "Administrador",
    description: "Soporte técnico, usuarios, roles, cargos y estado institucional del sistema.",
    allowed: ["ADMIN", "ADMIN_SISTEMA"],
    cards: [
      { title: "Usuarios", description: "Gestión técnica de usuarios y perfiles.", href: "/admin/usuarios/usuario/", backend: true },
      { title: "Roles y cargos", description: "Grupos, cargos y unidades organizacionales.", href: "/admin/usuarios/asignacioncargo/", backend: true },
      { title: "Unidades organizacionales", description: "Secciones y subsecciones institucionales.", href: "/admin/usuarios/unidadorganizacional/", backend: true },
      { title: "Django Admin", description: "Administración técnica completa.", href: "/admin/", backend: true },
      { title: "Estado técnico", description: "Health check del backend.", href: "/health/", backend: true },
    ],
  },
  estadistica: {
    key: "ESTADISTICA",
    title: "Estadística",
    description: "Consulta, consolidación, cierre y apertura de periodos académicos.",
    allowed: ["ENCARGADO_ESTADISTICA", "ESTADISTICA"],
    cards: [
      { title: "Catálogos", description: "Consulta de estructura académica.", href: "/admin/catalogos/", backend: true },
      { title: "Periodos", description: "Periodos escolares y estado operativo.", href: "/actas/periodos/", backend: true },
      { title: "Cierre y apertura", description: "Flujo operativo del Bloque 8.5.", href: "/actas/periodos/", backend: true },
      { title: "Historial", description: "Consulta institucional de trayectoria.", href: "/trayectoria/historial/", backend: true },
      { title: "Kárdex institucional", description: "Vista oficial derivada, no visible para discentes.", href: "/trayectoria/kardex/", backend: true },
      { title: "Reportes", description: "Pendiente de Bloque 9.", badge: "Pendiente" },
    ],
  },
  docente: {
    key: "DOCENTE",
    title: "Docente",
    description: "Asignaciones docentes, captura preliminar y actas asociadas.",
    allowed: ["DOCENTE"],
    cards: [
      { title: "Mis asignaciones", description: "Grupos y programas asignados.", href: "/validacion/docente/asignaciones/", backend: true },
      { title: "Captura de calificaciones", description: "Disponible desde cada asignación docente.", href: "/validacion/docente/asignaciones/", backend: true },
      { title: "Actas", description: "Actas docentes y cortes académicos.", href: "/evaluacion/actas/docente/", backend: true },
      { title: "Resumen académico", description: "Resumen de cálculo por asignación.", badge: "Backend actual" },
    ],
  },
  discente: {
    key: "DISCENTE",
    title: "Discente",
    description: "Carga académica, actas publicadas e historial académico personal.",
    allowed: ["DISCENTE"],
    cards: [
      { title: "Mi carga académica", description: "Inscripciones a asignatura generadas por grupo.", href: "/validacion/discente/carga/", backend: true },
      { title: "Mis actas publicadas", description: "Actas disponibles para consulta del discente.", href: "/evaluacion/actas/discente/", backend: true },
      { title: "Mi historial académico", description: "Trayectoria académica personal.", href: "/trayectoria/mi-historial/", backend: true },
      { title: "Situación académica", description: "Estado académico vigente.", href: "/trayectoria/mi-historial/", backend: true },
    ],
  },
  jefaturaCarrera: {
    key: "JEFE_CARRERA",
    title: "Jefatura de carrera",
    description: "Operación de asignaciones docentes, actas y trayectoria por carrera.",
    allowed: ["JEFE_CARRERA", "JEFATURA_CARRERA", "JEFE_SUB_EJEC_CTR"],
    cards: [
      { title: "Asignaciones docentes", description: "Asignación de docente a asignatura y grupo.", href: "/validacion/jefatura/asignaciones-docentes/", backend: true },
      { title: "Actas pendientes", description: "Validación por jefatura de carrera.", href: "/evaluacion/actas/jefatura-carrera/pendientes/", backend: true },
      { title: "Pendientes de asignación docente", description: "Diagnóstico previo a cierre de periodo.", href: "/actas/pendientes-asignacion-docente/", backend: true },
      { title: "Consulta de trayectoria", description: "Historiales en ámbito autorizado.", href: "/trayectoria/historial/", backend: true },
    ],
  },
  jefaturaAcademica: {
    key: "JEFE_ACADEMICO",
    title: "Jefatura académica",
    description: "Formalización y consulta institucional de actas.",
    allowed: ["JEFE_ACADEMICO", "JEFATURA_ACADEMICA"],
    cards: [
      { title: "Actas por formalizar", description: "Actas pendientes de formalización.", href: "/evaluacion/actas/jefatura-academica/pendientes/", backend: true },
      { title: "Actas formalizadas", description: "Consulta institucional de actas.", href: "/evaluacion/actas/estadistica/", backend: true },
      { title: "Consulta institucional", description: "Trayectoria e historiales.", href: "/trayectoria/historial/", backend: true },
      { title: "Cierres de periodo", description: "Consulta de cierres cuando aplique.", href: "/actas/periodos/", backend: true },
    ],
  },
  jefaturaPedagogica: {
    key: "JEFE_PEDAGOGICA",
    title: "Jefatura pedagógica",
    description: "Consulta académica, trayectoria y planeación/evaluación.",
    allowed: ["JEFE_PEDAGOGICA", "JEFE_SUB_PLAN_EVAL"],
    cards: [
      { title: "Consulta académica", description: "Actas y seguimiento académico.", href: "/evaluacion/actas/planeacion-evaluacion/consulta/", backend: true },
      { title: "Historial y trayectoria", description: "Consulta de trayectoria académica.", href: "/trayectoria/historial/", backend: true },
      { title: "Indicadores futuros", description: "Pendiente de tableros analíticos.", badge: "Futuro" },
      { title: "Reportes", description: "Pendiente de Bloque 9.", badge: "Pendiente" },
    ],
  },
};

export function getProfilesForUser(user: AuthenticatedUser) {
  const values = new Set([user.perfil_principal ?? "", ...user.roles, ...user.cargos_vigentes.map((cargo) => cargo.cargo_codigo)]);
  if (user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA") || user.perfil_principal === "ADMIN") {
    return Object.values(dashboardProfiles);
  }
  return Object.values(dashboardProfiles).filter((profile) => profile.allowed.some((role) => values.has(role)));
}

export function canAccessProfile(user: AuthenticatedUser, profile: DashboardProfile) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = new Set([user.perfil_principal ?? "", ...user.roles, ...user.cargos_vigentes.map((cargo) => cargo.cargo_codigo)]);
  return profile.allowed.some((role) => values.has(role));
}
