export const microcopy = {
  accessDenied: {
    title: "Acceso restringido",
    default: "No tienes permiso para consultar esta sección.",
    operation: "Tu perfil no tiene habilitada esta operación.",
    help: "Si consideras que necesitas acceso, contacta a Estadística o al administrador del sistema.",
  },
  empty: {
    defaultTitle: "No hay registros para mostrar.",
    defaultDescription: "Cuando existan registros autorizados, aparecerán en esta sección.",
    noResultsTitle: "Sin resultados",
    noResultsDescription: "No encontramos registros con los filtros seleccionados. Ajusta los criterios e intenta nuevamente.",
    noDataTitle: "Aún no hay registros",
    noDataDescription: "Cuando se capture información autorizada, aparecerá en esta sección.",
    pendingTitle: "Configuración pendiente",
    pendingDescription: "Este módulo requiere datos base antes de poder operar.",
  },
  errors: {
    forbidden: "No tienes permiso para realizar esta acción.",
    notFound: "No encontramos el registro solicitado.",
    validation: "Revisa la información capturada.",
    unexpected: "Ocurrió un error inesperado. Intenta nuevamente o contacta soporte.",
    network: "No fue posible conectar con el servidor.",
  },
  academicLoad: {
    personal: "Aquí se muestran tus asignaturas inscritas para el periodo activo.",
    privacy: "Esta vista es personal y no muestra información de otros discentes.",
  },
  historial: {
    internal: "El historial académico interno conserva la secuencia completa de resultados y eventos. No sustituye al kárdex oficial.",
  },
  kardex: {
    oficial: "El kárdex oficial es un documento institucional y solo puede ser generado por perfiles autorizados.",
  },
  actas: {
    noOficial: "El acta aún no es oficial hasta su formalización.",
    conformidad: "La conformidad del discente es informativa y no bloquea el flujo académico.",
    soloLectura: "Después de la remisión, la conformidad queda en solo lectura.",
  },
  auditoria: {
    eventos: "La auditoría institucional muestra eventos críticos registrados por el sistema.",
    exportaciones: "El historial de exportaciones muestra descargas PDF/XLSX y sus folios técnicos.",
  },
  reportes: {
    preview: "La vista previa puede estar limitada. Descarga el XLSX para revisión completa.",
    sensitive: "Los reportes nominales contienen información académica sensible.",
  },
  catalogos: {
    readOnly: "Tu perfil permite consultar este catálogo.",
    backendValidation: "Los cambios se validan en backend antes de guardarse.",
  },
  periodos: {
    diagnostico: "El diagnóstico no modifica datos; solo identifica bloqueantes y advertencias.",
    cierre: "El cierre de periodo requiere que no existan bloqueantes.",
    apertura: "La apertura no asigna docentes automáticamente.",
  },
  sensitive: {
    academic: "Esta sección contiene información académica sensible. Consúltala únicamente para fines institucionales autorizados.",
    noMilitaryId: "No se muestra matrícula militar por defecto.",
    internalHistory: "El historial interno no sustituye al kárdex oficial.",
    inconformidad: "Los comentarios de inconformidad se resguardan como evidencia del sistema.",
  },
} as const;

export function accessDeniedMessage(context: "section" | "operation" = "section") {
  return context === "operation" ? microcopy.accessDenied.operation : microcopy.accessDenied.default;
}
