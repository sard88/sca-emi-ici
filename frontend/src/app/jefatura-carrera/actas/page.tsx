"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ActasFilters } from "@/components/operacion-actas/ActasFilters";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getJefaturaCarreraActasPendientes } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessJefaturaCarreraActas } from "@/lib/dashboard";
import type { ActaResumen } from "@/lib/types";

export default function JefaturaCarreraActasPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<ActaResumen[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        setItems((await getJefaturaCarreraActasPendientes(filters)).items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar las actas pendientes.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessJefaturaCarreraActas(user)) void load();
  }, [user, filters]);

  return (
    <AppShell>
      {!user ? null : !canAccessJefaturaCarreraActas(user) ? (
        <ErrorMessage message="No tienes permiso para revisar actas de carrera." />
      ) : (
        <div className="space-y-5">
          <PageHeader title="Actas por validar" description="Revisa las actas remitidas para validación de carrera." user={user} />
          <p className="text-sm text-[#5f6764]">Consulta el estado académico de las actas asignadas a tu carrera.</p>

          <div className="rounded-2xl border border-[#eadfce] bg-white/90 p-4">
            <ActasFilters onApply={setFilters} includeEstado={false} />
          </div>

          {loading ? <LoadingState label="Cargando actas..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyState title="Sin actas pendientes por ahora." description="Sin información disponible." /> : null}

          {!loading && !error && items.length > 0 ? (
            <section className="overflow-hidden rounded-2xl border border-[#e7dccb] bg-white/90 shadow-sm">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[#eadfce] text-sm">
                  <thead className="bg-[#f7f0e3]">
                    <tr className="text-left text-xs font-black uppercase tracking-[0.08em] text-[#5f6764]">
                      <th className="px-4 py-3">Corte</th>
                      <th className="px-4 py-3">Grupo</th>
                      <th className="px-4 py-3">Asignatura</th>
                      <th className="px-4 py-3">Período académico</th>
                      <th className="px-4 py-3">Estado</th>
                      <th className="px-4 py-3">Acción</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#f0e7d8] bg-white/95 text-[#152b25]">
                    {items.map((acta) => (
                      <tr key={acta.acta_id}>
                        <td className="px-4 py-3 font-bold">{acta.corte_label || acta.corte_codigo || "-"}</td>
                        <td className="px-4 py-3">{acta.grupo?.label || acta.grupo?.nombre || "-"}</td>
                        <td className="px-4 py-3">{acta.programa_asignatura?.label || acta.programa_asignatura?.nombre || "-"}</td>
                        <td className="px-4 py-3">{acta.periodo?.label || acta.periodo?.nombre || "-"}</td>
                        <td className="px-4 py-3">
                          <span className="rounded-lg border border-[#d8c5a7] bg-[#fbf5ea] px-2.5 py-1 text-xs font-black text-[#5a3b2a]">
                            {toEstadoVisible(acta.estado_acta_label || acta.estado_acta)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <Link href={`/jefatura-carrera/actas/${acta.acta_id}`} className="rounded-lg border border-[#7a123d] bg-[#7a123d] px-3 py-1.5 text-xs font-black text-white hover:bg-[#671033]">
                            Revisar acta
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function toEstadoVisible(estado: string) {
  const normalized = (estado || "").toUpperCase();
  if (normalized.includes("BORRADOR")) return "En elaboración";
  if (normalized.includes("REMITIDO")) return "Pendiente de revisión";
  if (normalized.includes("VALIDADO")) return "Validada por carrera";
  if (normalized.includes("FORMALIZADO")) return "Formalizada";
  if (normalized.includes("PUBLICADO")) return "Publicada";
  return estado;
}
