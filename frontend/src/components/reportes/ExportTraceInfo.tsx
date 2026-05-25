import type { DownloadResult } from "@/lib/types";

export function ExportTraceInfo({ result }: { result: DownloadResult | null }) {
  if (!result) return null;

  return (
    <div className="rounded-2xl border border-[#b7d9c9] bg-[#edf8f2] px-4 py-3 text-sm text-[#0b4a3d]">
      <p className="font-black">Documento generado correctamente.</p>
      <p className="mt-1 font-medium">
        Archivo: <span className="font-black">{result.filename}</span>
        {result.registroExportacionId ? (
          <>
            {" "}
            · Folio técnico de auditoría: <span className="font-black">#{result.registroExportacionId}</span>
          </>
        ) : null}
      </p>
    </div>
  );
}
