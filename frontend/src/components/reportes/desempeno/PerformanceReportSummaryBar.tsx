import type { ReporteDesempenoRespuesta } from "@/lib/types";
import { PerformanceMetricCard } from "./PerformanceMetricCard";
import { PerformanceReportBadge } from "./PerformanceReportBadge";

const MAX_SUMMARY_METRICS = 4;

export function PerformanceReportSummaryBar({ data }: { data: ReporteDesempenoRespuesta | null }) {
  if (!data) return null;

  const summaryEntries = Object.entries(data.resumen ?? {})
    .filter(([, value]) => value !== null && value !== undefined && value !== "")
    .slice(0, MAX_SUMMARY_METRICS);

  return (
    <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-4">
      <PerformanceMetricCard label="Registros" value={data.total} />
      <PerformanceMetricCard label="Columnas" value={data.columnas.length} tone="dorado" />
      {summaryEntries.map(([key, value]) => (
        <PerformanceMetricCard key={key} label={humanizeKey(key)} value={formatSummary(value)} tone="guinda" />
      ))}
      <div className="rounded-[1.25rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
        <p className="text-xs font-black uppercase tracking-[0.14em] text-[#9f6a22]">Disponibilidad</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <PerformanceReportBadge label="Vista previa JSON" />
          <PerformanceReportBadge label="XLSX auditado" tone="dorado" />
        </div>
      </div>
    </section>
  );
}

function formatSummary(value: unknown) {
  if (typeof value === "boolean") return value ? "Sí" : "No";
  if (typeof value === "number") return Number.isInteger(value) ? value : value.toFixed(1);
  if (typeof value === "string") return value;
  return "Dato compuesto";
}

function humanizeKey(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());
}
