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
      { title: "Administración", description: "Usuarios, grados, unidades, cargos y roles desde el portal.", href: "/administracion" },
      { title: "Catálogos académicos", description: "Carreras, planes, periodos, grupos, materias y esquemas.", href: "/catalogos" },
      { title: "Roles y cargos", description: "Grupos, cargos y unidades organizacionales.", href: "/admin/usuarios/asignacioncargo/", backend: true },
      { title: "Unidades organizacionales", description: "Secciones y subsecciones institucionales.", href: "/admin/usuarios/unidadorganizacional/", backend: true },
      { title: "Reportes y exportaciones", description: "Catálogo, actas exportables e historial documental.", href: "/reportes" },
      { title: "Reportes operativos y auditoría", description: "Actas, validaciones y exportaciones en XLSX.", href: "/reportes/operativos" },
      { title: "Reportes de desempeño", description: "Aprobados, reprobados, promedios y aprovechamiento académico.", href: "/reportes/desempeno" },
      { title: "Reportes de trayectoria", description: "Situación académica, movimientos e historial interno.", href: "/reportes/trayectoria" },
      { title: "Kárdex oficial", description: "Exportación PDF institucional de kárdex.", href: "/reportes/kardex" },
      { title: "Auditoría de exportaciones", description: "Trazabilidad institucional de documentos generados.", href: "/reportes/auditoria" },
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
      { title: "Catálogos académicos", description: "Operación de estructura académica desde el portal.", href: "/catalogos" },
      { title: "Usuarios académicos", description: "Consulta operativa de usuarios institucionales autorizados.", href: "/administracion/usuarios" },
      { title: "Periodos", description: "Periodos escolares y estado operativo.", href: "/actas/periodos/", backend: true },
      { title: "Cierre y apertura", description: "Flujo operativo del Bloque 8.5.", href: "/actas/periodos/", backend: true },
      { title: "Historial", description: "Consulta institucional de trayectoria.", href: "/trayectoria/historial/", backend: true },
      { title: "Kárdex institucional", description: "Vista oficial derivada, no visible para discentes.", href: "/trayectoria/kardex/", backend: true },
      { title: "Reportes y exportaciones", description: "Actas PDF/XLSX, historial y catálogo de reportes.", href: "/reportes" },
      { title: "Reportes operativos", description: "Actas, validaciones y exportaciones en XLSX.", href: "/reportes/operativos" },
      { title: "Desempeño académico", description: "Aprobados, reprobados, promedios y aprovechamiento.", href: "/reportes/desempeno" },
      { title: "Situación académica y trayectoria", description: "Extraordinarios, bajas, reingresos, movimientos e historial interno.", href: "/reportes/trayectoria" },
      { title: "Kárdex oficial PDF", description: "Exportación institucional para perfiles autorizados.", href: "/reportes/kardex" },
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
      { title: "Exportar mis actas", description: "Descarga PDF/XLSX de actas propias autorizadas.", href: "/reportes/actas" },
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
      { title: "Catálogos de mi ámbito", description: "Consulta de estructura académica autorizada.", href: "/catalogos" },
      { title: "Actas exportables", description: "Descarga documental de actas del ámbito autorizado.", href: "/reportes/actas" },
      { title: "Seguimiento de actas", description: "Reportes operativos filtrados por ámbito.", href: "/reportes/operativos" },
      { title: "Desempeño de mi carrera", description: "Indicadores académicos filtrados por ámbito.", href: "/reportes/desempeno" },
      { title: "Trayectoria de mi carrera", description: "Situación, movimientos e historial interno del ámbito autorizado.", href: "/reportes/trayectoria" },
      { title: "Kárdex oficial", description: "Exportación PDF de discentes del ámbito autorizado.", href: "/reportes/kardex" },
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
      { title: "Catálogos académicos", description: "Consulta institucional de estructura académica.", href: "/catalogos" },
      { title: "Cierres de periodo", description: "Consulta de cierres cuando aplique.", href: "/actas/periodos/", backend: true },
      { title: "Reportes y exportaciones", description: "Actas, historial de descargas y auditoría documental.", href: "/reportes" },
      { title: "Reportes operativos", description: "Validaciones, pendientes y formalización de actas.", href: "/reportes/operativos" },
      { title: "Desempeño académico", description: "Indicadores institucionales y cuadro de aprovechamiento.", href: "/reportes/desempeno" },
      { title: "Seguimiento de trayectoria", description: "Situación académica, bajas, reingresos e historial interno.", href: "/reportes/trayectoria" },
      { title: "Kárdex oficial", description: "Consulta documental PDF de kárdex institucional.", href: "/reportes/kardex" },
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
      { title: "Catálogos académicos", description: "Consulta autorizada de estructura académica.", href: "/catalogos" },
      { title: "Indicadores futuros", description: "Pendiente de tableros analíticos.", badge: "Futuro" },
      { title: "Reportes y exportaciones", description: "Catálogo documental y salidas disponibles.", href: "/reportes" },
      { title: "Consulta institucional", description: "Reportes operativos autorizados en XLSX.", href: "/reportes/operativos" },
      { title: "Desempeño académico", description: "Reportes autorizados de resultados y aprovechamiento.", href: "/reportes/desempeno" },
      { title: "Seguimiento de trayectoria", description: "Reportes autorizados de situación académica e historial interno.", href: "/reportes/trayectoria" },
      { title: "Kárdex oficial", description: "Exportación PDF autorizada de kárdex.", href: "/reportes/kardex" },
    ],
  },
};

function roleValues(user: AuthenticatedUser) {
  return new Set([user.perfil_principal ?? "", ...user.roles, ...user.cargos_vigentes.map((cargo) => cargo.cargo_codigo)]);
}

export function getProfilesForUser(user: AuthenticatedUser) {
  const values = roleValues(user);
  if (user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA") || user.perfil_principal === "ADMIN") {
    return Object.values(dashboardProfiles);
  }
  return Object.values(dashboardProfiles).filter((profile) => profile.allowed.some((role) => values.has(role)));
}

export function canAccessProfile(user: AuthenticatedUser, profile: DashboardProfile) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  return profile.allowed.some((role) => values.has(role));
}

export function canAccessReportes(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  return [
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "DOCENTE",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
  ].some((role) => values.has(role));
}

export function canAccessKardexPdf(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  return [
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
  ].some((role) => values.has(role));
}

export function canAccessReportesOperativos(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  return [
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
  ].some((role) => values.has(role));
}

export function canAccessReportesDesempeno(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  if (values.has("DISCENTE") || values.has("DOCENTE")) return false;
  return [
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
  ].some((role) => values.has(role));
}

export function canAccessReportesTrayectoria(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  if (values.has("DISCENTE") || values.has("DOCENTE")) return false;
  return [
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
  ].some((role) => values.has(role));
}

export function canAccessAdministracionPortal(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  if (values.has("DISCENTE") || values.has("DOCENTE")) return false;
  return [
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
  ].some((role) => values.has(role));
}

export function canAccessCatalogosPortal(user: AuthenticatedUser) {
  return canAccessAdministracionPortal(user);
}

export function canAccessAuditoriaExportaciones(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  return ["ENCARGADO_ESTADISTICA", "ESTADISTICA"].some((role) => values.has(role));
}
