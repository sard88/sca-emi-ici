"use client";

import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { useAuth } from "@/lib/auth";
import { canAccessReportesTrayectoria } from "@/lib/dashboard";
import { reportesTrayectoriaParaUsuario } from "@/lib/reportes-trayectoria";
import { TrajectoryReportCard } from "./TrajectoryReportCard";

export function TrajectoryReportsIndex() {
  const { user } = useAuth();
  const reportes = user ? reportesTrayectoriaParaUsuario(user) : [];

  return (
    <AppShell>
      {!user ? null : !canAccessReportesTrayectoria(user) ? (
        <ErrorMessage message="No tienes permiso para consultar reportes de trayectoria desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader
            title="Reportes de trayectoria y situación académica"
            description="Vista previa y descarga XLSX de situación académica, movimientos e historial interno. El portal consume APIs Django y no modifica datos."
            user={user}
          />

          <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-6 text-white shadow-institutional">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-[#d4af37]">Bloque 10C-3C</p>
            <h2 className="mt-3 text-3xl font-black">Trayectoria, situación académica e historial interno</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-white/84">
              Los reportes se generan en backend desde el Bloque 9I-M-E. El formato disponible es XLSX auditado; PDF, kárdex Excel, importación y bitácora transversal quedan pendientes.
            </p>
          </section>

          <section className="grid gap-4 xl:grid-cols-2">
            {reportes.map((config) => (
              <TrajectoryReportCard key={config.slug} config={config} />
            ))}
          </section>
        </div>
      )}
    </AppShell>
  );
}
