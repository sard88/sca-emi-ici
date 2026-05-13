import type { ReporteCatalogoItem } from "@/lib/types";
import { ReportAvailabilityBadge } from "./ReportAvailabilityBadge";

export function ReportCatalogCard({ item }: { item: ReporteCatalogoItem }) {
  return (
    <article className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-[11px] font-black uppercase tracking-[0.18em] text-[#9f6a22]">{item.codigo.replaceAll("_", " ")}</p>
          <h3 className="mt-2 text-lg font-black text-[#152b25]">{item.nombre}</h3>
        </div>
        <ReportAvailabilityBadge implementado={item.implementado} disponible={item.disponible} />
      </div>
      <p className="mt-3 text-sm leading-6 text-[#5f6764]">{item.descripcion}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {item.formatos_soportados.map((formato) => (
          <span key={formato} className="rounded-full border border-[#d8c5a7] bg-[#fffaf1] px-3 py-1 text-[11px] font-black text-[#5f4525]">
            {formato}
          </span>
        ))}
      </div>
      {item.nota ? <p className="mt-4 text-xs font-semibold text-[#7b837f]">{item.nota}</p> : null}
      {item.motivo_no_disponible ? <p className="mt-2 text-xs font-black text-[#8c1239]">{item.motivo_no_disponible}</p> : null}
    </article>
  );
}
