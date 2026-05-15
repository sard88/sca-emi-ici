"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import type { AuthenticatedUser } from "@/lib/types";
import { canAccessAdministracionPortal, canAccessAuditoria, canAccessCatalogosPortal, canAccessDiscenteActas, canAccessDiscenteCargaAcademica, canAccessDocenteOperacion, canAccessEstadisticaActas, canAccessJefaturaAcademicaActas, canAccessJefaturaCarreraActas, canAccessKardexPdf, canAccessMiHistorialAcademico, canAccessPeriodosOperativos, canAccessReportes, canAccessReportesDesempeno, canAccessReportesOperativos, canAccessReportesTrayectoria, canAccessTrayectoriaInstitucional, getProfilesForUser } from "@/lib/dashboard";
import { resolvePortalHref } from "@/lib/route-mapping";
import { ModuleIcon } from "@/components/ui/icons";

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
        canAccessEstadisticaActas(user) ? navItem("/estadistica/actas", "Seguimiento de actas", "ACTAS", pathname, "Actas") : null,
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
