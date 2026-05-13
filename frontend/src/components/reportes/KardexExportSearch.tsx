"use client";

import { useState } from "react";

export type KardexSearchFilters = {
  q: string;
  carrera: string;
  situacion: string;
};

export function KardexExportSearch({
  initialFilters,
  carreras,
  onSearch,
}: {
  initialFilters: KardexSearchFilters;
  carreras: string[];
  onSearch: (filters: KardexSearchFilters) => void;
}) {
  const [filters, setFilters] = useState(initialFilters);

  function update<K extends keyof KardexSearchFilters>(key: K, value: KardexSearchFilters[K]) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_180px_220px_auto]">
        <input
          value={filters.q}
          onChange={(event) => update("q", event.target.value)}
          placeholder="Buscar por nombre, carrera, grupo o ID interno..."
          className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c]"
        />
        <select
          value={filters.carrera}
          onChange={(event) => update("carrera", event.target.value)}
          className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]"
        >
          <option value="">Todas las carreras</option>
          {carreras.map((carrera) => (
            <option key={carrera} value={carrera}>{carrera}</option>
          ))}
        </select>
        <select
          value={filters.situacion}
          onChange={(event) => update("situacion", event.target.value)}
          className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]"
        >
          <option value="">Todas las situaciones</option>
          <option value="regular">Regular</option>
          <option value="baja_temporal">Baja temporal</option>
          <option value="baja_definitiva">Baja definitiva</option>
          <option value="egresado">Egresado</option>
        </select>
        <button
          type="button"
          onClick={() => onSearch(filters)}
          className="h-12 rounded-2xl bg-[#7a123d] px-5 text-sm font-black text-white shadow-lg shadow-[#7a123d]/18 transition hover:bg-[#8c1244]"
        >
          Buscar
        </button>
      </div>
    </section>
  );
}
