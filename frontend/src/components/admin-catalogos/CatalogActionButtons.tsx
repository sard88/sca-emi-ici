"use client";

import Link from "next/link";
import { activateResource, deactivateResource } from "@/lib/api";
import { confirmCatalogAction } from "./ConfirmActionDialog";
import type { AdminCatalogResourceConfig, ResourceItem } from "@/lib/types";

export function CatalogActionButtons({
  config,
  item,
  canWrite,
  onChanged,
}: {
  config: AdminCatalogResourceConfig;
  item: ResourceItem;
  canWrite: boolean;
  onChanged: () => void;
}) {
  const active = Boolean(item.activo ?? item.is_active);

  async function toggleActive() {
    const verb = active ? "inactivar" : "activar";
    if (!confirmCatalogAction(`¿Confirmas ${verb} este registro?`)) return;
    if (active) await deactivateResource(config.endpoint, item.id);
    else await activateResource(config.endpoint, item.id);
    onChanged();
  }

  return (
    <div className="flex flex-wrap gap-2">
      <Link href={`${config.ruta}/${item.id}`} className="rounded-xl border border-[#d8c5a7] bg-white px-3 py-2 text-xs font-black text-[#7a123d] transition hover:bg-[#fff7e8]">
        Detalle
      </Link>
      {canWrite && config.permiteInactivar ? (
        <button type="button" onClick={toggleActive} className="rounded-xl border border-[#d8c5a7] bg-white px-3 py-2 text-xs font-black text-[#5f4525] transition hover:bg-[#fff7e8]">
          {active ? "Inactivar" : "Activar"}
        </button>
      ) : null}
    </div>
  );
}
