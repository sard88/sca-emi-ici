"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  buscarPortal,
  getNotificaciones,
  marcarNotificacionLeida,
  marcarTodasNotificacionesLeidas,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { resolvePortalHref } from "@/lib/route-mapping";
import type { AuthenticatedUser, BusquedaGrupo, Notificacion } from "@/lib/types";

export function Topbar({ user }: { user: AuthenticatedUser }) {
  const { logout } = useAuth();
  const router = useRouter();
  const perfil = user.perfil_principal ?? user.roles[0] ?? "SIN ROL";
  const nombre = user.nombre_visible || user.username;
  const saludo = perfil === "ADMIN" ? "Administrador" : nombre;

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-30 border-b border-[#eadfce] bg-[#fffaf1]/86 px-4 py-4 backdrop-blur-xl sm:px-6 xl:pl-8 xl:pr-4 2xl:pr-6">
      <div className="flex w-full flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-[#101b18]">
            ¡Bienvenido, <span className="text-[#7a123d]">{saludo}</span>!
          </h2>
          <p className="mt-1 text-sm font-medium text-[#58615d]">Panel de control institucional</p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
          <PortalSearch />
          <NotificationBell />

          <details className="group relative">
            <summary className="flex h-14 cursor-pointer list-none items-center gap-3 rounded-2xl border border-[#e4d6c2] bg-white/90 px-3 pr-4 shadow-sm transition hover:border-[#d3b178] [&::-webkit-details-marker]:hidden">
              <div className="flex h-11 w-11 items-center justify-center overflow-hidden rounded-full border border-[#eadbc4] bg-[#f6efe5]">
                <Image src="/brand/institutions/emi-escudo.png" alt="Perfil institucional" width={34} height={42} className="h-8 w-auto object-contain opacity-80" />
              </div>
              <div className="min-w-0 text-left">
                <p className="max-w-36 truncate text-sm font-black text-[#152b25]">{nombre}</p>
                <p className="text-xs font-semibold text-[#58615d]">Rol: {perfil}</p>
              </div>
              <ChevronIcon className="h-4 w-4 text-[#152b25] transition group-open:rotate-180" />
            </summary>

            <div className="absolute right-0 z-40 mt-2 w-64 overflow-hidden rounded-2xl border border-[#eadfce] bg-white shadow-2xl shadow-[#6d5b43]/20">
              <div className="border-b border-[#f0e2cf] px-4 py-3">
                <p className="truncate text-sm font-black text-[#152b25]">{user.nombre_institucional || nombre}</p>
                <p className="mt-1 text-xs font-semibold text-[#58615d]">{user.correo || user.email || user.username}</p>
              </div>
              <div className="p-2">
                <Link href="/perfil" className="block rounded-xl px-3 py-2.5 text-sm font-bold text-[#152b25] hover:bg-[#f7efe2]">
                  Mi perfil
                </Link>
                <Link href="/dashboard" className="block rounded-xl px-3 py-2.5 text-sm font-bold text-[#152b25] hover:bg-[#f7efe2]">
                  Panel general
                </Link>
                <button type="button" onClick={handleLogout} className="block w-full rounded-xl px-3 py-2.5 text-left text-sm font-black text-[#7a123d] hover:bg-[#f7efe2]">
                  Cerrar sesión
                </button>
              </div>
            </div>
          </details>
        </div>
      </div>
    </header>
  );
}

function PortalSearch() {
  const [query, setQuery] = useState("");
  const [groups, setGroups] = useState<BusquedaGrupo[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const value = query.trim();
    if (value.length < 2) {
      setGroups([]);
      setError(null);
      setLoading(false);
      return;
    }

    const handle = window.setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await buscarPortal(value);
        setGroups(response.groups);
      } catch (err) {
        setGroups([]);
        setError(err instanceof Error ? err.message : "No fue posible buscar.");
      } finally {
        setLoading(false);
      }
    }, 280);

    return () => window.clearTimeout(handle);
  }, [query]);

  return (
    <div className="relative min-w-0 sm:w-[340px]">
      <SearchIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-[#6a716e]" />
      <input
        aria-label="Buscar en el sistema"
        placeholder="Buscar en el sistema..."
        value={query}
        onChange={(event) => {
          setQuery(event.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => window.setTimeout(() => setOpen(false), 180)}
        className="h-12 w-full rounded-2xl border border-[#e4d6c2] bg-white/90 pl-12 pr-14 text-sm font-medium text-[#293630] shadow-sm outline-none placeholder:text-[#7b837f] focus:border-[#bc955c]"
      />
      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 rounded-lg bg-[#f1e7d9] px-2 py-1 text-xs font-black text-[#6f6557]">Ctrl K</span>

      {open && query.trim().length > 0 ? (
        <div className="absolute right-0 z-50 mt-2 max-h-[28rem] w-full overflow-y-auto rounded-2xl border border-[#eadfce] bg-white p-2 shadow-2xl shadow-[#6d5b43]/20">
          {query.trim().length < 2 ? <SearchState text="Escribe al menos 2 caracteres." /> : null}
          {loading ? <SearchState text="Buscando información autorizada..." /> : null}
          {error ? <SearchState text={error} /> : null}
          {!loading && !error && query.trim().length >= 2 && groups.length === 0 ? <SearchState text="No hay resultados para tu perfil." /> : null}
          {!loading && !error && groups.map((group) => (
            <div key={group.label} className="py-1">
              <p className="px-3 py-1 text-[10px] font-black uppercase tracking-[0.18em] text-[#9f6a22]">{group.label}</p>
              {group.items.map((item) => {
                const resolved = resolvePortalHref(item.url, item.backend);
                if (!resolved) return null;
                return (
                  <a key={`${group.label}-${item.type}-${item.title}-${item.url}`} href={resolved.href} target={resolved.backend ? "_blank" : undefined} rel={resolved.backend ? "noreferrer" : undefined} className="block rounded-xl px-3 py-2.5 hover:bg-[#f7efe2]">
                    <p className="text-sm font-black text-[#152b25]">{item.title}</p>
                    <p className="mt-0.5 text-xs font-medium text-[#66716c]">{item.subtitle}</p>
                  </a>
                );
              })}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function NotificationBell() {
  const [items, setItems] = useState<Notificacion[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setLoading(true);
    try {
      const response = await getNotificaciones();
      setItems(response.items);
      setUnreadCount(response.unread_count);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function markRead(id: number) {
    await marcarNotificacionLeida(id);
    await refresh();
  }

  async function markAllRead() {
    await marcarTodasNotificacionesLeidas();
    await refresh();
  }

  return (
    <details className="group relative">
      <summary className="relative flex h-12 w-12 cursor-pointer list-none items-center justify-center rounded-2xl border border-[#e4d6c2] bg-white/86 text-[#152b25] shadow-sm [&::-webkit-details-marker]:hidden">
        <span className="sr-only">Notificaciones</span>
        <BellIcon className="h-6 w-6" />
        <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-[#7a123d] px-1 text-[10px] font-black text-white">{unreadCount}</span>
      </summary>
      <div className="absolute right-0 z-50 mt-2 w-80 overflow-hidden rounded-2xl border border-[#eadfce] bg-white shadow-2xl shadow-[#6d5b43]/20">
        <div className="flex items-center justify-between border-b border-[#f0e2cf] px-4 py-3">
          <div>
            <p className="text-sm font-black text-[#152b25]">Notificaciones</p>
            <p className="text-xs font-semibold text-[#66716c]">{unreadCount} sin leer</p>
          </div>
          <button type="button" onClick={markAllRead} disabled={unreadCount === 0} className="rounded-lg bg-[#f5ecde] px-2 py-1 text-[11px] font-black text-[#7a123d] disabled:opacity-50">
            Leer todas
          </button>
        </div>
        <div className="max-h-96 overflow-y-auto p-2">
          {loading ? <SearchState text="Cargando notificaciones..." /> : null}
          {!loading && items.length === 0 ? <SearchState text="No hay notificaciones registradas." /> : null}
          {!loading && items.map((item) => (
            <div key={item.id} className="rounded-xl px-3 py-3 hover:bg-[#f7efe2]">
              <div className="flex items-start gap-3">
                <span className={`mt-1 h-2.5 w-2.5 flex-none rounded-full ${item.leida ? "bg-[#c8bca9]" : "bg-[#7a123d]"}`} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-black text-[#152b25]">{item.titulo}</p>
                  <p className="mt-1 text-xs leading-5 text-[#66716c]">{item.mensaje}</p>
                  <p className="mt-1 text-[11px] font-bold uppercase tracking-[0.12em] text-[#9f6a22]">{formatDateTime(item.creada_en)}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <NotificationDestinationLink url={item.url_destino} />
                    {!item.leida ? (
                      <button type="button" onClick={() => markRead(item.id)} className="text-xs font-black text-[#7a123d]">
                        Marcar leída
                      </button>
                    ) : null}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </details>
  );
}

function NotificationDestinationLink({ url }: { url?: string | null }) {
  const resolved = resolvePortalHref(url, true);
  if (!resolved) return null;
  return (
    <a href={resolved.href} target={resolved.backend ? "_blank" : undefined} rel={resolved.backend ? "noreferrer" : undefined} className="text-xs font-black text-[#0b4a3d]">
      Abrir
    </a>
  );
}

function SearchState({ text }: { text: string }) {
  return <p className="px-3 py-3 text-sm font-semibold text-[#66716c]">{text}</p>;
}

function formatDateTime(value: string | null) {
  if (!value) return "Sin fecha";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="m20 20-4.4-4.4M11 18a7 7 0 1 1 0-14 7 7 0 0 1 0 14Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function BellIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M18 9a6 6 0 1 0-12 0c0 7-2.5 7.5-2.5 7.5h17S18 16 18 9Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M9.5 19a2.5 2.5 0 0 0 5 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="m6 9 6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
