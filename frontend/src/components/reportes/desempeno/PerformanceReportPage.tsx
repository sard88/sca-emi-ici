"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { DownloadStatusToast } from "@/components/reportes/DownloadStatusToast";
import { ExportTraceInfo } from "@/components/reportes/ExportTraceInfo";
import { EmptyExportsState } from "@/components/reportes/EmptyExportsState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getReporteDesempeno } from "@/lib/api";
import { canAccessReportesDesempeno } from "@/lib/dashboard";
import { canAccessReporteDesempeno, cleanPerformanceFilters, emptyPerformanceFilters } from "@/lib/reportes-desempeno";
import { useAuth } from "@/lib/auth";
import type { DownloadResult, ReporteDesempenoConfig, ReporteDesempenoRespuesta } from "@/lib/types";
import { PerformanceReportBadge } from "./PerformanceReportBadge";
import { PerformanceReportDownloadButton } from "./PerformanceReportDownloadButton";
import { PerformanceReportFilters } from "./PerformanceReportFilters";
import { PerformanceReportPrivacyNotice } from "./PerformanceReportPrivacyNotice";
import { PerformanceReportSummaryBar } from "./PerformanceReportSummaryBar";
import { PerformanceReportTable } from "./PerformanceReportTable";

export function PerformanceReportPage({ config }: { config: ReporteDesempenoConfig }) {
  const { user } = useAuth();
  const [filters, setFilters] = useState<Record<string, string>>(() => emptyPerformanceFilters(config));
  const [appliedFilters, setAppliedFilters] = useState<Record<string, string>>({});
  const [data, setData] = useState<ReporteDesempenoRespuesta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [lastDownload, setLastDownload] = useState<DownloadResult | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getReporteDesempeno(config.slug, { ...appliedFilters, limit: "100" });
        setData(response);
      } catch (err) {
        setData(null);
        setError(err instanceof Error ? err.message : "No fue posible consultar el reporte de desempeño.");
      } finally {
        setLoading(false);
      }
    }

    if (user && canAccessReporteDesempeno(user, config)) void load();
  }, [user, config, appliedFilters]);

  function handleApply() {
    setAppliedFilters(cleanPerformanceFilters(filters));
    setLastDownload(null);
    setDownloadError(null);
  }

  function handleClear() {
    const empty = emptyPerformanceFilters(config);
    setFilters(empty);
    setAppliedFilters({});
    setLastDownload(null);
    setDownloadError(null);
  }

  return (
    <AppShell>
      {!user ? null : !canAccessReportesDesempeno(user) || !canAccessReporteDesempeno(user, config) ? (
        <ErrorMessage message="No tienes permiso para consultar reportes de desempeño desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader title={config.titulo} description={config.descripcion} user={user} />

          <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-5 text-white shadow-institutional">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="flex flex-wrap gap-2">
                  <PerformanceReportBadge label="XLSX disponible" tone="dorado" />
                  {config.pdfPendiente ? <PerformanceReportBadge label="PDF pendiente" tone="neutral" /> : null}
                  <PerformanceReportBadge label={config.nominal ? "Reporte nominal" : "Reporte agregado"} tone={config.nominal ? "guinda" : "verde"} />
                </div>
                <p className="mt-4 max-w-3xl text-sm leading-6 text-white/82">{config.ayuda}</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link
                  href="/reportes/desempeno"
                  className="rounded-xl border border-white/30 px-5 py-3 text-sm font-black text-white transition hover:bg-white/10"
                >
                  Volver a desempeño
                </Link>
                <PerformanceReportDownloadButton
                  slug={config.slug}
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

          <PerformanceReportPrivacyNotice config={config} />

          <PerformanceReportFilters
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

          {loading ? <LoadingState label="Cargando vista previa del reporte..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}

          {!loading && !error ? <PerformanceReportSummaryBar data={data} /> : null}
          {!loading && !error && data && data.items.length === 0 ? (
            <EmptyExportsState title="No hay resultados para los filtros seleccionados." description="Ajusta los filtros o descarga el XLSX si necesitas confirmar el reporte completo." />
          ) : null}
          {!loading && !error && data && data.items.length > 0 ? (
            <PerformanceReportTable columns={data.columnas} items={data.items} />
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
