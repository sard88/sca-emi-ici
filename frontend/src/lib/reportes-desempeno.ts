import type { AuthenticatedUser, ReporteDesempenoCodigo, ReporteDesempenoConfig, ReporteDesempenoFiltro } from "./types";

const filtroPeriodo: ReporteDesempenoFiltro = { key: "periodo", label: "Periodo académico", type: "relation", relation: { endpoint: "/api/catalogos/periodos/", valueKey: "id", labelKey: "label", search: true } };
const filtroCarrera: ReporteDesempenoFiltro = { key: "carrera", label: "Carrera", type: "relation", relation: { endpoint: "/api/catalogos/carreras/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } };
const filtroGrupo: ReporteDesempenoFiltro = { key: "grupo", label: "Grupo", type: "relation", relation: { endpoint: "/api/catalogos/grupos/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } };
const filtroAsignatura: ReporteDesempenoFiltro = { key: "asignatura", label: "Asignatura", type: "relation", relation: { endpoint: "/api/catalogos/materias/", valueKey: "clave", labelKey: "label", activeOnly: true, search: true } };
const filtroDocente: ReporteDesempenoFiltro = { key: "docente", label: "Docente", type: "relation", relation: { endpoint: "/api/admin/usuarios/", valueKey: "username", labelKey: "label", search: true, queryParams: { activo: true } } };
const filtroAntiguedad: ReporteDesempenoFiltro = { key: "antiguedad", label: "Antigüedad", type: "relation", relation: { endpoint: "/api/catalogos/antiguedades/", valueKey: "id", labelKey: "label", activeOnly: true, search: true } };

const filtrosBase: ReporteDesempenoFiltro[] = [
  filtroPeriodo,
  filtroCarrera,
  filtroGrupo,
  filtroAsignatura,
  filtroDocente,
  filtroAntiguedad,
  { key: "anio_formacion", label: "Año de formación", type: "select", options: numericOptions("Todos", 1, 6) },
  { key: "semestre", label: "Semestre", type: "select", options: numericOptions("Todos", 1, 12) },
  { key: "fecha_desde", label: "Desde", type: "date" },
  { key: "fecha_hasta", label: "Hasta", type: "date" },
];

const filtrosCuadro: ReporteDesempenoFiltro[] = [
  ...filtrosBase.filter((filtro) => !["docente", "asignatura"].includes(filtro.key)),
  {
    key: "rango_aprovechamiento",
    label: "Rango",
    type: "select",
    options: [
      { value: "", label: "Todos" },
      { value: "Excelente", label: "Excelente aprovechamiento" },
      { value: "Alto", label: "Alto aprovechamiento" },
      { value: "Buen", label: "Buen aprovechamiento" },
    ],
  },
  {
    key: "incluir_con_reprobadas",
    label: "Incluir con reprobadas",
    type: "select",
    options: [
      { value: "", label: "No" },
      { value: "true", label: "Sí" },
    ],
  },
];

const filtrosOpcionesAcademicas: ReporteDesempenoFiltro[] = [
  ...filtrosBase,
  {
    key: "incluir_no_numericas",
    label: "No numéricas",
    type: "select",
    options: [
      { value: "", label: "Excluir" },
      { value: "true", label: "Incluir" },
    ],
  },
  {
    key: "incluir_extraordinarios",
    label: "Extraordinarios",
    type: "select",
    options: [
      { value: "", label: "Según resultado oficial" },
      { value: "true", label: "Incluir marca EE" },
    ],
  },
];

export const reportesDesempeno: ReporteDesempenoConfig[] = [
  {
    slug: "aprobados-reprobados",
    titulo: "Aprobados y reprobados",
    descripcion: "Indicadores agregados de aprobación y reprobación por periodo, carrera, grupo, asignatura y docente.",
    ruta: "/reportes/desempeno/aprobados-reprobados",
    tipoDocumento: "REPORTE_APROBADOS_REPROBADOS",
    endpointVistaPrevia: "/api/reportes/desempeno/aprobados-reprobados/",
    endpointDescarga: "/api/exportaciones/reportes/aprobados-reprobados/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosOpcionesAcademicas,
    columnasDestacadas: ["periodo", "carrera", "grupo", "asignatura", "total_evaluados", "aprobados", "reprobados"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Basado en resultados oficiales consolidados y actas FINAL formalizadas.",
    nominal: false,
    datosSensibles: false,
  },
  {
    slug: "promedios",
    titulo: "Promedios académicos",
    descripcion: "Promedios por grupo, asignatura, docente, carrera y año de formación.",
    ruta: "/reportes/desempeno/promedios",
    tipoDocumento: "REPORTE_PROMEDIOS_ACADEMICOS",
    endpointVistaPrevia: "/api/reportes/desempeno/promedios/",
    endpointDescarga: "/api/exportaciones/reportes/promedios/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosOpcionesAcademicas,
    columnasDestacadas: ["dimension", "periodo", "carrera", "grupo", "asignatura", "promedio"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "La vista previa toma las columnas que devuelve el backend; el XLSX contiene hojas por dimensión.",
    nominal: false,
    datosSensibles: false,
  },
  {
    slug: "distribucion",
    titulo: "Distribución de calificaciones",
    descripcion: "Distribución de calificaciones oficiales por rangos institucionales.",
    ruta: "/reportes/desempeno/distribucion",
    tipoDocumento: "REPORTE_DISTRIBUCION_CALIFICACIONES",
    endpointVistaPrevia: "/api/reportes/desempeno/distribucion/",
    endpointDescarga: "/api/exportaciones/reportes/distribucion/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosBase,
    columnasDestacadas: ["periodo", "carrera", "grupo", "asignatura", "rango", "total_discentes", "porcentaje"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "No genera gráficas; deja datos tabulares listos para análisis posterior.",
    nominal: false,
    datosSensibles: false,
  },
  {
    slug: "exentos",
    titulo: "Exentos por asignatura",
    descripcion: "Relación autorizada de exenciones del componente examen final.",
    ruta: "/reportes/desempeno/exentos",
    tipoDocumento: "REPORTE_EXENTOS",
    endpointVistaPrevia: "/api/reportes/desempeno/exentos/",
    endpointDescarga: "/api/exportaciones/reportes/exentos/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosBase,
    columnasDestacadas: ["periodo", "carrera", "grupo", "asignatura", "nombre_discente", "componente_exento"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Exento se refiere al examen final, no a toda la evaluación final.",
    nominal: true,
    datosSensibles: true,
    privacidad: "Este reporte contiene información nominal y solo debe consultarse por personal autorizado.",
  },
  {
    slug: "docentes",
    titulo: "Desempeño por docente",
    descripcion: "Indicadores por docente, grupo y asignatura impartida.",
    ruta: "/reportes/desempeno/docentes",
    tipoDocumento: "REPORTE_DESEMPENO_DOCENTE",
    endpointVistaPrevia: "/api/reportes/desempeno/docentes/",
    endpointDescarga: "/api/exportaciones/reportes/desempeno-docente/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosBase,
    columnasDestacadas: ["periodo", "carrera", "docente", "grupo", "asignatura", "promedio", "actas_formalizadas"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Reporte institucional; el docente no ve comparativos globales en esta versión.",
    nominal: false,
    datosSensibles: false,
  },
  {
    slug: "cohorte",
    titulo: "Desempeño por antigüedad",
    descripcion: "Indicadores por carrera, antigüedad, año de formación y semestre.",
    ruta: "/reportes/desempeno/cohorte",
    tipoDocumento: "REPORTE_DESEMPENO_COHORTE",
    endpointVistaPrevia: "/api/reportes/desempeno/cohorte/",
    endpointDescarga: "/api/exportaciones/reportes/desempeno-cohorte/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosBase,
    columnasDestacadas: ["periodo", "carrera", "antiguedad", "anio_formacion", "promedio", "aprobados", "reprobados"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "Permite observar tendencias agregadas por antigüedad y año de formación.",
    nominal: false,
    datosSensibles: false,
  },
  {
    slug: "reprobados-nominal",
    titulo: "Reprobados nominal",
    descripcion: "Seguimiento autorizado de discentes con resultado reprobatorio vigente.",
    ruta: "/reportes/desempeno/reprobados-nominal",
    tipoDocumento: "REPORTE_REPROBADOS_NOMINAL",
    endpointVistaPrevia: "/api/reportes/desempeno/reprobados-nominal/",
    endpointDescarga: "/api/exportaciones/reportes/reprobados-nominal/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosBase,
    columnasDestacadas: ["periodo", "carrera", "grupo", "asignatura", "nombre_discente", "resultado_oficial"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "No muestra matrícula militar por defecto; backend limita por permisos y ámbito.",
    nominal: true,
    datosSensibles: true,
    privacidad: "Este reporte contiene información nominal y debe usarse únicamente para seguimiento académico autorizado.",
  },
  {
    slug: "cuadro-aprovechamiento",
    titulo: "Cuadro de aprovechamiento",
    descripcion: "Clasificación de mejores promedios por rangos de aprovechamiento académico.",
    ruta: "/reportes/desempeno/cuadro-aprovechamiento",
    tipoDocumento: "CUADRO_APROVECHAMIENTO",
    endpointVistaPrevia: "/api/reportes/desempeno/cuadro-aprovechamiento/",
    endpointDescarga: "/api/exportaciones/reportes/cuadro-aprovechamiento/xlsx/",
    formatosDisponibles: ["XLSX"],
    pdfPendiente: true,
    filtros: filtrosCuadro,
    columnasDestacadas: ["rango_aprovechamiento", "lugar", "carrera", "grupo", "nombre_discente", "promedio"],
    rolesSugeridos: rolesInstitucionales(),
    ayuda: "PDF pendiente. El XLSX usa resultados oficiales formalizados y clasifica por rangos institucionales.",
    nominal: true,
    datosSensibles: true,
    privacidad: "Este cuadro contiene información nominal de aprovechamiento académico y solo debe consultarse por perfiles autorizados.",
  },
];

export function getReporteDesempenoConfig(slug: string): ReporteDesempenoConfig | undefined {
  return reportesDesempeno.find((item) => item.slug === slug);
}

export const reportesDesempenoCodigos = reportesDesempeno.map((item) => item.slug);

export function cleanPerformanceFilters(filters: Record<string, string>) {
  return Object.fromEntries(
    Object.entries(filters)
      .map(([key, value]) => [key, value.trim()])
      .filter(([, value]) => Boolean(value)),
  );
}

export function emptyPerformanceFilters(config: ReporteDesempenoConfig) {
  return Object.fromEntries(config.filtros.map((filtro) => [filtro.key, ""]));
}

export function isReporteDesempenoCodigo(value: string): value is ReporteDesempenoCodigo {
  return reportesDesempenoCodigos.includes(value as ReporteDesempenoCodigo);
}

export function reportesDesempenoParaUsuario(user: AuthenticatedUser) {
  return reportesDesempeno.filter((config) => canAccessReporteDesempeno(user, config));
}

export function canAccessReporteDesempeno(user: AuthenticatedUser, config: ReporteDesempenoConfig) {
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
