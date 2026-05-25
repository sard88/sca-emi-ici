import type { AdminCatalogResourceConfig } from "@/lib/types";

export function CatalogResourceFilters({
  config,
  values,
  onChange,
  onSubmit,
  onClear,
}: {
  config: AdminCatalogResourceConfig;
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
  onSubmit: () => void;
  onClear: () => void;
}) {
  if (!config.filters || config.filters.length === 0) return null;

  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
      <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h3 className="text-base font-black text-[#101b18]">Filtros</h3>
          <p className="text-sm text-[#5f6764]">Los filtros se envían como querystring y el backend aplica permisos y ámbito.</p>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={onClear} className="rounded-xl border border-[#d8c5a7] bg-white px-4 py-2 text-xs font-black text-[#5f4525] transition hover:bg-[#fff7e8]">Limpiar</button>
          <button type="button" onClick={onSubmit} className="rounded-xl bg-[#0b4a3d] px-4 py-2 text-xs font-black text-white shadow-sm transition hover:bg-[#08372e]">Buscar</button>
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {config.filters.map((filter) => (
          <label key={filter.key} className="space-y-1">
            <span className="px-1 text-xs font-black uppercase tracking-[0.12em] text-[#7b6b58]">{filter.label}</span>
            <input
              value={values[filter.key] ?? ""}
              onChange={(event) => onChange(filter.key, event.target.value)}
              placeholder={filter.placeholder}
              className="h-12 w-full rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c]"
            />
          </label>
        ))}
      </div>
    </section>
  );
}
