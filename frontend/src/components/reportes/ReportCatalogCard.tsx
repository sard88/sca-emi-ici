import type { ReporteCatalogoItem } from "@/lib/types";
import { ReportAvailabilityBadge } from "./ReportAvailabilityBadge";
import Link from "next/link";

export function ReportCatalogCard({ item, actionHref, actionLabel = "Abrir módulo" }: { item: ReporteCatalogoItem; actionHref?: string; actionLabel?: string }) {
  const safeDescription = sanitizeTechnicalText(item.descripcion);
  const safeNote = item.nota ? sanitizeTechnicalText(item.nota) : null;
  const safeReason = item.motivo_no_disponible ? sanitizeTechnicalText(item.motivo_no_disponible) : null;

  return (
    <article className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-[11px] font-black uppercase tracking-[0.18em] text-[#9f6a22]">{item.codigo.replaceAll("_", " ")}</p>
          <h3 className="mt-2 text-lg font-black text-[#152b25]">{item.nombre}</h3>
        </div>
        <ReportAvailabilityBadge implementado={item.implementado} disponible={item.disponible} />
      </div>
      <p className="mt-3 text-sm leading-6 text-[#5f6764]">{safeDescription}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {item.formatos_soportados.map((formato) => (
          <span key={formato} className="rounded-full border border-[#d8c5a7] bg-[#fffaf1] px-3 py-1 text-[11px] font-black text-[#5f4525]">
            {formato}
          </span>
        ))}
      </div>
      {safeNote ? <p className="mt-4 text-xs font-semibold text-[#7b837f]">{safeNote}</p> : null}
      {safeReason ? <p className="mt-2 text-xs font-black text-[#8c1239]">{safeReason}</p> : null}
      {actionHref && item.implementado && item.disponible ? (
        <Link href={actionHref} className="mt-4 inline-flex rounded-xl border border-[#d8c5a7] px-4 py-2 text-xs font-black text-[#7a123d] transition hover:border-[#bc955c] hover:bg-[#fff7e8]">
          {actionLabel}
        </Link>
      ) : null}
    </article>
  );
}

function sanitizeTechnicalText(text: string) {
  const source = (text || "").trim();
  const lower = source.toLowerCase();
  const isTechnical =
    lower.includes("bloque 9") ||
    lower.includes("bloque 10") ||
    lower.includes("xlsx implementado") ||
    lower.includes("pdf implementado") ||
    lower.includes("pdf queda pendiente") ||
    lower.includes("xlsx queda pendiente") ||
    lower.includes("serviciokardex") ||
    lower.includes("familia de endpoints") ||
    lower.includes("endpoints xlsx") ||
    lower.includes("documento interno") ||
    lower.includes("no sustituye kárdex oficial") ||
    lower.includes("no visible ni exportable") ||
    lower.includes("subbloques posteriores") ||
    lower.includes("backend") ||
    lower.includes("django") ||
    lower.includes("api") ||
    lower.includes("payload") ||
    lower.includes("fuente de verdad") ||
    lower.includes("trazabilidad técnica") ||
    lower.includes("auditoría técnica") ||
    lower.includes("ids internos");

  if (!isTechnical) return source;

  if (lower.includes("trayectoria") || lower.includes("situación") || lower.includes("situacion")) {
    return "Consulta información académica disponible según tu ámbito.";
  }
  if (lower.includes("kárdex") || lower.includes("kardex") || lower.includes("documento")) {
    return "Consulta documentos académicos disponibles según tu perfil autorizado.";
  }
  if (lower.includes("acta")) {
    return "Consulta las actas disponibles según tu ámbito académico.";
  }
  if (lower.includes("export")) {
    return "Los documentos disponibles corresponden a la información académica registrada.";
  }
  return "Consulta reportes disponibles según tu perfil autorizado.";
}
