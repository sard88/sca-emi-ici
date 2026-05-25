"use client";

import { useCallback, useEffect, useState } from "react";
import { createResource, listResource } from "@/lib/api";
import type { ResourceItem } from "@/lib/types";
import { CatalogBooleanBadge } from "./CatalogBadges";
import { CatalogResourceForm } from "./CatalogResourceForm";
import type { AdminCatalogResourceConfig } from "@/lib/types";

const componentConfig = (endpoint: string): AdminCatalogResourceConfig => ({
  slug: "componentes-evaluacion",
  titulo: "Componentes de evaluación",
  descripcion: "Componentes por corte dentro del esquema seleccionado.",
  ruta: "",
  endpoint,
  categoria: "catalogos",
  tableColumns: [],
  formFields: [
    {
      key: "corte_codigo",
      label: "Corte",
      type: "select",
      required: true,
      options: [
        { value: "", label: "Seleccionar corte" },
        { value: "P1", label: "Parcial 1" },
        { value: "P2", label: "Parcial 2" },
        { value: "P3", label: "Parcial 3" },
        { value: "FINAL", label: "Evaluación final" },
      ],
    },
    { key: "nombre", label: "Nombre", required: true },
    { key: "porcentaje", label: "Porcentaje", type: "number", required: true },
    { key: "es_examen", label: "Es examen", type: "boolean" },
    { key: "orden", label: "Orden", type: "number" },
  ],
  permiteCrear: true,
  permiteEditar: false,
  permiteInactivar: false,
});

export function EvaluationComponentsPanel({ esquemaId, canWrite }: { esquemaId: number; canWrite: boolean }) {
  const endpoint = `/api/catalogos/esquemas-evaluacion/${esquemaId}/componentes/`;
  const [items, setItems] = useState<ResourceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listResource(endpoint, { page_size: "100" });
      setItems(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible cargar componentes.");
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <section className="space-y-4 rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-lg font-black text-[#101b18]">Componentes de evaluación</h3>
          <p className="mt-1 text-sm leading-6 text-[#5f6764]">Los componentes se guardan en backend. La suma por corte se conserva como regla institucional de evaluación.</p>
        </div>
        {canWrite ? (
          <button type="button" onClick={() => setShowForm((value) => !value)} className="rounded-xl bg-[#0b4a3d] px-4 py-2 text-xs font-black text-white shadow-sm transition hover:bg-[#08372e]">
            {showForm ? "Ocultar formulario" : "Agregar componente"}
          </button>
        ) : null}
      </div>

      {showForm ? (
        <CatalogResourceForm
          config={componentConfig(endpoint)}
          canWrite={canWrite}
          submitLabel="Agregar componente"
          onCancel={() => setShowForm(false)}
          onSubmit={async (payload) => {
            await createResource(endpoint, payload);
            await load();
            setShowForm(false);
          }}
        />
      ) : null}

      {loading ? <p className="text-sm font-black text-[#10372e]">Cargando componentes...</p> : null}
      {error ? <p className="text-sm font-black text-[#7a123d]">{error}</p> : null}
      {!loading && !error && items.length === 0 ? <p className="text-sm font-bold text-[#5f6764]">Aún no hay componentes registrados para este esquema.</p> : null}
      {!loading && !error && items.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-left text-sm">
            <thead>
              <tr className="bg-[#0b4a3d] text-white">
                <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Corte</th>
                <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Nombre</th>
                <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Porcentaje</th>
                <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Examen</th>
                <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Orden</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                  <td className="px-4 py-3 font-bold text-[#263b34]">{String(item.corte_label ?? item.corte_codigo ?? "N/A")}</td>
                  <td className="px-4 py-3 text-[#263b34]">{String(item.nombre ?? "N/A")}</td>
                  <td className="px-4 py-3 text-[#263b34]">{String(item.porcentaje ?? "N/A")}</td>
                  <td className="px-4 py-3"><CatalogBooleanBadge value={item.es_examen} /></td>
                  <td className="px-4 py-3 text-[#263b34]">{String(item.orden ?? "N/A")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
