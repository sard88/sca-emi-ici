import type { AuthenticatedUser, ReporteTrayectoriaCodigo, ReporteTrayectoriaConfig, ReporteTrayectoriaFiltro } from "./types";

const filtroPeriodo: ReporteTrayectoriaFiltro = { key: "periodo", label: "Periodo", type: "relation", relation: { endpoint: "/api/catalogos/periodos/", valueKey: "id", labelKey: "label", search: true } };
const filtroCarrera: ReporteTrayectoriaFiltro = { key: "carrera", label: "Carrera", type: "relation", relation: { endpoint: "/api/catalogos/carreras/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } };
const filtroGrupo: ReporteTrayectoriaFiltro = { key: "grupo", label: "Grupo", type: "relation", relation: { endpoint: "/api/catalogos/grupos/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } };
const filtroPlan: ReporteTrayectoriaFiltro = { key: "plan", label: "Plan", type: "relation", relation: { endpoint: "/api/catalogos/planes/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } };
const filtroAntiguedad: ReporteTrayectoriaFiltro = { key: "antiguedad", label: "Antigüedad", type: "relation", relation: { endpoint: "/api/catalogos/antiguedades/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } };
const filtroAsignatura: ReporteTrayectoriaFiltro = { key: "asignatura", label: "Asignatura", type: "relation", relation: { endpoint: "/api/catalogos/materias/", valueKey: "clave", labelKey: "label", activeOnly: true, search: true } };
const filtroDocente: ReporteTrayectoriaFiltro = { key: "docente", label: "Docente", type: "relation", relation: { endpoint: "/api/admin/usuarios/", valueKey: "username", labelKey: "label", search: true, queryParams: { activo: true } } };
const filtroSituacion: ReporteTrayectoriaFiltro = { key: "situacion", label: "Situación", type: "relation", relation: { endpoint: "/api/catalogos/situaciones-academicas/", valueKey: "clave", labelKey: "label", activeOnly: true, search: true } };

const filtrosBase: ReporteTrayectoriaFiltro[] = [
  filtroPeriodo,
  filtroCarrera,
  filtroGrupo,
  filtroPlan,
  filtroAntiguedad,
  { key: "anio_formacion", label: "Año de formación", type: "select", options: numericOptions("Todos", 1, 6) },
  { key: "semestre", label: "Semestre", type: "select", options: numericOptions("Todos", 1, 12) },
  { key: "fecha_desde", label: "Desde", type: "date" },
  { key: "fecha_hasta", label: "Hasta", type: "date" },
];

const filtrosAcademicos: ReporteTrayectoriaFiltro[] = [
  ...filtrosBase,
  filtroAsignatura,
  filtroDocente,
];

const filtrosSituacion: ReporteTrayectoriaFiltro[] = [
  ...filtrosBase,
  filtroSituacion,
  { key: "discente", label: "Discente", placeholder: "ID o nombre" },
];

const filtrosEventos: ReporteTrayectoriaFiltro[] = [
  ...filtrosBase,
  { key: "discente", label: "Discente", placeholder: "ID o nombre" },
  {
    key: "baja_abierta",
    label: "Baja abierta",
    type: "select",
    options: booleanOptions("Todas"),
  },
];

const filtrosExtraordinarios: ReporteTrayectoriaFiltro[] = [
  ...filtrosAcademicos,
  { key: "discente", label: "Discente", placeholder: "ID o nombre" },
  {
    key: "aprobado",
    label: "Aprobado",
    type: "select",
    options: booleanOptions("Todos"),
  },
];

const filtrosMovimientos: ReporteTrayectoriaFiltro[] = [
  filtroPeriodo,
  filtroCarrera,
  filtroAntiguedad,
  { key: "discente", label: "Discente", placeholder: "ID o nombre" },
  { key: "grupo_origen", label: "Grupo origen", type: "relation", relation: { endpoint: "/api/catalogos/grupos/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } },
  { key: "grupo_destino", label: "Grupo destino", type: "relation", relation: { endpoint: "/api/catalogos/grupos/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } },
  {
    key: "tipo_movimiento",
    label: "Tipo de movimiento",
    type: "select",
    options: [
      { value: "", label: "Todos" },
      { value: "cambio_grupo", label: "Cambio de grupo" },
      { value: "alta_extemporanea", label: "Alta extemporánea" },
      { value: "baja_extemporanea", label: "Baja extemporánea" },
    ],
  },
  { key: "fecha_desde", label: "Desde", type: "date" },
  { key: "fecha_hasta", label: "Hasta", type: "date" },
];

const filtrosHistorial: ReporteTrayectoriaFiltro[] = [
  ...filtrosAcademicos,
  { key: "discente", label: "Discente", placeholder: "ID o nombre" },
  {
    key: "incluir_extraordinarios",
    label: "Extraordinarios",
    type: "select",
    options: booleanOptions("Incluir por defecto"),
  },
  {
    key: "incluir_eventos",
    label: "Eventos",
    type: "select",
    options: booleanOptions("Incluir por defecto"),
  },
  {
    key: "incluir_movimientos",
    label: "Movimientos",
    type: "select",
    options: booleanOptions("Incluir por defecto"),
  },
];

const filtrosHistorialDiscente: ReporteTrayectoriaFiltro[] = [
  { key: "discente_id", label: "ID de discente", placeholder: "Ej. 123" },
  ...filtrosHistorial.filter((filtro) => filtro.key !== "discente"),
];

export const reportesTrayectoria: ReporteTrayectoriaConfig[] = [
  {
    slug: "extraordinarios",
    titulo: "Extraordinarios registrados",
    descripcion: "Relación institucional de extraordinarios con ordinario previo, resultado extraordinario y marca EE cuando aplica.",
    ruta: "/reportes/trayectoria/extraordinarios",
    tipoDocumento: "REPORTE_EXTRAORDINARIOS",
    endpointVistaPrevia: "/api/reportes/situacion/extraordinarios/",
    endpointDescarga: "/api/exportaciones/reportes/extraordinarios/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosExtraordinarios,
    columnasDestacadas: ["extraordinario_id", "periodo", "carrera", "grupo", "asignatura", "nombre_discente", "marca"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "No modifica resultados; solo reporta evidencia registrada por trayectoria académica.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: avisoPrivacidad(),
  },
  {
    slug: "situacion-actual",
    titulo: "Situación académica actual",
    descripcion: "Vista nominal de situación vigente, último evento, baja abierta y señales de seguimiento académico.",
    ruta: "/reportes/trayectoria/situacion-actual",
    tipoDocumento: "REPORTE_SITUACION_ACADEMICA",
    endpointVistaPrevia: "/api/reportes/situacion/actual/",
    endpointDescarga: "/api/exportaciones/reportes/situacion-actual/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosSituacion,
    columnasDestacadas: ["discente_id", "nombre", "carrera", "grupo_actual", "situacion_actual", "baja_abierta"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Reporte nominal restringido; el backend filtra por ámbito institucional.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: avisoPrivacidad(),
  },
  {
    slug: "bajas-temporales",
    titulo: "Bajas temporales",
    descripcion: "Eventos de baja temporal, abiertas o cerradas, con motivo y posible reingreso asociado.",
    ruta: "/reportes/trayectoria/bajas-temporales",
    tipoDocumento: "REPORTE_BAJAS_TEMPORALES",
    endpointVistaPrevia: "/api/reportes/situacion/bajas-temporales/",
    endpointDescarga: "/api/exportaciones/reportes/bajas-temporales/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosEventos,
    columnasDestacadas: ["evento_id", "periodo", "carrera", "nombre", "fecha_inicio", "baja_abierta"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Muestra eventos registrados; no abre, cierra ni modifica bajas.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: avisoPrivacidad(),
  },
  {
    slug: "bajas-definitivas",
    titulo: "Bajas definitivas",
    descripcion: "Eventos de baja definitiva registrados en trayectoria académica.",
    ruta: "/reportes/trayectoria/bajas-definitivas",
    tipoDocumento: "REPORTE_BAJAS_DEFINITIVAS",
    endpointVistaPrevia: "/api/reportes/situacion/bajas-definitivas/",
    endpointDescarga: "/api/exportaciones/reportes/bajas-definitivas/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosEventos.filter((filtro) => filtro.key !== "baja_abierta"),
    columnasDestacadas: ["evento_id", "periodo", "carrera", "nombre", "fecha_inicio", "situacion"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Reporte de evidencia; no altera situación académica.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: avisoPrivacidad(),
  },
  {
    slug: "reingresos",
    titulo: "Reingresos",
    descripcion: "Eventos de reingreso y relación con baja temporal previa cuando el backend puede derivarla.",
    ruta: "/reportes/trayectoria/reingresos",
    tipoDocumento: "REPORTE_REINGRESOS",
    endpointVistaPrevia: "/api/reportes/situacion/reingresos/",
    endpointDescarga: "/api/exportaciones/reportes/reingresos/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosEventos.filter((filtro) => filtro.key !== "baja_abierta"),
    columnasDestacadas: ["evento_id", "periodo", "carrera", "nombre", "fecha_inicio", "observaciones"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Solo reporta reingresos registrados; no genera movimientos ni adscripciones.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: avisoPrivacidad(),
  },
  {
    slug: "egresables",
    titulo: "Egresables / egresados",
    descripcion: "Reporte derivado de situación y trayectoria disponible para identificar egresables o egresados.",
    ruta: "/reportes/trayectoria/egresables",
    tipoDocumento: "REPORTE_EGRESADOS_EGRESABLES",
    endpointVistaPrevia: "/api/reportes/situacion/egresables/",
    endpointDescarga: "/api/exportaciones/reportes/egresables/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosSituacion,
    columnasDestacadas: ["discente_id", "nombre", "carrera", "ultimo_grupo", "egresable", "egresado"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Si no existe flujo formal de egreso, el backend lo documenta como derivado.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: avisoPrivacidad(),
  },
  {
    slug: "situacion-agregado",
    titulo: "Situación académica agregada",
    descripcion: "Totales por situación académica, carrera, grupo, periodo y antigüedad.",
    ruta: "/reportes/trayectoria/situacion-agregado",
    tipoDocumento: "REPORTE_SITUACION_ACADEMICA_AGREGADO",
    endpointVistaPrevia: "/api/reportes/situacion/agregado/",
    endpointDescarga: "/api/exportaciones/reportes/situacion-agregado/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosSituacion.filter((filtro) => filtro.key !== "discente"),
    columnasDestacadas: ["periodo", "carrera", "grupo", "situacion_academica", "total_discentes", "porcentaje"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Reporte agregado: no muestra nombres ni matrícula militar.",
    nominal: false,
    agregado: true,
    datosSensibles: false,
  },
  {
    slug: "movimientos-academicos",
    titulo: "Movimientos académicos",
    descripcion: "Movimientos registrados de trayectoria académica con usuario, grupos y estado operativo.",
    ruta: "/reportes/trayectoria/movimientos-academicos",
    tipoDocumento: "REPORTE_MOVIMIENTOS_ACADEMICOS",
    endpointVistaPrevia: "/api/reportes/movimientos/",
    endpointDescarga: "/api/exportaciones/reportes/movimientos-academicos/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosMovimientos,
    columnasDestacadas: ["movimiento_id", "tipo_movimiento", "fecha_movimiento", "nombre_discente", "grupo_origen", "grupo_destino"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "El portal no aplica movimientos; solo muestra evidencia autorizada.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: avisoPrivacidad(),
  },
  {
    slug: "cambios-grupo",
    titulo: "Cambios de grupo",
    descripcion: "Reporte específico de cambios de grupo registrados, con origen y destino.",
    ruta: "/reportes/trayectoria/cambios-grupo",
    tipoDocumento: "REPORTE_CAMBIOS_GRUPO",
    endpointVistaPrevia: "/api/reportes/movimientos/cambios-grupo/",
    endpointDescarga: "/api/exportaciones/reportes/cambios-grupo/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosMovimientos.filter((filtro) => filtro.key !== "tipo_movimiento"),
    columnasDestacadas: ["movimiento_id", "fecha", "nombre", "grupo_origen", "grupo_destino", "observaciones"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "No inventa intentos fallidos; solo reporta cambios registrados.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: avisoPrivacidad(),
  },
  {
    slug: "historial-interno",
    titulo: "Historial académico interno",
    descripcion: "Historial institucional filtrable con resultados, extraordinarios, eventos y movimientos.",
    ruta: "/reportes/trayectoria/historial-interno",
    tipoDocumento: "REPORTE_HISTORIAL_ACADEMICO_INTERNO",
    endpointVistaPrevia: "/api/reportes/historial-interno/",
    endpointDescarga: "/api/exportaciones/reportes/historial-interno/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosHistorial,
    columnasDestacadas: ["discente_id", "nombre", "periodo", "asignatura", "resultado_oficial", "marca"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Historial interno: conserva evidencia ordinaria aunque exista EE. No es kárdex oficial.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: "Este historial interno contiene información académica sensible. No debe presentarse como kárdex oficial.",
  },
  {
    slug: "historial-interno-discente",
    titulo: "Historial interno por discente",
    descripcion: "Exportación institucional del historial interno de un discente específico mediante ID interno.",
    ruta: "/reportes/trayectoria/historial-interno-discente",
    tipoDocumento: "HISTORIAL_ACADEMICO",
    endpointVistaPrevia: "/api/reportes/historial-interno/<discente_id>/",
    endpointDescarga: "/api/exportaciones/reportes/historial-interno/<discente_id>/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosHistorialDiscente,
    columnasDestacadas: ["discente_id", "nombre", "periodo", "asignatura", "resultado_oficial", "marca"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Requiere ID interno de discente. No acepta matrícula militar y no es kárdex oficial.",
    nominal: true,
    agregado: false,
    datosSensibles: true,
    privacidad: "La exportación de historial interno por discente está reservada para perfiles institucionales autorizados.",
    requiereDiscenteId: true,
  },
];

export function getReporteTrayectoriaConfig(slug: string): ReporteTrayectoriaConfig | undefined {
  return reportesTrayectoria.find((item) => item.slug === slug);
}

export const reportesTrayectoriaCodigos = reportesTrayectoria.map((item) => item.slug);

export function cleanTrajectoryFilters(filters: Record<string, string>) {
  return Object.fromEntries(
    Object.entries(filters)
      .map(([key, value]) => [key, value.trim()])
      .filter(([, value]) => Boolean(value)),
  );
}

export function emptyTrajectoryFilters(config: ReporteTrayectoriaConfig) {
  return Object.fromEntries(config.filtros.map((filtro) => [filtro.key, ""]));
}

export function isReporteTrayectoriaCodigo(value: string): value is ReporteTrayectoriaCodigo {
  return reportesTrayectoriaCodigos.includes(value as ReporteTrayectoriaCodigo);
}

export function reportesTrayectoriaParaUsuario(user: AuthenticatedUser) {
  return reportesTrayectoria.filter((config) => canAccessReporteTrayectoria(user, config));
}

export function canAccessReporteTrayectoria(user: AuthenticatedUser, config: ReporteTrayectoriaConfig) {
  const values = roleValues(user);
  if (isAdmin(user, values)) return true;
  if (values.has("DISCENTE") || values.has("DOCENTE")) return false;
  return config.rolesSugeridos.some((role) => values.has(role));
}

function numericOptions(emptyLabel: string, start: number, end: number) {
  return [
    { value: "", label: emptyLabel },
    ...Array.from({ length: end - start + 1 }, (_, index) => {
      const value = String(start + index);
      return { value, label: value };
    }),
  ];
}

function booleanOptions(emptyLabel: string) {
  return [
    { value: "", label: emptyLabel },
    { value: "true", label: "Sí" },
    { value: "false", label: "No" },
  ];
}

function rolesInstitucionales() {
  return [
    "ADMIN",
    "ADMIN_SISTEMA",
    "ENCARGADO_ESTADISTICA",
    "ESTADISTICA",
    "JEFE_CARRERA",
    "JEFATURA_CARRERA",
    "JEFE_SUB_EJEC_CTR",
    "JEFE_ACADEMICO",
    "JEFATURA_ACADEMICA",
    "JEFE_PEDAGOGICA",
    "JEFE_SUB_PLAN_EVAL",
  ];
}

function roleValues(user: AuthenticatedUser) {
  return new Set([user.perfil_principal ?? "", ...user.roles, ...user.cargos_vigentes.map((cargo) => cargo.cargo_codigo)]);
}

function isAdmin(user: AuthenticatedUser, values: Set<string>) {
  return user.perfil_principal === "ADMIN" || values.has("ADMIN") || values.has("ADMIN_SISTEMA");
}

function avisoPrivacidad() {
  return "Este reporte contiene información académica sensible y solo debe consultarse por personal autorizado.";
}
