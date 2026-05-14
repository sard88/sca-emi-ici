"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { TeacherActaActionButtons } from "@/components/operacion-actas/ActaActionPanels";
import { ActaExportActions } from "@/components/operacion-actas/ActaExportActions";
import { ActaComponentsTable, ActaDetailTable, ActaValidationTimeline } from "@/components/operacion-actas/ActaTables";
import { ActaOfficialNotice, ActaReadonlyNotice, ActaStatusBadge } from "@/components/operacion-actas/ActaStatusBadge";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDocenteActaDetalle } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDocenteOperacion } from "@/lib/dashboard";
import type { ActaDetalle } from "@/lib/types";

export default function DocenteActaDetallePage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [data, setData] = useState<ActaDetalle | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getDocenteActaDetalle(params.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible cargar el acta.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    if (user && canAccessDocenteOperacion(user)) void load();
  }, [user, load]);

  return (
    <AppShell showRightPanel={false}>
      {!user ? null : !canAccessDocenteOperacion(user) ? (
        <ErrorMessage message="No tienes permiso para consultar esta acta." />
      ) : (
        <div className="space-y-6">
          <PageHeader title={data ? `Acta ${data.acta.corte_label}` : "Detalle de acta"} description="Gestión docente sin modificar calificaciones oficiales." user={user} />
          <Link className="inline-flex rounded-xl border border-[#d8c5a7] px-4 py-2 text-sm font-black text-[#6f4a16]" href="/docente/actas">
            Volver a mis actas
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
                    <p className="mt-2 text-sm text-white/82">{data.acta.grupo?.label} · {data.acta.periodo?.label}</p>
                  </div>
                  <ActaStatusBadge estado={data.acta.estado_acta} label={data.acta.estado_acta_label} />
                </div>
              </section>
              <TeacherActaActionButtons acta={data.acta} onChanged={() => void load()} />
              <ActaReadonlyNotice visible={data.acta.solo_lectura} />
              <ActaOfficialNotice oficial={data.acta.es_documento_oficial} />
              <ActaExportActions acta={data.acta} />
              <ActaComponentsTable componentes={data.componentes} />
              <ActaDetailTable filas={data.filas} />
              <ActaValidationTimeline validaciones={data.validaciones} />
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
