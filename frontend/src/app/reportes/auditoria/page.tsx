"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyExportsState } from "@/components/reportes/EmptyExportsState";
import { ExportHistoryTable } from "@/components/reportes/ExportHistoryTable";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { descargarAuditoriaEventosXlsx, getAuditoriaEventos, getAuditoriaExportaciones } from "@/lib/api";
import { canAccessAuditoria, canAccessAuditoriaEventos, canAccessAuditoriaExportaciones } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";
import type { BitacoraEventoCritico, ExportacionRegistro } from "@/lib/types";

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
  const [eventos, setEventos] = useState<BitacoraEventoCritico[]>([]);
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
          {!loading && !error && tab === "eventos" ? <EventosTable items={eventos} total={totalEventos} /> : null}
        </div>
      )}
    </AppShell>
  );
}

function tabClass(active: boolean) {
  return `border-b-2 px-4 py-3 text-sm font-bold ${active ? "border-[#9f2241] text-[#9f2241]" : "border-transparent text-[#6b6258] hover:text-[#9f2241]"}`;
}

function EventosTable({ items, total }: { items: BitacoraEventoCritico[]; total: number }) {
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
            </tr>
          </thead>
          <tbody className="divide-y divide-[#f1e7d8]">
            {items.map((item) => (
              <tr key={item.id}>
                <td className="px-4 py-3 whitespace-nowrap">{formatDate(item.creado_en)}</td>
                <td className="px-4 py-3">{item.usuario.username || "Sistema"}</td>
                <td className="px-4 py-3">{item.modulo}</td>
                <td className="px-4 py-3 font-semibold text-[#4b4038]">{item.evento_codigo}</td>
                <td className="px-4 py-3">{item.resultado}</td>
                <td className="px-4 py-3">{[item.objeto_tipo, item.objeto_id].filter(Boolean).join(" #") || "N/A"}</td>
                <td className="px-4 py-3 max-w-[24rem]">{item.resumen}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function formatDate(value: string | null) {
  if (!value) return "";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}
