import { clsx } from "clsx";
import type { InputHTMLAttributes } from "react";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={clsx(
        "w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-carbon outline-none transition placeholder:text-gray-400 focus:border-guinda focus:ring-4 focus:ring-guinda/10",
        className,
      )}
      {...props}
    />
  );
}
