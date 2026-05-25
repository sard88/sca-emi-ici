"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { DownloadStatusToast } from "@/components/reportes/DownloadStatusToast";
import { EmptyExportsState } from "@/components/reportes/EmptyExportsState";
import { ExportTraceInfo } from "@/components/reportes/ExportTraceInfo";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getReporteTrayectoria } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessReportesTrayectoria } from "@/lib/dashboard";
import { canAccessReporteTrayectoria, cleanTrajectoryFilters, emptyTrajectoryFilters } from "@/lib/reportes-trayectoria";
import type { DownloadResult, ReporteTrayectoriaConfig, ReporteTrayectoriaRespuesta } from "@/lib/types";
import { InternalHistoryDiscenteSelector } from "./InternalHistoryDiscenteSelector";
import { TrajectoryReportBadge } from "./TrajectoryReportBadge";
import { TrajectoryReportDownloadButton } from "./TrajectoryReportDownloadButton";
import { TrajectoryReportFilters } from "./TrajectoryReportFilters";
import { TrajectoryReportPrivacyNotice } from "./TrajectoryReportPrivacyNotice";
import { TrajectoryReportSummaryBar } from "./TrajectoryReportSummaryBar";
import { TrajectoryReportTable } from "./TrajectoryReportTable";

export function TrajectoryReportPage({ config }: { config: ReporteTrayectoriaConfig }) {
  const { user } = useAuth();
  const [filters, setFilters] = useState<Record<string, string>>(() => emptyTrajectoryFilters(config));
  const [appliedFilters, setAppliedFilters] = useState<Record<string, string>>({});
  const [data, setData] = useState<ReporteTrayectoriaRespuesta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [lastDownload, setLastDownload] = useState<DownloadResult | null>(null);

  useEffect(() => {
    async function load() {
      if (config.requiereDiscenteId && !appliedFilters.discente_id) {
        setData(null);
        setError(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const response = await getReporteTrayectoria(config.slug, { ...appliedFilters, limit: "100" });
        setData(response);
      } catch (err) {
        setData(null);
        setError(err instanceof Error ? err.message : "No fue posible consultar el reporte de trayectoria.");
      } finally {
        setLoading(false);
      }
    }

    if (user && canAccessReporteTrayectoria(user, config)) void load();
  }, [user, config, appliedFilters]);

  function handleApply() {
    const clean = cleanTrajectoryFilters(filters);
    setAppliedFilters(clean);
    setLastDownload(null);
    setDownloadError(null);
  }

  function handleClear() {
    const empty = emptyTrajectoryFilters(config);
    setFilters(empty);
    setAppliedFilters({});
    setLastDownload(null);
    setDownloadError(null);
  }

  return (
    <AppShell>
      {!user ? null : !canAccessReportesTrayectoria(user) || !canAccessReporteTrayectoria(user, config) ? (
        <ErrorMessage message="No tienes permiso para consultar reportes de trayectoria desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader title={config.titulo} description={config.descripcion} user={user} />

          <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-5 text-white shadow-institutional">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="flex flex-wrap gap-2">
                  <TrajectoryReportBadge label="XLSX disponible" tone="dorado" />
                  {config.pdfPendiente ? <TrajectoryReportBadge label="PDF pendiente" tone="neutral" /> : null}
                  <TrajectoryReportBadge label={config.nominal ? "Reporte nominal" : "Reporte agregado"} tone={config.nominal ? "guinda" : "verde"} />
                  {config.requiereDiscenteId ? <TrajectoryReportBadge label="Discente requerido" tone="dorado" /> : null}
                </div>
                <p className="mt-4 max-w-3xl text-sm leading-6 text-white/82">{config.ayuda}</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link
                  href="/reportes/trayectoria"
                  className="rounded-xl border border-white/30 px-5 py-3 text-sm font-black text-white transition hover:bg-white/10"
                >
                  Volver a trayectoria
                </Link>
                <TrajectoryReportDownloadButton
                  config={config}
                  filters={appliedFilters}
                  onDone={(result) => {
                    setDownloadError(null);
                    setLastDownload(result);
                  }}
                  onError={(message) => {
                    setLastDownload(null);
                    setDownloadError(message);
                  }}
                />
              </div>
            </div>
          </section>

          <TrajectoryReportPrivacyNotice config={config} />
          <InternalHistoryDiscenteSelector config={config} discenteId={filters.discente_id ?? ""} />

          <TrajectoryReportFilters
            config={config}
            values={filters}
            onChange={(key, value) => setFilters((current) => ({ ...current, [key]: value }))}
            onSubmit={handleApply}
            onClear={handleClear}
          />

          <ExportTraceInfo result={lastDownload} />
          <DownloadStatusToast message={downloadError} tone="error" />
          {lastDownload ? (
            <DownloadStatusToast
              message="Puedes consultar esta descarga en Reportes y exportaciones > Historial de exportaciones."
              tone="info"
            />
          ) : null}

          {config.requiereDiscenteId && !appliedFilters.discente_id ? (
            <EmptyExportsState
              title="Discente requerido para consultar este historial interno."
              description="Captura un ID interno de discente y aplica filtros. El historial interno no es kárdex oficial."
            />
          ) : null}
          {loading ? <LoadingState label="Cargando vista previa del reporte..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}

          {!loading && !error && (!config.requiereDiscenteId || appliedFilters.discente_id) ? <TrajectoryReportSummaryBar data={data} /> : null}
          {!loading && !error && data && data.items.length === 0 ? (
            <EmptyExportsState title="No hay resultados para los filtros seleccionados." description="Ajusta los filtros o descarga el XLSX si necesitas confirmar el reporte completo." />
          ) : null}
          {!loading && !error && data && data.items.length > 0 ? (
            <TrajectoryReportTable columns={data.columnas} items={data.items} />
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
