"use client";

import Image from "next/image";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/states/EmptyState";
import { DashboardGrid } from "./DashboardGrid";
import { getProfilesForUser, type DashboardCardItem } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";
import { careerBrand } from "@/config/branding";

const careers = [
  { code: "IC", label: "Ingeniería Civil" },
  { code: "ICE", label: "Ingeniería en Comunicaciones y Electrónica" },
  { code: "ICI", label: "Ingeniería en Computación e Informática" },
  { code: "II", label: "Ingeniería Industrial" },
];

export function GeneralDashboard() {
  const { user } = useAuth();

  if (!user) return null;

  const profiles = getProfilesForUser(user);
  const quickAccesses = buildQuickAccesses(profiles.flatMap((profile) => profile.cards));

  return (
    <AppShell>
      <div className="space-y-6">
        <InstitutionalHero />

        <section id="accesos-rapidos">
          <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h3 className="text-lg font-black text-[#101b18]">Accesos rápidos</h3>
              <p className="text-sm text-[#5f6764]">
                Funciones disponibles según el rol o cargo activo. El orden por uso quedará listo cuando exista actividad registrada.
              </p>
            </div>
          </div>
          {quickAccesses.length > 0 ? (
            <DashboardGrid cards={quickAccesses} />
          ) : (
            <EmptyState title="Sin accesos configurados" description="El backend no devolvió roles o cargos suficientes para construir el dashboard." />
          )}
        </section>

        <CareerBanner />
      </div>
    </AppShell>
  );
}

function InstitutionalHero() {
  return (
    <section className="relative overflow-hidden rounded-[1.75rem] bg-[#073f34] p-6 text-white shadow-institutional sm:p-8 lg:p-10">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(255,255,255,0.10),transparent_18rem),linear-gradient(135deg,#073f34_0%,#075445_52%,#07372f_100%)]" />
      <div className="absolute right-8 top-8 hidden h-48 w-72 opacity-45 sm:block" aria-hidden="true">
        <DotPattern />
      </div>
      <div className="relative max-w-3xl">
        <p className="text-xs font-black uppercase tracking-[0.34em] text-[#d4af37]">Panel institucional</p>
        <h2 className="mt-5 text-4xl font-black tracking-tight sm:text-5xl">Panel institucional</h2>
        <p className="mt-5 max-w-2xl text-base leading-7 text-white/86 sm:text-lg sm:leading-8">
          Centro de gestión académica. Accede a las herramientas clave para administrar y dar seguimiento institucional.
        </p>
        <a
          href="#accesos-rapidos"
          className="mt-7 inline-flex items-center gap-3 rounded-xl border border-[#d4af37] px-5 py-3 text-sm font-black text-[#f4d98b] transition hover:bg-white/10"
        >
          Ver documentación
          <span aria-hidden="true">↗</span>
        </a>
      </div>
    </section>
  );
}

function CareerBanner() {
  return (
    <section aria-label="Carreras de la Escuela Militar de Ingeniería" className="overflow-hidden rounded-[1.5rem] bg-gradient-to-r from-[#073f34] via-[#0b4a3d] to-[#073f34] px-5 py-4 shadow-institutional">
      <div className="grid grid-cols-4 items-center justify-items-center gap-3 rounded-[1.15rem] border border-white/12 bg-[#062f29]/36 px-3 py-2 sm:px-8">
        {careers.map((career) => {
          const brand = careerBrand[career.code];
          return (
            <div key={career.code} className="group relative flex h-20 w-20 items-center justify-center overflow-hidden rounded-full transition hover:-translate-y-0.5 sm:h-24 sm:w-24" title={brand.name}>
              <span className="absolute inset-0 rounded-full border border-[#d4af37]/24 bg-[radial-gradient(circle,rgba(212,175,55,0.14)_0%,rgba(212,175,55,0.06)_42%,transparent_72%)] blur-[2px]" aria-hidden="true" />
              <Image
                src={brand.logoApiPath}
                alt={brand.name}
                width={104}
                height={104}
                className="relative h-full w-full rounded-full object-cover drop-shadow-[0_12px_18px_rgba(0,0,0,0.36)]"
              />
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
        Array.from({ length: 18 }).map((__, col) => (
          <circle key={`${row}-${col}`} cx={col * 16 + 4} cy={row * 16 + 4} r="1.3" fill="currentColor" opacity="0.9" />
        )),
      )}
    </svg>
  );
}
