"use client";

import type { ActaExportable, DownloadResult } from "@/lib/types";
import {
  descargarActaPdf,
  descargarActaXlsx,
  descargarCalificacionFinalPdf,
  descargarCalificacionFinalXlsx,
} from "@/lib/api";
import { DocumentStateBadge } from "./DocumentStateBadge";
import { ExportFormatMenu } from "./ExportFormatMenu";

export function ActaExportCard({
  acta,
  onDownloaded,
  onError,
  showCalificacionFinal = true,
}: {
  acta: ActaExportable;
  onDownloaded?: (result: DownloadResult) => void;
  onError?: (message: string) => void;
  showCalificacionFinal?: boolean;
}) {
  return (
    <article className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <p className="text-[11px] font-black uppercase tracking-[0.18em] text-[#9f6a22]">
            {acta.carrera_clave} · {acta.periodo} · Grupo {acta.grupo}
          </p>
          <h3 className="mt-2 text-xl font-black text-[#152b25]">{acta.programa_asignatura}</h3>
          <p className="mt-1 text-sm font-semibold text-[#5f6764]">Docente: {acta.docente}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <DocumentStateBadge oficial={acta.es_documento_oficial} estado={acta.estado_documental} />
          <span className="rounded-full border border-[#d8c5a7] bg-[#fffaf1] px-3 py-1 text-[11px] font-black uppercase tracking-[0.12em] text-[#5f4525]">
            {acta.corte_nombre}
          </span>
        </div>
      </div>

      <dl className="mt-5 grid gap-3 sm:grid-cols-3">
        <Info label="Estado" value={acta.estado_acta_label} />
        <Info label="Carrera" value={acta.carrera} />
        <Info label="Formalización" value={formatDate(acta.fecha_formalizacion)} />
      </dl>

      {!acta.es_documento_oficial ? (
        <p className="mt-4 rounded-2xl border border-[#efc3c7] bg-[#fff1f2] px-4 py-3 text-xs font-bold text-[#8c1239]">
          Esta acta se exportará con marca visible de documento no oficial.
        </p>
      ) : null}

      <div className="mt-5 space-y-4">
        <div>
          <p className="mb-2 text-xs font-black uppercase tracking-[0.14em] text-[#9f6a22]">Acta del corte</p>
          <ExportFormatMenu
            pdfAction={() => descargarActaPdf(acta.acta_id)}
            xlsxAction={() => descargarActaXlsx(acta.acta_id)}
            canPdf={acta.puede_exportar_pdf}
            canXlsx={acta.puede_exportar_xlsx}
            onDone={onDownloaded}
            onError={onError}
          />
        </div>

        {showCalificacionFinal && acta.calificacion_final_disponible ? (
          <div>
            <p className="mb-2 text-xs font-black uppercase tracking-[0.14em] text-[#9f6a22]">Calificación final consolidada</p>
            <ExportFormatMenu
              pdfAction={() => descargarCalificacionFinalPdf(acta.asignacion_docente_id)}
              xlsxAction={() => descargarCalificacionFinalXlsx(acta.asignacion_docente_id)}
              canPdf
              canXlsx
              onDone={onDownloaded}
              onError={onError}
            />
          </div>
        ) : null}
      </div>
    </article>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[#eadfce] bg-[#fffaf1] p-3">
      <dt className="text-[10px] font-black uppercase tracking-[0.14em] text-[#9f6a22]">{label}</dt>
      <dd className="mt-1 text-xs font-black text-[#152b25]">{value}</dd>
    </div>
  );
}

function formatDate(value: string | null) {
  if (!value) return "Pendiente";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium" }).format(new Date(value));
}
