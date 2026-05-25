"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { DownloadStatusToast } from "@/components/reportes/DownloadStatusToast";
import { ExportTraceInfo } from "@/components/reportes/ExportTraceInfo";
import { KardexExportCard } from "@/components/reportes/KardexExportCard";
import { KardexExportEmptyState } from "@/components/reportes/KardexExportEmptyState";
import { KardexExportHelpText } from "@/components/reportes/KardexExportHelpText";
import { KardexExportSearch, type KardexSearchFilters } from "@/components/reportes/KardexExportSearch";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getKardexExportables } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessKardexPdf } from "@/lib/dashboard";
import type { DownloadResult, KardexExportable } from "@/lib/types";

const initialFilters: KardexSearchFilters = {
  q: "",
  carrera: "",
  situacion: "",
};

export default function KardexReportesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<KardexExportable[]>([]);
  const [filters, setFilters] = useState<KardexSearchFilters>(initialFilters);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [lastDownload, setLastDownload] = useState<DownloadResult | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getKardexExportables(filters);
        setItems(response.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar discentes con kárdex exportable.");
      } finally {
        setLoading(false);
      }
    }

    if (user && canAccessKardexPdf(user)) void load();
  }, [user, filters]);

  const carreras = useMemo(() => Array.from(new Set(items.map((item) => item.carrera.clave))).sort(), [items]);
  const hasFilters = Boolean(filters.q || filters.carrera || filters.situacion);

  return (
    <AppShell>
      {!user ? null : !canAccessKardexPdf(user) ? (
        <ErrorMessage message="No tienes permiso para consultar ni exportar kárdex oficial desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader
            title="Kárdex oficial"
            description="Exportación institucional del kárdex académico en PDF para perfiles autorizados."
            user={user}
          />

          <KardexExportHelpText />

          <KardexExportSearch
            initialFilters={filters}
            carreras={carreras}
            onSearch={(nextFilters) => {
              setLastDownload(null);
              setDownloadError(null);
              setFilters(nextFilters);
            }}
          />

          <ExportTraceInfo result={lastDownload} />
          <DownloadStatusToast message={downloadError} tone="error" />

          {loading ? <LoadingState label="Cargando discentes autorizados..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}

          {!loading && !error && items.length === 0 ? <KardexExportEmptyState filtered={hasFilters} /> : null}

          {!loading && !error && items.length > 0 ? (
            <section className="grid gap-4">
              {items.map((item) => (
                <KardexExportCard
                  key={item.discente_id}
                  item={item}
                  onDownloaded={(result) => {
                    setDownloadError(null);
                    setLastDownload(result);
                  }}
                  onError={(message) => {
                    setLastDownload(null);
                    setDownloadError(message);
                  }}
                />
              ))}
            </section>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
