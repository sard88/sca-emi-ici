"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ActaListCard } from "@/components/operacion-actas/OperationCards";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDocenteAsignacionDetalle, generarActaDocente } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDocenteOperacion } from "@/lib/dashboard";
import type { DocenteAsignacionDetalle } from "@/lib/types";

export default function DocenteAsignacionDetallePage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [data, setData] = useState<DocenteAsignacionDetalle | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getDocenteAsignacionDetalle(params.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible consultar la asignación.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    if (user && canAccessDocenteOperacion(user)) void load();
  }, [user, load]);

  async function generar(corte: string) {
    setActionError(null);
    try {
      await generarActaDocente(params.id, corte);
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "No fue posible generar el acta.");
    }
  }

  return (
    <AppShell>
      {!user ? null : !canAccessDocenteOperacion(user) ? (
        <ErrorMessage message="No tienes permiso para consultar esta asignación." />
      ) : (
        <div className="space-y-6">
          <PageHeader title={data?.item.materia?.nombre || "Detalle de asignación"} description="Discentes inscritos, cortes disponibles y actas generadas." user={user} />
          {loading ? <LoadingState label="Cargando detalle..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {actionError ? <ErrorMessage message={actionError} /> : null}
          {data ? (
            <>
              <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-5 text-white shadow-institutional">
                <p className="text-xs font-black uppercase tracking-[0.22em] text-[#d4af37]">{data.item.periodo?.label}</p>
                <h2 className="mt-2 text-2xl font-black">{data.item.materia?.nombre}</h2>
                <p className="mt-2 text-sm text-white/82">{data.item.grupo?.label} · {data.item.carrera?.nombre} · {data.discentes.length} discentes</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {data.cortes.map((corte) => (
                    <Link key={corte} className="rounded-xl bg-white px-4 py-2 text-sm font-black text-[#073f34]" href={`/docente/asignaciones/${params.id}/captura/${corte}`}>
                      Capturar {corte}
                    </Link>
                  ))}
                  <Link className="rounded-xl border border-white/30 px-4 py-2 text-sm font-black text-white" href={`/docente/asignaciones/${params.id}/resumen`}>
                    Ver resumen
                  </Link>
                </div>
              </section>

              <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
                <h3 className="text-base font-black text-[#101b18]">Generar borrador de acta</h3>
                <p className="mt-1 text-sm text-[#5f6764]">El backend valida completitud y evita duplicados de actas activas.</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {data.cortes.map((corte) => (
                    <button key={corte} className="rounded-xl bg-[#7a123d] px-4 py-2 text-sm font-black text-white" onClick={() => void generar(corte)}>
                      Generar {corte}
                    </button>
                  ))}
                </div>
              </section>

              <section className="grid gap-4 xl:grid-cols-2">
                {data.actas.map((acta) => <ActaListCard key={acta.acta_id} acta={acta} href={`/docente/actas/${acta.acta_id}`} />)}
              </section>
              {data.actas.length === 0 ? <EmptyState title="Sin actas generadas." description="Genera un borrador cuando la captura preliminar esté lista." /> : null}
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
