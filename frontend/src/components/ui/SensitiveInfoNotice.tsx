import { clsx } from "clsx";
import { microcopy } from "@/lib/microcopy";
import { Icon } from "./icons";

export function SensitiveInfoNotice({ text = microcopy.sensitive.academic, compact = false }: { text?: string; compact?: boolean }) {
  return (
    <div className={clsx("rounded-2xl border border-[#d4af37]/35 bg-[#fff8e6] font-bold text-[#72530d]", compact ? "px-3 py-2 text-xs" : "px-4 py-3 text-sm")}>
      <div className="flex items-start gap-2">
        <Icon name="warning" className="mt-0.5 h-4 w-4 shrink-0" />
        <span>{text}</span>
      </div>
    </div>
  );
}
