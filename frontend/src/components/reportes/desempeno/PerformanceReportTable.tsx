import type { ReporteDesempenoColumna, ReporteDesempenoItem } from "@/lib/types";

const MAX_PREVIEW_ROWS = 100;

export function PerformanceReportTable({ columns, items }: { columns: ReporteDesempenoColumna[]; items: ReporteDesempenoItem[] }) {
  const previewItems = items.slice(0, MAX_PREVIEW_ROWS);

  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 shadow-sm">
      <div className="flex flex-col gap-2 border-b border-[#eadfce] p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-base font-black text-[#101b18]">Vista previa</h3>
          <p className="text-sm text-[#5f6764]">La tabla usa columnas devueltas por Django; el XLSX contiene el reporte completo.</p>
        </div>
        {items.length > MAX_PREVIEW_ROWS ? (
          <p className="rounded-full bg-[#fff7e8] px-3 py-1 text-xs font-black text-[#7b4c0c]">
            Vista limitada a {MAX_PREVIEW_ROWS} filas. Descarga el XLSX para revisar todo.
          </p>
        ) : null}
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead>
            <tr className="bg-[#0b4a3d] text-white">
              {columns.map((column) => (
                <th key={column.key} className="whitespace-nowrap px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">
                  {column.label || humanizeKey(column.key)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {previewItems.map((item, rowIndex) => (
              <tr key={rowIndex} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                {columns.map((column) => (
                  <td key={`${rowIndex}-${column.key}`} className="max-w-[320px] px-4 py-3 align-top text-[#263b34]">
                    {formatValue(item[column.key], column.key)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function formatValue(value: unknown, key: string) {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "boolean") return value ? "Sí" : "No";
  if (typeof value === "number") {
    if (key.includes("porcentaje") || key.startsWith("pct_")) return `${value.toFixed(1)}%`;
    if (key.includes("promedio") || key.includes("calificacion") || key.includes("desviacion")) return value.toFixed(1);
    return Number.isInteger(value) ? String(value) : value.toFixed(1);
  }
  if (typeof value === "string") return value;
  return "Dato compuesto";
}

function humanizeKey(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());
}
