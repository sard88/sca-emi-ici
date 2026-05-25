"use client";

import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { PerformanceReportCard } from "@/components/reportes/desempeno/PerformanceReportCard";
import { reportesDesempenoParaUsuario } from "@/lib/reportes-desempeno";
import { canAccessReportesDesempeno } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";

export default function ReportesDesempenoIndexPage() {
  const { user } = useAuth();
  const reportes = user ? reportesDesempenoParaUsuario(user) : [];

  return (
    <AppShell>
      {!user ? null : !canAccessReportesDesempeno(user) ? (
        <ErrorMessage message="No tienes permiso para consultar reportes de desempeño desde el portal." />
      ) : (
        <div className="space-y-5">
          <PageHeader
            title="Reportes de desempeño académico"
            description="Consulta indicadores académicos según los resultados disponibles."
            user={user}
          />

          <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-6 text-white shadow-institutional">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-[#d4af37]">Reporte institucional</p>
            <h2 className="mt-3 text-3xl font-black">Desempeño y aprovechamiento académico</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-white/84">
              Consulta reportes disponibles según tu perfil autorizado.
            </p>
          </section>

          <section className="grid gap-4 xl:grid-cols-2 2xl:grid-cols-3">
            {reportes.map((config) => (
              <PerformanceReportCard key={config.slug} config={config} />
            ))}
          </section>
        </div>
      )}
    </AppShell>
  );
}
