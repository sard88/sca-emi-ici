"use client";

import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import {
  buscarHistoriales,
  cerrarPeriodo,
  crearAperturaPeriodo,
  crearCambioGrupo,
  crearExtraordinario,
  crearMovimientoAcademico,
  crearSituacionAcademica,
  getApertura,
  getAperturas,
  getCierre,
  getCierres,
  getDiagnosticoCierrePeriodo,
  getExtraordinario,
  getExtraordinarios,
  getHistorialDiscente,
  getMiHistorial,
  getMovimientoAcademico,
  getMovimientosAcademicos,
  getOpcionesInscripcionesExtraordinario,
  getPendientesAsignacionDocente,
  getPeriodos,
  getSituacion,
  getSituaciones,
  listResource,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessMiHistorialAcademico, canAccessPeriodosOperativos, canAccessTrayectoriaInstitucional, canAccessTrayectoriaOperativa, canOperateTrayectoria } from "@/lib/dashboard";
import type {
  AuthenticatedUser,
  DiagnosticoCierrePeriodoDTO,
  ExtraordinarioDTO,
  HistorialAcademicoDTO,
  MovimientoAcademicoDTO,
  PendienteAsignacionDocenteDTO,
  PeriodoOperativoDTO,
  SituacionAcademicaDTO,
} from "@/lib/types";

type RecordValue = Record<string, unknown>;
type FilterState = Record<string, string>;
type SelectOption = { value: string; label: string };

type LoadState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};

const emptyState = <T,>(): LoadState<T> => ({ data: null, loading: false, error: null });

function AccessPage({
  title,
  description,
  allowed,
  children,
}: {
  title: string;
  description: string;
  allowed: (user: AuthenticatedUser) => boolean;
  children: (user: AuthenticatedUser) => ReactNode;
}) {
  const { user } = useAuth();
  return (
    <AppShell showRightPanel={false}>
      {!user ? null : !allowed(user) ? (
        <ErrorMessage message="No tienes permiso para consultar este módulo desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader title={title} description={description} user={user} />
          {children(user)}
        </div>
      )}
    </AppShell>
  );
}

export function TrajectoryHomeCards() {
  return (
    <AccessPage
      title="Trayectoria académica"
      description="Historiales, extraordinarios, situaciones académicas y movimientos sin modificar reglas de dominio."
      allowed={canAccessTrayectoriaOperativa}
    >
      {(user) => {
        if (canAccessMiHistorialAcademico(user) && !canAccessTrayectoriaInstitucional(user)) {
          return (
            <div className="grid gap-4 xl:grid-cols-2">
              <ModuleCard title="Mi historial académico" href="/trayectoria/mi-historial" description="Consulta personal de resultados, eventos y movimientos visibles. No es kárdex oficial." tone="verde" />
              <ModuleCard title="Mi carga académica" href="/discente/carga-academica" description="Asignaturas inscritas, docente, grupo y estado de actas visibles para tu perfil." />
              <ModuleCard title="Mis actas publicadas" href="/discente/actas" description="Resultados publicados y conformidad informativa por acta." tone="dorado" />
            </div>
          );
        }
        const institutional = canAccessTrayectoriaInstitucional(user);
        const operator = canOperateTrayectoria(user);
        return (
          <div className="grid gap-4 xl:grid-cols-2">
            {canAccessMiHistorialAcademico(user) ? <ModuleCard title="Mi historial académico" href="/trayectoria/mi-historial" description="Consulta personal de resultados, eventos y movimientos visibles. No es kárdex oficial." tone="verde" /> : null}
            {institutional ? <ModuleCard title="Buscar historial académico" href="/trayectoria/historial" description="Consulta institucional filtrada por ámbito autorizado." /> : null}
            {institutional ? <ModuleCard title="Extraordinarios" href="/trayectoria/extraordinarios" description="Seguimiento de extraordinarios registrados y marca EE cuando aplique." /> : null}
            {operator ? <ModuleCard title="Registrar extraordinario" href="/trayectoria/extraordinarios/nuevo" description="Registro operativo con validación real en backend." tone="dorado" /> : null}
            {institutional ? <ModuleCard title="Situaciones académicas" href="/trayectoria/situaciones" description="Bajas temporales, bajas definitivas, reingresos y eventos de trayectoria." /> : null}
            {operator ? <ModuleCard title="Registrar situación" href="/trayectoria/situaciones/nuevo" description="Alta de evento académico con confirmación y validación backend." tone="dorado" /> : null}
            {institutional ? <ModuleCard title="Movimientos académicos" href="/movimientos-academicos" description="Cambios de grupo y evidencia operativa sin borrar historial." /> : null}
            {operator ? <ModuleCard title="Cambio de grupo" href="/movimientos-academicos/cambio-grupo" description="Movimiento transaccional: adscripción, inscripciones y bloqueos por actas vivas." tone="guinda" /> : null}
            {canAccessPeriodosOperativos(user) ? <ModuleCard title="Cierre y apertura de periodo" href="/periodos" description="Diagnóstico, cierre, apertura y pendientes de asignación docente." tone="verde" /> : null}
          </div>
        );
      }}
    </AccessPage>
  );
}

function ModuleCard({ title, description, href, tone = "neutral" }: { title: string; description: string; href: string; tone?: "neutral" | "guinda" | "dorado" | "verde" }) {
  const toneClass = {
    neutral: "border-[#eadfce] bg-white/90 text-[#101b18]",
    guinda: "border-[#7a123d]/25 bg-[#fff5f8] text-[#2a101a]",
    dorado: "border-[#d4af37]/35 bg-[#fff8e6] text-[#2f2208]",
    verde: "border-[#0b4a3d]/20 bg-[#f0faf6] text-[#0b2d26]",
  }[tone];
  return (
    <Link href={href} className={`block rounded-[1.5rem] border p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-institutional ${toneClass}`}>
      <p className="text-xs font-black uppercase tracking-[0.18em] text-[#b46c13]">Operación 10C-6</p>
      <h2 className="mt-2 text-xl font-black">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-[#5f6764]">{description}</p>
      <span className="mt-4 inline-flex rounded-xl bg-[#7a123d] px-4 py-2 text-sm font-black text-white">Abrir</span>
    </Link>
  );
}

export function MyHistoryView() {
  const [state, setState] = useState<LoadState<HistorialAcademicoDTO>>(emptyState);
  useEffect(() => {
    setState({ data: null, loading: true, error: null });
    getMiHistorial()
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, []);

  return (
    <AccessPage title="Mi historial académico" description="Consulta personal de trayectoria. Esta vista no sustituye al kárdex oficial." allowed={canAccessMiHistorialAcademico}>
      {() => <HistoryContent state={state} own />}
    </AccessPage>
  );
}

export function InstitutionalHistorySearch() {
  const [filters, setFilters] = useState<FilterState>({});
  const [state, setState] = useState<LoadState<Array<RecordValue>>>(emptyState);
  const load = useCallback(() => {
    setState({ data: null, loading: true, error: null });
    buscarHistoriales(filters)
      .then((data) => setState({ data: data.items as Array<RecordValue>, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [filters]);
  useEffect(() => { void load(); }, [load]);

  return (
    <AccessPage title="Búsqueda institucional de historial" description="Consulta de discentes filtrada por permisos y ámbito de carrera." allowed={canAccessTrayectoriaInstitucional}>
      {() => (
        <div className="space-y-5">
          <SensitiveInfoNotice text="El historial interno contiene información académica sensible y no es kárdex oficial." />
          <FiltersBar filters={filters} setFilters={setFilters} fields={["q", "carrera", "grupo", "plan", "antiguedad", "situacion"]} onSearch={load} />
          <StateBlock state={state} loadingLabel="Buscando historiales..." emptyTitle="No hay discentes para los filtros." />
          {state.data ? <DataTable items={state.data} detailBase="/trayectoria/historial" detailKey="id" /> : null}
        </div>
      )}
    </AccessPage>
  );
}

export function InstitutionalHistoryDetail({ discenteId }: { discenteId: string }) {
  const [state, setState] = useState<LoadState<HistorialAcademicoDTO>>(emptyState);
  useEffect(() => {
    setState({ data: null, loading: true, error: null });
    getHistorialDiscente(discenteId)
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [discenteId]);

  return (
    <AccessPage title="Detalle de historial académico" description="Vista institucional de resultados, eventos y movimientos preservados." allowed={canAccessTrayectoriaInstitucional}>
      {() => <HistoryContent state={state} />}
    </AccessPage>
  );
}

function HistoryContent({ state, own = false }: { state: LoadState<HistorialAcademicoDTO>; own?: boolean }) {
  return (
    <div className="space-y-5">
      <StateBlock state={state} loadingLabel="Cargando historial..." emptyTitle="No se encontró historial." />
      {state.data ? (
        <>
          <SensitiveInfoNotice text={own ? "Esta vista es informativa y no corresponde al kárdex oficial." : "Historial interno sensible. Consulta exclusiva para perfiles autorizados."} />
          <Card className="p-5">
            <p className="text-xs font-black uppercase tracking-[0.18em] text-[#b46c13]">Discente</p>
            <h2 className="mt-2 text-2xl font-black text-[#101b18]">{formatValue(state.data.discente)}</h2>
            <p className="mt-2 text-sm text-[#5f6764]">{state.data.aviso_privacidad || "Historial académico interno."}</p>
          </Card>
          <HistoryResultsTable items={state.data.resultados as Array<RecordValue>} />
          <HistoryEventsTable items={state.data.eventos as Array<RecordValue>} />
          <DataSection title="Extraordinarios" items={state.data.extraordinarios as Array<RecordValue>} />
          <HistoryMovementsTable items={state.data.movimientos as Array<RecordValue>} />
        </>
      ) : null}
    </div>
  );
}

export function HistoryResultsTable({ items }: { items: Array<RecordValue> }) {
  return <DataSection title="Resultados oficiales" items={items} columns={["periodo", "materia", "grupo", "tipo_resultado", "calificacion", "codigo_resultado", "codigo_marca"]} />;
}

export function HistoryEventsTable({ items }: { items: Array<RecordValue> }) {
  return <DataSection title="Eventos de situación académica" items={items} columns={["situacion", "periodo", "fecha_inicio", "fecha_fin", "motivo", "registrado_por"]} />;
}

export function HistoryMovementsTable({ items }: { items: Array<RecordValue> }) {
  return <DataSection title="Movimientos académicos" items={items} columns={["tipo_movimiento_label", "periodo", "grupo_origen", "grupo_destino", "fecha_movimiento", "observaciones"]} />;
}

export function ExtraordinaryList() {
  const [filters, setFilters] = useState<FilterState>({});
  const [state, setState] = useState<LoadState<Array<ExtraordinarioDTO>>>(emptyState);
  const load = useCallback(() => {
    setState({ data: null, loading: true, error: null });
    getExtraordinarios(filters)
      .then((data) => setState({ data: data.items, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [filters]);
  useEffect(() => { void load(); }, [load]);

  return <ListPage title="Extraordinarios registrados" description="Consulta de extraordinarios con filtros seguros." allowed={canAccessTrayectoriaInstitucional} filters={filters} setFilters={setFilters} fields={["periodo", "carrera", "grupo", "discente", "asignatura", "aprobado", "fecha_desde", "fecha_hasta"]} onSearch={load} state={state} detailBase="/trayectoria/extraordinarios" createHref="/trayectoria/extraordinarios/nuevo" createLabel="Registrar extraordinario" />;
}

export function ExtraordinaryForm() {
  const router = useRouter();
  const [payload, setPayload] = useState<FilterState>({});
  const [state, setState] = useState<{ saving: boolean; error: string | null; ok: string | null }>({ saving: false, error: null, ok: null });
  async function submit() {
    if (!window.confirm("Registrar extraordinario puede actualizar resultado vigente y situación académica según reglas backend. ¿Continuamos?")) return;
    setState({ saving: true, error: null, ok: null });
    try {
      const response = await crearExtraordinario(payload as unknown as { inscripcion_materia_id: string; calificacion: string; fecha_aplicacion?: string; observaciones?: string });
      setState({ saving: false, error: null, ok: "Extraordinario registrado correctamente." });
      router.push(`/trayectoria/extraordinarios/${response.item.id}`);
    } catch (error) {
      setState({ saving: false, error: error instanceof Error ? error.message : "No fue posible registrar el extraordinario.", ok: null });
    }
  }
  return <FormPage title="Registrar extraordinario" description="El backend valida acta FINAL formalizada, ordinario reprobatorio y duplicidad." allowed={canOperateTrayectoria} payload={payload} setPayload={setPayload} fields={["inscripcion_materia_id", "fecha_aplicacion", "calificacion", "observaciones"]} state={state} onSubmit={submit} submitLabel="Registrar extraordinario" />;
}

export function ExtraordinaryDetail({ id }: { id: string }) {
  return <DetailPage title="Detalle de extraordinario" description="Evidencia operativa del extraordinario registrado." allowed={canAccessTrayectoriaInstitucional} load={() => getExtraordinario(id).then((r) => r.item)} />;
}

export function AcademicSituationList() {
  const [filters, setFilters] = useState<FilterState>({});
  const [state, setState] = useState<LoadState<Array<SituacionAcademicaDTO>>>(emptyState);
  const load = useCallback(() => {
    setState({ data: null, loading: true, error: null });
    getSituaciones(filters)
      .then((data) => setState({ data: data.items, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [filters]);
  useEffect(() => { void load(); }, [load]);
  return <ListPage title="Situaciones académicas" description="Eventos de trayectoria: bajas, reingresos y situaciones vigentes." allowed={canAccessTrayectoriaInstitucional} filters={filters} setFilters={setFilters} fields={["discente", "situacion", "periodo", "carrera", "fecha_desde", "fecha_hasta"]} onSearch={load} state={state} detailBase="/trayectoria/situaciones" createHref="/trayectoria/situaciones/nuevo" createLabel="Registrar situación" />;
}

export function AcademicSituationForm() {
  const router = useRouter();
  const [payload, setPayload] = useState<FilterState>({});
  const [state, setState] = useState<{ saving: boolean; error: string | null; ok: string | null }>({ saving: false, error: null, ok: null });
  async function submit() {
    const code = payload.situacion_codigo || payload.situacion;
    const strong = code === "BAJA_DEFINITIVA" ? "Baja definitiva es una acción crítica. " : code === "REINGRESO" ? "Reingreso puede cerrar baja temporal abierta. " : "";
    if (!window.confirm(`${strong}El backend aplicará las reglas institucionales. ¿Continuamos?`)) return;
    setState({ saving: true, error: null, ok: null });
    try {
      const response = await crearSituacionAcademica(payload as unknown as { discente_id: string; situacion_codigo: string; periodo_id?: string; fecha_inicio?: string; fecha_fin?: string; motivo?: string; observaciones?: string });
      setState({ saving: false, error: null, ok: "Situación registrada correctamente." });
      router.push(`/trayectoria/situaciones/${response.item.id}`);
    } catch (error) {
      setState({ saving: false, error: error instanceof Error ? error.message : "No fue posible registrar la situación.", ok: null });
    }
  }
  return <FormPage title="Registrar situación académica" description="Usa códigos como BAJA_TEMPORAL, BAJA_DEFINITIVA o REINGRESO. El backend decide y valida." allowed={canOperateTrayectoria} payload={payload} setPayload={setPayload} fields={["discente_id", "situacion_codigo", "periodo_id", "fecha_inicio", "fecha_fin", "motivo", "observaciones"]} state={state} onSubmit={submit} submitLabel="Registrar situación" />;
}

export function AcademicSituationDetail({ id }: { id: string }) {
  return <DetailPage title="Detalle de situación académica" description="Evento académico preservado sin eliminar evidencia anterior." allowed={canAccessTrayectoriaInstitucional} load={() => getSituacion(id).then((r) => r.item)} />;
}

export function AcademicMovementsList() {
  const [filters, setFilters] = useState<FilterState>({});
  const [state, setState] = useState<LoadState<Array<MovimientoAcademicoDTO>>>(emptyState);
  const load = useCallback(() => {
    setState({ data: null, loading: true, error: null });
    getMovimientosAcademicos(filters)
      .then((data) => setState({ data: data.items, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [filters]);
  useEffect(() => { void load(); }, [load]);
  return <ListPage title="Movimientos académicos" description="Consulta de movimientos preservando evidencia académica." allowed={canAccessTrayectoriaInstitucional} filters={filters} setFilters={setFilters} fields={["periodo", "carrera", "grupo_origen", "grupo_destino", "discente", "tipo_movimiento", "fecha_desde", "fecha_hasta"]} onSearch={load} state={state} detailBase="/movimientos-academicos" createHref="/movimientos-academicos/nuevo" createLabel="Registrar movimiento" />;
}

export function AcademicMovementForm({ cambioGrupo = false }: { cambioGrupo?: boolean }) {
  const router = useRouter();
  const [payload, setPayload] = useState<FilterState>(cambioGrupo ? { tipo_movimiento: "cambio_grupo" } : {});
  const [state, setState] = useState<{ saving: boolean; error: string | null; ok: string | null }>({ saving: false, error: null, ok: null });
  async function submit() {
    if (!window.confirm("Este movimiento puede afectar adscripciones e inscripciones. El backend validará actas vivas y reglas de ámbito. ¿Continuamos?")) return;
    setState({ saving: true, error: null, ok: null });
    try {
      const response = cambioGrupo
        ? await crearCambioGrupo(payload as unknown as { discente_id: string; periodo_id: string; grupo_origen_id: string; grupo_destino_id: string; fecha_movimiento?: string; observaciones?: string })
        : await crearMovimientoAcademico(payload as unknown as { discente_id: string; periodo_id: string; tipo_movimiento: string; grupo_origen_id?: string; grupo_destino_id?: string; fecha_movimiento?: string; observaciones?: string });
      setState({ saving: false, error: null, ok: "Movimiento registrado correctamente." });
      router.push(`/movimientos-academicos/${response.item.id}`);
    } catch (error) {
      setState({ saving: false, error: error instanceof Error ? error.message : "No fue posible registrar el movimiento.", ok: null });
    }
  }
  return <FormPage title={cambioGrupo ? "Registrar cambio de grupo" : "Registrar movimiento académico"} description="No se borra evidencia previa. Las reglas transaccionales viven en backend." allowed={canOperateTrayectoria} payload={payload} setPayload={setPayload} fields={cambioGrupo ? ["discente_id", "periodo_id", "grupo_origen_id", "grupo_destino_id", "fecha_movimiento", "observaciones"] : ["discente_id", "periodo_id", "tipo_movimiento", "grupo_origen_id", "grupo_destino_id", "fecha_movimiento", "observaciones"]} state={state} onSubmit={submit} submitLabel={cambioGrupo ? "Aplicar cambio de grupo" : "Registrar movimiento"} />;
}

export function ChangeGroupForm() {
  return <AcademicMovementForm cambioGrupo />;
}

export function AcademicMovementDetail({ id }: { id: string }) {
  return <DetailPage title="Detalle de movimiento académico" description="Efecto operativo sobre adscripción e inscripciones cuando el backend lo reporta." allowed={canAccessTrayectoriaInstitucional} load={() => getMovimientoAcademico(id).then((r) => r.item)} />;
}

export function PeriodsOperationalList() {
  const [state, setState] = useState<LoadState<Array<PeriodoOperativoDTO>>>(emptyState);
  useEffect(() => {
    setState({ data: null, loading: true, error: null });
    getPeriodos()
      .then((data) => setState({ data: data.items, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, []);
  return (
    <AccessPage title="Periodos operativos" description="Diagnóstico, cierre, apertura y pendientes de asignación docente." allowed={canAccessPeriodosOperativos}>
      {(user) => (
        <div className="space-y-5">
          <div className="flex flex-wrap gap-2">
            <LinkButton href="/periodos/cierres">Procesos de cierre</LinkButton>
            {canOperateTrayectoria(user) ? <LinkButton href="/periodos/apertura">Abrir periodo</LinkButton> : null}
            <LinkButton href="/periodos/aperturas">Procesos de apertura</LinkButton>
            <LinkButton href="/periodos/pendientes-asignacion-docente">Pendientes de asignación docente</LinkButton>
          </div>
          <StateBlock state={state} loadingLabel="Cargando periodos..." emptyTitle="No hay periodos registrados." />
          <div className="grid gap-4 xl:grid-cols-2">
            {(state.data || []).map((periodo) => <PeriodCard key={periodo.id} periodo={periodo} canOperate={canOperateTrayectoria(user)} />)}
          </div>
        </div>
      )}
    </AccessPage>
  );
}

function PeriodCard({ periodo, canOperate }: { periodo: PeriodoOperativoDTO; canOperate: boolean }) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.18em] text-[#b46c13]">{periodo.estado_label || periodo.estado}</p>
          <h2 className="mt-2 text-xl font-black text-[#101b18]">{periodo.label || periodo.clave}</h2>
          <p className="mt-1 text-sm text-[#5f6764]">{periodo.fecha_inicio} a {periodo.fecha_fin}</p>
        </div>
        <PeriodStatusBadge estado={periodo.estado || ""} label={periodo.estado_label || ""} />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {periodo.acciones?.puede_diagnosticar ? <LinkButton href={`/periodos/${periodo.id}/diagnostico`}>Diagnosticar cierre</LinkButton> : null}
        {canOperate && periodo.acciones?.puede_usarse_como_origen_apertura ? <LinkButton href="/periodos/apertura">Usar como origen</LinkButton> : null}
      </div>
    </Card>
  );
}

export function PeriodStatusBadge({ estado, label }: { estado: string; label: string }) {
  const color = estado === "cerrado" ? "bg-[#f4eee2] text-[#72530d]" : estado === "activo" ? "bg-[#edf8f2] text-[#0b4a3d]" : "bg-[#fff5f8] text-[#7a123d]";
  return <span className={`rounded-full px-3 py-1 text-xs font-black uppercase tracking-[0.16em] ${color}`}>{label || estado}</span>;
}

export function ClosureDiagnosticPanel({ periodoId }: { periodoId: string }) {
  const [state, setState] = useState<LoadState<DiagnosticoCierrePeriodoDTO>>(emptyState);
  const [observaciones, setObservaciones] = useState("");
  const [saving, setSaving] = useState(false);
  const router = useRouter();
  const load = useCallback(() => {
    setState({ data: null, loading: true, error: null });
    getDiagnosticoCierrePeriodo(periodoId)
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [periodoId]);
  useEffect(() => { void load(); }, [load]);

  async function closePeriod() {
    if (!window.confirm("Cerrar un periodo cambia su estado y genera evidencia de cierre. No promueve discentes ni abre el siguiente periodo. ¿Continuamos?")) return;
    setSaving(true);
    try {
      const response = await cerrarPeriodo(periodoId, { observaciones });
      router.push(`/periodos/cierres/${response.item.id}`);
    } catch (error) {
      setState((current) => ({ ...current, error: error instanceof Error ? error.message : "No fue posible cerrar el periodo." }));
    } finally {
      setSaving(false);
    }
  }

  return (
    <AccessPage title="Diagnóstico de cierre" description="El diagnóstico no modifica datos; solo evalúa bloqueantes y advertencias." allowed={canAccessPeriodosOperativos}>
      {(user) => (
        <div className="space-y-5">
          <StateBlock state={state} loadingLabel="Diagnosticando periodo..." emptyTitle="No hay diagnóstico." />
          {state.data ? (
            <>
              <MetricGrid resumen={state.data.resumen} />
              <ClosureBlockersList title="Bloqueantes" items={state.data.bloqueantes} tone="danger" />
              <ClosureBlockersList title="Advertencias" items={state.data.advertencias} tone="warning" />
              <ClosureStudentClassificationTable diagnostico={state.data} />
              <ClosePeriodActionPanel canOperate={canOperateTrayectoria(user)} canClose={state.data.puede_cerrar} observaciones={observaciones} setObservaciones={setObservaciones} saving={saving} onClose={closePeriod} />
            </>
          ) : null}
        </div>
      )}
    </AccessPage>
  );
}

export function ClosureBlockersList({ title, items, tone }: { title: string; items: Array<unknown>; tone: "danger" | "warning" }) {
  if (!items.length) return <EmptyState title={`Sin ${title.toLowerCase()}.`} description="El backend no reportó elementos en esta categoría." />;
  const color = tone === "danger" ? "border-[#7a123d]/30 bg-[#fff5f8] text-[#7a123d]" : "border-[#d4af37]/40 bg-[#fff8e6] text-[#72530d]";
  return (
    <Card className="p-5">
      <h2 className="text-lg font-black text-[#101b18]">{title}</h2>
      <ul className="mt-3 space-y-2">
        {items.map((item, index) => <li key={`${title}-${index}`} className={`rounded-2xl border px-4 py-3 text-sm font-bold ${color}`}>{formatValue(item)}</li>)}
      </ul>
    </Card>
  );
}

export function ClosureStudentClassificationTable({ diagnostico }: { diagnostico: DiagnosticoCierrePeriodoDTO }) {
  const rows = [
    ...(diagnostico.discentes_promovibles || []).map((item) => ({ ...item, clasificacion: "Promovible" })),
    ...(diagnostico.discentes_pendientes_extraordinario || []).map((item) => ({ ...item, clasificacion: "Extraordinario pendiente" })),
    ...(diagnostico.discentes_baja_temporal || []).map((item) => ({ ...item, clasificacion: "Baja temporal" })),
    ...(diagnostico.discentes_baja_definitiva || []).map((item) => ({ ...item, clasificacion: "Baja definitiva" })),
    ...(diagnostico.discentes_egresables || []).map((item) => ({ ...item, clasificacion: "Egresable" })),
  ];
  return <DataSection title="Clasificación de discentes" items={rows} columns={["clasificacion", "discente_id", "nombre", "grupo", "motivo"]} />;
}

export function ClosePeriodActionPanel({ canOperate, canClose, observaciones, setObservaciones, saving, onClose }: { canOperate: boolean; canClose: boolean; observaciones: string; setObservaciones: (value: string) => void; saving: boolean; onClose: () => void }) {
  return (
    <Card className="border-[#7a123d]/20 bg-[#fff8e6] p-5">
      <h2 className="text-lg font-black text-[#101b18]">Cierre de periodo</h2>
      <p className="mt-2 text-sm leading-6 text-[#5f6764]">{canOperate ? "Cerrar genera evidencia de cierre. La promoción y apertura ocurren en otro paso." : "Consulta de diagnóstico. Tu perfil no ejecuta el cierre desde el portal."}</p>
      {canOperate ? (
        <>
          <textarea className="mt-4 min-h-28 w-full rounded-2xl border border-[#d8c5a7] bg-white px-4 py-3 text-sm outline-none focus:border-[#7a123d]" value={observaciones} onChange={(event) => setObservaciones(event.target.value)} placeholder="Observaciones opcionales" />
          <Button className="mt-3" disabled={!canClose || saving} onClick={onClose}>{saving ? "Cerrando..." : "Cerrar periodo"}</Button>
          {!canClose ? <p className="mt-2 text-sm font-bold text-[#7a123d]">El cierre está bloqueado por el diagnóstico.</p> : null}
        </>
      ) : null}
    </Card>
  );
}

export function ClosureProcessDetail({ id }: { id: string }) {
  return <DetailPage title="Proceso de cierre" description="Evidencia generada por el cierre de periodo." allowed={canAccessPeriodosOperativos} load={() => getCierre(id).then((r) => r.item)} extra={(item) => item.detalles ? <DataSection title="Detalles por discente" items={item.detalles as Array<RecordValue>} /> : null} />;
}

export function OpeningPeriodForm() {
  const router = useRouter();
  const [payload, setPayload] = useState<FilterState>({});
  const [state, setState] = useState<{ saving: boolean; error: string | null; ok: string | null }>({ saving: false, error: null, ok: null });
  async function submit() {
    if (!window.confirm("La apertura promoverá únicamente discentes promovibles y creará/actualizará adscripciones y grupos destino de forma idempotente. ¿Continuamos?")) return;
    setState({ saving: true, error: null, ok: null });
    try {
      const response = await crearAperturaPeriodo(payload as unknown as { periodo_origen_id: string; periodo_destino_id: string; observaciones?: string });
      router.push(`/periodos/aperturas/${response.item.id}`);
    } catch (error) {
      setState({ saving: false, error: error instanceof Error ? error.message : "No fue posible ejecutar la apertura.", ok: null });
    }
  }
  return <FormPage title="Apertura de periodo" description="Promueve solo discentes promovibles desde un origen cerrado. No asigna docentes automáticamente." allowed={canOperateTrayectoria} payload={payload} setPayload={setPayload} fields={["periodo_origen_id", "periodo_destino_id", "observaciones"]} state={state} onSubmit={submit} submitLabel="Ejecutar apertura" />;
}

export function ClosureProcessesList() {
  return <ProcessList title="Procesos de cierre" description="Cierres de periodo ejecutados." allowed={canAccessPeriodosOperativos} load={getCierres} detailBase="/periodos/cierres" />;
}

export function OpeningProcessesList() {
  return <ProcessList title="Procesos de apertura" description="Aperturas de periodo ejecutadas." allowed={canAccessPeriodosOperativos} load={getAperturas} detailBase="/periodos/aperturas" />;
}

export function OpeningProcessDetail({ id }: { id: string }) {
  return <DetailPage title="Proceso de apertura" description="Resultado de promoción y creación/reuso de grupos destino." allowed={canAccessPeriodosOperativos} load={() => getApertura(id).then((r) => r.item)} />;
}

export function PendingTeacherAssignmentsTable() {
  const [filters, setFilters] = useState<FilterState>({});
  const [state, setState] = useState<LoadState<Array<PendienteAsignacionDocenteDTO>>>(emptyState);
  const load = useCallback(() => {
    setState({ data: null, loading: true, error: null });
    getPendientesAsignacionDocente(filters)
      .then((data) => setState({ data: data.items, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [filters]);
  useEffect(() => { void load(); }, [load]);
  return (
    <AccessPage title="Pendientes de asignación docente" description="Materias sin docente asignado para el periodo seleccionado." allowed={canAccessPeriodosOperativos}>
      {() => (
        <div className="space-y-5">
          <FiltersBar filters={filters} setFilters={setFilters} fields={["periodo", "carrera", "grupo", "semestre"]} onSearch={load} />
          <StateBlock state={state} loadingLabel="Cargando pendientes..." emptyTitle="No hay pendientes con los filtros seleccionados." />
          {state.data ? <DataTable items={state.data as Array<RecordValue>} columns={["periodo", "carrera", "grupo", "materia", "programa_asignatura", "estado", "accion_sugerida"]} /> : null}
        </div>
      )}
    </AccessPage>
  );
}

function ProcessList<T extends { id: number }>({ title, description, allowed, load, detailBase }: { title: string; description: string; allowed: (user: AuthenticatedUser) => boolean; load: () => Promise<{ items: T[] }>; detailBase: string }) {
  const [state, setState] = useState<LoadState<T[]>>(emptyState);
  useEffect(() => {
    setState({ data: null, loading: true, error: null });
    load()
      .then((data) => setState({ data: data.items, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [load]);
  return (
    <AccessPage title={title} description={description} allowed={allowed}>
      {() => (
        <div className="space-y-5">
          <StateBlock state={state} loadingLabel="Cargando procesos..." emptyTitle="No hay procesos registrados." />
          {state.data ? <DataTable items={state.data as Array<RecordValue>} detailBase={detailBase} detailKey="id" /> : null}
        </div>
      )}
    </AccessPage>
  );
}

function ListPage<T extends { id: number }>({ title, description, allowed, filters, setFilters, fields, onSearch, state, detailBase, createHref, createLabel }: { title: string; description: string; allowed: (user: AuthenticatedUser) => boolean; filters: FilterState; setFilters: (value: FilterState) => void; fields: string[]; onSearch: () => void; state: LoadState<T[]>; detailBase: string; createHref?: string; createLabel?: string }) {
  return (
    <AccessPage title={title} description={description} allowed={allowed}>
      {(user) => (
        <div className="space-y-5">
          <div className="flex flex-wrap gap-2">
            {createHref && canOperateTrayectoria(user) ? <LinkButton href={createHref}>{createLabel || "Nuevo"}</LinkButton> : null}
          </div>
          <FiltersBar filters={filters} setFilters={setFilters} fields={fields} onSearch={onSearch} />
          <StateBlock state={state} loadingLabel="Cargando registros..." emptyTitle="No hay registros para los filtros seleccionados." />
          {state.data ? <DataTable items={state.data as Array<RecordValue>} detailBase={detailBase} detailKey="id" /> : null}
        </div>
      )}
    </AccessPage>
  );
}

function FormPage({ title, description, allowed, payload, setPayload, fields, state, onSubmit, submitLabel }: { title: string; description: string; allowed: (user: AuthenticatedUser) => boolean; payload: FilterState; setPayload: (value: FilterState) => void; fields: string[]; state: { saving: boolean; error: string | null; ok: string | null }; onSubmit: () => void; submitLabel: string }) {
  return (
    <AccessPage title={title} description={description} allowed={allowed}>
      {() => (
        <Card className="p-5">
          <SensitiveInfoNotice text="Captura únicamente IDs internos autorizados. No uses matrícula militar." />
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {fields.map((field) => (
              <SmartFormField
                key={field}
                field={field}
                payload={payload}
                onChange={(value) => setPayload({ ...payload, [field]: value })}
              />
            ))}
          </div>
          {state.error ? <div className="mt-4"><ErrorMessage message={state.error} /></div> : null}
          {state.ok ? <OperationSuccessNotice text={state.ok} /> : null}
          <Button className="mt-4" disabled={state.saving} onClick={onSubmit}>{state.saving ? "Guardando..." : submitLabel}</Button>
        </Card>
      )}
    </AccessPage>
  );
}

function SmartFormField({ field, payload, onChange }: { field: string; payload: FilterState; onChange: (value: string) => void }) {
  const value = payload[field] || "";
  if (field === "inscripcion_materia_id") {
    return (
      <AsyncSelectField
        label={labelFor(field)}
        value={value}
        onChange={onChange}
        searchEnabled
        loadOptions={(q) => getOpcionesInscripcionesExtraordinario({ q, page_size: "50" }).then((data) => data.items.map((item) => ({ value: String(item.inscripcion_materia_id), label: item.label })))}
      />
    );
  }
  if (field === "discente_id") {
    return (
      <AsyncSelectField
        label={labelFor(field)}
        value={value}
        onChange={onChange}
        searchEnabled
        loadOptions={(q) => buscarHistoriales({ q, page_size: "50" }).then((data) => data.items.map((item) => ({ value: String(item.id), label: formatValue(item) })))}
      />
    );
  }
  if (field === "situacion_codigo") {
    return (
      <AsyncSelectField
        label={labelFor(field)}
        value={value}
        onChange={onChange}
        loadOptions={() => listResource("/api/catalogos/situaciones-academicas/", { activo: "true", page_size: "100" }).then((data) => data.items.map((item) => ({ value: String(item.clave), label: optionLabel(item) })))}
      />
    );
  }
  if (field === "periodo_id") {
    return (
      <AsyncSelectField
        label={labelFor(field)}
        value={value}
        onChange={onChange}
        loadOptions={() => getPeriodos({ estado: "activo", page_size: "100" }).then((data) => data.items.map((item) => ({ value: String(item.id), label: optionLabel(item) })))}
      />
    );
  }
  if (field === "periodo_origen_id") {
    return (
      <AsyncSelectField
        label={labelFor(field)}
        value={value}
        onChange={onChange}
        loadOptions={() => getPeriodos({ estado: "cerrado", page_size: "100" }).then((data) => data.items.map((item) => ({ value: String(item.id), label: optionLabel(item) })))}
      />
    );
  }
  if (field === "periodo_destino_id") {
    return (
      <AsyncSelectField
        label={labelFor(field)}
        value={value}
        onChange={onChange}
        loadOptions={async () => {
          const [planificados, activos] = await Promise.all([
            getPeriodos({ estado: "planificado", page_size: "100" }),
            getPeriodos({ estado: "activo", page_size: "100" }),
          ]);
          return [...planificados.items, ...activos.items].map((item) => ({ value: String(item.id), label: optionLabel(item) }));
        }}
      />
    );
  }
  if (field === "tipo_movimiento") {
    return (
      <StaticSelectField
        label={labelFor(field)}
        value={value}
        onChange={onChange}
        options={[
          { value: "cambio_grupo", label: "Cambio de grupo" },
          { value: "alta_extemporanea", label: "Alta extemporánea" },
          { value: "baja_extemporanea", label: "Baja extemporánea" },
        ]}
      />
    );
  }
  if (field === "grupo_origen_id" || field === "grupo_destino_id") {
    const excludeValue = field === "grupo_destino_id" ? payload.grupo_origen_id : "";
    return (
      <AsyncSelectField
        label={labelFor(field)}
        value={value}
        onChange={onChange}
        searchEnabled
        disabled={!payload.periodo_id}
        helper={!payload.periodo_id ? "Selecciona primero el periodo." : undefined}
        loadOptions={(q) => listResource("/api/catalogos/grupos/", { activo: "true", periodo: payload.periodo_id, q, page_size: "100" }).then((data) => data.items.filter((item) => String(item.id) !== String(excludeValue)).map((item) => ({ value: String(item.id), label: optionLabel(item) })))}
        reloadKey={payload.periodo_id}
      />
    );
  }
  if (field === "calificacion") {
    return <TextField label={labelFor(field)} value={value} onChange={onChange} type="number" min="0" max="10" step="0.1" />;
  }
  return <TextField label={labelFor(field)} value={value} onChange={onChange} textarea={field === "observaciones" || field === "motivo"} type={field.startsWith("fecha") ? "date" : "text"} />;
}

function AsyncSelectField({ label, value, onChange, loadOptions, searchEnabled = false, disabled = false, helper, reloadKey = "" }: { label: string; value: string; onChange: (value: string) => void; loadOptions: (q: string) => Promise<SelectOption[]>; searchEnabled?: boolean; disabled?: boolean; helper?: string; reloadKey?: string }) {
  const [options, setOptions] = useState<SelectOption[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    if (disabled) {
      setOptions([]);
      return;
    }
    loadOptions(search)
      .then((items) => {
        if (active) setOptions(items);
      })
      .catch((err) => {
        if (active) setError(err instanceof Error ? err.message : "No fue posible cargar opciones.");
      });
    return () => {
      active = false;
    };
  }, [disabled, loadOptions, reloadKey, search]);
  return (
    <label className="block">
      <span className="text-xs font-black uppercase tracking-[0.16em] text-[#7a4b0d]">{label}</span>
      {searchEnabled ? <input className="mt-2 w-full rounded-2xl border border-[#d8c5a7] bg-white px-4 py-3 text-sm outline-none focus:border-[#7a123d]" value={search} disabled={disabled} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar..." /> : null}
      <select className="mt-2 w-full rounded-2xl border border-[#d8c5a7] bg-white px-4 py-3 text-sm outline-none focus:border-[#7a123d] disabled:bg-[#f5efe6] disabled:text-[#8a8176]" value={value} disabled={disabled} onChange={(event) => onChange(event.target.value)}>
        <option value="">Seleccionar</option>
        {options.map((option) => <option key={`${label}-${option.value}`} value={option.value}>{option.label}</option>)}
      </select>
      {helper ? <span className="mt-1 block text-xs font-bold text-[#7a4b0d]">{helper}</span> : null}
      {error ? <span className="mt-1 block text-xs font-bold text-[#7a123d]">{error}</span> : null}
    </label>
  );
}

function StaticSelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: SelectOption[] }) {
  return (
    <label className="block">
      <span className="text-xs font-black uppercase tracking-[0.16em] text-[#7a4b0d]">{label}</span>
      <select className="mt-2 w-full rounded-2xl border border-[#d8c5a7] bg-white px-4 py-3 text-sm outline-none focus:border-[#7a123d]" value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Seleccionar</option>
        {options.map((option) => <option key={`${label}-${option.value}`} value={option.value}>{option.label}</option>)}
      </select>
    </label>
  );
}

function DetailPage<T extends RecordValue>({ title, description, allowed, load, extra }: { title: string; description: string; allowed: (user: AuthenticatedUser) => boolean; load: () => Promise<T>; extra?: (item: T) => ReactNode }) {
  const [state, setState] = useState<LoadState<T>>(emptyState);
  useEffect(() => {
    setState({ data: null, loading: true, error: null });
    load()
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((error: Error) => setState({ data: null, loading: false, error: error.message }));
  }, [load]);
  return (
    <AccessPage title={title} description={description} allowed={allowed}>
      {() => (
        <div className="space-y-5">
          <StateBlock state={state} loadingLabel="Cargando detalle..." emptyTitle="No se encontró el registro." />
          {state.data ? <DataSection title="Detalle" items={[state.data]} /> : null}
          {state.data && extra ? extra(state.data) : null}
        </div>
      )}
    </AccessPage>
  );
}

function DataSection({ title, items, columns }: { title: string; items: Array<RecordValue>; columns?: string[] }) {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-black text-[#101b18]">{title}</h2>
        <span className="rounded-full bg-[#fff4df] px-3 py-1 text-xs font-black text-[#7a4b0d]">{items.length} registros</span>
      </div>
      <div className="mt-4">
        <DataTable items={items} columns={columns} />
      </div>
    </Card>
  );
}

function DataTable({ items, columns, detailBase, detailKey }: { items: Array<RecordValue>; columns?: string[]; detailBase?: string; detailKey?: string }) {
  const keys = useMemo(() => columns || Array.from(new Set(items.flatMap((item) => Object.keys(item)))).filter((key) => !["url_detalle"].includes(key)).slice(0, 8), [columns, items]);
  if (!items.length) return <EmptyState title="Sin registros." description="No hay datos para mostrar." />;
  return (
    <div className="overflow-x-auto rounded-[1.25rem] border border-[#eadfce]">
      <table className="min-w-full divide-y divide-[#eadfce] text-sm">
        <thead className="bg-[#fff8e6]">
          <tr>
            {keys.map((key) => <th key={key} className="px-4 py-3 text-left text-xs font-black uppercase tracking-[0.16em] text-[#7a4b0d]">{labelFor(key)}</th>)}
            {detailBase ? <th className="px-4 py-3 text-left text-xs font-black uppercase tracking-[0.16em] text-[#7a4b0d]">Acción</th> : null}
          </tr>
        </thead>
        <tbody className="divide-y divide-[#f0e4d1] bg-white">
          {items.map((item, index) => (
            <tr key={`${detailBase || "row"}-${String(item.id ?? index)}`}>
              {keys.map((key) => <td key={key} className="max-w-[340px] px-4 py-3 align-top text-[#24342f]">{formatValue(item[key])}</td>)}
              {detailBase ? <td className="px-4 py-3"><Link className="font-black text-[#7a123d]" href={`${detailBase}/${encodeURIComponent(String(item[detailKey || "id"]))}`}>Ver detalle</Link></td> : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FiltersBar({ filters, setFilters, fields, onSearch }: { filters: FilterState; setFilters: (value: FilterState) => void; fields: string[]; onSearch: () => void }) {
  return (
    <Card className="p-5">
      <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-4">
        {fields.map((field) => <TextField key={field} label={labelFor(field)} value={filters[field] || ""} onChange={(value) => setFilters({ ...filters, [field]: value })} type={field.startsWith("fecha") ? "date" : "text"} />)}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button onClick={onSearch}>Actualizar</Button>
        <button className="rounded-xl border border-[#d8c5a7] px-4 py-2 text-sm font-black text-[#6f4a16]" onClick={() => setFilters({})} type="button">Limpiar filtros</button>
      </div>
    </Card>
  );
}

function TextField({ label, value, onChange, type = "text", textarea = false, min, max, step }: { label: string; value: string; onChange: (value: string) => void; type?: string; textarea?: boolean; min?: string; max?: string; step?: string }) {
  const className = "w-full rounded-2xl border border-[#d8c5a7] bg-white px-4 py-3 text-sm outline-none focus:border-[#7a123d]";
  return (
    <label className="block">
      <span className="text-xs font-black uppercase tracking-[0.16em] text-[#7a4b0d]">{label}</span>
      {textarea ? <textarea className={`${className} mt-2 min-h-28`} value={value} onChange={(event) => onChange(event.target.value)} /> : <input className={`${className} mt-2`} type={type} min={min} max={max} step={step} value={value} onChange={(event) => onChange(event.target.value)} />}
    </label>
  );
}

function optionLabel(item: unknown) {
  if (!item || typeof item !== "object") return String(item ?? "Opción");
  const record = item as RecordValue;
  return String(record.label || record.nombre_institucional || record.nombre || record.clave || record.username || record.id || "Opción");
}

function StateBlock<T>({ state, loadingLabel, emptyTitle }: { state: LoadState<T>; loadingLabel: string; emptyTitle: string }) {
  if (state.loading) return <LoadingState label={loadingLabel} />;
  if (state.error) return <ErrorMessage message={state.error} />;
  if (!state.data) return null;
  if (Array.isArray(state.data) && state.data.length === 0) return <EmptyState title={emptyTitle} description="Ajusta filtros o intenta nuevamente más tarde." />;
  return null;
}

function MetricGrid({ resumen }: { resumen: Record<string, number> }) {
  return (
    <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
      {Object.entries(resumen).map(([key, value]) => <Card key={key} className="p-4"><p className="text-xs font-black uppercase tracking-[0.16em] text-[#b46c13]">{labelFor(key)}</p><p className="mt-2 text-2xl font-black text-[#101b18]">{value}</p></Card>)}
    </div>
  );
}

export function MovementImpactSummary({ impacto }: { impacto?: Record<string, unknown> }) {
  if (!impacto) return null;
  return <DataSection title="Impacto del movimiento" items={[impacto]} />;
}

export function MovementSafetyNotice() {
  return <SensitiveInfoNotice text="Los movimientos no borran evidencia previa y pueden bloquearse si existen actas vivas." />;
}

export function HistoryPrivacyNotice() {
  return <SensitiveInfoNotice text="Este historial interno es sensible y no debe presentarse como kárdex oficial." />;
}

export function SensitiveInfoNotice({ text }: { text: string }) {
  return <div className="rounded-2xl border border-[#d4af37]/35 bg-[#fff8e6] px-4 py-3 text-sm font-bold text-[#72530d]">{text}</div>;
}

export function OperationSuccessNotice({ text }: { text: string }) {
  return <div className="mt-4 rounded-2xl border border-[#0b4a3d]/20 bg-[#edf8f2] px-4 py-3 text-sm font-bold text-[#0b4a3d]">{text}</div>;
}

export function OperationWarningNotice({ text }: { text: string }) {
  return <div className="rounded-2xl border border-[#d4af37]/40 bg-[#fff8e6] px-4 py-3 text-sm font-bold text-[#72530d]">{text}</div>;
}

export function AccessDeniedState() {
  return <ErrorMessage message="No tienes permiso para realizar esta operación." />;
}

function LinkButton({ href, children }: { href: string; children: ReactNode }) {
  return <Link className="rounded-xl bg-[#7a123d] px-4 py-2 text-sm font-black text-white shadow-sm" href={href}>{children}</Link>;
}

function labelFor(key: string) {
  const labels: Record<string, string> = {
    q: "Búsqueda",
    carrera: "Carrera ID",
    grupo: "Grupo ID",
    plan: "Plan ID",
    antiguedad: "Antigüedad ID",
    situacion: "Situación",
    situacion_codigo: "Código de situación",
    periodo: "Periodo ID",
    periodo_id: "Periodo ID",
    periodo_origen_id: "Periodo origen ID",
    periodo_destino_id: "Periodo destino ID",
    discente: "Discente ID",
    discente_id: "Discente ID",
    asignatura: "Asignatura ID",
    aprobado: "Aprobado true/false",
    fecha_desde: "Fecha desde",
    fecha_hasta: "Fecha hasta",
    fecha_aplicacion: "Fecha aplicación",
    fecha_inicio: "Fecha inicio",
    fecha_fin: "Fecha fin",
    calificacion: "Calificación",
    inscripcion_materia_id: "Inscripción materia ID",
    tipo_movimiento: "Tipo movimiento",
    tipo_movimiento_label: "Tipo movimiento",
    grupo_origen: "Grupo origen ID",
    grupo_origen_id: "Grupo origen ID",
    grupo_destino: "Grupo destino ID",
    grupo_destino_id: "Grupo destino ID",
    fecha_movimiento: "Fecha movimiento",
    observaciones: "Observaciones",
    motivo: "Motivo",
    codigo_marca: "Marca",
  };
  return labels[key] || key.replaceAll("_", " ");
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "boolean") return value ? "Sí" : "No";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(1);
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.length ? value.map(formatValue).join(", ") : "N/A";
  if (typeof value === "object") {
    const obj = value as RecordValue;
    return String(obj.label || obj.nombre_institucional || obj.nombre || obj.clave || obj.username || obj.id || JSON.stringify(obj));
  }
  return String(value);
}
