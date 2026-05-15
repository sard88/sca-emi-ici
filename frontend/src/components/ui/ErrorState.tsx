"use client";

import Link from "next/link";
import { clsx } from "clsx";
import { microcopy } from "@/lib/microcopy";
import { Icon } from "./icons";

export type ErrorStateVariant = "error" | "forbidden" | "validation" | "network" | "notFound";

type ErrorStateProps = {
  title?: string;
  description?: string;
  details?: string;
  retry?: () => void;
  backHref?: string;
  variant?: ErrorStateVariant;
  compact?: boolean;
};

const variantCopy: Record<ErrorStateVariant, { title: string; description: string }> = {
  error: { title: "No fue posible completar la solicitud", description: microcopy.errors.unexpected },
  forbidden: { title: "Acceso restringido", description: `${microcopy.errors.forbidden} ${microcopy.accessDenied.help}` },
  validation: { title: "Información por revisar", description: microcopy.errors.validation },
  network: { title: "Sin conexión con el servidor", description: microcopy.errors.network },
  notFound: { title: "Registro no encontrado", description: microcopy.errors.notFound },
};

const toneByVariant: Record<ErrorStateVariant, string> = {
  error: "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]",
  forbidden: "border-[#d4af37]/40 bg-[#fff8e6] text-[#72530d]",
  validation: "border-[#d4af37]/40 bg-[#fff8e6] text-[#72530d]",
  network: "border-[#b6d5eb] bg-[#eef7ff] text-[#1d4d71]",
  notFound: "border-[#d8c5a7] bg-[#fffaf1] text-[#6f4a16]",
};

export function ErrorState({ title, description, details, retry, backHref, variant = "error", compact = false }: ErrorStateProps) {
  const copy = variantCopy[variant];
  return (
    <section className={clsx("rounded-[1.5rem] border px-4 py-3 shadow-sm", toneByVariant[variant], compact ? "text-sm" : "p-5")}>
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white/70">
          <Icon name={variant === "forbidden" ? "blocked" : variant === "notFound" ? "search" : "warning"} className="h-5 w-5" />
        </span>
        <div className="min-w-0">
          <h3 className="font-black">{title || copy.title}</h3>
          <p className="mt-1 text-sm leading-6">{description || copy.description}</p>
          {details ? <p className="mt-2 break-words rounded-xl bg-white/65 px-3 py-2 text-xs font-bold">{details}</p> : null}
          {retry || backHref ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {retry ? <button type="button" className="rounded-xl bg-[#7a123d] px-4 py-2 text-sm font-black text-white" onClick={retry}>Intentar nuevamente</button> : null}
              {backHref ? <Link className="rounded-xl border border-[#d8c5a7] bg-white/70 px-4 py-2 text-sm font-black text-[#6f4a16]" href={backHref}>Volver</Link> : null}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
