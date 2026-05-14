import { CatalogBooleanBadge } from "./CatalogBadges";
import type { ResourceItem } from "@/lib/types";

export function CatalogResourceDetail({ item }: { item: ResourceItem }) {
  const entries = Object.entries(item).filter(([key]) => !["id", "componentes"].includes(key) && !key.toLowerCase().includes("password"));

  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm">
      <h3 className="text-lg font-black text-[#101b18]">Resumen del registro</h3>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {entries.slice(0, 18).map(([key, value]) => (
          <div key={key} className="rounded-2xl border border-[#f0e5d6] bg-[#fffaf1]/70 p-3">
            <p className="text-[11px] font-black uppercase tracking-[0.12em] text-[#9f6a22]">{humanizeKey(key)}</p>
            <div className="mt-2 text-sm font-bold text-[#263b34]">{formatValue(value)}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "boolean") return <CatalogBooleanBadge value={value} />;
  if (typeof value === "object") {
    const item = value as { label?: unknown; nombre?: unknown; name?: unknown; clave?: unknown };
    return String(item.label ?? item.nombre ?? item.name ?? item.clave ?? "Dato compuesto");
  }
  return String(value);
}

function humanizeKey(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());
}
