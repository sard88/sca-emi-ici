"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { StudentConformityForm } from "@/components/operacion-actas/StudentConformityForm";
import { ActaDetailTable } from "@/components/operacion-actas/ActaTables";
import { ActaReadonlyNotice, ActaStatusBadge } from "@/components/operacion-actas/ActaStatusBadge";
import { ConformityTimeline, OfficialStatusNotice, ProcessTimeline, SensitiveTraceNotice, buildActaProcessSteps } from "@/components/trazabilidad";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDiscenteActaDetalle } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDiscenteActas } from "@/lib/dashboard";
import type { DiscenteActaDetalle } from "@/lib/types";

export default function DiscenteActaDetallePage() {
  const params = useParams<{ detalleId: string }>();
  const { user } = useAuth();
  const [data, setData] = useState<DiscenteActaDetalle | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getDiscenteActaDetalle(params.detalleId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible cargar el detalle.");
    } finally {
      setLoading(false);
    }
  }, [params.detalleId]);

  useEffect(() => {
    if (user && canAccessDiscenteActas(user)) void load();
  }, [user, load]);

  return (
    <AppShell showRightPanel={false}>
      {!user ? null : !canAccessDiscenteActas(user) ? (
        <ErrorMessage message="No tienes permiso para consultar este detalle." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Detalle individual de acta" description="Solo ves tu información. No se muestran datos de otros discentes." user={user} />
          <Link className="inline-flex rounded-xl border border-[#d8c5a7] px-4 py-2 text-sm font-black text-[#6f4a16]" href="/discente/actas">
            Volver a mis actas
          </Link>
          {loading ? <LoadingState label="Cargando detalle..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {data ? (
            <>
              <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-5 text-white shadow-institutional">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-xs font-black uppercase tracking-[0.22em] text-[#d4af37]">Acta #{data.acta.acta_id}</p>
                    <h2 className="mt-2 text-2xl font-black">{data.acta.materia?.nombre}</h2>
                    <p className="mt-2 text-sm text-white/82">Resultado visible: {data.detalle.resultado_corte ?? data.detalle.resultado_final_preliminar ?? "N/A"}</p>
                  </div>
                  <ActaStatusBadge estado={data.acta.estado_acta} label={data.acta.estado_acta_label} />
                </div>
              </section>
              <SensitiveTraceNotice text="La conformidad es informativa y no bloquea el flujo académico." tone="info" />
              <OfficialStatusNotice acta={data.acta} />
              <ProcessTimeline title="Línea de tiempo del acta" description="Estados visibles para tu detalle personal." steps={buildActaProcessSteps(data.acta)} />
              <ConformityTimeline acta={data.acta} historial={data.historial_conformidad} />
              <ActaReadonlyNotice visible={!data.puede_registrar_conformidad} message="La conformidad está en solo lectura para el estado actual del acta." />
              <ActaDetailTable filas={[data.detalle]} />
              <StudentConformityForm detalleId={data.detalle.detalle_id} disabled={!data.puede_registrar_conformidad} onDone={() => void load()} />
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
