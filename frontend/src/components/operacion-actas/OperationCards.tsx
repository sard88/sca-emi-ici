import Link from "next/link";
import type { ActaResumen, DocenteAsignacion } from "@/lib/types";
import { ActaStatusBadge } from "./ActaStatusBadge";

export function TeacherAssignmentCard({ asignacion }: { asignacion: DocenteAsignacion }) {
  const cortes = ["P1", "P2", "P3", "FINAL"];
  return (
    <article className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-5 shadow-sm">
      <p className="text-xs font-black uppercase tracking-[0.18em] text-[#b46c13]">{asignacion.periodo?.label || "Periodo"}</p>
      <h3 className="mt-2 text-xl font-black text-[#101b18]">{asignacion.materia?.nombre || asignacion.programa_asignatura?.label}</h3>
      <p className="mt-1 text-sm text-[#5f6764]">{asignacion.grupo?.label} · {asignacion.carrera?.nombre} · {asignacion.num_discentes ?? 0} discentes</p>
      <p className="mt-3 rounded-2xl bg-[#fffaf1] px-3 py-2 text-xs font-bold text-[#6f4a16]">{asignacion.estado_operativo}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link className="rounded-xl bg-[#7a123d] px-4 py-2 text-sm font-black text-white" href={`/docente/asignaciones/${asignacion.asignacion_id}`}>
          Ver detalle
        </Link>
        <Link className="rounded-xl bg-[#0b4a3d] px-4 py-2 text-sm font-black text-white" href={`/docente/asignaciones/${asignacion.asignacion_id}/resumen`}>
          Resumen
        </Link>
        {cortes.map((corte) => (
          <Link key={corte} className="rounded-xl border border-[#d8c5a7] px-3 py-2 text-sm font-black text-[#6f4a16]" href={`/docente/asignaciones/${asignacion.asignacion_id}/captura/${corte}`}>
            Capturar {corte}
          </Link>
        ))}
      </div>
    </article>
  );
}

export function ActaListCard({ acta, href }: { acta: ActaResumen; href: string }) {
  return (
    <article className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.18em] text-[#b46c13]">Acta #{acta.acta_id} · {acta.corte_label}</p>
          <h3 className="mt-2 text-xl font-black text-[#101b18]">{acta.materia?.nombre || acta.programa_asignatura?.label}</h3>
          <p className="mt-1 text-sm text-[#5f6764]">{acta.grupo?.label} · {acta.periodo?.label} · {acta.docente?.nombre_institucional || acta.docente?.nombre}</p>
        </div>
        <ActaStatusBadge estado={acta.estado_acta} label={acta.estado_acta_label} />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link className="rounded-xl bg-[#7a123d] px-4 py-2 text-sm font-black text-white" href={href}>
          Ver acta
        </Link>
        {acta.es_documento_oficial ? <span className="rounded-xl bg-[#edf8f2] px-3 py-2 text-xs font-black text-[#0b4a3d]">Documento oficial</span> : null}
      </div>
    </article>
  );
}
