"use client";

import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { OperativeReportCard } from "@/components/reportes/operativos/OperativeReportCard";
import { reportesOperativosParaUsuario } from "@/lib/reportes-operativos";
import { canAccessReportesOperativos } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";

export default function ReportesOperativosIndexPage() {
  const { user } = useAuth();
  const reportes = user ? reportesOperativosParaUsuario(user) : [];

  return (
    <AppShell>
      {!user ? null : !canAccessReportesOperativos(user) ? (
        <ErrorMessage message="No tienes permiso para consultar reportes operativos desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader
            title="Reportes operativos"
            description="Vista previa y descarga XLSX de actas, validaciones y exportaciones realizadas. El backend valida permisos y registra auditoría."
            user={user}
          />

          <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-6 text-white shadow-institutional">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-[#d4af37]">Bloque 10C-3A</p>
            <h2 className="mt-3 text-3xl font-black">Integración visual de reportes operativos</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-white/84">
              Estos reportes se calculan en Django y se descargan como XLSX auditado. El portal solo muestra información autorizada y dispara la descarga.
            </p>
          </section>

          <section className="grid gap-4 xl:grid-cols-2">
            {reportes.map((config) => (
              <OperativeReportCard key={config.slug} config={config} />
            ))}
          </section>
        </div>
      )}
    </AppShell>
  );
}
