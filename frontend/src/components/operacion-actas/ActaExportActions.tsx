"use client";

import { useState } from "react";
import { descargarActaPdf, descargarActaXlsx } from "@/lib/api";
import type { ActaResumen, DownloadResult } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { ExportTraceInfo } from "@/components/reportes/ExportTraceInfo";
import { DownloadStatusToast } from "@/components/reportes/DownloadStatusToast";

export function ActaExportActions({ acta }: { acta: ActaResumen }) {
  const [loading, setLoading] = useState<string | null>(null);
  const [result, setResult] = useState<DownloadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function download(kind: "pdf" | "xlsx") {
    setLoading(kind);
    setError(null);
    setResult(null);
    try {
      const response = kind === "pdf" ? await descargarActaPdf(acta.acta_id) : await descargarActaXlsx(acta.acta_id);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "La descarga falló. Intenta nuevamente o contacta soporte.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <section className="space-y-3 rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      <div>
        <h3 className="text-base font-black text-[#101b18]">Exportaciones</h3>
        <p className="text-sm text-[#5f6764]">Los archivos se generan en Django y registran auditoría.</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <Button disabled={Boolean(loading)} onClick={() => void download("pdf")}>
          {loading === "pdf" ? "Generando PDF..." : "Exportar PDF"}
        </Button>
        <Button disabled={Boolean(loading)} className="bg-[#0b4a3d] hover:bg-[#0a5c4b]" onClick={() => void download("xlsx")}>
          {loading === "xlsx" ? "Generando Excel..." : "Exportar Excel"}
        </Button>
      </div>
      <ExportTraceInfo result={result} />
      <DownloadStatusToast message={error} tone="error" />
    </section>
  );
}
