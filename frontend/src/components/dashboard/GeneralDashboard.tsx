"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/states/EmptyState";
import { DashboardGrid } from "./DashboardGrid";
import { getProfilesForUser, type DashboardCardItem } from "@/lib/dashboard";
import { getDashboardResumen } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { careerBrand } from "@/config/branding";
import type { DashboardResumen } from "@/lib/types";

const careers = [
  { code: "IC", label: "Ingeniería Civil" },
  { code: "ICE", label: "Ingeniería en Comunicaciones y Electrónica" },
  { code: "ICI", label: "Ingeniería en Computación e Informática" },
  { code: "II", label: "Ingeniería Industrial" },
];

export function GeneralDashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardResumen | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        setSummary(await getDashboardResumen());
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar el resumen.");
      } finally {
        setLoading(false);
      }
    }

    if (user) void load();
  }, [user]);

  if (!user) return null;

  const profiles = getProfilesForUser(user);
  const fallbackQuickAccesses = buildQuickAccesses(profiles.flatMap((profile) => profile.cards));
  const isDiscente = user.perfil_principal === "DISCENTE" || user.roles.includes("DISCENTE");
  const isDocente = user.perfil_principal === "DOCENTE" || user.roles.includes("DOCENTE");
  const isJefaturaCarrera =
    user.perfil_principal === "JEFE_CARRERA" ||
    user.roles.includes("JEFE_CARRERA") ||
    user.roles.includes("JEFATURA_CARRERA") ||
    user.roles.includes("JEFE_SUB_EJEC_CTR") ||
    user.cargos_vigentes.some((cargo) => ["JEFE_CARRERA", "JEFATURA_CARRERA", "JEFE_SUB_EJEC_CTR"].includes(cargo.cargo_codigo));
  const isJefaturaAcademica =
    user.perfil_principal === "JEFE_ACADEMICO" ||
    user.roles.includes("JEFE_ACADEMICO") ||
    user.roles.includes("JEFATURA_ACADEMICA") ||
    user.cargos_vigentes.some((cargo) => ["JEFE_ACADEMICO", "JEFATURA_ACADEMICA"].includes(cargo.cargo_codigo));
  const liveCards =
    summary?.cards.map((card) => ({
      title: card.title,
      description: card.description,
      href: ensurePeriodsRouteByTitle(
        card.title,
        isDiscente
        ? forceDiscenteDashboardRoute(card.title, card.href ?? undefined)
        : isDocente
          ? forceDocenteDashboardRoute(card.title, card.href ?? undefined)
          : isJefaturaCarrera
            ? forceJefaturaCarreraRoute(card.title, card.href ?? undefined)
            : isJefaturaAcademica
              ? forceJefaturaAcademicaRoute(card.title, card.href ?? undefined)
          : card.href ?? undefined,
      ),
      backend: false,
      value: card.value,
      tone: card.tone,
    })).filter((card) => isSafeFrontendRoute(card.href)) ?? [];

  const rawQuickAccesses = summary?.quick_accesses?.length
    ? summary.quick_accesses.map((item) => ({
        title: item.label,
        description: item.description || "Acceso disponible para tu perfil.",
        href: item.url,
        backend: item.backend,
      }))
    : fallbackQuickAccesses;
  const quickAccesses = rawQuickAccesses.map((item) => ({
    ...item,
    href: ensurePeriodsRouteByTitle(
      item.title,
      isDiscente
      ? forceDiscenteDashboardRoute(item.title, item.href)
      : isDocente
        ? forceDocenteDashboardRoute(item.title, item.href)
        : isJefaturaCarrera
          ? forceJefaturaCarreraRoute(item.title, item.href)
          : isJefaturaAcademica
            ? forceJefaturaAcademicaRoute(item.title, item.href)
        : item.href,
    ),
    backend: false,
  })).filter((item) => isSafeFrontendRoute(item.href));

  return (
    <AppShell showRightPanel>
      <div className="space-y-5">
        <InstitutionalHero />

        <section aria-label="Resumen institucional">
          <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h3 className="text-lg font-black text-[#101b18]">Resumen institucional</h3>
              <p className="text-sm text-[#5f6764]">Información actual según tu rol y ámbito autorizado.</p>
            </div>
          </div>
          {loading ? <EmptyState title="Cargando resumen" description="Estamos consultando la información autorizada." /> : null}
          {!loading && error ? <EmptyState title="Resumen no disponible" description={error} /> : null}
          {!loading && !error && liveCards.length > 0 ? <DashboardGrid cards={liveCards} /> : null}
          {!loading && !error && liveCards.length === 0 ? <EmptyState title="Sin datos de resumen" description="No hay registros para mostrar en este momento." /> : null}
        </section>

        <section id="accesos-rapidos">
          <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h3 className="text-lg font-black text-[#101b18]">Accesos rápidos</h3>
              <p className="text-sm text-[#5f6764]">Funciones disponibles según el rol o cargo activo.</p>
            </div>
          </div>
          {quickAccesses.length > 0 ? (
            <DashboardGrid cards={quickAccesses} />
          ) : (
            <EmptyState title="Sin accesos configurados" description="No hay accesos disponibles para este perfil en este momento." />
          )}
        </section>

        <CareerBanner />
      </div>
    </AppShell>
  );
}

function InstitutionalHero() {
  return (
    <section className="relative overflow-hidden rounded-[1.35rem] bg-[#073f34] p-5 text-white shadow-institutional sm:p-6 lg:p-7">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(255,255,255,0.10),transparent_18rem),linear-gradient(135deg,#073f34_0%,#075445_52%,#07372f_100%)]" />
      <div className="absolute right-7 top-6 hidden h-36 w-56 opacity-35 sm:block" aria-hidden="true">
        <DotPattern />
      </div>
      <div className="relative max-w-3xl">
        <p className="mb-3 text-xs font-black uppercase tracking-[0.3em] text-[#d4af37]">Panel institucional</p>
        <h2 className="text-3xl font-black tracking-tight sm:text-4xl">Panel institucional</h2>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-white/86 sm:text-base sm:leading-7">
          Centro de gestión académica. Accede a las herramientas clave para administrar y dar seguimiento institucional.
        </p>
        <a href="#accesos-rapidos" className="mt-4 inline-flex items-center gap-2 rounded-xl border border-[#d4af37] px-4 py-2 text-sm font-black text-[#f4d98b] transition hover:bg-white/10">
          Ver accesos
          <span aria-hidden="true">↗</span>
        </a>
      </div>
    </section>
  );
}

function CareerBanner() {
  return (
    <section aria-label="Carreras de la Escuela Militar de Ingeniería" className="overflow-hidden rounded-[1.2rem] bg-gradient-to-r from-[#073f34] via-[#0b4a3d] to-[#073f34] px-4 py-3 shadow-institutional">
      <div className="grid grid-cols-4 items-center justify-items-center gap-2 rounded-xl border border-white/12 bg-[#062f29]/36 px-2 py-2 sm:px-6">
        {careers.map((career) => {
          const brand = careerBrand[career.code];
          return (
            <div key={career.code} className="group relative flex h-16 w-16 items-center justify-center overflow-hidden rounded-full transition hover:-translate-y-0.5 sm:h-20 sm:w-20" title={brand.name}>
              <span className="absolute inset-0 rounded-full border border-[#d4af37]/24 bg-[radial-gradient(circle,rgba(212,175,55,0.14)_0%,rgba(212,175,55,0.06)_42%,transparent_72%)] blur-[2px]" aria-hidden="true" />
              <Image src={brand.logoApiPath} alt={brand.name} width={88} height={88} className="relative h-full w-full rounded-full object-cover drop-shadow-[0_12px_18px_rgba(0,0,0,0.36)]" />
            </div>
          );
        })}
      </div>
    </section>
  );
}

function buildQuickAccesses(cards: DashboardCardItem[]) {
  const seen = new Set<string>();
  const result: DashboardCardItem[] = [];

  for (const card of cards) {
    const key = `${card.title}-${card.href ?? ""}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(card);
    if (result.length === 8) break;
  }

  return result;
}

function DotPattern() {
  return (
    <svg className="h-full w-full text-[#d4af37]" viewBox="0 0 288 192" fill="none" aria-hidden="true">
      {Array.from({ length: 12 }).map((_, row) =>
        Array.from({ length: 18 }).map((__, col) => <circle key={`${row}-${col}`} cx={col * 16 + 4} cy={row * 16 + 4} r="1.3" fill="currentColor" opacity="0.9" />),
      )}
    </svg>
  );
}

function forceDiscenteDashboardRoute(title: string, currentHref?: string) {
  const normalized = normalizeTitle(title);
  if (normalized === "actas publicadas") return "/discente/actas";
  if (normalized === "conformidad pendiente") return "/discente/actas";
  if (normalized === "historial") return "/discente/historial-academico";
  if (normalized === "mis actas") return "/discente/actas";
  if (normalized === "mi historial") return "/discente/historial-academico";
  return currentHref;
}

function forceDocenteDashboardRoute(title: string, currentHref?: string) {
  const normalized = normalizeTitle(title);
  if (normalized === "asignaciones activas") return "/docente/asignaciones";
  if (normalized === "mis asignaciones") return "/docente/asignaciones";
  if (normalized === "actas en borrador") return "/docente/actas?estado=borrador";
  if (normalized === "actas publicadas") return "/docente/actas?estado=publicadas";
  if (normalized === "actas remitidas") return "/docente/actas?estado=remitidas";
  if (normalized === "actas docente") return "/docente/actas";
  if (normalized === "exportar mis actas") return undefined;
  return currentHref;
}

function forceJefaturaCarreraRoute(title: string, currentHref?: string) {
  const normalized = normalizeTitle(title);
  if (normalized === "actas por validar") return "/jefatura-carrera/actas";
  if (normalized === "actas remitidas") return "/jefatura-carrera/actas";
  if (normalized === "asignaciones docentes") return "/periodos/pendientes-asignacion-docente";
  if (normalized === "periodos activos") return "/periodos";
  if (normalized === "pendientes de asignacion docente") return "/periodos/pendientes-asignacion-docente";
  if (normalized === "grupos activos") return "/periodos";
  if (normalized === "trayectoria operativa de mi carrera") return "/trayectoria";
  if (normalized === "actas exportables") return "/reportes/actas";
  if (normalized === "catalogos de mi ambito") return undefined;
  if (normalized === "kardex oficial") return undefined;
  if (normalized === "historial de exportaciones") return undefined;
  if (normalized === "auditoria institucional") return undefined;
  return currentHref;
}

function forceJefaturaAcademicaRoute(title: string, currentHref?: string) {
  const normalized = normalizeTitle(title);
  if (normalized === "actas por formalizar") return "/jefatura-academica/actas";
  if (normalized === "actas formalizadas") return "/jefatura-academica/actas?estado=formalizadas";
  if (normalized === "formalizadas recientes") return "/jefatura-academica/actas?estado=formalizadas";
  if (normalized === "periodos activos") return "/periodos";
  if (normalized === "procesos de cierre") return "/periodos";
  if (normalized === "seguimiento institucional de trayectoria") return "/trayectoria";
  if (normalized === "reportes y exportaciones") return "/reportes";
  if (normalized === "desempeno academico") return "/reportes/desempeno";
  if (normalized === "reportes de trayectoria") return "/reportes/trayectoria";
  if (normalized === "kardex oficial") return "/reportes";
  return currentHref;
}

function normalizeTitle(value: string) {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .trim()
    .toLowerCase();
}

function isSafeFrontendRoute(href?: string) {
  if (!href) return true;
  const lower = href.toLowerCase();
  if (lower.startsWith("http://") || lower.startsWith("https://")) return false;
  if (lower.includes("localhost:8000") || lower.includes("localhost:8080") || lower.includes("127.0.0.1")) return false;
  if (lower.startsWith("/admin") || lower.startsWith("/health")) return false;
  return true;
}

function ensurePeriodsRouteByTitle(title: string, href?: string) {
  const normalized = normalizeTitle(title);
  if (normalized === "periodos activos" || normalized === "periodos" || normalized === "periodo activo" || normalized === "periodos operativos") {
    return "/periodos";
  }
  return href;
}
