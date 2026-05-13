import type {
  ActividadRecienteItem,
  AuthMe,
  AuthenticatedUser,
  BusquedaResponse,
  CalendarioMes,
  DashboardResumen,
  EventoCalendario,
  NotificacionesResponse,
  PerfilUsuario,
  PortalQuickAccess,
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

export function backendUrl(path: string) {
  if (path.startsWith("http")) return path;
  return apiUrl(path.startsWith("/") ? path : `/${path}`);
}
