import type { ReporteOperativoRespuesta } from "@/lib/types";
import { OperativeReportBadge } from "./OperativeReportBadge";

export function OperativeReportSummaryBar({ data }: { data: ReporteOperativoRespuesta | null }) {
  if (!data) return null;

  return (
    <section className="grid gap-3 md:grid-cols-3">
      <div className="rounded-[1.25rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
        <p className="text-xs font-black uppercase tracking-[0.14em] text-[#9f6a22]">Registros</p>
        <p className="mt-2 text-3xl font-black text-[#10372e]">{data.total}</p>
      </div>
      <div className="rounded-[1.25rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
        <p className="text-xs font-black uppercase tracking-[0.14em] text-[#9f6a22]">Columnas</p>
        <p className="mt-2 text-3xl font-black text-[#10372e]">{data.columnas.length}</p>
      </div>
      <div className="rounded-[1.25rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
        <p className="text-xs font-black uppercase tracking-[0.14em] text-[#9f6a22]">Disponibilidad</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <OperativeReportBadge label="Vista previa JSON" />
          <OperativeReportBadge label="XLSX auditado" tone="dorado" />
        </div>
      </div>
    </section>
  );
}
