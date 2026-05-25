import { ReportFilterField } from "@/components/reportes/ReportFilterField";
import type { ReporteOperativoConfig } from "@/lib/types";

export function OperativeReportFilters({
  config,
  values,
  onChange,
  onSubmit,
  onClear,
}: {
  config: ReporteOperativoConfig;
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
  onSubmit: () => void;
  onClear: () => void;
}) {
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
      <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h3 className="text-base font-black text-[#101b18]">Filtros</h3>
          <p className="text-sm text-[#5f6764]">Se envían al backend como querystring y también se usan para la descarga XLSX.</p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onClear}
            className="rounded-xl border border-[#d8c5a7] bg-white px-4 py-2 text-xs font-black text-[#5f4525] transition hover:bg-[#fff7e8]"
          >
            Limpiar
          </button>
          <button
            type="button"
            onClick={onSubmit}
            className="rounded-xl bg-[#0b4a3d] px-4 py-2 text-xs font-black text-white shadow-sm transition hover:bg-[#08372e]"
          >
            Aplicar filtros
          </button>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {config.filtros.map((filter) => (
          <ReportFilterField key={filter.key} filter={filter} value={values[filter.key] ?? ""} onChange={(value) => onChange(filter.key, value)} />
        ))}
      </div>
    </section>
  );
}
