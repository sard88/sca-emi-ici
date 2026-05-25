import { clsx } from "clsx";
import type { ButtonHTMLAttributes } from "react";

export function Button({ className, type = "button", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type={type}
      className={clsx(
        "inline-flex items-center justify-center rounded-xl bg-guinda px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-guinda-accent disabled:cursor-not-allowed disabled:opacity-60",
        className,
      )}
      {...props}
    />
  );
}
