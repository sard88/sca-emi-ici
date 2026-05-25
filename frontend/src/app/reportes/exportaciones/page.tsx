"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyExportsState } from "@/components/reportes/EmptyExportsState";
import { ExportHistoryTable } from "@/components/reportes/ExportHistoryTable";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getExportaciones } from "@/lib/api";
import { canAccessAuditoriaExportaciones, canAccessReportes } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";
import type { ExportacionRegistro } from "@/lib/types";

export default function HistorialExportacionesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<ExportacionRegistro[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formato, setFormato] = useState("");
  const [estado, setEstado] = useState("");
  const [tipoDocumento, setTipoDocumento] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getExportaciones({
          limit: "80",
          formato,
          estado,
          tipo_documento: tipoDocumento,
        });
        setItems(response.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar el historial de exportaciones.");
      } finally {
        setLoading(false);
      }
    }

    if (user && canAccessReportes(user)) void load();
  }, [user, formato, estado, tipoDocumento]);

  return (
    <AppShell>
      {!user ? null : !canAccessReportes(user) ? (
        <ErrorMessage message="No tienes permiso para consultar historial de exportaciones desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader
            title="Historial de exportaciones"
            description="Consulta tus descargas documentales registradas. Los perfiles autorizados pueden ver una trazabilidad más amplia."
            user={user}
          />

          <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
            <div className="grid gap-3 md:grid-cols-3">
              <select value={formato} onChange={(event) => setFormato(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]">
                <option value="">Todos los formatos</option>
                <option value="PDF">PDF</option>
                <option value="XLSX">Excel</option>
              </select>
              <select value={estado} onChange={(event) => setEstado(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]">
                <option value="">Todos los estados</option>
                <option value="GENERADA">Generada</option>
                <option value="FALLIDA">Fallida</option>
                <option value="SOLICITADA">Solicitada</option>
              </select>
              <input
                value={tipoDocumento}
                onChange={(event) => setTipoDocumento(event.target.value)}
                placeholder="Tipo de documento, ej. ACTA..."
                className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c]"
              />
            </div>
          </section>

          {loading ? <LoadingState label="Cargando historial de exportaciones..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyExportsState /> : null}
          {!loading && !error && items.length > 0 ? (
            <ExportHistoryTable items={items} showUser={canAccessAuditoriaExportaciones(user)} />
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
