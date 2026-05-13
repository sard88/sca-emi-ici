"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyExportsState } from "@/components/reportes/EmptyExportsState";
import { ExportHistoryTable } from "@/components/reportes/ExportHistoryTable";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getAuditoriaExportaciones } from "@/lib/api";
import { canAccessAuditoriaExportaciones } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";
import type { ExportacionRegistro } from "@/lib/types";

export default function AuditoriaExportacionesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<ExportacionRegistro[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fechaDesde, setFechaDesde] = useState("");
  const [fechaHasta, setFechaHasta] = useState("");
  const [usuario, setUsuario] = useState("");
  const [estado, setEstado] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getAuditoriaExportaciones({
          limit: "120",
          fecha_desde: fechaDesde,
          fecha_hasta: fechaHasta,
          usuario,
          estado,
        });
        setItems(response.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar auditoría de exportaciones.");
      } finally {
        setLoading(false);
      }
    }

    if (user && canAccessAuditoriaExportaciones(user)) void load();
  }, [user, fechaDesde, fechaHasta, usuario, estado]);

  return (
    <AppShell>
      {!user ? null : !canAccessAuditoriaExportaciones(user) ? (
        <ErrorMessage message="No tienes permiso para consultar la auditoría institucional de exportaciones." />
      ) : (
        <div className="space-y-6">
          <PageHeader
            title="Auditoría de exportaciones"
            description="Consulta institucional de documentos generados, usuarios solicitantes, estados y folios técnicos."
            user={user}
          />

          <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
            <div className="grid gap-3 md:grid-cols-4">
              <input type="date" value={fechaDesde} onChange={(event) => setFechaDesde(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]" />
              <input type="date" value={fechaHasta} onChange={(event) => setFechaHasta(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]" />
              <input value={usuario} onChange={(event) => setUsuario(event.target.value)} placeholder="Usuario o nombre..." className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c]" />
              <select value={estado} onChange={(event) => setEstado(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]">
                <option value="">Todos los estados</option>
                <option value="GENERADA">Generada</option>
                <option value="FALLIDA">Fallida</option>
                <option value="SOLICITADA">Solicitada</option>
              </select>
            </div>
          </section>

          {loading ? <LoadingState label="Cargando auditoría institucional..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyExportsState title="No hay registros de auditoría con los filtros seleccionados." /> : null}
          {!loading && !error && items.length > 0 ? <ExportHistoryTable items={items} showUser /> : null}
        </div>
      )}
    </AppShell>
  );
}
