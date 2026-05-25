import type { ReporteTrayectoriaConfig } from "@/lib/types";

export function TrajectoryReportPrivacyNotice({ config }: { config: ReporteTrayectoriaConfig }) {
  if (!config.nominal && !config.datosSensibles) return null;

  return (
    <section className="rounded-[1.5rem] border border-[#e7c3ce] bg-[#fff7f9] p-4 text-sm leading-6 text-[#5f0f30] shadow-sm">
      <p className="font-black text-[#7a123d]">Reporte académico sensible</p>
      <p className="mt-1">
        {config.privacidad ?? "Este reporte contiene información académica sensible y solo debe consultarse por personal autorizado."}
      </p>
      {config.slug.includes("historial-interno") ? (
        <p className="mt-2 font-black">El historial interno no es kárdex oficial.</p>
      ) : null}
    </section>
  );
}
