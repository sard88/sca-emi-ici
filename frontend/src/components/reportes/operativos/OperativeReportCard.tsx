import Link from "next/link";
import type { ReporteOperativoConfig } from "@/lib/types";
import { OperativeReportBadge } from "./OperativeReportBadge";

export function OperativeReportCard({ config }: { config: ReporteOperativoConfig }) {
  return (
    <article className="group rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-[#bc955c]">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-[11px] font-black uppercase tracking-[0.18em] text-[#9f6a22]">{config.tipoDocumento.replaceAll("_", " ")}</p>
          <h3 className="mt-2 text-lg font-black text-[#152b25]">{config.titulo}</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          <OperativeReportBadge label="XLSX disponible" />
          <OperativeReportBadge label="PDF pendiente" tone="dorado" />
        </div>
      </div>
      <p className="mt-3 text-sm leading-6 text-[#5f6764]">{config.descripcion}</p>
      <p className="mt-3 text-xs font-bold leading-5 text-[#7b837f]">{config.ayuda}</p>
      <div className="mt-5 flex flex-wrap gap-3">
        <Link
          href={config.ruta}
          className="rounded-xl bg-[#7a123d] px-4 py-2 text-xs font-black text-white shadow-sm transition hover:bg-[#5f0f30]"
        >
          Ver reporte
        </Link>
        <span className="rounded-xl border border-[#d8c5a7] bg-white px-4 py-2 text-xs font-black text-[#7a123d]">
          Descarga XLSX dentro de la vista
        </span>
      </div>
    </article>
  );
}
