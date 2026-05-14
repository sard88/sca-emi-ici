import { backendUrl } from "./api";

const legacyRouteMap: Record<string, string | null> = {
  "/trayectoria/kardex/": "/reportes/kardex",
  "/admin/catalogos/": "/catalogos",
  "/admin/usuarios/usuario/": "/administracion/usuarios",
  "/admin/usuarios/asignacioncargo/": "/administracion/cargos",
  "/admin/usuarios/unidadorganizacional/": "/administracion/unidades",
  "/validacion/discente/carga/": "/trayectoria/mi-historial",
  "/evaluacion/actas/planeacion-evaluacion/consulta/": "/reportes/operativos",
};

function normalizedPath(path: string) {
  if (!path || path.startsWith("http")) return path;
  const value = path.startsWith("/") ? path : `/${path}`;
  return value.endsWith("/") ? value : `${value}/`;
}

export function mapLegacyPortalRoute(path?: string | null) {
  if (!path) return null;
  if (path.startsWith("http")) return path;
  const normalized = normalizedPath(path);
  if (Object.prototype.hasOwnProperty.call(legacyRouteMap, normalized)) {
    return legacyRouteMap[normalized];
  }
  return path;
}

export function resolvePortalHref(path?: string | null, backend = false) {
  const mapped = mapLegacyPortalRoute(path);
  if (!mapped) return null;
  if (mapped.startsWith("http")) return { href: mapped, backend: true };
  if (mapped !== path) return { href: mapped, backend: false };
  return { href: backend ? backendUrl(mapped) : mapped, backend };
}
