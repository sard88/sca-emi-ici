"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDiscenteCargaAcademica } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { DiscenteCargaAcademicaItem, DiscenteCargaAcademicaResponse } from "@/lib/types";

export default function DiscenteCargaAcademicaPage() {
  const { user } = useAuth();
  const [state, setState] = useState<{ loading: boolean; error: string | null; data: DiscenteCargaAcademicaResponse | null }>({
    loading: true,
    error: null,
    data: null,
  });

  useEffect(() => {
    if (!user) return;
    setState({ loading: true, error: null, data: null });
    getDiscenteCargaAcademica()
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => setState({ loading: false, error: error instanceof Error ? error.message : "No fue posible cargar tu carga académica.", data: null }));
  }, [user]);

  return (
    <AppShell>
      {!user ? null : (
        <div className="space-y-5">
          <PageHeader
            title="Mi carga académica"
            description="Asignaturas inscritas, grupo, docente y estado de actas visibles para tu perfil."
            user={user}
          />
          <p className="rounded-2xl border border-[#d4af37]/35 bg-[#fff8e6] px-4 py-3 text-sm font-bold text-[#72530d]">
            Esta vista muestra solo tus inscripciones. No sustituye al kárdex oficial ni expone matrícula militar.
          </p>
          {state.loading ? <LoadingState label="Cargando carga académica..." /> : null}
          {state.error ? <ErrorMessage message={state.error} /> : null}
          {!state.loading && !state.error && state.data?.items.length === 0 ? (
            <EmptyState title="Sin carga académica registrada" description="No hay inscripciones visibles para tu perfil en este momento." />
          ) : null}
          {!state.loading && !state.error && state.data && state.data.items.length > 0 ? (
            <>
              <section className="grid gap-3 md:grid-cols-3">
                <Metric label="Periodo actual" value={formatValue(state.data.periodo_actual)} />
                <Metric label="Asignaturas" value={String(state.data.total)} />
                <Metric label="Vista" value="Personal" />
              </section>
              <section className="overflow-hidden rounded-[1.5rem] border border-[#eadfce] bg-white/88 shadow-sm">
                <div className="border-b border-[#eadfce] px-4 py-3">
                  <h2 className="text-base font-black text-[#101b18]">Asignaturas inscritas</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="bg-[#0b4a3d] text-white">
                      <tr>
                        <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Asignatura</th>
                        <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Docente</th>
                        <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Grupo</th>
                        <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Estado</th>
                        <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Actas</th>
                      </tr>
                    </thead>
                    <tbody>
                      {state.data.items.map((item) => (
                        <tr key={item.inscripcion_id} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                          <td className="px-4 py-3 align-top">
                            <p className="font-black text-[#101b18]">{item.asignatura.nombre}</p>
                            <p className="text-xs font-bold text-[#7b6b58]">{item.asignatura.clave}</p>
                          </td>
                          <td className="px-4 py-3 align-top text-[#263b34]">{formatValue(item.docente)}</td>
                          <td className="px-4 py-3 align-top text-[#263b34]">{formatValue(item.grupo)}</td>
                          <td className="px-4 py-3 align-top">
                            <span className="rounded-full bg-[#edf8f2] px-3 py-1 text-xs font-black text-[#0b4a3d]">{item.estado_inscripcion_label}</span>
                          </td>
                          <td className="px-4 py-3 align-top">
                            <ActasSummary item={item} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <section className="rounded-[1.25rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
      <p className="text-xs font-black uppercase tracking-[0.16em] text-[#b46c13]">{label}</p>
      <p className="mt-2 text-lg font-black text-[#101b18]">{value}</p>
    </section>
  );
}

function ActasSummary({ item }: { item: DiscenteCargaAcademicaItem }) {
  if (!item.actas.length) return <span className="text-xs font-bold text-[#7b6b58]">Sin actas publicadas o en proceso.</span>;
  return (
    <div className="space-y-2">
      {item.actas.map((acta) => (
        <div key={acta.acta_id} className="rounded-xl border border-[#eadfce] px-3 py-2">
          <p className="text-xs font-black text-[#101b18]">{acta.corte_label}</p>
          <p className="text-xs text-[#5f6764]">{acta.estado_acta_label}</p>
          <Link className="mt-1 inline-block text-xs font-black text-[#7a123d]" href="/discente/actas">
            Ver mis actas
          </Link>
        </div>
      ))}
    </div>
  );
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "string") return value;
  if (typeof value === "number") return String(value);
  if (typeof value === "object") {
    const item = value as Record<string, unknown>;
    return String(item.label || item.nombre_institucional || item.nombre || item.clave || item.username || item.id || "N/A");
  }
  return String(value);
}
