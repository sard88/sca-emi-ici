"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyExportsState } from "@/components/reportes/EmptyExportsState";
import { ActaExportCard } from "@/components/reportes/ActaExportCard";
import { DownloadStatusToast } from "@/components/reportes/DownloadStatusToast";
import { ExportTraceInfo } from "@/components/reportes/ExportTraceInfo";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getActasExportables } from "@/lib/api";
import { canAccessReportes } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";
import type { ActaExportable, DownloadResult } from "@/lib/types";

export default function ActasExportablesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<ActaExportable[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [lastDownload, setLastDownload] = useState<DownloadResult | null>(null);
  const [texto, setTexto] = useState("");
  const [estado, setEstado] = useState("");
  const [corte, setCorte] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getActasExportables();
        setItems(response.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar actas exportables.");
      } finally {
        setLoading(false);
      }
    }

    if (user && canAccessReportes(user)) void load();
  }, [user]);

  const filtered = useMemo(() => {
    const query = texto.trim().toLowerCase();
    return items.filter((item) => {
      const matchesText = !query || [item.programa_asignatura, item.docente, item.grupo, item.carrera, item.periodo]
        .join(" ")
        .toLowerCase()
        .includes(query);
      const matchesEstado = !estado || item.estado_acta === estado;
      const matchesCorte = !corte || item.corte_codigo === corte;
      return matchesText && matchesEstado && matchesCorte;
    });
  }, [items, texto, estado, corte]);

  const estados = Array.from(new Map(items.map((item) => [item.estado_acta, item.estado_acta_label])).entries());
  const cortes = Array.from(new Map(items.map((item) => [item.corte_codigo, item.corte_nombre])).entries());
  const renderedAssignments = new Set<number>();

  return (
    <AppShell>
      {!user ? null : !canAccessReportes(user) ? (
        <ErrorMessage message="No tienes permiso para consultar actas exportables desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader
            title="Actas exportables"
            description="Descarga actas PDF/XLSX autorizadas. Cada archivo generado queda registrado en auditoría con folio técnico."
            user={user}
          />

          <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
            <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_220px_220px]">
              <input
                value={texto}
                onChange={(event) => setTexto(event.target.value)}
                placeholder="Buscar por asignatura, docente, grupo o periodo..."
                className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c]"
              />
              <select value={estado} onChange={(event) => setEstado(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]">
                <option value="">Todos los estados</option>
                {estados.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
              <select value={corte} onChange={(event) => setCorte(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]">
                <option value="">Todos los cortes</option>
                {cortes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </div>
          </section>

          <ExportTraceInfo result={lastDownload} />
          <DownloadStatusToast message={downloadError} tone="error" />

          {loading ? <LoadingState label="Cargando actas exportables..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}

          {!loading && !error && filtered.length === 0 ? (
            <EmptyExportsState title="No hay actas exportables para tu perfil." description="El backend no devolvió actas disponibles con los permisos actuales o filtros aplicados." />
          ) : null}

          {!loading && !error && filtered.length > 0 ? (
            <section className="grid gap-4">
              {filtered.map((acta) => {
                const showCalificacionFinal = !renderedAssignments.has(acta.asignacion_docente_id);
                renderedAssignments.add(acta.asignacion_docente_id);
                return (
                  <ActaExportCard
                    key={acta.acta_id}
                    acta={acta}
                    showCalificacionFinal={showCalificacionFinal}
                    onDownloaded={(result) => {
                      setDownloadError(null);
                      setLastDownload(result);
                    }}
                    onError={(message) => {
                      setLastDownload(null);
                      setDownloadError(message);
                    }}
                  />
                );
              })}
            </section>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
