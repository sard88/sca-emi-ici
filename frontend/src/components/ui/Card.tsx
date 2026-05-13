import type { ReactNode } from "react";
import { clsx } from "clsx";

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return <section className={clsx("rounded-3xl border border-black/5 bg-white/90 p-6 shadow-institutional", className)}>{children}</section>;
}
