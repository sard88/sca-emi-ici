"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyExportsState } from "@/components/reportes/EmptyExportsState";
import { ExportHistoryTable } from "@/components/reportes/ExportHistoryTable";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { AuditEventDetailDrawer, ProcessStateBadge, SensitiveTraceNotice } from "@/components/trazabilidad";
import { descargarAuditoriaEventosXlsx, getAuditoriaEventos, getAuditoriaExportaciones, getAuditoriaResumen } from "@/lib/api";
import { canAccessAuditoria, canAccessAuditoriaEventos, canAccessAuditoriaExportaciones } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";
import type { AuditEventDTO, AuditEventSummaryDTO, ExportacionRegistro } from "@/lib/types";

type Tab = "exportaciones" | "eventos";

const MODULOS = [
  "AUTENTICACION",
  "ADMINISTRACION",
  "CATALOGOS",
  "EVALUACION",
  "ACTAS",
  "CONFORMIDAD",
  "TRAYECTORIA",
  "MOVIMIENTOS",
  "PERIODOS",
  "REPORTES",
  "EXPORTACIONES",
];

export default function AuditoriaExportacionesPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("exportaciones");
  const [exportaciones, setExportaciones] = useState<ExportacionRegistro[]>([]);
  const [eventos, setEventos] = useState<AuditEventDTO[]>([]);
  const [resumenEventos, setResumenEventos] = useState<AuditEventSummaryDTO | null>(null);
  const [eventoDetalle, setEventoDetalle] = useState<AuditEventDTO | null>(null);
  const [totalEventos, setTotalEventos] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [folio, setFolio] = useState<string | null>(null);
  const [fechaDesde, setFechaDesde] = useState("");
  const [fechaHasta, setFechaHasta] = useState("");
  const [usuario, setUsuario] = useState("");
  const [estado, setEstado] = useState("");
  const [modulo, setModulo] = useState("");
  const [evento, setEvento] = useState("");
  const [resultado, setResultado] = useState("");
  const [severidad, setSeveridad] = useState("");
  const canExportaciones = user ? canAccessAuditoriaExportaciones(user) : false;
  const canEventos = user ? canAccessAuditoriaEventos(user) : false;
  const canAuditoria = user ? canAccessAuditoria(user) : false;
  const showTabs = canExportaciones && canEventos;

  const filtrosExportaciones = useMemo(() => ({
    limit: "120",
    fecha_desde: fechaDesde,
    fecha_hasta: fechaHasta,
    usuario,
    estado,
  }), [estado, fechaDesde, fechaHasta, usuario]);

  const filtrosEventos = useMemo(() => ({
    page_size: "50",
    fecha_desde: fechaDesde,
    fecha_hasta: fechaHasta,
    usuario,
    modulo,
    evento_codigo: evento,
    resultado,
    severidad,
  }), [evento, fechaDesde, fechaHasta, modulo, resultado, severidad, usuario]);

  useEffect(() => {
    if (!user || !canAuditoria) return;
    if (tab === "exportaciones" && !canExportaciones) {
      setTab("eventos");
      return;
    }
    if (tab === "eventos" && !canEventos) {
      setTab("exportaciones");
      return;
    }

    async function load() {
      setLoading(true);
      setError(null);
      try {
        if (tab === "exportaciones") {
          const response = await getAuditoriaExportaciones(filtrosExportaciones);
          setExportaciones(response.items);
        } else {
          const response = await getAuditoriaEventos(filtrosEventos);
          setEventos(response.items);
          setTotalEventos(response.total);
          getAuditoriaResumen(filtrosEventos)
            .then(setResumenEventos)
            .catch(() => setResumenEventos(null));
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar la auditoría institucional.");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [canAuditoria, canEventos, canExportaciones, filtrosEventos, filtrosExportaciones, tab, user]);

  async function descargarEventos() {
    setError(null);
    setFolio(null);
    try {
      const result = await descargarAuditoriaEventosXlsx(filtrosEventos);
      setFolio(result.registroExportacionId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible descargar la bitácora.");
    }
  }

  return (
    <AppShell>
      {!user ? null : !canAuditoria ? (
        <ErrorMessage message="No tienes permiso para consultar la auditoría institucional." />
      ) : (
        <div className="space-y-5">
          <PageHeader
            title="Auditoría institucional"
            description="Consulta eventos críticos transversales y exportaciones auditadas según permisos separados."
            user={user}
          />

          {showTabs ? (
            <div className="flex flex-wrap gap-2 border-b border-[#eadfce]">
              <button type="button" onClick={() => setTab("exportaciones")} className={tabClass(tab === "exportaciones")}>Exportaciones auditadas</button>
              <button type="button" onClick={() => setTab("eventos")} className={tabClass(tab === "eventos")}>Eventos críticos</button>
            </div>
          ) : null}

          <section className="rounded-lg border border-[#eadfce] bg-white p-4 shadow-sm">
            <div className="grid gap-3 md:grid-cols-4">
              <input type="date" value={fechaDesde} onChange={(event) => setFechaDesde(event.target.value)} className="h-11 rounded-lg border border-[#e4d6c2] bg-white px-3 text-sm outline-none focus:border-[#bc955c]" />
              <input type="date" value={fechaHasta} onChange={(event) => setFechaHasta(event.target.value)} className="h-11 rounded-lg border border-[#e4d6c2] bg-white px-3 text-sm outline-none focus:border-[#bc955c]" />
              <input value={usuario} onChange={(event) => setUsuario(event.target.value)} placeholder="Usuario o nombre..." className="h-11 rounded-lg border border-[#e4d6c2] bg-white px-3 text-sm outline-none focus:border-[#bc955c]" />
              {tab === "exportaciones" ? (
                <select value={estado} onChange={(event) => setEstado(event.target.value)} className="h-11 rounded-lg border border-[#e4d6c2] bg-white px-3 text-sm outline-none focus:border-[#bc955c]">
                  <option value="">Todos los estados</option>
                  <option value="GENERADA">Generada</option>
                  <option value="FALLIDA">Fallida</option>
                  <option value="SOLICITADA">Solicitada</option>
                </select>
              ) : (
                <select value={modulo} onChange={(event) => setModulo(event.target.value)} className="h-11 rounded-lg border border-[#e4d6c2] bg-white px-3 text-sm outline-none focus:border-[#bc955c]">
                  <option value="">Todos los módulos</option>
                  {MODULOS.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              )}
            </div>
            {tab === "eventos" ? (
              <div className="mt-3 grid gap-3 md:grid-cols-4">
                <input value={evento} onChange={(event) => setEvento(event.target.value.toUpperCase())} placeholder="Código de evento..." className="h-11 rounded-lg border border-[#e4d6c2] bg-white px-3 text-sm outline-none focus:border-[#bc955c]" />
                <select value={resultado} onChange={(event) => setResultado(event.target.value)} className="h-11 rounded-lg border border-[#e4d6c2] bg-white px-3 text-sm outline-none focus:border-[#bc955c]">
                  <option value="">Todos los resultados</option>
                  <option value="EXITOSO">Exitoso</option>
                  <option value="FALLIDO">Fallido</option>
                  <option value="BLOQUEADO">Bloqueado</option>
                </select>
                <select value={severidad} onChange={(event) => setSeveridad(event.target.value)} className="h-11 rounded-lg border border-[#e4d6c2] bg-white px-3 text-sm outline-none focus:border-[#bc955c]">
                  <option value="">Todas las severidades</option>
                  <option value="INFO">Info</option>
                  <option value="ADVERTENCIA">Advertencia</option>
                  <option value="CRITICO">Crítico</option>
                </select>
                <button type="button" onClick={descargarEventos} className="h-11 rounded-lg bg-[#235b4e] px-4 text-sm font-bold text-white hover:bg-[#1d4d42]">Descargar XLSX</button>
              </div>
            ) : null}
          </section>

          <p className="text-sm text-[#6b6258]">
            Aviso de privacidad: esta vista omite contraseñas, tokens, cookies, sesiones y payloads completos de calificaciones, actas, historiales o reportes.
          </p>
          {folio ? <p className="text-sm font-semibold text-[#235b4e]">Folio técnico de exportación: {folio}</p> : null}

          {loading ? <LoadingState label="Cargando auditoría institucional..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && tab === "exportaciones" && exportaciones.length === 0 ? <EmptyExportsState title="No hay registros de auditoría con los filtros seleccionados." /> : null}
          {!loading && !error && tab === "exportaciones" && exportaciones.length > 0 ? <ExportHistoryTable items={exportaciones} showUser /> : null}
          {!loading && !error && tab === "eventos" ? (
            <>
              <EventosSummary resumen={resumenEventos} total={totalEventos} />
              <EventosTable items={eventos} total={totalEventos} onSelect={setEventoDetalle} />
              <AuditEventDetailDrawer item={eventoDetalle} onClose={() => setEventoDetalle(null)} />
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function tabClass(active: boolean) {
  return `border-b-2 px-4 py-3 text-sm font-bold ${active ? "border-[#9f2241] text-[#9f2241]" : "border-transparent text-[#6b6258] hover:text-[#9f2241]"}`;
}

function EventosSummary({ resumen, total }: { resumen: AuditEventSummaryDTO | null; total: number }) {
  const values = [
    { label: "Eventos recientes", value: Number(resumen?.eventos_recientes ?? resumen?.total ?? total) },
    { label: "Eventos críticos", value: Number(resumen?.eventos_criticos ?? countBy(resumen?.por_severidad, "CRITICO")) },
    { label: "Bloqueados", value: Number(resumen?.eventos_bloqueados ?? countBy(resumen?.por_resultado, "BLOQUEADO")) },
    { label: "Fallidos", value: Number(resumen?.eventos_fallidos ?? countBy(resumen?.por_resultado, "FALLIDO")) },
  ];
  return (
    <section className="grid gap-3 md:grid-cols-4">
      {values.map((item) => (
        <div key={item.label} className="rounded-[1.25rem] border border-[#eadfce] bg-white p-4 shadow-sm">
          <p className="text-xs font-black uppercase tracking-[0.16em] text-[#b46c13]">{item.label}</p>
          <p className="mt-2 text-2xl font-black text-[#101b18]">{item.value}</p>
        </div>
      ))}
      {!resumen ? <div className="md:col-span-4"><SensitiveTraceNotice text="El resumen de auditoría no está disponible para estos filtros o perfil; la tabla sigue operando." tone="info" /></div> : null}
    </section>
  );
}

function EventosTable({ items, total, onSelect }: { items: AuditEventDTO[]; total: number; onSelect: (item: AuditEventDTO) => void }) {
  if (items.length === 0) return <EmptyExportsState title="No hay eventos críticos con los filtros seleccionados." />;
  return (
    <section className="overflow-hidden rounded-lg border border-[#eadfce] bg-white shadow-sm">
      <div className="border-b border-[#eadfce] px-4 py-3 text-sm font-semibold text-[#4b4038]">Total filtrado: {total}</div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-[#eadfce] text-sm">
          <thead className="bg-[#f8f3ea] text-left text-xs uppercase text-[#6b6258]">
            <tr>
              <th className="px-4 py-3">Fecha</th>
              <th className="px-4 py-3">Usuario</th>
              <th className="px-4 py-3">Módulo</th>
              <th className="px-4 py-3">Evento</th>
              <th className="px-4 py-3">Resultado</th>
              <th className="px-4 py-3">Objeto</th>
              <th className="px-4 py-3">Resumen</th>
              <th className="px-4 py-3">Detalle</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#f1e7d8]">
            {items.map((item) => (
              <tr key={item.id}>
                <td className="px-4 py-3 whitespace-nowrap">{formatDate(item.creado_en)}</td>
                <td className="px-4 py-3">{formatUsuario(item.usuario)}</td>
                <td className="px-4 py-3">{item.modulo}</td>
                <td className="px-4 py-3 font-semibold text-[#4b4038]">{item.evento_codigo}</td>
                <td className="px-4 py-3"><ProcessStateBadge state={item.resultado || "INFO"} /></td>
                <td className="px-4 py-3">{[item.objeto_tipo, item.objeto_id].filter(Boolean).join(" #") || "N/A"}</td>
                <td className="px-4 py-3 max-w-[24rem]">{item.resumen}</td>
                <td className="px-4 py-3"><button type="button" className="font-black text-[#7a123d]" onClick={() => onSelect(item)}>Abrir</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function formatDate(value?: string | null) {
  if (!value) return "";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

function formatUsuario(value: AuditEventDTO["usuario"]) {
  if (!value) return "Sistema";
  if (typeof value === "string") return value;
  return value.username || value.nombre || "Sistema";
}

function countBy(value: unknown, key: string) {
  if (!Array.isArray(value)) return 0;
  const match = value.find((item) => {
    if (!item || typeof item !== "object") return false;
    const row = item as Record<string, unknown>;
    return row.resultado === key || row.severidad === key;
  });
  return Number((match as Record<string, unknown> | undefined)?.total || 0);
}
