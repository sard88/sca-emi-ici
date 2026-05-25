import type { ReporteDesempenoConfig } from "@/lib/types";

export function PerformanceReportFilters({
  config,
  values,
  onChange,
  onSubmit,
  onClear,
}: {
  config: ReporteDesempenoConfig;
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
          <p className="text-sm text-[#5f6764]">Los filtros se envían al backend y se reutilizan en la descarga XLSX auditada.</p>
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
        {config.filtros.map((filter) => {
          const commonClass = "h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c]";
          return (
            <label key={filter.key} className="space-y-1">
              <span className="px-1 text-xs font-black uppercase tracking-[0.12em] text-[#7b6b58]">{filter.label}</span>
              {filter.type === "select" ? (
                <select
                  value={values[filter.key] ?? ""}
                  onChange={(event) => onChange(filter.key, event.target.value)}
                  className={commonClass}
                >
                  {(filter.options ?? []).map((option) => (
                    <option key={`${filter.key}-${option.value}`} value={option.value}>{option.label}</option>
                  ))}
                </select>
              ) : (
                <input
                  value={values[filter.key] ?? ""}
                  type={filter.type === "date" ? "date" : "text"}
                  onChange={(event) => onChange(filter.key, event.target.value)}
                  placeholder={filter.placeholder}
                  className={commonClass}
                />
              )}
            </label>
          );
        })}
      </div>
    </section>
  );
}
