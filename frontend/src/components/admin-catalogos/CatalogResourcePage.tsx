"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuth } from "@/lib/auth";
import { createResource, getResource, listResource, updateResource } from "@/lib/api";
import type { AdminCatalogResourceConfig, AuthenticatedUser, ResourceItem } from "@/lib/types";
import { CatalogResourceDetail } from "./CatalogResourceDetail";
import { CatalogResourceFilters } from "./CatalogResourceFilters";
import { CatalogResourceForm } from "./CatalogResourceForm";
import { CatalogResourceTable } from "./CatalogResourceTable";
import { CatalogEmptyState, CatalogErrorState, CatalogLoadingState } from "./CatalogStates";
import { EvaluationComponentsPanel } from "./EvaluationComponentsPanel";

export function CatalogResourcePage({
  config,
  resourceId,
  canRead,
  canWrite,
  backHref,
}: {
  config: AdminCatalogResourceConfig;
  resourceId?: string;
  canRead: (user: AuthenticatedUser) => boolean;
  canWrite: (user: AuthenticatedUser) => boolean;
  backHref: string;
}) {
  const { user } = useAuth();
  const [items, setItems] = useState<ResourceItem[]>([]);
  const [item, setItem] = useState<ResourceItem | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [appliedFilters, setAppliedFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);

  const writable = user ? canWrite(user) && !config.soloLectura : false;
  const canCreate = writable && config.permiteCrear && !resourceId;
  const canEdit = writable && config.permiteEditar;

  useEffect(() => {
    async function load() {
      if (!user || !canRead(user)) return;
      setLoading(true);
      setError(null);
      try {
        if (resourceId) {
          const response = await getResource(config.endpoint, resourceId);
          setItem(response.item);
        } else {
          const response = await listResource(config.endpoint, { ...appliedFilters, page_size: "50" });
          setItems(response.items);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar la información.");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [user, resourceId, config, appliedFilters, refreshToken, canRead]);

  function refresh() {
    setRefreshToken((value) => value + 1);
  }

  return (
    <AppShell>
      {!user ? null : !canRead(user) ? (
        <CatalogErrorState message="No tienes permiso para consultar este módulo desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader title={config.titulo} description={config.descripcion} user={user} />

          <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-5 text-white shadow-institutional">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.28em] text-[#d4af37]">{config.categoria === "administracion" ? "Administración institucional" : "Catálogos académicos"}</p>
                <h2 className="mt-3 text-2xl font-black">{resourceId ? "Detalle del registro" : "Listado operativo"}</h2>
                <p className="mt-3 max-w-3xl text-sm leading-6 text-white/82">{config.ayuda ?? "El portal muestra y envía datos; Django conserva las reglas de validación reales."}</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link href={resourceId ? config.ruta : backHref} className="rounded-xl border border-white/30 px-5 py-3 text-sm font-black text-white transition hover:bg-white/10">
                  {resourceId ? "Volver al listado" : "Volver al índice"}
                </Link>
                {canCreate ? (
                  <button type="button" onClick={() => setShowCreate((value) => !value)} className="rounded-xl bg-[#d4af37] px-5 py-3 text-sm font-black text-[#10372e] shadow-sm transition hover:bg-[#c49b20]">
                    {showCreate ? "Ocultar formulario" : "Crear registro"}
                  </button>
                ) : null}
              </div>
            </div>
          </section>

          {!resourceId ? (
            <CatalogResourceFilters
              config={config}
              values={filters}
              onChange={(key, value) => setFilters((current) => ({ ...current, [key]: value }))}
              onSubmit={() => setAppliedFilters(cleanFilters(filters))}
              onClear={() => {
                setFilters({});
                setAppliedFilters({});
              }}
            />
          ) : null}

          {showCreate ? (
            <CatalogResourceForm
              config={config}
              canWrite={writable}
              submitLabel="Crear registro"
              onCancel={() => setShowCreate(false)}
              onSubmit={async (payload) => {
                await createResource(config.endpoint, payload);
                setShowCreate(false);
                refresh();
              }}
            />
          ) : null}

          {loading ? <CatalogLoadingState /> : null}
          {error ? <CatalogErrorState message={error} /> : null}

          {!loading && !error && resourceId && item ? (
            <>
              <CatalogResourceDetail item={item} />
              {config.formFields.length > 0 ? (
                <CatalogResourceForm
                  config={config}
                  item={item}
                  canWrite={canEdit}
                  submitLabel="Guardar cambios"
                  onSubmit={async (payload) => {
                    const response = await updateResource(config.endpoint, resourceId, payload);
                    setItem(response.item);
                    refresh();
                  }}
                />
              ) : null}
              {config.slug === "esquemas-evaluacion" ? <EvaluationComponentsPanel esquemaId={Number(resourceId)} canWrite={writable} /> : null}
            </>
          ) : null}

          {!loading && !error && !resourceId && items.length === 0 ? <CatalogEmptyState /> : null}
          {!loading && !error && !resourceId && items.length > 0 ? (
            <CatalogResourceTable config={config} items={items} canWrite={writable} onChanged={refresh} />
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function cleanFilters(values: Record<string, string>) {
  return Object.fromEntries(Object.entries(values).map(([key, value]) => [key, value.trim()]).filter(([, value]) => value));
}
