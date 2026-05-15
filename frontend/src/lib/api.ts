import type {
  ActividadRecienteItem,
  ActaExportable,
  ActaDetalle,
  ActasListResponse,
  AsignacionesListResponse,
  AuthMe,
  AuthenticatedUser,
  AuditEventDTO,
  AuditEventSummaryDTO,
  BitacoraEventosResponse,
  BusquedaResponse,
  CalendarioMes,
  CapturaPreliminarCorte,
  CapturaPreliminarPayload,
  CambioGrupoPayload,
  DashboardResumen,
  DiagnosticoCierrePeriodoDTO,
  DiscenteCargaAcademicaResponse,
  DiscenteActaDetalle,
  DiscenteActasResponse,
  DownloadResult,
  DocenteAsignacionDetalle,
  EventoCalendario,
  ExtraordinarioDTO,
  ExtraordinarioPayload,
  ExportacionRegistro,
  HistorialAcademicoDTO,
  HistorialSearchResponse,
  InscripcionExtraordinarioOpcion,
  KardexExportable,
  MovimientoAcademicoDTO,
  MovimientoAcademicoPayload,
  NotificacionesResponse,
  PerfilUsuario,
  PendienteAsignacionDocenteDTO,
  PeriodoOperativoDTO,
  PortalQuickAccess,
  ProcesoAperturaPeriodoDTO,
  ProcesoCierrePeriodoDTO,
  ResumenCalculoAcademico,
  ReporteDesempenoCodigo,
  ReporteDesempenoRespuesta,
  ReporteOperativoCodigo,
  ReporteOperativoRespuesta,
  ReporteTrayectoriaCodigo,
  ReporteTrayectoriaRespuesta,
  ReporteCatalogoItem,
  ResourceDetailResponse,
  ResourceListResponse,
  SituacionAcademicaDTO,
  SituacionAcademicaPayload,
  TrayectoriaListResponse,
} from "./types";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
let csrfToken: string | null = null;

function apiUrl(path: string) {
  return `${BACKEND_URL}${path}`;
}

async function parseJson<T>(response: Response): Promise<T> {
  const data = (await response.json()) as T;
  if (!response.ok) {
    const message = typeof data === "object" && data
      ? String((data as { error?: unknown; message?: unknown }).error ?? (data as { message?: unknown }).message ?? "No fue posible completar la solicitud.")
      : "No fue posible completar la solicitud.";
    const error = new Error(message) as Error & { errors?: Record<string, string[]>; status?: number };
    error.status = response.status;
    if (typeof data === "object" && data && "errors" in data) {
      error.errors = (data as { errors?: Record<string, string[]> }).errors;
    }
    throw error;
  }
  return data;
}

async function apiGet<T>(path: string) {
  const response = await fetch(apiUrl(path), {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });
  return parseJson<T>(response);
}

async function apiMutate<T>(path: string, method = "POST", body: unknown = {}) {
  const token = await getCsrfToken();
  const response = await fetch(apiUrl(path), {
    method,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: method === "DELETE" ? undefined : JSON.stringify(body),
  });
  return parseJson<T>(response);
}

export async function getCsrfToken() {
  if (csrfToken) return csrfToken;
  const data = await apiGet<{ csrfToken: string }>("/api/auth/csrf/");
  csrfToken = data.csrfToken;
  return csrfToken;
}

export async function login(username: string, password: string) {
  const token = await getCsrfToken();
  const response = await fetch(apiUrl("/api/auth/login/"), {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: JSON.stringify({ username, password }),
  });
  const data = await parseJson<{ ok: true; csrfToken: string; user: AuthenticatedUser }>(response);
  csrfToken = data.csrfToken;
  return data;
}

export async function logout() {
  const data = await apiMutate<{ ok: true }>("/api/auth/logout/");
  csrfToken = null;
  return data;
}

export async function getMe() {
  return apiGet<AuthMe>("/api/auth/me/");
}

export async function getDashboardResumen() {
  return apiGet<DashboardResumen>("/api/dashboard/resumen/");
}

export async function getActividadReciente() {
  return apiGet<{ items: ActividadRecienteItem[] }>("/api/dashboard/actividad-reciente/");
}

export async function getNotificaciones(limit = 8) {
  return apiGet<NotificacionesResponse>(`/api/notificaciones/?limit=${limit}`);
}

export async function marcarNotificacionLeida(id: number) {
  return apiMutate<{ ok: true }>(`/api/notificaciones/${id}/leer/`);
}

export async function marcarTodasNotificacionesLeidas() {
  return apiMutate<{ ok: true; unread_count: number }>("/api/notificaciones/leer-todas/");
}

export async function getCalendarioMes(year: number, month: number) {
  return apiGet<CalendarioMes>(`/api/calendario/mes/?year=${year}&month=${month}`);
}

export async function getEventosProximos() {
  return apiGet<{ items: EventoCalendario[] }>("/api/calendario/proximos/");
}

export async function buscarPortal(query: string) {
  return apiGet<BusquedaResponse>(`/api/busqueda/?q=${encodeURIComponent(query)}`);
}

export async function getPerfilMe() {
  return apiGet<PerfilUsuario>("/api/perfil/me/");
}

export async function getAccesosRapidos() {
  return apiGet<{ persisted: boolean; items: PortalQuickAccess[] }>("/api/accesos-rapidos/");
}

export async function crearAccesoRapido(payload: { etiqueta: string; url: string; icono?: string; orden?: number }) {
  return apiMutate<{ ok: true; item: PortalQuickAccess }>("/api/accesos-rapidos/crear/", "POST", payload);
}

export async function eliminarAccesoRapido(id: number) {
  return apiMutate<{ ok: true }>(`/api/accesos-rapidos/${id}/`, "DELETE");
}

export async function getReportesCatalogo() {
  return apiGet<{ items: ReporteCatalogoItem[] }>("/api/reportes/catalogo/");
}

export async function getExportaciones(params: Record<string, string> = {}) {
  return apiGet<{ items: ExportacionRegistro[] }>(`/api/exportaciones/${queryString(params)}`);
}

export async function getAuditoriaExportaciones(params: Record<string, string> = {}) {
  return apiGet<{ items: ExportacionRegistro[] }>(`/api/auditoria/exportaciones/${queryString(params)}`);
}

export async function getAuditoriaEventos(params: Record<string, string> = {}) {
  return apiGet<BitacoraEventosResponse>(`/api/auditoria/eventos/${queryString(params)}`);
}

export async function getAuditoriaEventoDetalle(id: number | string) {
  return apiGet<{ ok: boolean; item: AuditEventDTO }>(`/api/auditoria/eventos/${encodeURIComponent(String(id))}/`).then((data) => data.item);
}

export async function getAuditoriaResumen(params: Record<string, string> = {}) {
  return apiGet<AuditEventSummaryDTO & { resumen?: AuditEventSummaryDTO }>(`/api/auditoria/eventos/resumen/${queryString(params)}`).then((data) => data.resumen || data);
}

export async function getEventosCriticosPorObjeto(objetoTipo: string, objetoId: number | string, params: Record<string, string> = {}) {
  return getAuditoriaEventos({
    ...params,
    objeto_tipo: objetoTipo,
    objeto_id: String(objetoId),
  });
}

export async function descargarAuditoriaEventosXlsx(params: Record<string, string> = {}) {
  return downloadFile(`/api/exportaciones/auditoria/eventos/xlsx/${queryString(params)}`, {
    forbidden: "No tienes permiso para exportar la bitácora de eventos.",
    fallback: "La descarga de la bitácora falló. Intenta nuevamente o contacta soporte.",
  });
}

export async function getActasExportables() {
  return apiGet<{ items: ActaExportable[] }>("/api/exportaciones/actas-disponibles/");
}

export async function getKardexExportables(params: Record<string, string> = {}) {
  return apiGet<{ items: KardexExportable[] }>(`/api/exportaciones/kardex-disponibles/${queryString(params)}`);
}

export async function descargarActaPdf(actaId: number) {
  return downloadFile(`/api/exportaciones/actas/${actaId}/pdf/`);
}

export async function descargarActaXlsx(actaId: number) {
  return downloadFile(`/api/exportaciones/actas/${actaId}/xlsx/`);
}

export async function descargarCalificacionFinalPdf(asignacionDocenteId: number) {
  return downloadFile(`/api/exportaciones/asignaciones/${asignacionDocenteId}/calificacion-final/pdf/`);
}

export async function descargarCalificacionFinalXlsx(asignacionDocenteId: number) {
  return downloadFile(`/api/exportaciones/asignaciones/${asignacionDocenteId}/calificacion-final/xlsx/`);
}

export async function descargarKardexPdf(discenteId: number) {
  return downloadFile(`/api/exportaciones/kardex/${discenteId}/pdf/`, {
    forbidden: "No tienes permiso para exportar este kárdex.",
    notFound: "No se encontró el discente o no existe información suficiente para generar el kárdex.",
    fallback: "No fue posible generar el kárdex. Intenta nuevamente o contacta soporte.",
  });
}

export async function getReporteOperativo(slug: ReporteOperativoCodigo, params: Record<string, string> = {}) {
  return apiGet<ReporteOperativoRespuesta>(`/api/reportes/operativos/${slug}/${queryString(params)}`);
}

export async function getReporteOperativoActasEstado(params: Record<string, string> = {}) {
  return getReporteOperativo("actas-estado", params);
}

export async function getReporteOperativoActasPendientes(params: Record<string, string> = {}) {
  return getReporteOperativo("actas-pendientes", params);
}

export async function getReporteOperativoInconformidades(params: Record<string, string> = {}) {
  return getReporteOperativo("inconformidades", params);
}

export async function getReporteOperativoSinConformidad(params: Record<string, string> = {}) {
  return getReporteOperativo("sin-conformidad", params);
}

export async function getReporteOperativoActasFormalizadas(params: Record<string, string> = {}) {
  return getReporteOperativo("actas-formalizadas", params);
}

export async function getReporteOperativoValidacionesActa(params: Record<string, string> = {}) {
  return getReporteOperativo("validaciones-acta", params);
}

export async function getReporteOperativoExportacionesRealizadas(params: Record<string, string> = {}) {
  return getReporteOperativo("exportaciones-realizadas", params);
}

export async function descargarReporteOperativoXlsx(slug: ReporteOperativoCodigo, params: Record<string, string> = {}) {
  return downloadFile(`/api/exportaciones/reportes/${slug}/xlsx/${queryString(params)}`, {
    forbidden: "No tienes permiso para exportar este reporte.",
    fallback: "La descarga del reporte falló. Intenta nuevamente o contacta soporte.",
  });
}

export async function descargarReporteActasEstadoXlsx(params: Record<string, string> = {}) {
  return descargarReporteOperativoXlsx("actas-estado", params);
}

export async function descargarReporteActasPendientesXlsx(params: Record<string, string> = {}) {
  return descargarReporteOperativoXlsx("actas-pendientes", params);
}

export async function descargarReporteInconformidadesXlsx(params: Record<string, string> = {}) {
  return descargarReporteOperativoXlsx("inconformidades", params);
}

export async function descargarReporteSinConformidadXlsx(params: Record<string, string> = {}) {
  return descargarReporteOperativoXlsx("sin-conformidad", params);
}

export async function descargarReporteActasFormalizadasXlsx(params: Record<string, string> = {}) {
  return descargarReporteOperativoXlsx("actas-formalizadas", params);
}

export async function descargarReporteValidacionesActaXlsx(params: Record<string, string> = {}) {
  return descargarReporteOperativoXlsx("validaciones-acta", params);
}

export async function descargarReporteExportacionesRealizadasXlsx(params: Record<string, string> = {}) {
  return descargarReporteOperativoXlsx("exportaciones-realizadas", params);
}

export async function getReporteDesempeno(slug: ReporteDesempenoCodigo, params: Record<string, string> = {}) {
  return apiGet<ReporteDesempenoRespuesta>(`/api/reportes/desempeno/${slug}/${queryString(params)}`);
}

export async function getReporteDesempenoAprobadosReprobados(params: Record<string, string> = {}) {
  return getReporteDesempeno("aprobados-reprobados", params);
}

export async function getReporteDesempenoPromedios(params: Record<string, string> = {}) {
  return getReporteDesempeno("promedios", params);
}

export async function getReporteDesempenoDistribucion(params: Record<string, string> = {}) {
  return getReporteDesempeno("distribucion", params);
}

export async function getReporteDesempenoExentos(params: Record<string, string> = {}) {
  return getReporteDesempeno("exentos", params);
}

export async function getReporteDesempenoDocentes(params: Record<string, string> = {}) {
  return getReporteDesempeno("docentes", params);
}

export async function getReporteDesempenoCohorte(params: Record<string, string> = {}) {
  return getReporteDesempeno("cohorte", params);
}

export async function getReporteDesempenoReprobadosNominal(params: Record<string, string> = {}) {
  return getReporteDesempeno("reprobados-nominal", params);
}

export async function getReporteDesempenoCuadroAprovechamiento(params: Record<string, string> = {}) {
  return getReporteDesempeno("cuadro-aprovechamiento", params);
}

const desempenoDownloadEndpoint: Record<ReporteDesempenoCodigo, string> = {
  "aprobados-reprobados": "aprobados-reprobados",
  promedios: "promedios",
  distribucion: "distribucion",
  exentos: "exentos",
  docentes: "desempeno-docente",
  cohorte: "desempeno-cohorte",
  "reprobados-nominal": "reprobados-nominal",
  "cuadro-aprovechamiento": "cuadro-aprovechamiento",
};

export async function descargarReporteDesempenoXlsx(slug: ReporteDesempenoCodigo, params: Record<string, string> = {}) {
  return downloadFile(`/api/exportaciones/reportes/${desempenoDownloadEndpoint[slug]}/xlsx/${queryString(params)}`, {
    forbidden: "No tienes permiso para exportar este reporte de desempeño.",
    fallback: "La descarga del reporte falló. Intenta nuevamente o contacta soporte.",
  });
}

export async function descargarReporteAprobadosReprobadosXlsx(params: Record<string, string> = {}) {
  return descargarReporteDesempenoXlsx("aprobados-reprobados", params);
}

export async function descargarReportePromediosXlsx(params: Record<string, string> = {}) {
  return descargarReporteDesempenoXlsx("promedios", params);
}

export async function descargarReporteDistribucionXlsx(params: Record<string, string> = {}) {
  return descargarReporteDesempenoXlsx("distribucion", params);
}

export async function descargarReporteExentosXlsx(params: Record<string, string> = {}) {
  return descargarReporteDesempenoXlsx("exentos", params);
}

export async function descargarReporteDesempenoDocenteXlsx(params: Record<string, string> = {}) {
  return descargarReporteDesempenoXlsx("docentes", params);
}

export async function descargarReporteDesempenoCohorteXlsx(params: Record<string, string> = {}) {
  return descargarReporteDesempenoXlsx("cohorte", params);
}

export async function descargarReporteReprobadosNominalXlsx(params: Record<string, string> = {}) {
  return descargarReporteDesempenoXlsx("reprobados-nominal", params);
}

export async function descargarReporteCuadroAprovechamientoXlsx(params: Record<string, string> = {}) {
  return descargarReporteDesempenoXlsx("cuadro-aprovechamiento", params);
}

const trayectoriaPreviewEndpoint: Record<ReporteTrayectoriaCodigo, string> = {
  extraordinarios: "/api/reportes/situacion/extraordinarios/",
  "situacion-actual": "/api/reportes/situacion/actual/",
  "bajas-temporales": "/api/reportes/situacion/bajas-temporales/",
  "bajas-definitivas": "/api/reportes/situacion/bajas-definitivas/",
  reingresos: "/api/reportes/situacion/reingresos/",
  egresables: "/api/reportes/situacion/egresables/",
  "situacion-agregado": "/api/reportes/situacion/agregado/",
  "movimientos-academicos": "/api/reportes/movimientos/",
  "cambios-grupo": "/api/reportes/movimientos/cambios-grupo/",
  "historial-interno": "/api/reportes/historial-interno/",
  "historial-interno-discente": "/api/reportes/historial-interno/",
};

const trayectoriaDownloadEndpoint: Record<ReporteTrayectoriaCodigo, string> = {
  extraordinarios: "/api/exportaciones/reportes/extraordinarios/xlsx/",
  "situacion-actual": "/api/exportaciones/reportes/situacion-actual/xlsx/",
  "bajas-temporales": "/api/exportaciones/reportes/bajas-temporales/xlsx/",
  "bajas-definitivas": "/api/exportaciones/reportes/bajas-definitivas/xlsx/",
  reingresos: "/api/exportaciones/reportes/reingresos/xlsx/",
  egresables: "/api/exportaciones/reportes/egresables/xlsx/",
  "situacion-agregado": "/api/exportaciones/reportes/situacion-agregado/xlsx/",
  "movimientos-academicos": "/api/exportaciones/reportes/movimientos-academicos/xlsx/",
  "cambios-grupo": "/api/exportaciones/reportes/cambios-grupo/xlsx/",
  "historial-interno": "/api/exportaciones/reportes/historial-interno/xlsx/",
  "historial-interno-discente": "/api/exportaciones/reportes/historial-interno/",
};

export async function getReporteTrayectoria(slug: ReporteTrayectoriaCodigo, params: Record<string, string> = {}) {
  if (slug === "historial-interno-discente") {
    const discenteId = params.discente_id;
    if (!discenteId) throw new Error("Captura un ID de discente válido para consultar el historial interno por discente.");
    const rest = { ...params };
    delete rest.discente_id;
    return getReporteHistorialInternoDiscente(discenteId, rest);
  }
  return apiGet<ReporteTrayectoriaRespuesta>(`${trayectoriaPreviewEndpoint[slug]}${queryString(params)}`);
}

export async function getReporteSituacionExtraordinarios(params: Record<string, string> = {}) {
  return getReporteTrayectoria("extraordinarios", params);
}

export async function getReporteSituacionActual(params: Record<string, string> = {}) {
  return getReporteTrayectoria("situacion-actual", params);
}

export async function getReporteBajasTemporales(params: Record<string, string> = {}) {
  return getReporteTrayectoria("bajas-temporales", params);
}

export async function getReporteBajasDefinitivas(params: Record<string, string> = {}) {
  return getReporteTrayectoria("bajas-definitivas", params);
}

export async function getReporteReingresos(params: Record<string, string> = {}) {
  return getReporteTrayectoria("reingresos", params);
}

export async function getReporteEgresables(params: Record<string, string> = {}) {
  return getReporteTrayectoria("egresables", params);
}

export async function getReporteSituacionAgregado(params: Record<string, string> = {}) {
  return getReporteTrayectoria("situacion-agregado", params);
}

export async function getReporteMovimientosAcademicos(params: Record<string, string> = {}) {
  return getReporteTrayectoria("movimientos-academicos", params);
}

export async function getReporteCambiosGrupo(params: Record<string, string> = {}) {
  return getReporteTrayectoria("cambios-grupo", params);
}

export async function getReporteHistorialInterno(params: Record<string, string> = {}) {
  return getReporteTrayectoria("historial-interno", params);
}

export async function getReporteHistorialInternoDiscente(discenteId: string | number, params: Record<string, string> = {}) {
  return apiGet<ReporteTrayectoriaRespuesta>(`/api/reportes/historial-interno/${encodeURIComponent(String(discenteId))}/${queryString(params)}`);
}

export async function descargarReporteTrayectoriaXlsx(slug: ReporteTrayectoriaCodigo, params: Record<string, string> = {}) {
  if (slug === "historial-interno-discente") {
    const discenteId = params.discente_id;
    if (!discenteId) throw new Error("Captura un ID de discente válido para descargar el historial interno por discente.");
    const rest = { ...params };
    delete rest.discente_id;
    return descargarReporteHistorialInternoDiscenteXlsx(discenteId, rest);
  }
  return downloadFile(`${trayectoriaDownloadEndpoint[slug]}${queryString(params)}`, {
    forbidden: "No tienes permiso para exportar este reporte de trayectoria.",
    notFound: "No se encontró información suficiente para generar este reporte.",
    fallback: "La descarga del reporte falló. Intenta nuevamente o contacta soporte.",
  });
}

export async function descargarReporteExtraordinariosXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("extraordinarios", params);
}

export async function descargarReporteSituacionActualXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("situacion-actual", params);
}

export async function descargarReporteBajasTemporalesXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("bajas-temporales", params);
}

export async function descargarReporteBajasDefinitivasXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("bajas-definitivas", params);
}

export async function descargarReporteReingresosXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("reingresos", params);
}

export async function descargarReporteEgresablesXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("egresables", params);
}

export async function descargarReporteSituacionAgregadoXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("situacion-agregado", params);
}

export async function descargarReporteMovimientosAcademicosXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("movimientos-academicos", params);
}

export async function descargarReporteCambiosGrupoXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("cambios-grupo", params);
}

export async function descargarReporteHistorialInternoXlsx(params: Record<string, string> = {}) {
  return descargarReporteTrayectoriaXlsx("historial-interno", params);
}

export async function descargarReporteHistorialInternoDiscenteXlsx(discenteId: string | number, params: Record<string, string> = {}) {
  return downloadFile(`/api/exportaciones/reportes/historial-interno/${encodeURIComponent(String(discenteId))}/xlsx/${queryString(params)}`, {
    forbidden: "No tienes permiso para exportar este historial interno.",
    notFound: "No se encontró el discente o no existe información suficiente para generar el historial interno.",
    fallback: "No fue posible descargar el historial interno. Intenta nuevamente o contacta soporte.",
  });
}

export async function listResource(endpoint: string, params: Record<string, string> = {}) {
  return apiGet<ResourceListResponse>(`${ensureTrailingSlash(endpoint)}${queryString(params)}`);
}

export async function getResource(endpoint: string, id: number | string) {
  return apiGet<ResourceDetailResponse>(`${ensureTrailingSlash(endpoint)}${encodeURIComponent(String(id))}/`);
}

export async function createResource(endpoint: string, payload: Record<string, unknown>) {
  return apiMutate<ResourceDetailResponse>(ensureTrailingSlash(endpoint), "POST", payload);
}

export async function updateResource(endpoint: string, id: number | string, payload: Record<string, unknown>) {
  return apiMutate<ResourceDetailResponse>(`${ensureTrailingSlash(endpoint)}${encodeURIComponent(String(id))}/`, "PATCH", payload);
}

export async function activateResource(endpoint: string, id: number | string) {
  return apiMutate<ResourceDetailResponse>(`${ensureTrailingSlash(endpoint)}${encodeURIComponent(String(id))}/activar/`);
}

export async function deactivateResource(endpoint: string, id: number | string) {
  return apiMutate<ResourceDetailResponse>(`${ensureTrailingSlash(endpoint)}${encodeURIComponent(String(id))}/inactivar/`);
}

export async function closeResource(endpoint: string, id: number | string, payload: Record<string, unknown> = {}) {
  return apiMutate<ResourceDetailResponse>(`${ensureTrailingSlash(endpoint)}${encodeURIComponent(String(id))}/cerrar/`, "POST", payload);
}

export async function getDocenteAsignaciones(params: Record<string, string> = {}) {
  return apiGet<AsignacionesListResponse>(`/api/docente/asignaciones/${queryString(params)}`);
}

export async function getDocenteAsignacionDetalle(id: number | string) {
  return apiGet<DocenteAsignacionDetalle>(`/api/docente/asignaciones/${encodeURIComponent(String(id))}/`);
}

export async function getDocenteCaptura(asignacionId: number | string, corte: string) {
  return apiGet<CapturaPreliminarCorte>(`/api/docente/asignaciones/${encodeURIComponent(String(asignacionId))}/captura/${encodeURIComponent(corte)}/`);
}

export async function guardarDocenteCaptura(asignacionId: number | string, corte: string, payload: CapturaPreliminarPayload) {
  return apiMutate<CapturaPreliminarCorte>(`/api/docente/asignaciones/${encodeURIComponent(String(asignacionId))}/captura/${encodeURIComponent(corte)}/`, "POST", payload);
}

export async function getDocenteResumen(asignacionId: number | string) {
  return apiGet<ResumenCalculoAcademico>(`/api/docente/asignaciones/${encodeURIComponent(String(asignacionId))}/resumen/`);
}

export async function getDocenteActas(params: Record<string, string> = {}) {
  return apiGet<ActasListResponse>(`/api/docente/actas/${queryString(params)}`);
}

export async function getDocenteActaDetalle(actaId: number | string) {
  return apiGet<ActaDetalle>(`/api/docente/actas/${encodeURIComponent(String(actaId))}/`);
}

export async function generarActaDocente(asignacionId: number | string, corte: string) {
  return apiMutate<{ ok: true; item: unknown; detalle: ActaDetalle }>(`/api/docente/asignaciones/${encodeURIComponent(String(asignacionId))}/actas/generar/`, "POST", { corte_codigo: corte });
}

export async function regenerarActaDocente(actaId: number | string) {
  return apiMutate<{ ok: true; item: unknown }>(`/api/docente/actas/${encodeURIComponent(String(actaId))}/regenerar/`);
}

export async function publicarActaDocente(actaId: number | string) {
  return apiMutate<{ ok: true; item: unknown; detalle: ActaDetalle }>(`/api/docente/actas/${encodeURIComponent(String(actaId))}/publicar/`);
}

export async function remitirActaDocente(actaId: number | string) {
  return apiMutate<{ ok: true; item: unknown; detalle: ActaDetalle }>(`/api/docente/actas/${encodeURIComponent(String(actaId))}/remitir/`);
}

export async function getDiscenteActas() {
  return apiGet<DiscenteActasResponse>("/api/discente/actas/");
}

export async function getDiscenteCargaAcademica() {
  return apiGet<DiscenteCargaAcademicaResponse>("/api/discente/carga-academica/");
}

export async function getDiscenteActaDetalle(detalleId: number | string) {
  return apiGet<DiscenteActaDetalle>(`/api/discente/actas/${encodeURIComponent(String(detalleId))}/`);
}

export async function registrarConformidadDiscente(detalleId: number | string, payload: { tipo_conformidad: string; comentario?: string }) {
  return apiMutate<{ ok: true; item: unknown }>(`/api/discente/actas/${encodeURIComponent(String(detalleId))}/conformidad/`, "POST", payload);
}

export async function getJefaturaCarreraActasPendientes(params: Record<string, string> = {}) {
  return apiGet<ActasListResponse>(`/api/jefatura-carrera/actas/pendientes/${queryString(params)}`);
}

export async function getJefaturaCarreraActaDetalle(actaId: number | string) {
  return apiGet<ActaDetalle>(`/api/jefatura-carrera/actas/${encodeURIComponent(String(actaId))}/`);
}

export async function validarActaJefaturaCarrera(actaId: number | string, payload: { observacion?: string } = {}) {
  return apiMutate<{ ok: true; item: unknown; detalle: ActaDetalle }>(`/api/jefatura-carrera/actas/${encodeURIComponent(String(actaId))}/validar/`, "POST", payload);
}

export async function getJefaturaAcademicaActasPendientes(params: Record<string, string> = {}) {
  return apiGet<ActasListResponse>(`/api/jefatura-academica/actas/pendientes/${queryString(params)}`);
}

export async function getJefaturaAcademicaActaDetalle(actaId: number | string) {
  return apiGet<ActaDetalle>(`/api/jefatura-academica/actas/${encodeURIComponent(String(actaId))}/`);
}

export async function formalizarActaJefaturaAcademica(actaId: number | string, payload: { observacion?: string } = {}) {
  return apiMutate<{ ok: true; item: unknown; detalle: ActaDetalle }>(`/api/jefatura-academica/actas/${encodeURIComponent(String(actaId))}/formalizar/`, "POST", payload);
}

export async function getEstadisticaActas(params: Record<string, string> = {}) {
  return apiGet<ActasListResponse>(`/api/estadistica/actas/${queryString(params)}`);
}

export async function getEstadisticaActaDetalle(actaId: number | string) {
  return apiGet<ActaDetalle>(`/api/estadistica/actas/${encodeURIComponent(String(actaId))}/`);
}

export async function getMiHistorial() {
  return apiGet<HistorialAcademicoDTO>("/api/trayectoria/mi-historial/");
}

export async function buscarHistoriales(params: Record<string, string> = {}) {
  return apiGet<HistorialSearchResponse>(`/api/trayectoria/historial/${queryString(params)}`);
}

export async function getHistorialDiscente(discenteId: number | string) {
  return apiGet<HistorialAcademicoDTO>(`/api/trayectoria/historial/${encodeURIComponent(String(discenteId))}/`);
}

export async function getExtraordinarios(params: Record<string, string> = {}) {
  return apiGet<TrayectoriaListResponse<ExtraordinarioDTO>>(`/api/trayectoria/extraordinarios/${queryString(params)}`);
}

export async function getExtraordinario(id: number | string) {
  return apiGet<{ ok: true; item: ExtraordinarioDTO }>(`/api/trayectoria/extraordinarios/${encodeURIComponent(String(id))}/`);
}

export async function getOpcionesInscripcionesExtraordinario(params: Record<string, string> = {}) {
  return apiGet<TrayectoriaListResponse<InscripcionExtraordinarioOpcion>>(`/api/trayectoria/opciones/inscripciones-extraordinario/${queryString(params)}`);
}

export async function crearExtraordinario(payload: ExtraordinarioPayload) {
  return apiMutate<{ ok: true; item: ExtraordinarioDTO }>("/api/trayectoria/extraordinarios/", "POST", payload);
}

export async function getSituaciones(params: Record<string, string> = {}) {
  return apiGet<TrayectoriaListResponse<SituacionAcademicaDTO>>(`/api/trayectoria/situaciones/${queryString(params)}`);
}

export async function getSituacion(id: number | string) {
  return apiGet<{ ok: true; item: SituacionAcademicaDTO }>(`/api/trayectoria/situaciones/${encodeURIComponent(String(id))}/`);
}

export async function crearSituacionAcademica(payload: SituacionAcademicaPayload) {
  return apiMutate<{ ok: true; item: SituacionAcademicaDTO }>("/api/trayectoria/situaciones/", "POST", payload);
}

export async function getMovimientosAcademicos(params: Record<string, string> = {}) {
  return apiGet<TrayectoriaListResponse<MovimientoAcademicoDTO>>(`/api/relaciones/movimientos/${queryString(params)}`);
}

export async function getMovimientoAcademico(id: number | string) {
  return apiGet<{ ok: true; item: MovimientoAcademicoDTO }>(`/api/relaciones/movimientos/${encodeURIComponent(String(id))}/`);
}

export async function crearMovimientoAcademico(payload: MovimientoAcademicoPayload) {
  return apiMutate<{ ok: true; item: MovimientoAcademicoDTO }>("/api/relaciones/movimientos/", "POST", payload);
}

export async function crearCambioGrupo(payload: CambioGrupoPayload) {
  return apiMutate<{ ok: true; item: MovimientoAcademicoDTO }>("/api/relaciones/movimientos/cambio-grupo/", "POST", payload);
}

export async function getPeriodos(params: Record<string, string> = {}) {
  return apiGet<TrayectoriaListResponse<PeriodoOperativoDTO>>(`/api/periodos/${queryString(params)}`);
}

export async function getDiagnosticoCierrePeriodo(periodoId: number | string) {
  return apiGet<DiagnosticoCierrePeriodoDTO>(`/api/periodos/${encodeURIComponent(String(periodoId))}/diagnostico-cierre/`);
}

export async function cerrarPeriodo(periodoId: number | string, payload: { observaciones?: string } = {}) {
  return apiMutate<{ ok: true; item: ProcesoCierrePeriodoDTO }>(`/api/periodos/${encodeURIComponent(String(periodoId))}/cerrar/`, "POST", payload);
}

export async function getCierres(params: Record<string, string> = {}) {
  return apiGet<TrayectoriaListResponse<ProcesoCierrePeriodoDTO>>(`/api/cierres/${queryString(params)}`);
}

export async function getCierre(id: number | string) {
  return apiGet<{ ok: true; item: ProcesoCierrePeriodoDTO }>(`/api/cierres/${encodeURIComponent(String(id))}/`);
}

export async function crearAperturaPeriodo(payload: { periodo_origen_id: string | number; periodo_destino_id: string | number; observaciones?: string }) {
  return apiMutate<{ ok: true; item: ProcesoAperturaPeriodoDTO }>("/api/aperturas/crear/", "POST", payload);
}

export async function getAperturas(params: Record<string, string> = {}) {
  return apiGet<TrayectoriaListResponse<ProcesoAperturaPeriodoDTO>>(`/api/aperturas/${queryString(params)}`);
}

export async function getApertura(id: number | string) {
  return apiGet<{ ok: true; item: ProcesoAperturaPeriodoDTO }>(`/api/aperturas/${encodeURIComponent(String(id))}/`);
}

export async function getPendientesAsignacionDocente(params: Record<string, string> = {}) {
  return apiGet<{ ok: true; total: number; periodo?: PeriodoOperativoDTO; items: PendienteAsignacionDocenteDTO[] }>(`/api/pendientes-asignacion-docente/${queryString(params)}`);
}

export function backendUrl(path: string) {
  if (path.startsWith("http")) return path;
  return apiUrl(path.startsWith("/") ? path : `/${path}`);
}

function ensureTrailingSlash(path: string) {
  return path.endsWith("/") ? path : `${path}/`;
}

function queryString(params: Record<string, string>) {
  const filtered = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) filtered.set(key, value);
  });
  const value = filtered.toString();
  return value ? `?${value}` : "";
}

async function downloadFile(
  path: string,
  messages: { forbidden?: string; notFound?: string; fallback?: string } = {},
): Promise<DownloadResult> {
  const response = await fetch(apiUrl(path), {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    if (response.status === 403 && messages.forbidden) throw new Error(messages.forbidden);
    if (response.status === 404 && messages.notFound) throw new Error(messages.notFound);
    throw new Error(await readDownloadError(response, messages.fallback));
  }

  const blob = await response.blob();
  const filename = filenameFromDisposition(response.headers.get("Content-Disposition")) || "exportacion";
  const registroExportacionId = response.headers.get("X-Registro-Exportacion-Id");
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
  return {
    filename,
    registroExportacionId,
    contentType: blob.type || response.headers.get("Content-Type") || "application/octet-stream",
    size: blob.size,
  };
}

async function readDownloadError(response: Response, fallback = "La exportación falló. Intenta nuevamente o contacta soporte.") {
  const contentType = response.headers.get("Content-Type") || "";
  if (contentType.includes("application/json")) {
    try {
      const data = (await response.json()) as { error?: unknown };
      if (data.error) {
        return typeof data.error === "string" ? data.error : JSON.stringify(data.error);
      }
    } catch {
      return fallback;
    }
  }
  const text = await response.text();
  return text || fallback;
}

function filenameFromDisposition(disposition: string | null) {
  if (!disposition) return null;
  const utfMatch = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utfMatch?.[1]) return decodeURIComponent(utfMatch[1]);
  const asciiMatch = disposition.match(/filename="?([^";]+)"?/i);
  return asciiMatch?.[1] ?? null;
}
