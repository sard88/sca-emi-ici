import type { ReporteDesempenoConfig } from "@/lib/types";

export function PerformanceReportPrivacyNotice({ config }: { config: ReporteDesempenoConfig }) {
  if (!config.nominal && !config.datosSensibles) return null;

  return (
    <section className="rounded-[1.5rem] border border-[#e7c3ce] bg-[#fff7f9] p-4 text-sm leading-6 text-[#5f0f30] shadow-sm">
      <p className="font-black text-[#7a123d]">Reporte nominal restringido</p>
      <p className="mt-1">{config.privacidad ?? "Este reporte contiene información nominal y solo debe consultarse por personal autorizado."}</p>
    </section>
  );
}
