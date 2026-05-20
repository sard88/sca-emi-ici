"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getPeriodos } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessPeriodosOperativos } from "@/lib/dashboard";
import type { PeriodoOperativoDTO } from "@/lib/types";

export default function PeriodosPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<PeriodoOperativoDTO[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getPeriodos();
        setItems(response.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar períodos.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessPeriodosOperativos(user)) void load();
  }, [user]);

  return (
    <AppShell showRightPanel={false}>
      {!user ? null : !canAccessPeriodosOperativos(user) ? (
        <ErrorMessage message="No tienes permiso para consultar períodos académicos." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Períodos académicos" description="Consulta los períodos académicos registrados y sus procesos de cierre." user={user} />
          {loading ? <LoadingState label="Cargando períodos..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyState title="Sin períodos registrados para mostrar." description="Sin información disponible." /> : null}
          {!loading && !error && items.length > 0 ? (
            <section className="overflow-x-auto rounded-[1.5rem] border border-[#eadfce] bg-white/88 shadow-sm">
              <table className="min-w-full border-collapse text-left text-sm">
                <thead>
                  <tr className="bg-[#0b4a3d] text-white">
                    <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Período académico</th>
                    <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Estado</th>
                    <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Fecha de inicio</th>
                    <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Fecha de cierre</th>
                    <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Observación</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((periodo) => (
                    <tr key={periodo.id} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                      <td className="px-4 py-3 font-bold text-[#263b34]">{periodo.nombre || periodo.clave || `Período ${periodo.id}`}</td>
                      <td className="px-4 py-3 text-[#263b34]">{periodo.estado_label || periodo.estado || "Sin información"}</td>
                      <td className="px-4 py-3 text-[#263b34]">{formatDate(periodo.fecha_inicio)}</td>
                      <td className="px-4 py-3 text-[#263b34]">{formatDate(periodo.fecha_fin)}</td>
                      <td className="px-4 py-3 text-[#263b34]">{periodo.observaciones || "Sin información"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function formatDate(value?: string | null) {
  if (!value) return "Sin información";
  try {
    return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium" }).format(new Date(value));
  } catch {
    return "Sin información";
  }
}
