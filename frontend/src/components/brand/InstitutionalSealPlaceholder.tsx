import { clsx } from "clsx";

export function InstitutionalSealPlaceholder({ label, className }: { label: string; className?: string }) {
  return (
    <div
      aria-label={label}
      className={clsx(
        "flex aspect-square h-12 items-center justify-center rounded-full border border-oro/40 bg-gradient-to-br from-marfil to-white text-xs font-black tracking-widest text-guinda shadow-sm",
        className,
      )}
    >
      {label.slice(0, 6)}
    </div>
  );
}
