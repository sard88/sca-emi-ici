import { clsx } from "clsx";

export function ExportStatusBadge({ estado, label }: { estado: string; label?: string }) {
  const normalized = estado.toUpperCase();
  return (
    <span
      className={clsx(
        "rounded-full border px-3 py-1 text-[11px] font-black uppercase tracking-[0.12em]",
        normalized === "GENERADA" && "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
        normalized === "FALLIDA" && "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]",
        normalized !== "GENERADA" && normalized !== "FALLIDA" && "border-[#d8c5a7] bg-[#fff7e8] text-[#9f6a22]",
      )}
    >
      {label || estado}
    </span>
  );
}
