import type { AuthMe, AuthenticatedUser } from "./types";

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

export async function getCsrfToken() {
  if (csrfToken) return csrfToken;
  const response = await fetch(apiUrl("/api/auth/csrf/"), {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });
  const data = await parseJson<{ csrfToken: string }>(response);
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
  const token = await getCsrfToken();
  const response = await fetch(apiUrl("/api/auth/logout/"), {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: JSON.stringify({}),
  });
  csrfToken = null;
  return parseJson<{ ok: true }>(response);
}

export async function getMe() {
  const response = await fetch(apiUrl("/api/auth/me/"), {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });
  return parseJson<AuthMe>(response);
}

export function backendUrl(path: string) {
  if (path.startsWith("http")) return path;
  return apiUrl(path.startsWith("/") ? path : `/${path}`);
}
