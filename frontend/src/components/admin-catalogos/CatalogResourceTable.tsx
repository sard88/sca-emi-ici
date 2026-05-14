import { CatalogBooleanBadge, CatalogStatusBadge } from "./CatalogBadges";
import { CatalogActionButtons } from "./CatalogActionButtons";
import type { AdminCatalogResourceConfig, ResourceItem } from "@/lib/types";

export function CatalogResourceTable({
  config,
  items,
  canWrite,
  onChanged,
}: {
  config: AdminCatalogResourceConfig;
  items: ResourceItem[];
  canWrite: boolean;
  onChanged: () => void;
}) {
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 shadow-sm">
      <div className="border-b border-[#eadfce] p-4">
        <h3 className="text-base font-black text-[#101b18]">Registros</h3>
        <p className="mt-1 text-sm text-[#5f6764]">Tabla operativa con acciones controladas por permisos del backend.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead>
            <tr className="bg-[#0b4a3d] text-white">
              {config.tableColumns.map((column) => (
                <th key={column.key} className="whitespace-nowrap px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">{column.label}</th>
              ))}
              <th className="whitespace-nowrap px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                {config.tableColumns.map((column) => (
                  <td key={`${item.id}-${column.key}`} className="max-w-[320px] px-4 py-3 align-top text-[#263b34]">
                    {formatCell(item[column.key], column.type)}
                  </td>
                ))}
                <td className="px-4 py-3 align-top">
                  <CatalogActionButtons config={config} item={item} canWrite={canWrite} onChanged={onChanged} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function formatCell(value: unknown, type?: string) {
  if (type === "boolean") return <CatalogBooleanBadge value={value} />;
  if (type === "status") return <CatalogStatusBadge value={value} />;
  if (type === "relation") return relationLabel(value);
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "boolean") return <CatalogBooleanBadge value={value} />;
  if (typeof value === "object") return relationLabel(value);
  return String(value);
}

function relationLabel(value: unknown) {
  if (!value || typeof value !== "object") return "N/A";
  const item = value as { label?: unknown; nombre?: unknown; name?: unknown; clave?: unknown; username?: unknown };
  return String(item.label ?? item.nombre ?? item.name ?? item.clave ?? item.username ?? "N/A");
}
