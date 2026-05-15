"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { clsx } from "clsx";
import { microcopy } from "@/lib/microcopy";
import { Icon, iconNames, type IconName } from "./icons";

export type EmptyStateVariant = "default" | "search" | "restricted" | "noData" | "pending" | "success";

type EmptyStateProps = {
  title?: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  onAction?: () => void;
  icon?: IconName | ReactNode;
  variant?: EmptyStateVariant;
  compact?: boolean;
};

const variantIcon: Record<EmptyStateVariant, IconName> = {
  default: "empty",
  search: "search",
  restricted: "blocked",
  noData: "empty",
  pending: "pending",
  success: "success",
};

const variantCopy: Record<EmptyStateVariant, { title: string; description: string }> = {
  default: { title: microcopy.empty.defaultTitle, description: microcopy.empty.defaultDescription },
  search: { title: microcopy.empty.noResultsTitle, description: microcopy.empty.noResultsDescription },
  restricted: { title: microcopy.accessDenied.title, description: `${microcopy.accessDenied.default} ${microcopy.accessDenied.help}` },
  noData: { title: microcopy.empty.noDataTitle, description: microcopy.empty.noDataDescription },
  pending: { title: microcopy.empty.pendingTitle, description: microcopy.empty.pendingDescription },
  success: { title: "Proceso completado", description: "No hay acciones pendientes en este momento." },
};

export function EmptyState({ title, description, actionLabel, actionHref, onAction, icon, variant = "default", compact = false }: EmptyStateProps) {
  const copy = variantCopy[variant];
  const iconName = isIconName(icon) ? icon : variantIcon[variant];
  const iconNode = isIconName(icon) || !icon ? <Icon name={iconName} className={compact ? "h-5 w-5" : "h-7 w-7"} /> : icon;
  const actionClass = "mt-4 inline-flex rounded-xl bg-[#7a123d] px-4 py-2 text-sm font-black text-white shadow-sm";

  return (
    <div className={clsx("rounded-[1.5rem] border border-dashed border-[#d8c5a7] bg-white/82 text-center shadow-sm", compact ? "p-4" : "p-8")}>
      <span className={clsx("mx-auto flex items-center justify-center rounded-2xl border border-[#dfc79f] bg-[#fffaf1] text-[#7a123d]", compact ? "h-10 w-10" : "h-14 w-14")}>
        {iconNode}
      </span>
      <h3 className={clsx("font-black text-[#101b18]", compact ? "mt-3 text-base" : "mt-4 text-lg")}>{title || copy.title}</h3>
      <p className={clsx("mx-auto mt-2 max-w-2xl text-[#5f6764]", compact ? "text-xs leading-5" : "text-sm leading-6")}>{description || copy.description}</p>
      {actionHref && actionLabel ? <Link className={actionClass} href={actionHref}>{actionLabel}</Link> : null}
      {!actionHref && onAction && actionLabel ? <button type="button" className={actionClass} onClick={onAction}>{actionLabel}</button> : null}
    </div>
  );
}

function isIconName(value: unknown): value is IconName {
  return typeof value === "string" && iconNames.includes(value as IconName);
}
