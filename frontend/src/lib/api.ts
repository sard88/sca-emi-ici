import type {
  ActividadRecienteItem,
  ActaExportable,
  AuthMe,
  AuthenticatedUser,
  BusquedaResponse,
  CalendarioMes,
  DashboardResumen,
  DownloadResult,
  EventoCalendario,
  ExportacionRegistro,
  KardexExportable,
  NotificacionesResponse,
  PerfilUsuario,
  PortalQuickAccess,
  ReporteDesempenoCodigo,
  ReporteDesempenoRespuesta,
  ReporteOperativoCodigo,
  ReporteOperativoRespuesta,
  ReporteCatalogoItem,
} from "./types";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
let csrfToken: string | null = null;

function apiUrl(path: string) {
  return `${BACKEND_URL}${path}`;
}

async function parseJson<T>(response: Response): Promise<T> {
  const data = (await response.json()) as T;
  if (!response.ok) {
    const message = typeof data === "object" && data && "error" in data
      ? String((data as { error?: unknown }).error)
      : "No fue posible completar la solicitud.";
    throw new Error(message);
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

export function backendUrl(path: string) {
  if (path.startsWith("http")) return path;
  return apiUrl(path.startsWith("/") ? path : `/${path}`);
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
