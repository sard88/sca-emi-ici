import type { ReactNode } from "react";
import { clsx } from "clsx";

export function StatusBadge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "success" | "warning" }) {
  return (
    <span
      className={clsx(
        "inline-flex rounded-full px-3 py-1 text-xs font-semibold",
        tone === "success" && "bg-militar/10 text-militar",
        tone === "warning" && "bg-oro/20 text-militar-olive",
        tone === "neutral" && "bg-gray-100 text-gray-700",
      )}
    >
      {children}
    </span>
  );
}
