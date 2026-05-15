"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { HeadValidationActionPanel } from "@/components/operacion-actas/ActaActionPanels";
import { ActaExportActions } from "@/components/operacion-actas/ActaExportActions";
import { ActaComponentsTable, ActaDetailTable, ActaValidationTimeline } from "@/components/operacion-actas/ActaTables";
import { ActaStatusBadge } from "@/components/operacion-actas/ActaStatusBadge";
import { AuditTrailPanel, ConformitySummaryPanel, OfficialStatusNotice, ProcessTimeline, buildActaProcessSteps } from "@/components/trazabilidad";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getJefaturaCarreraActaDetalle } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessAuditoriaEventos, canAccessJefaturaCarreraActas } from "@/lib/dashboard";
import type { ActaDetalle } from "@/lib/types";

export default function JefaturaCarreraActaDetallePage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [data, setData] = useState<ActaDetalle | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getJefaturaCarreraActaDetalle(params.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible cargar el acta.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    if (user && canAccessJefaturaCarreraActas(user)) void load();
  }, [user, load]);

  return (
    <AppShell showRightPanel={false}>
      {!user ? null : !canAccessJefaturaCarreraActas(user) ? (
        <ErrorMessage message="No tienes permiso para consultar esta acta." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Revisión de acta" description="Validación por jefatura de carrera. No modifica calificaciones." user={user} />
          <Link className="inline-flex rounded-xl border border-[#d8c5a7] px-4 py-2 text-sm font-black text-[#6f4a16]" href="/jefatura-carrera/actas">
            Volver a pendientes
          </Link>
          {loading ? <LoadingState label="Cargando acta..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {data ? (
            <>
              <section className="rounded-[1.75rem] border border-[#d8c5a7] bg-[#073f34] p-5 text-white shadow-institutional">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-xs font-black uppercase tracking-[0.22em] text-[#d4af37]">Acta #{data.acta.acta_id}</p>
                    <h2 className="mt-2 text-2xl font-black">{data.acta.materia?.nombre}</h2>
                    <p className="mt-2 text-sm text-white/82">{data.acta.grupo?.label} · {data.acta.docente?.nombre_institucional || data.acta.docente?.nombre}</p>
                  </div>
                  <ActaStatusBadge estado={data.acta.estado_acta} label={data.acta.estado_acta_label} />
                </div>
              </section>
              <HeadValidationActionPanel acta={data.acta} onChanged={() => void load()} />
              <OfficialStatusNotice acta={data.acta} />
              <ProcessTimeline title="Timeline de estado del acta" description="Estados del acta reportados por backend." steps={buildActaProcessSteps(data.acta)} />
              <ActaExportActions acta={data.acta} />
              <ConformitySummaryPanel filas={data.filas} />
              <ActaComponentsTable componentes={data.componentes} />
              <ActaDetailTable filas={data.filas} />
              <ActaValidationTimeline validaciones={data.validaciones} />
              {canAccessAuditoriaEventos(user) ? <AuditTrailPanel objetoTipo="ACTA" objetoId={data.acta.acta_id} /> : null}
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
