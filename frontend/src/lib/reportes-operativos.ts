import type { AuthenticatedUser, ReporteOperativoCodigo, ReporteOperativoConfig, ReporteOperativoFiltro } from "./types";

const filtrosActas: ReporteOperativoFiltro[] = [
  { key: "periodo", label: "Periodo académico", placeholder: "Ej. 2025-2026" },
  { key: "carrera", label: "Carrera", placeholder: "Ej. ICI" },
  { key: "grupo", label: "Grupo", placeholder: "Ej. ICI-4A" },
  { key: "asignatura", label: "Asignatura", placeholder: "Unidad de aprendizaje" },
  { key: "docente", label: "Docente", placeholder: "Nombre o usuario" },
  {
    key: "corte",
    label: "Corte",
    type: "select",
    options: [
      { value: "", label: "Todos" },
      { value: "P1", label: "Parcial 1" },
      { value: "P2", label: "Parcial 2" },
      { value: "P3", label: "Parcial 3" },
      { value: "FINAL", label: "Evaluación final" },
    ],
  },
  {
    key: "estado_acta",
    label: "Estado del acta",
    type: "select",
    options: [
      { value: "", label: "Todos" },
      { value: "BORRADOR_DOCENTE", label: "Borrador docente" },
      { value: "PUBLICADO_DISCENTE", label: "Publicado a discentes" },
      { value: "REMITIDO_JEFATURA_CARRERA", label: "Remitido a jefatura de carrera" },
      { value: "VALIDADO_JEFATURA_CARRERA", label: "Validado por jefatura de carrera" },
      { value: "FORMALIZADO_JEFATURA_ACADEMICA", label: "Formalizado por jefatura académica" },
    ],
  },
  { key: "fecha_desde", label: "Desde", type: "date" },
  { key: "fecha_hasta", label: "Hasta", type: "date" },
];

const filtrosPendientes: ReporteOperativoFiltro[] = [
  ...filtrosActas.filter((filtro) => filtro.key !== "estado_acta"),
  {
    key: "tipo_pendiente",
    label: "Tipo de pendiente",
    type: "select",
    options: [
      { value: "", label: "Todos" },
      { value: "carrera", label: "Jefatura de carrera" },
      { value: "academica", label: "Jefatura académica" },
    ],
  },
];

const filtrosValidaciones: ReporteOperativoFiltro[] = [
  { key: "periodo", label: "Periodo académico", placeholder: "Ej. 2025-2026" },
  { key: "carrera", label: "Carrera", placeholder: "Ej. ICI" },
  { key: "grupo", label: "Grupo", placeholder: "Ej. ICI-4A" },
  { key: "usuario", label: "Usuario firmante", placeholder: "Nombre o usuario" },
  {
    key: "etapa_validacion",
    label: "Etapa",
    type: "select",
    options: [
      { value: "", label: "Todas" },
      { value: "DOCENTE", label: "Docente" },
      { value: "JEFATURA_CARRERA", label: "Jefatura de carrera" },
      { value: "JEFATURA_ACADEMICA", label: "Jefatura académica" },
      { value: "SISTEMA", label: "Sistema" },
    ],
  },
  {
    key: "accion",
    label: "Acción",
    type: "select",
    options: [
      { value: "", label: "Todas" },
      { value: "PUBLICA", label: "Publica" },
      { value: "REMITE", label: "Remite" },
      { value: "VALIDA", label: "Valida" },
      { value: "FORMALIZA", label: "Formaliza" },
      { value: "ARCHIVA", label: "Archiva" },
    ],
  },
  { key: "cargo", label: "Cargo", placeholder: "Código de cargo" },
  { key: "fecha_desde", label: "Desde", type: "date" },
  { key: "fecha_hasta", label: "Hasta", type: "date" },
];

const filtrosExportaciones: ReporteOperativoFiltro[] = [
  { key: "fecha_desde", label: "Desde", type: "date" },
  { key: "fecha_hasta", label: "Hasta", type: "date" },
  { key: "usuario", label: "Usuario", placeholder: "Nombre o usuario" },
  { key: "tipo_documento", label: "Tipo documental", placeholder: "Ej. REPORTE_ACTAS_ESTADO" },
  {
    key: "formato",
    label: "Formato",
    type: "select",
    options: [
      { value: "", label: "Todos" },
      { value: "PDF", label: "PDF" },
      { value: "XLSX", label: "Excel XLSX" },
    ],
  },
  {
    key: "estado_exportacion",
    label: "Estado",
    type: "select",
    options: [
      { value: "", label: "Todos" },
      { value: "SOLICITADA", label: "Solicitada" },
      { value: "GENERADA", label: "Generada" },
      { value: "FALLIDA", label: "Fallida" },
      { value: "DESCARGADA", label: "Descargada" },
    ],
  },
];

export const reportesOperativos: ReporteOperativoConfig[] = [
  {
    slug: "actas-estado",
    titulo: "Actas por estado",
    descripcion: "Seguimiento operativo del flujo de actas por periodo, carrera, grupo, asignatura, corte y estado.",
    ruta: "/reportes/operativos/actas-estado",
    tipoDocumento: "REPORTE_ACTAS_ESTADO",
    endpointVistaPrevia: "/api/reportes/operativos/actas-estado/",
    endpointDescarga: "/api/exportaciones/reportes/actas-estado/xlsx/",
    filtros: filtrosActas,
    columnasDestacadas: ["acta_id", "periodo", "carrera", "grupo", "materia", "corte", "estado_acta"],
    rolesSugeridos: ["ADMIN", "ENCARGADO_ESTADISTICA", "JEFE_CARRERA", "JEFE_ACADEMICO"],
    ayuda: "Útil para consolidar el avance documental sin abrir acta por acta.",
  },
  {
    slug: "actas-pendientes",
    titulo: "Actas pendientes de validación",
    descripcion: "Actas que requieren atención de jefatura de carrera o jefatura académica.",
    ruta: "/reportes/operativos/actas-pendientes",
    tipoDocumento: "REPORTE_ACTAS_PENDIENTES",
    endpointVistaPrevia: "/api/reportes/operativos/actas-pendientes/",
    endpointDescarga: "/api/exportaciones/reportes/actas-pendientes/xlsx/",
    filtros: filtrosPendientes,
    columnasDestacadas: ["acta_id", "tipo_pendiente", "periodo", "carrera", "grupo", "asignatura", "dias_estado"],
    rolesSugeridos: ["ADMIN", "ENCARGADO_ESTADISTICA", "JEFE_CARRERA", "JEFE_ACADEMICO"],
    ayuda: "Separa pendientes de jefatura de carrera y de jefatura académica.",
  },
  {
    slug: "inconformidades",
    titulo: "Actas con inconformidades",
    descripcion: "Seguimiento autorizado de inconformidades registradas por discentes.",
    ruta: "/reportes/operativos/inconformidades",
    tipoDocumento: "REPORTE_INCONFORMIDADES",
    endpointVistaPrevia: "/api/reportes/operativos/inconformidades/",
    endpointDescarga: "/api/exportaciones/reportes/inconformidades/xlsx/",
    filtros: filtrosActas,
    columnasDestacadas: ["acta_id", "periodo", "carrera", "grupo", "asignatura", "nombre_discente", "fecha_inconformidad"],
    rolesSugeridos: ["ADMIN", "ENCARGADO_ESTADISTICA", "JEFE_CARRERA", "JEFE_ACADEMICO", "JEFE_PEDAGOGICA"],
    ayuda: "El comentario se muestra solo a perfiles autorizados por el backend.",
  },
  {
    slug: "sin-conformidad",
    titulo: "Actas sin conformidad",
    descripcion: "Discentes incluidos en actas publicadas o superiores sin conformidad vigente registrada.",
    ruta: "/reportes/operativos/sin-conformidad",
    tipoDocumento: "REPORTE_ACTAS_SIN_CONFORMIDAD",
    endpointVistaPrevia: "/api/reportes/operativos/sin-conformidad/",
    endpointDescarga: "/api/exportaciones/reportes/sin-conformidad/xlsx/",
    filtros: filtrosActas,
    columnasDestacadas: ["acta_id", "periodo", "carrera", "grupo", "asignatura", "nombre_discente", "dias_desde_publicacion"],
    rolesSugeridos: ["ADMIN", "ENCARGADO_ESTADISTICA", "JEFE_CARRERA", "JEFE_ACADEMICO", "JEFE_PEDAGOGICA"],
    ayuda: "Reporte informativo de excepción; no bloquea por sí mismo el avance del acta.",
  },
  {
    slug: "actas-formalizadas",
    titulo: "Actas formalizadas",
    descripcion: "Actas cerradas institucionalmente por periodo, carrera, grupo, asignatura y corte.",
    ruta: "/reportes/operativos/actas-formalizadas",
    tipoDocumento: "REPORTE_ACTAS_FORMALIZADAS",
    endpointVistaPrevia: "/api/reportes/operativos/actas-formalizadas/",
    endpointDescarga: "/api/exportaciones/reportes/actas-formalizadas/xlsx/",
    filtros: filtrosActas,
    columnasDestacadas: ["acta_id", "periodo", "carrera", "grupo", "asignatura", "formalizada_en", "promedio_acta"],
    rolesSugeridos: ["ADMIN", "ENCARGADO_ESTADISTICA", "JEFE_CARRERA", "JEFE_ACADEMICO", "JEFE_PEDAGOGICA"],
    ayuda: "Consolida actas que ya llegaron al estado documental formalizado.",
  },
  {
    slug: "validaciones-acta",
    titulo: "Historial de validaciones de acta",
    descripcion: "Trazabilidad de etapas, acciones, firmantes, cargos e IP de validaciones de acta.",
    ruta: "/reportes/operativos/validaciones-acta",
    tipoDocumento: "REPORTE_VALIDACIONES_ACTA",
    endpointVistaPrevia: "/api/reportes/operativos/validaciones-acta/",
    endpointDescarga: "/api/exportaciones/reportes/validaciones-acta/xlsx/",
    filtros: filtrosValidaciones,
    columnasDestacadas: ["validacion_id", "acta_id", "periodo", "carrera", "etapa", "accion", "usuario", "fecha_hora"],
    rolesSugeridos: ["ADMIN", "ENCARGADO_ESTADISTICA", "JEFE_CARRERA", "JEFE_ACADEMICO"],
    ayuda: "Para revisar la trazabilidad institucional sin modificar el acta.",
  },
  {
    slug: "exportaciones-realizadas",
    titulo: "Exportaciones realizadas",
    descripcion: "Reporte XLSX de salidas documentales registradas en auditoría.",
    ruta: "/reportes/operativos/exportaciones-realizadas",
    tipoDocumento: "REPORTE_EXPORTACIONES",
    endpointVistaPrevia: "/api/reportes/operativos/exportaciones-realizadas/",
    endpointDescarga: "/api/exportaciones/reportes/exportaciones-realizadas/xlsx/",
    filtros: filtrosExportaciones,
    columnasDestacadas: ["registro_id", "creado_en", "usuario", "tipo_documento", "formato", "estado", "nombre_archivo"],
    rolesSugeridos: ["ADMIN", "ENCARGADO_ESTADISTICA", "JEFE_ACADEMICO"],
    ayuda: "Muestra metadatos de auditoría; no expone payloads completos de documentos.",
  },
];

export function getReporteOperativoConfig(slug: string): ReporteOperativoConfig | undefined {
  return reportesOperativos.find((item) => item.slug === slug);
}

export const reportesOperativosCodigos = reportesOperativos.map((item) => item.slug);

export function cleanReportFilters(filters: Record<string, string>) {
  return Object.fromEntries(
    Object.entries(filters)
      .map(([key, value]) => [key, value.trim()])
      .filter(([, value]) => Boolean(value)),
  );
}

export function emptyFilters(config: ReporteOperativoConfig) {
  return Object.fromEntries(config.filtros.map((filtro) => [filtro.key, ""]));
}

export function isReporteOperativoCodigo(value: string): value is ReporteOperativoCodigo {
  return reportesOperativosCodigos.includes(value as ReporteOperativoCodigo);
}

export function reportesOperativosParaUsuario(user: AuthenticatedUser) {
  return reportesOperativos.filter((config) => canAccessReporteOperativo(user, config));
}

export function canAccessReporteOperativo(user: AuthenticatedUser, config: ReporteOperativoConfig) {
  const values = roleValues(user);
  if (isAdmin(user, values)) return true;
  if (values.has("DISCENTE") || values.has("DOCENTE")) return false;
  return config.rolesSugeridos.some((role) => values.has(role));
}

function roleValues(user: AuthenticatedUser) {
  return new Set([user.perfil_principal ?? "", ...user.roles, ...user.cargos_vigentes.map((cargo) => cargo.cargo_codigo)]);
}

function isAdmin(user: AuthenticatedUser, values: Set<string>) {
  return user.perfil_principal === "ADMIN" || values.has("ADMIN") || values.has("ADMIN_SISTEMA");
}
