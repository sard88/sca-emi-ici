"use client";

import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { useAuth } from "@/lib/auth";
import type { AdminCatalogResourceConfig, AuthenticatedUser } from "@/lib/types";
import { AdminCatalogCard } from "./AdminCatalogCard";

export function AdminCatalogIndex({
  title,
  description,
  heroTitle,
  heroDescription,
  resources,
  canRead,
  canWrite,
}: {
  title: string;
  description: string;
  heroTitle: string;
  heroDescription: string;
  resources: AdminCatalogResourceConfig[];
  canRead: (user: AuthenticatedUser) => boolean;
  canWrite: (user: AuthenticatedUser) => boolean;
}) {
  const { user } = useAuth();
  const writable = user ? canWrite(user) : false;

  return (
    <AppShell>
      {!user ? null : !canRead(user) ? (
        <ErrorMessage message="No tienes permiso para consultar este módulo desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader title={title} description={description} user={user} />
          <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-6 text-white shadow-institutional">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-[#d4af37]">Bloque 10C-4</p>
            <h2 className="mt-3 text-3xl font-black">{heroTitle}</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-white/84">{heroDescription}</p>
          </section>
          <section className="grid gap-4 xl:grid-cols-2">
            {resources.map((config) => <AdminCatalogCard key={config.slug} config={config} canWrite={writable} />)}
          </section>
        </div>
      )}
    </AppShell>
  );
}
