"use client";

import type { DownloadResult, KardexExportable } from "@/lib/types";
import { descargarKardexPdf } from "@/lib/api";
import { KardexExportButton } from "./KardexExportButton";

export function KardexExportCard({
  item,
  onDownloaded,
  onError,
}: {
  item: KardexExportable;
  onDownloaded?: (result: DownloadResult) => void;
  onError?: (message: string) => void;
}) {
  return (
    <article className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <p className="text-[11px] font-black uppercase tracking-[0.18em] text-[#9f6a22]">
            {item.carrera.clave} · Discente #{item.discente_id}
          </p>
          <h3 className="mt-2 text-xl font-black text-[#152b25]">{item.nombre_completo}</h3>
          <p className="mt-1 text-sm font-semibold text-[#5f6764]">
            {item.grado_empleo ? `${item.grado_empleo} · ` : ""}
            {item.carrera.nombre}
          </p>
        </div>
        <span className="w-fit rounded-full border border-[#b7d9c9] bg-[#edf8f2] px-3 py-1 text-[11px] font-black uppercase tracking-[0.12em] text-[#0b4a3d]">
          PDF disponible
        </span>
      </div>

      <dl className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Info label="Plan de estudios" value={item.plan_estudios} />
        <Info label="Antigüedad" value={item.antiguedad} />
        <Info label="Grupo vigente" value={item.grupo_actual || "Sin grupo vigente"} />
        <Info label="Situación" value={item.situacion_actual} />
      </dl>

      {item.motivo_no_disponible ? (
        <p className="mt-4 rounded-2xl border border-[#efc3c7] bg-[#fff1f2] px-4 py-3 text-xs font-bold text-[#8c1239]">
          {item.motivo_no_disponible}
        </p>
      ) : null}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <KardexExportButton
          onExport={() => descargarKardexPdf(item.discente_id)}
          disabled={!item.puede_exportar_pdf}
          onDone={onDownloaded}
          onError={onError}
        />
        <span className="text-xs font-semibold text-[#6f7773]">
          La descarga queda registrada en auditoría documental.
        </span>
      </div>
    </article>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[#eadfce] bg-[#fffaf1] p-3">
      <dt className="text-[10px] font-black uppercase tracking-[0.14em] text-[#9f6a22]">{label}</dt>
      <dd className="mt-1 text-xs font-black text-[#152b25]">{value || "N/A"}</dd>
    </div>
  );
}
