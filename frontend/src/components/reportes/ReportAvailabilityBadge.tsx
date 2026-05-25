import { clsx } from "clsx";

export function ReportAvailabilityBadge({ implementado, disponible }: { implementado: boolean; disponible: boolean }) {
  const label = !implementado ? "Pendiente" : disponible ? "Disponible" : "Sin permiso";
  return (
    <span
      className={clsx(
        "rounded-full border px-3 py-1 text-[11px] font-black uppercase tracking-[0.12em]",
        !implementado && "border-[#d8c5a7] bg-[#fff7e8] text-[#9f6a22]",
        implementado && disponible && "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
        implementado && !disponible && "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]",
      )}
    >
      {label}
    </span>
  );
}
