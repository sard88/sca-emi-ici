"use client";

import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/states/EmptyState";
import { useAuth } from "@/lib/auth";

export default function DiscenteHistorialAcademicoPage() {
  const { user } = useAuth();

  return (
    <AppShell>
      {!user ? null : (
        <div className="space-y-5">
          <PageHeader title="Mi historial académico" description="Consulta informativa de tu trayectoria académica." user={user} />

          <section className="grid gap-4 md:grid-cols-2">
            <HistorySection title="Resultados oficiales" />
            <HistorySection title="Eventos académicos" />
            <HistorySection title="Extraordinarios" />
            <HistorySection title="Movimientos académicos" />
          </section>
        </div>
      )}
    </AppShell>
  );
}

function HistorySection({ title }: { title: string }) {
  return (
    <section className="rounded-[1.35rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
      <h2 className="text-base font-black text-[#101b18]">{title}</h2>
      <div className="mt-3">
        <EmptyState title="Sin información disponible." description="Sin registros por ahora." compact />
      </div>
    </section>
  );
}
