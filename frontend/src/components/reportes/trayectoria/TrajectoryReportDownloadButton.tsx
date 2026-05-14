"use client";

import { useState } from "react";
import type { DownloadResult, ReporteTrayectoriaConfig } from "@/lib/types";
import { descargarReporteTrayectoriaXlsx } from "@/lib/api";

export function TrajectoryReportDownloadButton({
  config,
  filters,
  onDone,
  onError,
}: {
  config: ReporteTrayectoriaConfig;
  filters: Record<string, string>;
  onDone: (result: DownloadResult) => void;
  onError: (message: string) => void;
}) {
  const [loading, setLoading] = useState(false);

  async function handleDownload() {
    if (config.requiereDiscenteId && !filters.discente_id) {
      onError("Captura un ID de discente válido para descargar el historial interno por discente.");
      return;
    }

    setLoading(true);
    try {
      const result = await descargarReporteTrayectoriaXlsx(config.slug, filters);
      onDone(result);
    } catch (err) {
      onError(err instanceof Error ? err.message : "La descarga falló. Intenta nuevamente o contacta soporte.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      type="button"
      onClick={handleDownload}
      disabled={loading}
      className="rounded-xl bg-[#7a123d] px-5 py-3 text-sm font-black text-white shadow-sm transition hover:bg-[#5f0f30] disabled:cursor-not-allowed disabled:opacity-60"
    >
      {loading ? "Generando XLSX..." : "Descargar XLSX"}
    </button>
  );
}
