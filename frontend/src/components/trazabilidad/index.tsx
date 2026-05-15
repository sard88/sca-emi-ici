"use client";

import { useEffect, useMemo, useState } from "react";
import { clsx } from "clsx";
import { getEventosCriticosPorObjeto } from "@/lib/api";
import type {
  ActaFilaDetalle,
  ActaResumen,
  AuditEventDTO,
  ConformidadDiscenteDTO,
  ExportTraceDTO,
  HistorialAcademicoDTO,
  MovimientoAcademicoDTO,
  MovementImpactDTO,
  PeriodoOperativoDTO,
  ProcessTimelineStepDTO,
  TimelineStepDTO,
  ValidacionActaDTO,
} from "@/lib/types";

const actaOrder = [
  "BORRADOR_DOCENTE",
  "PUBLICADO_DISCENTE",
  "REMITIDO_JEFATURA_CARRERA",
  "VALIDADO_JEFATURA_CARRERA",
  "FORMALIZADO_JEFATURA_ACADEMICA",
  "ARCHIVADO",
];

const stateLabels: Record<string, string> = {
  BORRADOR_DOCENTE: "Borrador docente",
  PUBLICADO_DISCENTE: "Publicado a discentes",
  REMITIDO_JEFATURA_CARRERA: "Remitido a jefatura de carrera",
  VALIDADO_JEFATURA_CARRERA: "Validado por jefatura de carrera",
  FORMALIZADO_JEFATURA_ACADEMICA: "Formalizado por jefatura académica",
  ARCHIVADO: "Archivado",
  EXITOSO: "Exitoso",
  FALLIDO: "Fallido",
  BLOQUEADO: "Bloqueado",
  INFO: "Info",
  ADVERTENCIA: "Advertencia",
  CRITICO: "Crítico",
  planificado: "Planificado",
  activo: "Activo",
  cerrado: "Cerrado",
  inactivo: "Inactivo",
  ACTIVO: "Activo",
  BAJA_TEMPORAL: "Baja temporal",
  BAJA_DEFINITIVA: "Baja definitiva",
  REINGRESO: "Reingreso",
  EGRESADO: "Egresado",
};

const badgeTone: Record<string, string> = {
  BORRADOR_DOCENTE: "border-[#d8c5a7] bg-[#fffaf1] text-[#7a4b0d]",
  PUBLICADO_DISCENTE: "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
  REMITIDO_JEFATURA_CARRERA: "border-[#e4c777] bg-[#fff7d6] text-[#795400]",
  VALIDADO_JEFATURA_CARRERA: "border-[#b6d5eb] bg-[#eef7ff] text-[#1d4d71]",
  FORMALIZADO_JEFATURA_ACADEMICA: "border-[#b7d9c9] bg-[#e8f7ef] text-[#064e3b]",
  ARCHIVADO: "border-[#d9d5cf] bg-[#f4f1eb] text-[#5f6764]",
  EXITOSO: "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
  FALLIDO: "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]",
  BLOQUEADO: "border-[#e4c777] bg-[#fff7d6] text-[#795400]",
  INFO: "border-[#b6d5eb] bg-[#eef7ff] text-[#1d4d71]",
  ADVERTENCIA: "border-[#e4c777] bg-[#fff7d6] text-[#795400]",
  CRITICO: "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]",
  activo: "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
  cerrado: "border-[#d8c5a7] bg-[#fffaf1] text-[#7a4b0d]",
  inactivo: "border-[#d9d5cf] bg-[#f4f1eb] text-[#5f6764]",
  planificado: "border-[#b6d5eb] bg-[#eef7ff] text-[#1d4d71]",
  BAJA_DEFINITIVA: "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]",
  BAJA_TEMPORAL: "border-[#e4c777] bg-[#fff7d6] text-[#795400]",
  REINGRESO: "border-[#b6d5eb] bg-[#eef7ff] text-[#1d4d71]",
  EGRESADO: "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
};

export function ProcessStateBadge({ state, label }: { state: string; label?: string }) {
  return (
    <span className={clsx("inline-flex rounded-full border px-3 py-1 text-xs font-black uppercase", badgeTone[state] ?? "border-[#eadfce] bg-white text-[#46534e]")}>
      {label || stateLabels[state] || state}
    </span>
  );
}

export function ProcessTimeline({ title = "Línea de tiempo", description, steps }: { title?: string; description?: string; steps: ProcessTimelineStepDTO[] }) {
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-5 shadow-sm">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-base font-black text-[#101b18]">{title}</h3>
          {description ? <p className="mt-1 text-sm text-[#5f6764]">{description}</p> : null}
        </div>
      </div>
      {steps.length ? (
        <div className="mt-5 space-y-3">
          {steps.map((step, index) => <ProcessTimelineStep key={step.id} step={step} last={index === steps.length - 1} />)}
        </div>
      ) : (
        <TimelineEmptyState text="No hay eventos suficientes para construir la línea de tiempo." />
      )}
    </section>
  );
}

export function ProcessTimelineStep({ step, last = false }: { step: TimelineStepDTO; last?: boolean }) {
  const status = step.status || "pending";
  const dotClass = {
    completed: "bg-[#0b4a3d]",
    current: "bg-[#d4af37]",
    pending: "bg-[#d9d5cf]",
    blocked: "bg-[#7a123d]",
    not_applicable: "bg-[#b8b0a3]",
  }[status];
  return (
    <div className="relative flex gap-3">
      <div className="flex flex-col items-center">
        <span className={clsx("mt-1 h-3 w-3 rounded-full ring-4 ring-white", dotClass)} />
        {!last ? <span className="mt-1 h-full min-h-10 w-px bg-[#eadfce]" /> : null}
      </div>
      <div className="min-w-0 flex-1 rounded-2xl border border-[#eadfce] bg-[#fffaf1]/70 px-4 py-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-black text-[#152b25]">{step.label}</p>
          <ProcessStateBadge state={status} label={statusLabel(status)} />
        </div>
        {step.description ? <p className="mt-1 text-sm text-[#5f6764]">{step.description}</p> : null}
        <p className="mt-2 text-xs font-bold text-[#7b6b58]">{[formatDate(step.date), step.actor, step.meta].filter(Boolean).join(" · ") || "Sin fecha registrada"}</p>
      </div>
    </div>
  );
}

export function ValidationTimeline({ validaciones }: { validaciones: ValidacionActaDTO[] }) {
  const steps = validaciones.map((validacion) => ({
    id: String(validacion.id),
    label: `${validacion.accion_label || validacion.accion} · ${validacion.etapa_validacion_label || validacion.etapa_validacion}`,
    description: validacion.comentario,
    status: "completed" as const,
    date: validacion.fecha_hora,
    actor: validacion.usuario?.nombre_institucional || validacion.usuario?.nombre || validacion.usuario?.username || "Usuario",
    meta: validacion.cargo || validacion.cargo_codigo || null,
  }));
  return <ProcessTimeline title="Timeline de validaciones" description="Remisión, validación y formalización registradas por el backend." steps={steps} />;
}

export function ConformityTimeline({ acta, historial }: { acta: ActaResumen; historial: ConformidadDiscenteDTO[] }) {
  const current = historial.find((item) => item.vigente) || historial[0];
  const steps: TimelineStepDTO[] = [
    {
      id: "publicada",
      label: "Acta publicada",
      status: acta.publicada_en ? "completed" : "pending",
      date: acta.publicada_en,
      description: "El resultado queda visible para el discente.",
    },
    {
      id: "conformidad",
      label: current ? current.estado_conformidad_label || current.estado_conformidad : "Conformidad pendiente",
      status: current ? "completed" : "current",
      date: current?.registrado_en,
      description: current ? "Registro personal de acuse, conformidad o inconformidad." : "Aún no has registrado conformidad.",
    },
    {
      id: "remitida",
      label: "Solo lectura después de remisión",
      status: acta.remitida_en ? "completed" : "pending",
      date: acta.remitida_en,
      description: "Después de la remisión, la conformidad queda en solo lectura.",
    },
    {
      id: "formalizada",
      label: "Acta formalizada",
      status: acta.formalizada_en ? "completed" : "pending",
      date: acta.formalizada_en,
      description: "La formalización consolida el documento oficial cuando aplica.",
    },
  ];
  return <ProcessTimeline title="Mi línea de conformidad" description="La conformidad es informativa y no bloquea el flujo académico." steps={steps} />;
}

export function ConformitySummaryPanel({ filas }: { filas: ActaFilaDetalle[] }) {
  const summary = filas.reduce(
    (acc, fila) => {
      const estado = fila.conformidad_vigente?.estado_conformidad;
      if (estado === "CONFORME") acc.conformes += 1;
      else if (estado === "INCONFORME") acc.inconformes += 1;
      else if (estado === "ACUSE") acc.acuses += 1;
      else acc.pendientes += 1;
      return acc;
    },
    { conformes: 0, inconformes: 0, acuses: 0, pendientes: 0 },
  );
  const total = filas.length;
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-5 shadow-sm">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-base font-black text-[#101b18]">Panel de conformidades</h3>
          <p className="mt-1 text-sm text-[#5f6764]">Resumen agregado sin comentarios completos de inconformidad.</p>
        </div>
        <ProcessStateBadge state={summary.pendientes ? "ADVERTENCIA" : "EXITOSO"} label={summary.pendientes ? "Con pendientes" : "Completo"} />
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <TraceMetric label="Total" value={total} />
        <TraceMetric label="Conformes" value={summary.conformes} />
        <TraceMetric label="Inconformes" value={summary.inconformes} />
        <TraceMetric label="Acuses" value={summary.acuses} />
        <TraceMetric label="Pendientes" value={summary.pendientes} />
      </div>
    </section>
  );
}

export function AuditTrailPanel({ objetoTipo, objetoId, title = "Eventos críticos relacionados", forbiddenMode = "hidden" }: { objetoTipo: string; objetoId: number | string; title?: string; forbiddenMode?: "hidden" | "message" }) {
  const [items, setItems] = useState<AuditEventDTO[]>([]);
  const [selected, setSelected] = useState<AuditEventDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setForbidden(false);
    getEventosCriticosPorObjeto(objetoTipo, objetoId, { page_size: "8" })
      .then((data) => {
        if (!active) return;
        setItems(data.items || []);
      })
      .catch((err: Error & { status?: number }) => {
        if (!active) return;
        if (err.status === 403) setForbidden(true);
        else setError(err.message || "No fue posible cargar eventos críticos.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [objetoId, objetoTipo]);

  if (forbidden && forbiddenMode === "hidden") return null;

  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-5 shadow-sm">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-base font-black text-[#101b18]">{title}</h3>
          <p className="mt-1 text-sm text-[#5f6764]">{objetoTipo} #{objetoId}</p>
        </div>
      </div>
      {loading ? <p className="mt-4 text-sm font-bold text-[#5f6764]">Consultando bitácora...</p> : null}
      {forbidden && forbiddenMode === "message" ? <SensitiveTraceNotice text="No tienes permiso para consultar eventos críticos de este objeto." /> : null}
      {error ? <SensitiveTraceNotice text={error} tone="danger" /> : null}
      {!loading && !forbidden && !error && items.length === 0 ? <TimelineEmptyState text={`No hay eventos críticos registrados para este objeto.`} /> : null}
      {!loading && !forbidden && !error && items.length ? (
        <div className="mt-4 grid gap-3 xl:grid-cols-2">
          {items.map((item) => <AuditEventCard key={String(item.id)} item={item} onOpen={() => setSelected(item)} />)}
        </div>
      ) : null}
      <AuditEventDetailDrawer item={selected} onClose={() => setSelected(null)} />
    </section>
  );
}

export function AuditEventCard({ item, onOpen }: { item: AuditEventDTO; onOpen?: () => void }) {
  return (
    <article className="rounded-2xl border border-[#eadfce] bg-[#fffaf1]/70 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <ProcessStateBadge state={item.resultado || "INFO"} />
        <ProcessStateBadge state={item.severidad || "INFO"} />
      </div>
      <p className="mt-3 text-sm font-black text-[#152b25]">{item.evento_nombre || item.evento_codigo || "Evento crítico"}</p>
      <p className="mt-1 text-xs font-bold text-[#7b6b58]">{[formatDate(item.creado_en), userLabel(item.usuario), item.modulo].filter(Boolean).join(" · ")}</p>
      {item.resumen ? <p className="mt-2 line-clamp-2 text-sm text-[#5f6764]">{item.resumen}</p> : null}
      {onOpen ? <button type="button" className="mt-3 text-sm font-black text-[#7a123d]" onClick={onOpen}>Ver detalle</button> : null}
    </article>
  );
}

export function AuditEventDetailDrawer({ item, onClose, showIp = true }: { item: AuditEventDTO | null; onClose: () => void; showIp?: boolean }) {
  if (!item) return null;
  const rows: Array<[string, unknown]> = [
    ["Evento", item.evento_nombre || item.evento_codigo],
    ["Usuario", userLabel(item.usuario) || item.username_snapshot],
    ["Módulo", item.modulo],
    ["Resultado", item.resultado],
    ["Severidad", item.severidad],
    ["Objeto", [item.objeto_tipo, item.objeto_id, item.objeto_repr].filter(Boolean).join(" · ")],
    ["Estado anterior", item.estado_anterior],
    ["Estado nuevo", item.estado_nuevo],
    ["Resumen", item.resumen],
    ["Ruta/método", [item.metodo_http, item.ruta].filter(Boolean).join(" ")],
    ["Fecha", formatDate(item.creado_en)],
    ...(showIp ? [["IP", item.ip_origen] as [string, unknown]] : []),
  ];
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-end bg-black/20 p-4">
      <aside className="max-h-[88vh] w-full max-w-xl overflow-y-auto rounded-[1.5rem] border border-[#eadfce] bg-white p-5 shadow-2xl">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.18em] text-[#b46c13]">Detalle de evento</p>
            <h3 className="mt-1 text-xl font-black text-[#101b18]">{item.evento_codigo || "Evento crítico"}</h3>
          </div>
          <button type="button" className="rounded-xl border border-[#d8c5a7] px-3 py-2 text-sm font-black text-[#6f4a16]" onClick={onClose}>Cerrar</button>
        </div>
        <div className="mt-4 divide-y divide-[#f0e4d1]">
          {rows.map(([label, value]) => (
            <div key={label} className="grid gap-1 py-3 sm:grid-cols-[150px_1fr]">
              <span className="text-xs font-black uppercase tracking-[0.12em] text-[#7a4b0d]">{label}</span>
              <span className="break-words text-sm text-[#263b34]">{formatValue(value)}</span>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}

export function OfficialStatusNotice({ acta, formalizationContext = false }: { acta: ActaResumen; formalizationContext?: boolean }) {
  const message = acta.es_documento_oficial
    ? "Acta formalizada. Información oficial protegida en solo lectura."
    : formalizationContext && acta.es_final
      ? "La formalización de acta FINAL actualiza resultados oficiales."
      : "Documento no oficial hasta su formalización.";
  return <SensitiveTraceNotice text={acta.solo_lectura ? `${message} Solo lectura.` : message} tone={acta.es_documento_oficial ? "success" : "warning"} />;
}

export function SensitiveTraceNotice({ text, tone = "warning" }: { text: string; tone?: "warning" | "danger" | "success" | "info" }) {
  const cls = {
    warning: "border-[#d4af37]/35 bg-[#fff8e6] text-[#72530d]",
    danger: "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]",
    success: "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
    info: "border-[#b6d5eb] bg-[#eef7ff] text-[#1d4d71]",
  }[tone];
  return <div className={clsx("rounded-2xl border px-4 py-3 text-sm font-bold", cls)}>{text}</div>;
}

export function PeriodProcessStepper({ activeStep = "diagnostico", periodo }: { activeStep?: "planificado" | "activo" | "diagnostico" | "cierre" | "apertura" | "pendientes"; periodo?: PeriodoOperativoDTO }) {
  const order = ["planificado", "activo", "diagnostico", "cierre", "apertura", "pendientes"];
  const current = order.indexOf(activeStep);
  const steps = [
    { id: "planificado", label: "Periodo planificado", status: stepStatus(0, current, periodo?.estado === "planificado") },
    { id: "activo", label: "Periodo activo", status: stepStatus(1, current, periodo?.estado === "activo") },
    { id: "diagnostico", label: "Diagnóstico de cierre", status: stepStatus(2, current) },
    { id: "cierre", label: "Cierre de periodo", status: stepStatus(3, current, periodo?.estado === "cerrado") },
    { id: "apertura", label: "Apertura del siguiente periodo", status: stepStatus(4, current) },
    { id: "pendientes", label: "Pendientes de asignación docente", status: stepStatus(5, current) },
  ] as TimelineStepDTO[];
  return <ProcessTimeline title="Proceso de cierre y apertura" description="Stepper institucional de referencia; no todos los pasos aplican a todos los periodos." steps={steps} />;
}

export function PeriodBlockersPanel({ bloqueantes, advertencias }: { bloqueantes: unknown[]; advertencias: unknown[] }) {
  return (
    <section className="grid gap-4 xl:grid-cols-2">
      <GroupedList title="Bloqueantes" items={bloqueantes} tone="danger" />
      <GroupedList title="Advertencias" items={advertencias} tone="warning" />
    </section>
  );
}

export function MovementImpactTimeline({ movimiento }: { movimiento: MovimientoAcademicoDTO }) {
  const impacto = (movimiento.impacto || {}) as MovementImpactDTO;
  const steps = [
    { id: "registrado", label: "Movimiento registrado", status: "completed", date: movimiento.fecha_movimiento, description: movimiento.tipo_movimiento_label || movimiento.tipo_movimiento },
    movimiento.grupo_origen ? { id: "origen", label: "Grupo origen", status: "completed", description: formatValue(movimiento.grupo_origen) } : null,
    movimiento.grupo_destino ? { id: "destino", label: "Grupo destino", status: "completed", description: formatValue(movimiento.grupo_destino) } : null,
    present(impacto.adscripcion_origen) ? { id: "adscripcion-origen", label: "Adscripción origen", status: "completed", description: formatValue(impacto.adscripcion_origen) } : null,
    present(impacto.adscripcion_destino) ? { id: "adscripcion-destino", label: "Adscripción destino", status: "completed", description: formatValue(impacto.adscripcion_destino) } : null,
    present(impacto.inscripciones_origen) ? { id: "inscripciones-origen", label: "Inscripciones origen", status: "completed", description: formatValue(impacto.inscripciones_origen) } : null,
    present(impacto.inscripciones_destino) ? { id: "inscripciones-destino", label: "Inscripciones destino", status: "completed", description: formatValue(impacto.inscripciones_destino) } : null,
    impacto.bloqueado ? { id: "bloqueado", label: "Movimiento bloqueado", status: "blocked", description: impacto.motivo_bloqueo || "El backend reportó bloqueo." } : null,
    impacto.aplicado ? { id: "aplicado", label: "Movimiento aplicado", status: "completed", description: "Existe evidencia de aplicación reportada por backend." } : null,
  ].filter(Boolean) as TimelineStepDTO[];
  return <ProcessTimeline title="Impacto del movimiento" description="Solo se muestran efectos con evidencia entregada por backend." steps={steps} />;
}

export function AcademicHistoryTimeline({ historial }: { historial: HistorialAcademicoDTO }) {
  const steps = useMemo(() => buildAcademicHistorySteps(historial), [historial]);
  return <ProcessTimeline title="Línea de tiempo del historial académico" description="Resultados, extraordinarios, situaciones y movimientos ordenados cronológicamente cuando hay fecha." steps={steps} />;
}

export function ExportTracePanel({ item }: { item: ExportTraceDTO }) {
  const folio = item.folio_tecnico || item.id;
  return (
    <article className="rounded-2xl border border-[#eadfce] bg-[#fffaf1]/70 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <ProcessStateBadge state={String(item.estado || "")} label={String(item.estado_label || item.estado || "Exportación")} />
        {item.formato ? <ProcessStateBadge state="INFO" label={item.formato} /> : null}
      </div>
      <p className="mt-3 text-sm font-black text-[#152b25]">Folio técnico {folio ? `#${folio}` : "no disponible"}</p>
      <p className="mt-1 text-sm text-[#5f6764]">{item.tipo_documento_label || item.tipo_documental || item.tipo_documento || "Documento"} · {item.nombre_documento || item.nombre_archivo || "Sin nombre"}</p>
      <dl className="mt-3 grid gap-2 text-xs sm:grid-cols-2">
        <TracePair label="Usuario" value={formatValue(item.usuario)} />
        <TracePair label="Fecha" value={formatDate(item.finalizado_en || item.creado_en || item.fecha)} />
        <TracePair label="Objeto" value={item.objeto || [item.objeto_tipo, item.objeto_id].filter(Boolean).join(" #")} />
        <TracePair label="Hash/tamaño" value={[item.hash_archivo || item.hash, item.tamano_bytes ? formatBytes(item.tamano_bytes) : null].filter(Boolean).join(" · ")} />
      </dl>
    </article>
  );
}

export function TimelineEmptyState({ text = "Sin eventos para mostrar." }: { text?: string }) {
  return <p className="mt-4 rounded-2xl border border-dashed border-[#d8c5a7] bg-[#fffaf1] px-4 py-3 text-sm font-bold text-[#7b6b58]">{text}</p>;
}

export function buildActaProcessSteps(acta: ActaResumen): TimelineStepDTO[] {
  const current = actaOrder.indexOf(acta.estado_acta);
  const dates: Record<string, string | null | undefined> = {
    BORRADOR_DOCENTE: acta.creado_en,
    PUBLICADO_DISCENTE: acta.publicada_en,
    REMITIDO_JEFATURA_CARRERA: acta.remitida_en,
    VALIDADO_JEFATURA_CARRERA: undefined,
    FORMALIZADO_JEFATURA_ACADEMICA: acta.formalizada_en,
    ARCHIVADO: undefined,
  };
  return actaOrder.map((state, index) => ({
    id: state,
    label: stateLabels[state],
    status: index < current ? "completed" : index === current ? "current" : "pending",
    date: dates[state] || null,
    description: state === "FORMALIZADO_JEFATURA_ACADEMICA" ? "El acta formalizada queda protegida como documento oficial." : undefined,
  }));
}

function buildAcademicHistorySteps(historial: HistorialAcademicoDTO): TimelineStepDTO[] {
  const rows: TimelineStepDTO[] = [
    ...historial.resultados.map((item, index) => ({
      id: `resultado-${item.inscripcion_id || index}`,
      label: item.tipo_resultado === "EXTRAORDINARIO" ? "Resultado extraordinario" : "Resultado académico",
      status: "completed" as const,
      date: stringField(item, ["fecha", "fecha_resultado", "formalizada_en", "creado_en"]),
      description: [formatValue(item.materia), formatValue(item.calificacion), item.codigo_resultado, item.codigo_marca].filter((value) => value && value !== "N/A").join(" · "),
      meta: item.tipo_resultado || "Ordinario",
    })),
    ...historial.extraordinarios.map((item) => ({
      id: `extraordinario-${item.id}`,
      label: "Extraordinario",
      status: "completed" as const,
      date: item.fecha_aplicacion,
      description: [formatValue(item.discente), formatValue(item.calificacion), item.codigo_marca].filter((value) => value && value !== "N/A").join(" · "),
      meta: "EE",
    })),
    ...historial.eventos.map((item) => ({
      id: `evento-${item.id}`,
      label: formatValue(item.situacion),
      status: "completed" as const,
      date: item.fecha_inicio,
      description: item.motivo,
      meta: "Situación académica",
    })),
    ...historial.movimientos.map((item) => ({
      id: `movimiento-${item.id}`,
      label: item.tipo_movimiento_label || item.tipo_movimiento || "Movimiento académico",
      status: "completed" as const,
      date: item.fecha_movimiento,
      description: [formatValue(item.grupo_origen), formatValue(item.grupo_destino)].filter((value) => value && value !== "N/A").join(" -> "),
      meta: "Movimiento",
    })),
  ];
  return rows.sort((a, b) => {
    const left = a.date ? new Date(a.date).getTime() : Number.MAX_SAFE_INTEGER;
    const right = b.date ? new Date(b.date).getTime() : Number.MAX_SAFE_INTEGER;
    return left - right;
  });
}

function GroupedList({ title, items, tone }: { title: string; items: unknown[]; tone: "danger" | "warning" }) {
  const color = tone === "danger" ? "border-[#7a123d]/30 bg-[#fff5f8] text-[#7a123d]" : "border-[#d4af37]/40 bg-[#fff8e6] text-[#72530d]";
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-5 shadow-sm">
      <h3 className="text-base font-black text-[#101b18]">{title}</h3>
      {items.length ? (
        <ul className="mt-3 space-y-2">
          {items.map((item, index) => <li key={`${title}-${index}`} className={clsx("rounded-2xl border px-4 py-3 text-sm font-bold", color)}>{formatValue(item)}</li>)}
        </ul>
      ) : (
        <TimelineEmptyState text={`Sin ${title.toLowerCase()} reportados.`} />
      )}
    </section>
  );
}

function TraceMetric({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-2xl border border-[#eadfce] bg-[#fffaf1] p-4">
      <p className="text-xs font-black uppercase tracking-[0.16em] text-[#b46c13]">{label}</p>
      <p className="mt-2 text-2xl font-black text-[#101b18]">{value}</p>
    </div>
  );
}

function TracePair({ label, value }: { label: string; value: unknown }) {
  return (
    <div>
      <dt className="font-black uppercase tracking-[0.12em] text-[#7a4b0d]">{label}</dt>
      <dd className="mt-1 text-[#263b34]">{formatValue(value)}</dd>
    </div>
  );
}

function statusLabel(status: string) {
  return {
    completed: "Completado",
    current: "Actual",
    pending: "Pendiente",
    blocked: "Bloqueado",
    not_applicable: "No aplica",
  }[status] || status;
}

function stepStatus(index: number, current: number, completedByState = false): TimelineStepDTO["status"] {
  if (completedByState || index < current) return "completed";
  if (index === current) return "current";
  return "pending";
}

function userLabel(user: AuditEventDTO["usuario"]) {
  if (!user) return "";
  if (typeof user === "string") return user;
  return user.nombre || user.username || "Sistema";
}

function present(value: unknown) {
  if (value === null || value === undefined || value === "") return false;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

function stringField(item: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = item[key];
    if (typeof value === "string" && value) return value;
  }
  return null;
}

function formatDate(value?: string | null) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function formatBytes(value: number) {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "boolean") return value ? "Sí" : "No";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(1);
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.length ? value.map(formatValue).join(", ") : "N/A";
  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    return String(obj.label || obj.nombre_institucional || obj.nombre || obj.clave || obj.username || obj.id || JSON.stringify(obj));
  }
  return String(value);
}
