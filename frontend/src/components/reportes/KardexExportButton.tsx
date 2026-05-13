"use client";

import { ExportActionButton } from "./ExportActionButton";
import type { DownloadResult } from "@/lib/types";

export function KardexExportButton({
  onExport,
  onDone,
  onError,
  disabled = false,
}: {
  onExport: () => Promise<DownloadResult>;
  onDone?: (result: DownloadResult) => void;
  onError?: (message: string) => void;
  disabled?: boolean;
}) {
  return (
    <ExportActionButton
      label="Exportar kárdex PDF"
      onExport={onExport}
      onDone={onDone}
      onError={onError}
      disabled={disabled}
    />
  );
}
