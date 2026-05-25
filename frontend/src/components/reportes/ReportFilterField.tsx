"use client";

import { useEffect, useState } from "react";
import { listResource } from "@/lib/api";
import type { ReportFilterRelation, ResourceItem } from "@/lib/types";

type FilterConfig = {
  key: string;
  label: string;
  type?: "text" | "select" | "date" | "relation";
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
  relation?: ReportFilterRelation;
};

const commonClass = "h-12 w-full rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c]";

export function ReportFilterField({
  filter,
  value,
  onChange,
  required = false,
}: {
  filter: FilterConfig;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
}) {
  return (
    <label className="space-y-1">
      <span className="px-1 text-xs font-black uppercase tracking-[0.12em] text-[#7b6b58]">
        {filter.label}
        {required ? " *" : ""}
      </span>
      {filter.type === "select" ? (
        <select value={value} onChange={(event) => onChange(event.target.value)} className={commonClass}>
          {(filter.options ?? []).map((option) => (
            <option key={`${filter.key}-${option.value}`} value={option.value}>{option.label}</option>
          ))}
        </select>
      ) : filter.type === "relation" && filter.relation ? (
        <RelationFilter filter={filter} value={value} onChange={onChange} />
      ) : (
        <input
          value={value}
          type={filter.type === "date" ? "date" : "text"}
          onChange={(event) => onChange(event.target.value)}
          placeholder={filter.placeholder}
          className={commonClass}
        />
      )}
    </label>
  );
}

function RelationFilter({ filter, value, onChange }: { filter: FilterConfig; value: string; onChange: (value: string) => void }) {
  const relation = filter.relation;
  const [items, setItems] = useState<ResourceItem[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!relation) return;
    const relationConfig = relation;
    let active = true;
    async function load() {
      setError(null);
      try {
        const response = await listResource(relationConfig.endpoint, cleanParams({
          page_size: "100",
          ...(relationConfig.activeOnly ? { activo: "true" } : {}),
          ...(relationConfig.queryParams ?? {}),
          ...(relationConfig.search && search.trim() ? { q: search.trim() } : {}),
        }));
        if (active) setItems(response.items);
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "No fue posible cargar opciones.");
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [relation, search]);

  if (!relation) return null;
  return (
    <div className="space-y-2">
      {relation.search ? (
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={`Buscar ${filter.label.toLowerCase()}...`}
          className={commonClass}
        />
      ) : null}
      <select value={value} onChange={(event) => onChange(event.target.value)} className={commonClass}>
        <option value="">Todos</option>
        {items.map((item) => (
          <option key={`${filter.key}-${item.id}`} value={optionValue(item, relation)}>
            {optionLabel(item, relation)}
          </option>
        ))}
      </select>
      {error ? <p className="px-1 text-xs font-bold text-[#7a123d]">{error}</p> : null}
    </div>
  );
}

function cleanParams(params: Record<string, string | number | boolean | undefined>) {
  return Object.fromEntries(Object.entries(params).filter(([, value]) => value !== undefined && value !== "").map(([key, value]) => [key, String(value)]));
}

function optionLabel(item: ResourceItem, relation: ReportFilterRelation) {
  const key = relation.labelKey ?? "label";
  return String(item[key] ?? item.label ?? item.nombre_institucional ?? item.nombre ?? item.clave ?? item.username ?? item.id);
}

function optionValue(item: ResourceItem, relation: ReportFilterRelation) {
  const key = relation.valueKey ?? "id";
  return String(item[key] ?? item.id);
}
