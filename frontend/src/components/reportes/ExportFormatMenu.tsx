"use client";

import type { DownloadResult } from "@/lib/types";
import { ExportActionButton } from "./ExportActionButton";

export function ExportFormatMenu({
  pdfAction,
  xlsxAction,
  canPdf,
  canXlsx,
  onDone,
  onError,
}: {
  pdfAction: () => Promise<DownloadResult>;
  xlsxAction: () => Promise<DownloadResult>;
  canPdf: boolean;
  canXlsx: boolean;
  onDone?: (result: DownloadResult) => void;
  onError?: (message: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <ExportActionButton label="Exportar PDF" onExport={pdfAction} onDone={onDone} onError={onError} disabled={!canPdf} />
      <ExportActionButton label="Exportar Excel" onExport={xlsxAction} onDone={onDone} onError={onError} disabled={!canXlsx} />
    </div>
  );
}
