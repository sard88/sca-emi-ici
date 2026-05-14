import type { ReporteTrayectoriaConfig } from "@/lib/types";

export function InternalHistoryDiscenteSelector({
  config,
  discenteId,
}: {
  config: ReporteTrayectoriaConfig;
  discenteId: string;
}) {
  if (!config.requiereDiscenteId) return null;

  return (
    <section className="rounded-[1.5rem] border border-[#d8c5a7] bg-[#fff7e8] p-4 text-sm leading-6 text-[#5f4525] shadow-sm">
      <p className="font-black text-[#7b4c0c]">Discente requerido</p>
      <p className="mt-1">
        Captura un ID interno de discente para consultar o descargar este historial. No uses matrícula militar ni nombres como identificador principal.
      </p>
      {!discenteId ? (
        <p className="mt-2 font-black text-[#7a123d]">
          Captura un ID de discente válido para consultar el historial interno por discente.
        </p>
      ) : null}
    </section>
  );
}
