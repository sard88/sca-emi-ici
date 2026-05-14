"use client";

import { useEffect, useState } from "react";
import { listResource } from "@/lib/api";
import type { ResourceItem } from "@/lib/types";

export function RelationSelect({
  endpoint,
  value,
  onChange,
  labelKey = "label",
  valueKey = "id",
  disabled = false,
  required = false,
  activeOnly = false,
  queryParams = {},
  searchEnabled = false,
  minSearchLength = 0,
  disabledReason,
}: {
  endpoint: string;
  value: string;
  onChange: (value: string) => void;
  labelKey?: string;
  valueKey?: string;
  disabled?: boolean;
  required?: boolean;
  activeOnly?: boolean;
  queryParams?: Record<string, string | number | boolean | undefined>;
  searchEnabled?: boolean;
  minSearchLength?: number;
  disabledReason?: string;
}) {
  const [items, setItems] = useState<ResourceItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const blocked = Boolean(disabledReason);

  useEffect(() => {
    let active = true;
    async function load() {
      if (blocked || (searchEnabled && search.trim().length < minSearchLength)) {
        setItems([]);
        return;
      }
      setError(null);
      try {
        const response = await listResource(endpoint, cleanParams({
          page_size: "100",
          limit: "100",
          ...(activeOnly ? { activo: "true" } : {}),
          ...queryParams,
          ...(searchEnabled && search.trim() ? { q: search.trim() } : {}),
        }));
        if (active) setItems(activeOnly ? response.items.filter(isActiveItem) : response.items);
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "No fue posible cargar opciones.");
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [activeOnly, blocked, endpoint, minSearchLength, queryParams, search, searchEnabled]);

  return (
    <div className="space-y-1">
      {searchEnabled ? (
        <input
          value={search}
          disabled={disabled || blocked}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Buscar opción..."
          className="mb-2 h-10 w-full rounded-xl border border-[#e4d6c2] bg-white px-3 text-sm font-medium outline-none focus:border-[#bc955c] disabled:bg-[#f5efe6] disabled:text-[#8a8176]"
        />
      ) : null}
      <select
        value={value}
        required={required}
        disabled={disabled || blocked}
        onChange={(event) => onChange(event.target.value)}
        className="h-12 w-full rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c] disabled:bg-[#f5efe6] disabled:text-[#8a8176]"
      >
        <option value="">Seleccionar</option>
        {items.map((item) => (
          <option key={item.id} value={optionValue(item, valueKey)}>
            {optionLabel(item, labelKey)}
          </option>
        ))}
      </select>
      {blocked ? <p className="text-xs font-bold text-[#7a4b0d]">{disabledReason}</p> : null}
      {error ? <p className="text-xs font-bold text-[#7a123d]">{error}</p> : null}
    </div>
  );
}

function cleanParams(params: Record<string, string | number | boolean | undefined>) {
  return Object.fromEntries(
    Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== "")
      .map(([key, value]) => [key, String(value)]),
  );
}

function isActiveItem(item: ResourceItem) {
  if (typeof item.activo === "boolean") return item.activo;
  if (typeof item.estado === "string") return item.estado.toLowerCase() === "activo";
  if (typeof item.is_active === "boolean") return item.is_active;
  return true;
}

function optionLabel(item: ResourceItem, labelKey: string) {
  const value = item[labelKey] ?? item.label ?? item.nombre ?? item.name ?? item.username ?? item.clave ?? item.id;
  return String(value);
}

function optionValue(item: ResourceItem, valueKey: string) {
  const value = item[valueKey] ?? item.id;
  return String(value);
}
