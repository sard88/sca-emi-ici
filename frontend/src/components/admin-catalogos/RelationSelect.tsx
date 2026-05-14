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
}: {
  endpoint: string;
  value: string;
  onChange: (value: string) => void;
  labelKey?: string;
  valueKey?: string;
  disabled?: boolean;
  required?: boolean;
}) {
  const [items, setItems] = useState<ResourceItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      setError(null);
      try {
        const response = await listResource(endpoint, { page_size: "100", limit: "100" });
        if (active) setItems(response.items);
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "No fue posible cargar opciones.");
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [endpoint]);

  return (
    <div className="space-y-1">
      <select
        value={value}
        required={required}
        disabled={disabled}
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
      {error ? <p className="text-xs font-bold text-[#7a123d]">{error}</p> : null}
    </div>
  );
}

function optionLabel(item: ResourceItem, labelKey: string) {
  const value = item[labelKey] ?? item.label ?? item.nombre ?? item.name ?? item.username ?? item.clave ?? item.id;
  return String(value);
}

function optionValue(item: ResourceItem, valueKey: string) {
  const value = item[valueKey] ?? item.id;
  return String(value);
}
