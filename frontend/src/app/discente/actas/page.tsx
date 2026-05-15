"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { ProcessStateBadge, SensitiveTraceNotice } from "@/components/trazabilidad";
import { getDiscenteActas } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDiscenteActas } from "@/lib/dashboard";

type StudentActaItem = Record<string, unknown> & { acta_id: number; detalle_id: number };

export default function DiscenteActasPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<StudentActaItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        setItems((await getDiscenteActas()).items as StudentActaItem[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar tus actas.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessDiscenteActas(user)) void load();
  }, [user]);

  return (
    <AppShell>
      {!user ? null : !canAccessDiscenteActas(user) ? (
        <ErrorMessage message="No tienes permiso para consultar actas de discente." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Mis actas publicadas" description="Consulta tus resultados publicados y registra acuse, conformidad o inconformidad informativa." user={user} />
          <SensitiveTraceNotice text="Después de la remisión, la conformidad queda en solo lectura. Solo se muestran tus propios detalles." tone="info" />
          {loading ? <LoadingState label="Cargando actas publicadas..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyState title="No tienes actas publicadas." description="Las actas aparecerán cuando el docente las publique." /> : null}
          <section className="grid gap-4 xl:grid-cols-2">
            {items.map((item) => (
              <article key={item.detalle_id} className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-5 shadow-sm">
                <p className="text-xs font-black uppercase tracking-[0.18em] text-[#b46c13]">Acta #{item.acta_id} · {String(item.corte_label || item.corte_codigo || "")}</p>
                <h3 className="mt-2 text-xl font-black text-[#101b18]">{String(item.asignatura || "Asignatura")}</h3>
                <p className="mt-1 text-sm text-[#5f6764]">Resultado visible: {String(item.resultado_visible ?? "N/A")} · {String(item.estado_acta_label || "")}</p>
                <p className="mt-2 text-sm font-bold text-[#0b4a3d]">Conformidad: {String((item.conformidad_vigente as { estado_conformidad_label?: string } | null)?.estado_conformidad_label || "Sin registro")}</p>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <ProcessStateBadge state="PUBLICADO_DISCENTE" label="Publicada" />
                  <span className="text-xs font-black text-[#b8a17b]">→</span>
                  <ProcessStateBadge state={(item.conformidad_vigente as { estado_conformidad?: string } | null)?.estado_conformidad || "ADVERTENCIA"} label={String((item.conformidad_vigente as { estado_conformidad_label?: string } | null)?.estado_conformidad_label || "Conformidad pendiente")} />
                  <span className="text-xs font-black text-[#b8a17b]">→</span>
                  <ProcessStateBadge state={String(item.estado_acta || "")} label={String(item.estado_acta_label || "Estado del acta")} />
                </div>
                <Link className="mt-4 inline-flex rounded-xl bg-[#7a123d] px-4 py-2 text-sm font-black text-white" href={`/discente/actas/${item.detalle_id}`}>
                  Revisar acta
                </Link>
              </article>
            ))}
          </section>
        </div>
      )}
    </AppShell>
  );
}
