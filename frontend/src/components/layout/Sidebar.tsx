"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import type { AuthenticatedUser } from "@/lib/types";
import { canAccessAdministracionPortal, canAccessAuditoria, canAccessCatalogosPortal, canAccessDiscenteActas, canAccessDiscenteCargaAcademica, canAccessDocenteOperacion, canAccessEstadisticaActas, canAccessJefaturaAcademicaActas, canAccessJefaturaCarreraActas, canAccessKardexPdf, canAccessMiHistorialAcademico, canAccessPeriodosOperativos, canAccessReportes, canAccessReportesDesempeno, canAccessReportesOperativos, canAccessReportesTrayectoria, canAccessTrayectoriaInstitucional, getProfilesForUser } from "@/lib/dashboard";
import { resolvePortalHref } from "@/lib/route-mapping";

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
  const sections = buildNavigationSections(user, pathname);

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

      <nav className="mt-4 flex-1 space-y-5 overflow-y-auto rounded-[1.75rem] border border-white bg-white/72 p-4 shadow-sm">
        {sections.map((section) => (
          <SidebarSection key={section.title} title={section.title} items={section.items} />
        ))}
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
  const links = buildNavigationSections(user, pathname).flatMap((section) => section.items);

  return (
    <div className="lg:hidden">
      <div className="flex gap-2 overflow-x-auto px-4 pb-2 pt-3">
        {links.map((item) => <MobilePill key={`${item.href}-${item.label}`} href={item.href} active={item.active} label={item.shortLabel ?? item.label} backend={item.backend} />)}
      </div>
    </div>
  );
}

type NavigationItem = {
  href: string;
  label: string;
  shortLabel?: string;
  icon: string;
  active: boolean;
  backend?: boolean;
};

type NavigationSection = {
  title: string;
  items: NavigationItem[];
};

function buildNavigationSections(user: AuthenticatedUser, pathname: string): NavigationSection[] {
  const profileLinks = getProfilesForUser(user).map((profile) => {
    const href = routeByProfile[profile.key] ?? "/dashboard";
    return navItem(href, profile.title, profile.key, pathname, profile.title);
  });
  const sections: NavigationSection[] = [
    { title: "Inicio", items: [navItem("/dashboard", "Panel general", "PANEL", pathname, "Panel"), ...profileLinks] },
    {
      title: "Mi espacio",
      items: [
        hasRole(user, "DOCENTE") && canAccessDocenteOperacion(user) ? navItem("/docente/asignaciones", "Mis asignaciones y captura", "DOCENTE", pathname, "Asignaciones") : null,
        hasRole(user, "DOCENTE") && canAccessDocenteOperacion(user) ? navItem("/docente/actas", "Mis actas", "ACTAS", pathname) : null,
        canAccessDiscenteCargaAcademica(user) ? navItem("/discente/carga-academica", "Mi carga académica", "DISCENTE", pathname, "Carga") : null,
        canAccessDiscenteActas(user) ? navItem("/discente/actas", "Mis actas", "ACTAS", pathname) : null,
        canAccessMiHistorialAcademico(user) ? navItem("/trayectoria/mi-historial", "Mi historial académico", "TRAYECTORIA", pathname, "Historial") : null,
      ].filter(Boolean) as NavigationItem[],
    },
    {
      title: "Operación académica",
      items: [
        canAccessEstadisticaActas(user) ? navItem("/estadistica/actas", "Consulta de actas", "ACTAS", pathname, "Actas") : null,
        canAccessJefaturaCarreraActas(user) ? navItem("/jefatura-carrera/actas", "Actas por validar", "ACTAS", pathname, "Validar") : null,
        canAccessJefaturaAcademicaActas(user) ? navItem("/jefatura-academica/actas", "Actas por formalizar", "ACTAS", pathname, "Formalizar") : null,
        canAccessTrayectoriaInstitucional(user) ? navItem("/trayectoria", "Trayectoria", "TRAYECTORIA", pathname) : null,
        canAccessTrayectoriaInstitucional(user) ? navItem("/movimientos-academicos", "Movimientos académicos", "TRAYECTORIA", pathname, "Movimientos") : null,
        canAccessPeriodosOperativos(user) ? navItem("/periodos", "Periodos", "PERIODOS", pathname) : null,
        canAccessPeriodosOperativos(user) ? navItem("/periodos/pendientes-asignacion-docente", "Pendientes de asignación docente", "PERIODOS", pathname, "Pendientes") : null,
      ].filter(Boolean) as NavigationItem[],
    },
    {
      title: "Gestión institucional",
      items: [
        canAccessAdministracionPortal(user) ? navItem("/administracion", "Administración", "ADMINISTRACION", pathname, "Admin") : null,
        canAccessCatalogosPortal(user) ? navItem("/catalogos", "Catálogos académicos", "CATALOGOS", pathname, "Catálogos") : null,
      ].filter(Boolean) as NavigationItem[],
    },
    {
      title: "Reportes y auditoría",
      items: [
        canAccessReportes(user) ? navItem("/reportes", "Reportes", "REPORTES", pathname) : null,
        canAccessKardexPdf(user) ? navItem("/reportes/kardex", "Kárdex oficial", "REPORTES", pathname, "Kárdex") : null,
        canAccessReportesOperativos(user) ? navItem("/reportes/operativos", "Reportes operativos", "REPORTES", pathname, "Operativos") : null,
        canAccessReportesDesempeno(user) ? navItem("/reportes/desempeno", "Desempeño académico", "REPORTES", pathname, "Desempeño") : null,
        canAccessReportesTrayectoria(user) ? navItem("/reportes/trayectoria", "Reportes de trayectoria", "REPORTES", pathname, "Reportes trayectoria") : null,
        canAccessReportes(user) ? navItem("/reportes/exportaciones", "Historial de exportaciones", "REPORTES", pathname, "Exportaciones") : null,
        canAccessAuditoria(user) ? navItem("/reportes/auditoria", "Auditoría institucional", "SEGURIDAD", pathname, "Auditoría") : null,
      ].filter(Boolean) as NavigationItem[],
    },
    {
      title: "Soporte técnico",
      items: isAdmin(user)
        ? [
            navItem("/admin/", "Django Admin", "ADMINISTRACION", pathname, "Django Admin", true),
            navItem("/health/", "Estado técnico", "SEGURIDAD", pathname, "Health", true),
          ]
        : [],
    },
  ];
  return sections.filter((section) => section.items.length > 0);
}

function navItem(href: string, label: string, icon: string, pathname: string, shortLabel?: string, backend = false): NavigationItem {
  const active = href === "/dashboard" ? pathname === href : pathname === href || pathname.startsWith(`${href}/`);
  return { href, label, shortLabel, icon, active, backend };
}

function isAdmin(user: AuthenticatedUser) {
  return user.perfil_principal === "ADMIN" || user.roles.includes("ADMIN") || user.roles.includes("ADMIN_SISTEMA");
}

function hasRole(user: AuthenticatedUser, role: string) {
  return user.perfil_principal === role || user.roles.includes(role) || user.cargos_vigentes.some((cargo) => cargo.cargo_codigo === role);
}

function SidebarSection({ title, items }: NavigationSection) {
  return (
    <section>
      <p className="px-2 text-xs font-black uppercase tracking-[0.22em] text-[#b46c13]">{title}</p>
      <div className="mt-3 space-y-1">
        {items.map((item) => <SidebarLink key={`${item.href}-${item.label}`} {...item} />)}
      </div>
    </section>
  );
}

function BrandChip({ label }: { label: string }) {
  return (
    <span className="flex h-12 w-12 items-center justify-center rounded-full border border-[#dfc79f] bg-[#fffaf1] text-xs font-black text-[#7a123d] shadow-sm">
      {label}
    </span>
  );
}

function MobilePill({ href, active, label, backend = false }: { href: string; active: boolean; label: string; backend?: boolean }) {
  const resolved = resolvePortalHref(href, backend);
  if (!resolved) return null;
  const className = clsx(
    "whitespace-nowrap rounded-full border px-4 py-2 text-xs font-black shadow-sm",
    active ? "border-[#7a123d] bg-[#7a123d] text-white" : "border-[#eadbc4] bg-white/80 text-[#1f2f2a]",
  );
  if (resolved.backend) {
    return (
      <a href={resolved.href} target="_blank" rel="noreferrer" className={className}>
        {label}
      </a>
    );
  }
  return (
    <Link href={resolved.href} className={className}>
      {label}
    </Link>
  );
}

function SidebarLink({ href, active, icon, label, backend = false }: NavigationItem) {
  const resolved = resolvePortalHref(href, backend);
  const className = clsx(
    "group flex items-center justify-between gap-3 rounded-2xl px-3 py-3 text-sm font-bold transition",
    active ? "bg-[#f6ead7] text-[#7a123d]" : "text-[#1f2f2a] hover:bg-[#f7efe2]",
  );
  const content = (
    <>
      <span className="flex items-center gap-3">
        <ModuleIcon name={icon} className="h-5 w-5 text-[#46534e] group-hover:text-[#7a123d]" />
        {label}
      </span>
      <span className="text-lg leading-none text-[#7b6b58]">›</span>
    </>
  );
  if (!resolved) return null;
  if (resolved.backend) {
    return <a href={resolved.href} target="_blank" rel="noreferrer" className={className}>{content}</a>;
  }
  return (
    <Link href={resolved.href} className={className}>
      {content}
    </Link>
  );
}

export function ModuleIcon({ name, className }: { name: string; className?: string }) {
  const normalized = name.toUpperCase();

  if (normalized.includes("ESTADISTICA")) return <ChartIcon className={className} />;
  if (normalized.includes("DOCENTE")) return <UsersIcon className={className} />;
  if (normalized.includes("DISCENTE")) return <IdIcon className={className} />;
  if (normalized.includes("TRAYECTORIA") || normalized.includes("PERIODO")) return <AcademicIcon className={className} />;
  if (normalized.includes("JEFE") || normalized.includes("JEFATURA")) return <AcademicIcon className={className} />;
  if (normalized.includes("REPORTE") || normalized.includes("ACTA")) return <DocumentIcon className={className} />;
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
