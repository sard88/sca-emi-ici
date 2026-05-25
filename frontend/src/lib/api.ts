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
  NotificacionesResponse,
  PerfilUsuario,
  PortalQuickAccess,
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

async function downloadFile(path: string): Promise<DownloadResult> {
  const response = await fetch(apiUrl(path), {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await readDownloadError(response));
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
  return { filename, registroExportacionId };
}

async function readDownloadError(response: Response) {
  const contentType = response.headers.get("Content-Type") || "";
  if (contentType.includes("application/json")) {
    try {
      const data = (await response.json()) as { error?: unknown };
      if (data.error) {
        return typeof data.error === "string" ? data.error : JSON.stringify(data.error);
      }
    } catch {
      return "La exportación falló. Intenta nuevamente o contacta soporte.";
    }
  }
  const text = await response.text();
  return text || "La exportación falló. Intenta nuevamente o contacta soporte.";
}

function filenameFromDisposition(disposition: string | null) {
  if (!disposition) return null;
  const utfMatch = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utfMatch?.[1]) return decodeURIComponent(utfMatch[1]);
  const asciiMatch = disposition.match(/filename="?([^";]+)"?/i);
  return asciiMatch?.[1] ?? null;
}
