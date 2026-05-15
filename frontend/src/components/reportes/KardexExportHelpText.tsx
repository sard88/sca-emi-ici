import { microcopy } from "@/lib/microcopy";

export function KardexExportHelpText() {
  return (
    <section className="rounded-[1.5rem] border border-[#d8c5a7] bg-[#fffaf1] p-5 text-sm leading-6 text-[#5f4525] shadow-sm">
      <p className="font-black text-[#7a123d]">Uso institucional del kárdex oficial</p>
      <p className="mt-2">
        El PDF se genera desde el servicio institucional de kárdex y queda auditado como salida documental.
        El portal solo permite seleccionar discentes autorizados y disparar la descarga.
      </p>
      <p className="mt-2 font-semibold">
        {microcopy.kardex.oficial} La versión Excel queda pendiente para un bloque posterior.
      </p>
    </section>
  );
}
