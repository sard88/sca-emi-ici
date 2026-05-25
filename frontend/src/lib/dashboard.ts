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
      { title: "Administración institucional", description: "Usuarios, grados, unidades, cargos y roles desde el portal.", href: "/administracion" },
      { title: "Catálogos académicos", description: "Carreras, planes, periodos, grupos, materias y esquemas.", href: "/catalogos" },
      { title: "Consulta institucional de actas", description: "Estados, cortes, validaciones y formalización desde el portal.", href: "/estadistica/actas" },
      { title: "Consulta institucional de trayectoria", description: "Historiales, extraordinarios, movimientos y situaciones académicas.", href: "/trayectoria/historial" },
      { title: "Periodos operativos", description: "Diagnóstico, cierre, apertura y pendientes de asignación docente.", href: "/periodos" },
      { title: "Reportes institucionales", description: "Documentos oficiales, reportes operativos, desempeño y trayectoria.", href: "/reportes" },
      { title: "Auditoría institucional", description: "Eventos críticos y exportaciones auditadas con permisos separados.", href: "/reportes/auditoria" },
      { title: "Django Admin", description: "Soporte técnico avanzado fuera del flujo operativo cotidiano.", href: "/admin/", backend: true },
      { title: "Estado técnico", description: "Health check del backend.", href: "/health/", backend: true },
    ],
  },
  estadistica: {
    key: "ESTADISTICA",
    title: "Estadística",
    description: "Consulta, consolidación, cierre y apertura de periodos académicos.",
    allowed: ["ENCARGADO_ESTADISTICA", "ESTADISTICA"],
    cards: [
      { title: "Catálogos académicos", description: "Operación de estructura académica desde el portal.", href: "/catalogos" },
      { title: "Usuarios académicos", description: "Consulta operativa de usuarios institucionales autorizados.", href: "/administracion/usuarios" },
      { title: "Consulta de actas", description: "Consulta operativa de estados, cortes y exportaciones.", href: "/estadistica/actas" },
      { title: "Trayectoria académica", description: "Historial institucional, extraordinarios, situaciones y movimientos.", href: "/trayectoria" },
      { title: "Movimientos académicos", description: "Cambios de grupo y movimientos operativos.", href: "/movimientos-academicos" },
      { title: "Cierre y apertura", description: "Diagnóstico, cierre, apertura y pendientes docentes.", href: "/periodos" },
      { title: "Reportes institucionales", description: "Actas, desempeño, trayectoria, kárdex y exportaciones.", href: "/reportes" },
      { title: "Auditoría institucional", description: "Eventos críticos y trazabilidad de exportaciones.", href: "/reportes/auditoria" },
    ],
  },
  docente: {
    key: "DOCENTE",
    title: "Docente",
    description: "Asignaciones docentes, captura preliminar y actas asociadas.",
    allowed: ["DOCENTE"],
    cards: [
      { title: "Mis asignaciones y captura", description: "Consulta tus grupos, captura calificaciones por corte y revisa resúmenes.", href: "/docente/asignaciones" },
      { title: "Mis actas", description: "Borradores, publicación, remisión y exportación.", href: "/docente/actas" },
      { title: "Exportar mis actas", description: "Descarga PDF/XLSX de actas propias autorizadas.", href: "/reportes/actas" },
    ],
  },
  discente: {
    key: "DISCENTE",
    title: "Discente",
    description: "Carga académica, actas publicadas e historial académico personal.",
    allowed: ["DISCENTE"],
    cards: [
      { title: "Mi carga académica", description: "Asignaturas inscritas, docente, grupo y estado de actas visibles.", href: "/discente/carga-academica" },
      { title: "Mis actas publicadas", description: "Consulta de resultados y conformidad informativa.", href: "/discente/actas" },
      { title: "Mi historial académico", description: "Trayectoria académica personal.", href: "/trayectoria/mi-historial" },
    ],
  },
  jefaturaCarrera: {
    key: "JEFE_CARRERA",
    title: "Jefatura de carrera",
    description: "Operación de asignaciones docentes, actas y trayectoria por carrera.",
    allowed: ["JEFE_CARRERA", "JEFATURA_CARRERA", "JEFE_SUB_EJEC_CTR"],
    cards: [
      { title: "Actas por validar", description: "Validación de actas remitidas por docentes.", href: "/jefatura-carrera/actas" },
      { title: "Pendientes de asignación docente", description: "Diagnóstico previo a cierre de periodo.", href: "/periodos/pendientes-asignacion-docente" },
      { title: "Trayectoria operativa de mi carrera", description: "Consulta historiales y seguimiento de discentes de tu ámbito.", href: "/trayectoria/historial" },
      { title: "Catálogos de mi ámbito", description: "Consulta de estructura académica autorizada.", href: "/catalogos" },
      { title: "Actas exportables", description: "Descarga documental de actas del ámbito autorizado.", href: "/reportes/actas" },
      { title: "Seguimiento de actas", description: "Reportes operativos filtrados por ámbito.", href: "/reportes/operativos" },
      { title: "Desempeño de mi carrera", description: "Indicadores académicos filtrados por ámbito.", href: "/reportes/desempeno" },
      { title: "Reportes de trayectoria", description: "Reportes XLSX y vistas agregadas de situación, movimientos e historial interno.", href: "/reportes/trayectoria" },
      { title: "Kárdex oficial", description: "Exportación PDF de discentes del ámbito autorizado.", href: "/reportes/kardex" },
    ],
  },
  jefaturaAcademica: {
    key: "JEFE_ACADEMICO",
    title: "Jefatura académica",
    description: "Formalización y consulta institucional de actas.",
    allowed: ["JEFE_ACADEMICO", "JEFATURA_ACADEMICA"],
    cards: [
      { title: "Actas por formalizar", description: "Formalización de actas validadas por carrera.", href: "/jefatura-academica/actas" },
      { title: "Actas formalizadas", description: "Consulta institucional de actas.", href: "/estadistica/actas" },
      { title: "Seguimiento institucional de trayectoria", description: "Consulta historiales, situaciones y movimientos autorizados.", href: "/trayectoria/historial" },
      { title: "Catálogos académicos", description: "Consulta institucional de estructura académica.", href: "/catalogos" },
      { title: "Procesos de cierre", description: "Consulta de diagnósticos, cierres y aperturas.", href: "/periodos/cierres" },
      { title: "Reportes y exportaciones", description: "Actas, historial de descargas y auditoría documental.", href: "/reportes" },
      { title: "Desempeño académico", description: "Indicadores institucionales y cuadro de aprovechamiento.", href: "/reportes/desempeno" },
      { title: "Reportes de trayectoria", description: "Situación académica, bajas, reingresos e historial interno.", href: "/reportes/trayectoria" },
      { title: "Kárdex oficial", description: "Consulta documental PDF de kárdex institucional.", href: "/reportes/kardex" },
    ],
  },
  jefaturaPedagogica: {
    key: "JEFE_PEDAGOGICA",
    title: "Jefatura pedagógica",
    description: "Consulta académica, trayectoria y planeación/evaluación.",
    allowed: ["JEFE_PEDAGOGICA", "JEFE_SUB_PLAN_EVAL"],
    cards: [
      { title: "Reportes operativos", description: "Seguimiento autorizado de actas, validaciones y pendientes.", href: "/reportes/operativos" },
      { title: "Desempeño académico", description: "Reportes autorizados de resultados y aprovechamiento.", href: "/reportes/desempeno" },
      { title: "Reportes de trayectoria", description: "Situación académica, movimientos e historial interno autorizado.", href: "/reportes/trayectoria" },
      { title: "Auditoría de eventos críticos", description: "Consulta de eventos institucionales permitidos por perfil.", href: "/reportes/auditoria" },
      { title: "Catálogos académicos", description: "Consulta autorizada de estructura académica.", href: "/catalogos" },
    ],
  },
};

function roleValues(user: AuthenticatedUser) {
  return new Set([user.perfil_principal ?? "", ...user.roles, ...user.cargos_vigentes.map((cargo) => cargo.cargo_codigo)]);
}

export function getProfilesForUser(user: AuthenticatedUser) {
  const values = roleValues(user);
  if (user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA") || user.perfil_principal === "ADMIN") {
    return [dashboardProfiles.admin];
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

export function canAccessDocenteOperacion(user: AuthenticatedUser) {
  const values = roleValues(user);
  return values.has("DOCENTE") || user.perfil_principal === "ADMIN" || values.has("ADMIN") || values.has("ADMIN_SISTEMA");
}

export function canAccessDiscenteActas(user: AuthenticatedUser) {
  const values = roleValues(user);
  return values.has("DISCENTE");
}

export function canAccessDiscenteCargaAcademica(user: AuthenticatedUser) {
  const values = roleValues(user);
  return values.has("DISCENTE");
}

export function canAccessMiHistorialAcademico(user: AuthenticatedUser) {
  const values = roleValues(user);
  return values.has("DISCENTE");
}

export function canAccessTrayectoriaOperativa(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  if (values.has("DOCENTE")) return false;
  return [
    "DISCENTE",
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

export function canAccessTrayectoriaInstitucional(user: AuthenticatedUser) {
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

export function canOperateTrayectoria(user: AuthenticatedUser) {
  const values = roleValues(user);
  return ["ADMIN", "ADMIN_SISTEMA", "ENCARGADO_ESTADISTICA", "ESTADISTICA"].some((role) => values.has(role) || user.perfil_principal === role);
}

export function canAccessPeriodosOperativos(user: AuthenticatedUser) {
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
  ].some((role) => values.has(role));
}

export function canAccessJefaturaCarreraActas(user: AuthenticatedUser) {
  const values = roleValues(user);
  return ["ADMIN", "ADMIN_SISTEMA", "JEFE_CARRERA", "JEFATURA_CARRERA", "JEFE_SUB_EJEC_CTR"].some((role) => values.has(role) || user.perfil_principal === role);
}

export function canAccessJefaturaAcademicaActas(user: AuthenticatedUser) {
  const values = roleValues(user);
  return ["ADMIN", "ADMIN_SISTEMA", "JEFE_ACADEMICO", "JEFATURA_ACADEMICA"].some((role) => values.has(role) || user.perfil_principal === role);
}

export function canAccessEstadisticaActas(user: AuthenticatedUser) {
  const values = roleValues(user);
  return ["ADMIN", "ADMIN_SISTEMA", "ENCARGADO_ESTADISTICA", "ESTADISTICA"].some((role) => values.has(role) || user.perfil_principal === role);
}

export function canAccessAuditoriaExportaciones(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  return ["ENCARGADO_ESTADISTICA", "ESTADISTICA", "JEFE_ACADEMICO", "JEFATURA_ACADEMICA"].some((role) => values.has(role));
}

export function canAccessAuditoriaEventos(user: AuthenticatedUser) {
  if (user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA")) return true;
  const values = roleValues(user);
  return ["ENCARGADO_ESTADISTICA", "ESTADISTICA", "JEFE_ACADEMICO", "JEFATURA_ACADEMICA", "JEFE_PEDAGOGICA", "JEFE_SUB_PLAN_EVAL"].some((role) => values.has(role));
}

export function canAccessAuditoria(user: AuthenticatedUser) {
  return canAccessAuditoriaEventos(user) || canAccessAuditoriaExportaciones(user);
}
