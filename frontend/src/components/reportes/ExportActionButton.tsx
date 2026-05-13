"use client";

import { useState } from "react";
import type { DownloadResult } from "@/lib/types";

export function ExportActionButton({
  label,
  onExport,
  onDone,
  onError,
  disabled = false,
}: {
  label: string;
  onExport: () => Promise<DownloadResult>;
  onDone?: (result: DownloadResult) => void;
  onError?: (message: string) => void;
  disabled?: boolean;
}) {
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    try {
      const result = await onExport();
      onDone?.(result);
    } catch (err) {
      onError?.(err instanceof Error ? err.message : "La exportación falló. Intenta nuevamente o contacta soporte.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || loading}
      className="rounded-xl border border-[#d8c5a7] bg-white px-4 py-2 text-xs font-black text-[#7a123d] shadow-sm transition hover:border-[#bc955c] hover:bg-[#fff7e8] disabled:cursor-not-allowed disabled:opacity-55"
    >
      {loading ? "Generando..." : label}
    </button>
  );
}
