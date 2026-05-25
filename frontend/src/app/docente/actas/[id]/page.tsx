"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { TeacherActaActionButtons } from "@/components/operacion-actas/ActaActionPanels";
import { ActaComponentsTable, ActaDetailTable } from "@/components/operacion-actas/ActaTables";
import { ActaReadonlyNotice, ActaStatusBadge } from "@/components/operacion-actas/ActaStatusBadge";
import { AuditTrailPanel, OfficialStatusNotice } from "@/components/trazabilidad";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { descargarActaPdf, descargarActaXlsx, getDocenteActaDetalle } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessAuditoriaEventos, canAccessDocenteOperacion } from "@/lib/dashboard";
import type { ActaDetalle, ActaFilaDetalle, ValidacionActaDTO } from "@/lib/types";

export default function DocenteActaDetallePage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [data, setData] = useState<ActaDetalle | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<"pdf" | "xlsx" | null>(null);

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

  const processSteps = useMemo(() => (data ? buildCompactProcessSteps(data) : []), [data]);

  return (
    <AppShell showRightPanel={false}>
      {!user ? null : !canAccessDocenteOperacion(user) ? (
        <ErrorMessage message="No tienes permiso para consultar esta acta." />
      ) : (
        <div className="space-y-4">
          <PageHeader title={data ? `Acta ${data.acta.corte_label}` : "Detalle de acta"} description="Seguimiento del estado del acta y detalle académico por discente." user={user} />
          <Link className="inline-flex rounded-xl border border-[#d8c5a7] px-4 py-2 text-sm font-black text-[#6f4a16]" href="/docente/actas">
            Volver a mis actas
          </Link>
          {loading ? <LoadingState label="Cargando acta..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {data ? (
            <>
              <section className="rounded-[1.5rem] border border-[#d8c5a7] bg-[#073f34] p-4 text-white shadow-institutional">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-xs font-black uppercase tracking-[0.22em] text-[#d4af37]">Acta #{data.acta.acta_id}</p>
                    <h2 className="mt-1 text-xl font-black">{data.acta.materia?.nombre}</h2>
                    <p className="mt-1 text-sm text-white/82">{data.acta.grupo?.label} · {data.acta.periodo?.label}</p>
                  </div>
                  <ActaStatusBadge estado={data.acta.estado_acta} label={data.acta.estado_acta_label} />
                </div>
              </section>

              <TeacherActaActionButtons acta={data.acta} onChanged={() => void load()} />
              <ActaReadonlyNotice visible={data.acta.solo_lectura} />
              <OfficialStatusNotice acta={data.acta} />

              <section className="rounded-[1.25rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
                <h3 className="text-sm font-black text-[#101b18]">Estado del acta</h3>
                <p className="mt-1 text-xs text-[#5f6764]">Los estados muestran el avance del acta desde su elaboración hasta su formalización institucional.</p>
                <p className="mt-1 text-[11px] text-[#7b6b58]">Actual: etapa en la que se encuentra el acta · Pendiente: etapa aún no completada.</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {processSteps.map((step) => (
                    <span
                      key={step.label}
                      className={[
                        "inline-flex items-center rounded-lg border px-2.5 py-1 text-xs font-black",
                        step.status === "completed"
                          ? "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]"
                          : step.status === "current"
                            ? "border-[#e4c777] bg-[#fff7d6] text-[#795400]"
                            : "border-[#d9d5cf] bg-[#f4f1eb] text-[#5f6764]",
                      ].join(" ")}
                      title={step.meta}
                    >
                      {step.label}
                    </span>
                  ))}
                </div>
              </section>

              <section className="rounded-[1.25rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
                <h3 className="text-sm font-black text-[#101b18]">Documentos del acta</h3>
                <p className="mt-1 text-xs text-[#5f6764]">Los documentos disponibles corresponden al estado académico registrado.</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {data.acta.url_pdf ? (
                    <button
                      type="button"
                      disabled={downloading !== null}
                      onClick={() => void downloadActaDocument(data.acta.acta_id, "pdf", setDownloading, setDownloadError)}
                      className="rounded-lg border border-[#7a123d] bg-[#7a123d] px-3 py-1.5 text-xs font-black text-white hover:bg-[#671033]"
                    >
                      {downloading === "pdf" ? "Descargando..." : "Descargar PDF"}
                    </button>
                  ) : (
                    <span className="rounded-lg border border-[#d8c5a7] bg-[#fffaf1] px-3 py-1.5 text-xs font-black text-[#7b6b58]">PDF no disponible</span>
                  )}
                  {data.acta.url_xlsx ? (
                    <button
                      type="button"
                      disabled={downloading !== null}
                      onClick={() => void downloadActaDocument(data.acta.acta_id, "xlsx", setDownloading, setDownloadError)}
                      className="rounded-lg border border-[#0b4a3d] bg-[#0b4a3d] px-3 py-1.5 text-xs font-black text-white hover:bg-[#083d33]"
                    >
                      {downloading === "xlsx" ? "Descargando..." : "Descargar XLSX"}
                    </button>
                  ) : (
                    <span className="rounded-lg border border-[#d8c5a7] bg-[#fffaf1] px-3 py-1.5 text-xs font-black text-[#7b6b58]">XLSX no disponible</span>
                  )}
                </div>
                {downloadError ? <p className="mt-3 text-xs font-bold text-[#7a123d]">{downloadError}</p> : null}
              </section>

              <CompactConformityPanel filas={data.filas} />

              <ActaComponentsTable componentes={data.componentes} />
              <ActaDetailTable filas={data.filas} componentes={data.componentes} showConformityComment />

              <CompactValidationTimeline validaciones={data.validaciones} />

              {canAccessAuditoriaEventos(user) ? <AuditTrailPanel objetoTipo="ACTA" objetoId={data.acta.acta_id} /> : null}
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function CompactConformityPanel({ filas }: { filas: ActaFilaDetalle[] }) {
  const inconformes = filas.filter((fila) => fila.conformidad_vigente?.estado_conformidad === "INCONFORME");
  const summary = filas.reduce(
    (acc, fila) => {
      const estado = fila.conformidad_vigente?.estado_conformidad;
      if (estado === "CONFORME" || estado === "ACUSE") acc.conformes += 1;
      else if (estado === "INCONFORME") acc.inconformes += 1;
      else acc.pendientes += 1;
      return acc;
    },
    { conformes: 0, inconformes: 0, pendientes: 0 },
  );

  const chips = [
    { label: "Total", value: filas.length },
    { label: "Conformes", value: summary.conformes },
    { label: "Inconformes", value: summary.inconformes },
    { label: "Pendientes", value: summary.pendientes },
  ];

  return (
    <section className="rounded-[1.25rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      <h3 className="text-sm font-black text-[#101b18]">Panel de conformidades</h3>
      <p className="mt-1 text-xs text-[#5f6764]">Resumen de conformidades registradas.</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {chips.map((chip) => (
          <span key={chip.label} className="inline-flex items-center gap-2 rounded-lg border border-[#eadfce] bg-[#fffaf1] px-2.5 py-1 text-xs font-black text-[#5a3b2a]">
            {chip.label}
            <span className="text-[#101b18]">{chip.value}</span>
          </span>
        ))}
      </div>
      {inconformes.length > 0 ? (
        <div className="mt-3 rounded-xl border border-[#eadfce] bg-[#fffaf1] p-3">
          <p className="text-xs font-black uppercase tracking-[0.08em] text-[#7a123d]">Comentarios de inconformidad</p>
          <div className="mt-2 space-y-2">
            {inconformes.map((fila, index) => (
              <div key={fila.detalle_id} className="rounded-lg border border-[#eadfce] bg-white/80 px-3 py-2 text-xs text-[#263b34]">
                <p className="font-black">
                  {index + 1}. {fila.discente?.nombre_institucional || fila.discente?.nombre || "Discente"}
                </p>
                <p className="mt-1 text-[#5a3b2a]">{fila.conformidad_vigente?.comentario || "Sin comentario registrado."}</p>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}

async function downloadActaDocument(
  actaId: number,
  format: "pdf" | "xlsx",
  setDownloading: (format: "pdf" | "xlsx" | null) => void,
  setDownloadError: (message: string | null) => void,
) {
  setDownloading(format);
  setDownloadError(null);
  try {
    if (format === "pdf") await descargarActaPdf(actaId);
    else await descargarActaXlsx(actaId);
  } catch (err) {
    setDownloadError(err instanceof Error ? err.message : "No fue posible descargar el documento.");
  } finally {
    setDownloading(null);
  }
}

function CompactValidationTimeline({ validaciones }: { validaciones: ValidacionActaDTO[] }) {
  return (
    <section className="rounded-[1.25rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      <h3 className="text-sm font-black text-[#101b18]">Validaciones del acta</h3>
      <p className="mt-1 text-xs text-[#5f6764]">Seguimiento de remisión, validación y formalización.</p>
      {validaciones.length === 0 ? (
        <p className="mt-2 text-sm text-[#5f6764]">Sin registros por ahora.</p>
      ) : (
        <div className="mt-3 overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-[#f7f0e3] text-xs font-black uppercase tracking-[0.08em] text-[#5f6764]">
              <tr>
                <th className="px-3 py-2 text-left">Etapa</th>
                <th className="px-3 py-2 text-left">Acción</th>
                <th className="px-3 py-2 text-left">Usuario</th>
                <th className="px-3 py-2 text-left">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f0e5d6] text-[#263b34]">
              {validaciones.map((validacion) => (
                <tr key={validacion.id}>
                  <td className="px-3 py-2">{validacion.etapa_validacion_label || validacion.etapa_validacion}</td>
                  <td className="px-3 py-2">{validacion.accion_label || validacion.accion}</td>
                  <td className="px-3 py-2">{validacion.usuario?.nombre_institucional || validacion.usuario?.nombre || validacion.usuario?.username || "Usuario"}</td>
                  <td className="px-3 py-2">{formatDate(validacion.fecha_hora)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function buildCompactProcessSteps(data: ActaDetalle) {
  const acta = data.acta;
  const ordered = [
    { key: "BORRADOR_DOCENTE", label: "Borrador", date: acta.creado_en },
    { key: "PUBLICADO_DISCENTE", label: "Publicada", date: acta.publicada_en },
    { key: "REMITIDO_JEFATURA_CARRERA", label: "Remitida", date: acta.remitida_en },
    { key: "VALIDADO_JEFATURA_CARRERA", label: "Validada", date: null },
    { key: "FORMALIZADO_JEFATURA_ACADEMICA", label: "Formalizada", date: acta.formalizada_en },
    { key: "ARCHIVADO", label: "Archivada", date: null },
  ];
  const current = ordered.findIndex((item) => item.key === acta.estado_acta);

  return ordered.map((item, index) => ({
    label: item.label,
    status: index < current ? "completed" : index === current ? "current" : "pending",
    meta: formatDate(item.date),
  }));
}

function formatDate(value?: string | null) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}
