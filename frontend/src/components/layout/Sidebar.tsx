"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import type { AuthenticatedUser } from "@/lib/types";
import { canAccessKardexPdf, canAccessReportes, canAccessReportesOperativos, getProfilesForUser } from "@/lib/dashboard";

const routeByProfile: Record<string, string> = {
  ADMIN: "/admin-soporte",
  ESTADISTICA: "/estadistica",
  DOCENTE: "/docente",
  DISCENTE: "/discente",
  JEFE_CARRERA: "/jefatura-carrera",
  JEFE_ACADEMICO: "/jefatura-academica",
  JEFE_PEDAGOGICA: "/jefatura-pedagogica",
};

export function Sidebar({ user }: { user: AuthenticatedUser }) {
  const pathname = usePathname();
  const profiles = getProfilesForUser(user);
  const showReportes = canAccessReportes(user);
  const showKardex = canAccessKardexPdf(user);
  const showReportesOperativos = canAccessReportesOperativos(user);

  return (
    <aside className="hidden min-h-screen w-[292px] shrink-0 border-r border-[#eadfce] bg-[#fffaf1]/92 p-4 shadow-[18px_0_44px_rgba(87,70,45,0.08)] backdrop-blur-xl lg:sticky lg:top-0 lg:flex lg:flex-col">
      <div className="rounded-[1.75rem] border border-white bg-white/86 p-4 shadow-institutional">
        <div className="flex items-center gap-3">
          <Image
            src="/brand/institutions/emi-escudo.png"
            alt="Escudo de la Escuela Militar de Ingeniería"
            width={72}
            height={88}
            className="h-20 w-auto object-contain"
            priority
          />
          <div>
            <p className="text-xs font-black uppercase tracking-[0.22em] text-[#a06116]">Escuela Militar</p>
            <p className="mt-1 text-xs font-black uppercase tracking-[0.22em] text-[#a06116]">de Ingeniería</p>
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <BrandChip label="EMI" />
          <BrandChip label="UDEFA" />
        </div>

        <h1 className="mt-6 text-xl font-black leading-tight text-[#10372e]">
          Sistema de Control Académico EMI
        </h1>
      </div>

      <nav className="mt-4 flex-1 space-y-6 rounded-[1.75rem] border border-white bg-white/72 p-4 shadow-sm">
        <Link
          href="/dashboard"
          className={clsx(
            "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-black transition",
            pathname === "/dashboard"
              ? "bg-gradient-to-r from-[#6b1238] to-[#8c1244] text-white shadow-lg shadow-[#7a123d]/20"
              : "text-[#152b25] hover:bg-[#f7efe2]",
          )}
        >
          <ModuleIcon name="PANEL" className="h-5 w-5" />
          Panel general
        </Link>

        <div>
          <p className="px-2 text-xs font-black uppercase tracking-[0.22em] text-[#b46c13]">Módulos</p>
          <div className="mt-4 space-y-1">
            {profiles.map((profile) => {
              const href = routeByProfile[profile.key] ?? "/dashboard";
              return (
                <Link
                  key={profile.key}
                  href={href}
                  className={clsx(
                    "group flex items-center justify-between gap-3 rounded-2xl px-3 py-3 text-sm font-bold transition",
                    pathname === href ? "bg-[#f6ead7] text-[#7a123d]" : "text-[#1f2f2a] hover:bg-[#f7efe2]",
                  )}
                >
                  <span className="flex items-center gap-3">
                    <ModuleIcon name={profile.key} className="h-5 w-5 text-[#46534e] group-hover:text-[#7a123d]" />
                    {profile.title}
                  </span>
                  <span className="text-lg leading-none text-[#7b6b58]">›</span>
                </Link>
              );
            })}
            {showReportes ? (
              <>
                <Link
                  href="/reportes"
                  className={clsx(
                    "group flex items-center justify-between gap-3 rounded-2xl px-3 py-3 text-sm font-bold transition",
                    pathname.startsWith("/reportes")
                      ? "bg-[#f6ead7] text-[#7a123d]"
                      : "text-[#1f2f2a] hover:bg-[#f7efe2]",
                  )}
                >
                  <span className="flex items-center gap-3">
                    <ModuleIcon name="REPORTES" className="h-5 w-5 text-[#46534e] group-hover:text-[#7a123d]" />
                    Reportes y exportaciones
                  </span>
                  <span className="text-lg leading-none text-[#7b6b58]">›</span>
                </Link>
                {showReportesOperativos ? (
                  <Link
                    href="/reportes/operativos"
                    className={clsx(
                      "ml-7 flex items-center justify-between rounded-2xl px-3 py-2 text-xs font-black transition",
                      pathname.startsWith("/reportes/operativos") ? "bg-[#fff4df] text-[#7a4b0d]" : "text-[#46534e] hover:bg-[#f7efe2]",
                    )}
                  >
                    Reportes operativos
                    <span className="text-base leading-none text-[#7b6b58]">›</span>
                  </Link>
                ) : null}
                {showKardex ? (
                  <Link
                    href="/reportes/kardex"
                    className={clsx(
                      "ml-7 flex items-center justify-between rounded-2xl px-3 py-2 text-xs font-black transition",
                      pathname === "/reportes/kardex" ? "bg-[#eef7f2] text-[#0b4a3d]" : "text-[#46534e] hover:bg-[#f7efe2]",
                    )}
                  >
                    Kárdex oficial
                    <span className="text-base leading-none text-[#7b6b58]">›</span>
                  </Link>
                ) : null}
              </>
            ) : null}
          </div>
        </div>
      </nav>

      <div className="mt-4 rounded-[1.5rem] border border-[#eadbc4] bg-white/76 p-5 shadow-sm">
        <div className="flex items-start gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl border border-[#dfc79f] text-[#b46c13]">
            <ModuleIcon name="SEGURIDAD" className="h-7 w-7" />
          </span>
          <div>
            <p className="text-sm font-black text-[#152b25]">Seguridad y confianza</p>
            <p className="mt-1 text-xs leading-5 text-[#5f6764]">Protegemos la información académica institucional.</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export function MobileModuleNav({ user }: { user: AuthenticatedUser }) {
  const pathname = usePathname();
  const profiles = getProfilesForUser(user);
  const showReportes = canAccessReportes(user);
  const showKardex = canAccessKardexPdf(user);
  const showReportesOperativos = canAccessReportesOperativos(user);

  return (
    <div className="lg:hidden">
      <div className="flex gap-2 overflow-x-auto px-4 pb-2 pt-3">
        <MobilePill href="/dashboard" active={pathname === "/dashboard"} label="Panel" />
        {profiles.map((profile) => (
          <MobilePill
            key={profile.key}
            href={routeByProfile[profile.key] ?? "/dashboard"}
            active={pathname === (routeByProfile[profile.key] ?? "/dashboard")}
            label={profile.title}
          />
        ))}
        {showReportes ? <MobilePill href="/reportes" active={pathname.startsWith("/reportes")} label="Reportes" /> : null}
        {showReportesOperativos ? <MobilePill href="/reportes/operativos" active={pathname.startsWith("/reportes/operativos")} label="Operativos" /> : null}
        {showKardex ? <MobilePill href="/reportes/kardex" active={pathname === "/reportes/kardex"} label="Kárdex" /> : null}
      </div>
    </div>
  );
}

function BrandChip({ label }: { label: string }) {
  return (
    <span className="flex h-12 w-12 items-center justify-center rounded-full border border-[#dfc79f] bg-[#fffaf1] text-xs font-black text-[#7a123d] shadow-sm">
      {label}
    </span>
  );
}

function MobilePill({ href, active, label }: { href: string; active: boolean; label: string }) {
  return (
    <Link
      href={href}
      className={clsx(
        "whitespace-nowrap rounded-full border px-4 py-2 text-xs font-black shadow-sm",
        active ? "border-[#7a123d] bg-[#7a123d] text-white" : "border-[#eadbc4] bg-white/80 text-[#1f2f2a]",
      )}
    >
      {label}
    </Link>
  );
}

export function ModuleIcon({ name, className }: { name: string; className?: string }) {
  const normalized = name.toUpperCase();

  if (normalized.includes("ESTADISTICA")) return <ChartIcon className={className} />;
  if (normalized.includes("DOCENTE")) return <UsersIcon className={className} />;
  if (normalized.includes("DISCENTE")) return <IdIcon className={className} />;
  if (normalized.includes("JEFE") || normalized.includes("JEFATURA")) return <AcademicIcon className={className} />;
  if (normalized.includes("REPORTE")) return <DocumentIcon className={className} />;
  if (normalized.includes("SEGURIDAD")) return <ShieldIcon className={className} />;
  if (normalized.includes("PANEL")) return <HomeIcon className={className} />;
  return <SettingsIcon className={className} />;
}

function HomeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M3.5 11.2 12 4l8.5 7.2V20h-5.2v-5.4H8.7V20H3.5v-8.8Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    </svg>
  );
}

function SettingsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z" stroke="currentColor" strokeWidth="1.8" />
      <path d="M19 13.6v-3.2l-2.1-.7a5.6 5.6 0 0 0-.7-1.6l1-2-2.3-2.3-2 .9a6 6 0 0 0-1.8-.4L10.4 2H7.2l-.7 2.2a5.6 5.6 0 0 0-1.6.7l-2-.9L.6 6.3l.9 2a6 6 0 0 0-.4 1.8L-1 10.8V14l2.1.7c.2.6.4 1.1.7 1.6l-1 2 2.3 2.3 2-.9c.5.3 1.1.5 1.8.7l.7 2.1h3.2l.7-2.1c.6-.2 1.1-.4 1.6-.7l2 .9 2.3-2.3-.9-2c.3-.5.5-1.1.7-1.8l1.8-.9Z" transform="translate(2.5 .3)" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
}

function ChartIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M4 19V5M4 19h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M8 16v-5M12 16V8M16 16v-3M20 16V6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function UsersIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM3.5 20a5.5 5.5 0 0 1 11 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M16 11.5a3 3 0 1 0-.8-5.9M16.5 14.5A5 5 0 0 1 21 20" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function IdIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 4h14v16H5V4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M9 9h6M9 13h6M9 17h4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function AcademicIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="m3 8.5 9-4 9 4-9 4-9-4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M7 10.5v4.2c0 1.1 2.2 2.8 5 2.8s5-1.7 5-2.8v-4.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 3.5 19 6v5.5c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9V6l7-2.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="m8.8 12.2 2.1 2.1 4.4-4.9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function DocumentIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M7 3.5h6.5L18 8v12.5H7V3.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M13.5 3.8V8H18M9.8 12h5.4M9.8 15h5.4M9.8 18h3.4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
