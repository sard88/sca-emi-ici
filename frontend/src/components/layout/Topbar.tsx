"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import type { AuthenticatedUser } from "@/lib/types";

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
          <div className="relative min-w-0 sm:w-[340px]">
            <SearchIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-[#6a716e]" />
            <input
              aria-label="Buscar en el sistema"
              placeholder="Buscar en el sistema..."
              disabled
              className="h-12 w-full rounded-2xl border border-[#e4d6c2] bg-white/90 pl-12 pr-14 text-sm font-medium text-[#5f6764] shadow-sm outline-none placeholder:text-[#7b837f] disabled:cursor-not-allowed"
            />
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 rounded-lg bg-[#f1e7d9] px-2 py-1 text-xs font-black text-[#6f6557]">Ctrl K</span>
          </div>

          <button
            type="button"
            aria-label="Notificaciones"
            className="relative flex h-12 w-12 items-center justify-center rounded-2xl border border-[#e4d6c2] bg-white/86 text-[#152b25] shadow-sm"
            title="Notificaciones pendientes de configurar"
          >
            <BellIcon className="h-6 w-6" />
            <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-[#7a123d] px-1 text-[10px] font-black text-white">0</span>
          </button>

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
                <button type="button" disabled className="flex w-full cursor-not-allowed items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm font-bold text-[#8b8276]">
                  Mi perfil
                  <span className="rounded-full bg-[#f5ecde] px-2 py-1 text-[10px] font-black uppercase text-[#9f6a22]">Próximo</span>
                </button>
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
