export const glosarioInstitucional = {
  discente: "Discente",
  docente: "Docente",
  asignatura: "Asignatura",
  materia: "Materia",
  programaAsignatura: "Programa de asignatura",
  antiguedad: "Antigüedad",
  periodoAcademico: "Periodo académico",
  anioFormacion: "Año de formación",
  kardexOficial: "Kárdex oficial",
  historialInterno: "Historial académico interno",
  acta: "Acta",
  evaluacionFinal: "Evaluación final",
  resultadoFinalPreliminar: "Resultado final preliminar",
  calificacionFinal: "Calificación final",
  conformidad: "Conformidad",
  inconformidad: "Inconformidad",
  bitacora: "Bitácora",
  registroExportacion: "Registro de exportación",
  auditoriaInstitucional: "Auditoría institucional",
} as const;

export type GlosarioKey = keyof typeof glosarioInstitucional;

export const termDescriptions: Record<GlosarioKey, string> = {
  discente: "Discente registrado en el sistema.",
  docente: "Profesor asignado a una asignatura y grupo.",
  asignatura: "Término operativo preferido para actas, reportes, carga académica y trayectoria.",
  materia: "Catálogo base de materias; en operación se muestra como asignatura.",
  programaAsignatura: "Relación entre materia/asignatura y plan de estudios.",
  antiguedad: "Cohorte académica institucional usada para agrupar discentes.",
  periodoAcademico: "Periodo operativo del ciclo académico.",
  anioFormacion: "Año de avance dentro del plan de estudios.",
  kardexOficial: "Documento institucional derivado del historial consolidado.",
  historialInterno: "Vista completa de trayectoria; no sustituye al kárdex oficial.",
  acta: "Instrumento académico por corte o evaluación final.",
  evaluacionFinal: "Corte final; distinto del resultado final preliminar.",
  resultadoFinalPreliminar: "Cálculo preliminar no oficial.",
  calificacionFinal: "Resultado oficial de la asignatura tras formalización.",
  conformidad: "Acuse o manifestación informativa del discente; no bloquea el flujo académico.",
  inconformidad: "Manifestación del discente con comentario obligatorio.",
  bitacora: "Eventos críticos registrados por el sistema.",
  registroExportacion: "Evidencia de descargas PDF/XLSX.",
  auditoriaInstitucional: "Consulta de eventos críticos y exportaciones.",
};

export const uiLabels = {
  actions: {
    save: "Guardar",
    create: "Crear",
    update: "Actualizar",
    consult: "Consultar",
    viewDetail: "Ver detalle",
    downloadXlsx: "Descargar XLSX",
    downloadPdf: "Descargar PDF",
    export: "Exportar",
    clearFilters: "Limpiar filtros",
    applyFilters: "Aplicar filtros",
    back: "Volver",
    confirm: "Confirmar",
    cancel: "Cancelar",
  },
  actas: {
    generarBorrador: "Generar borrador",
    regenerarBorrador: "Regenerar borrador",
    publicar: "Publicar acta",
    remitir: "Remitir acta",
    validar: "Validar acta",
    formalizar: "Formalizar acta",
  },
  badges: {
    documentoOficial: "Documento oficial",
    documentoNoOficial: "Documento no oficial",
    informacionSensible: "Información sensible",
    reporteNominal: "Reporte nominal",
    reporteAgregado: "Reporte agregado",
  },
} as const;

export function labelForTerm(key: GlosarioKey) {
  return glosarioInstitucional[key];
}

export function formatEntityName(entityType: string) {
  const normalized = entityType.toLowerCase().replaceAll("_", "-");
  const labels: Record<string, string> = {
    discente: glosarioInstitucional.discente,
    docente: glosarioInstitucional.docente,
    materia: glosarioInstitucional.asignatura,
    asignatura: glosarioInstitucional.asignatura,
    "programa-asignatura": glosarioInstitucional.programaAsignatura,
    antiguedad: glosarioInstitucional.antiguedad,
    periodo: glosarioInstitucional.periodoAcademico,
    kardex: glosarioInstitucional.kardexOficial,
    acta: glosarioInstitucional.acta,
    auditoria: glosarioInstitucional.auditoriaInstitucional,
  };
  return labels[normalized] || entityType;
}
