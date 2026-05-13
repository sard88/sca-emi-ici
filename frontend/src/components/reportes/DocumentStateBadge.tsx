import { clsx } from "clsx";

export function DocumentStateBadge({ oficial, estado }: { oficial: boolean; estado: string }) {
  return (
    <span
      className={clsx(
        "rounded-full border px-3 py-1 text-[11px] font-black uppercase tracking-[0.12em]",
        oficial ? "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]" : "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]",
      )}
    >
      {oficial ? "Oficial" : estado || "No oficial"}
    </span>
  );
}
