import { clsx } from "clsx";

const toneByState: Record<string, string> = {
  BORRADOR_DOCENTE: "border-[#d8c5a7] bg-[#fffaf1] text-[#7a4b0d]",
  PUBLICADO_DISCENTE: "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
  REMITIDO_JEFATURA_CARRERA: "border-[#e4c777] bg-[#fff7d6] text-[#795400]",
  VALIDADO_JEFATURA_CARRERA: "border-[#b6d5eb] bg-[#eef7ff] text-[#1d4d71]",
  FORMALIZADO_JEFATURA_ACADEMICA: "border-[#b7d9c9] bg-[#e8f7ef] text-[#064e3b]",
  ARCHIVADO: "border-[#d9d5cf] bg-[#f4f1eb] text-[#5f6764]",
};

export function ActaStatusBadge({ estado, label }: { estado: string; label?: string }) {
  return (
    <span className={clsx("inline-flex rounded-full border px-3 py-1 text-xs font-black", toneByState[estado] ?? "border-[#eadfce] bg-white text-[#46534e]")}>
      {label || estado}
    </span>
  );
}

export function ActaReadonlyNotice({ visible, message }: { visible?: boolean; message?: string }) {
  if (!visible) return null;
  return (
    <div className="rounded-2xl border border-[#d8c5a7] bg-[#fffaf1] px-4 py-3 text-sm font-bold text-[#6f4a16]">
      {message || "Esta acta está en modo solo lectura. No se permiten cambios desde el portal."}
    </div>
  );
}

export function ActaOfficialNotice({ oficial }: { oficial?: boolean }) {
  return (
    <div className={clsx("rounded-2xl border px-4 py-3 text-sm font-bold", oficial ? "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]" : "border-[#e7c1c8] bg-[#fff5f7] text-[#7a123d]")}>
      {oficial ? "Acta formalizada: información oficial protegida." : "Documento operativo no oficial hasta su formalización."}
    </div>
  );
}
