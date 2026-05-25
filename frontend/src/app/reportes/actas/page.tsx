"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyExportsState } from "@/components/reportes/EmptyExportsState";
import { ActaExportCard } from "@/components/reportes/ActaExportCard";
import { DownloadStatusToast } from "@/components/reportes/DownloadStatusToast";
import { ExportTraceInfo } from "@/components/reportes/ExportTraceInfo";
import { ExportFormatMenu } from "@/components/reportes/ExportFormatMenu";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { descargarCalificacionFinalPdf, descargarCalificacionFinalXlsx, getActasExportables } from "@/lib/api";
import { canAccessReportes } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";
import type { ActaExportable, DownloadResult } from "@/lib/types";

export default function ActasExportablesPage() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const tipoVista = (searchParams.get("tipo") || "").toLowerCase();
  const corteInicial = (searchParams.get("corte") || "").toUpperCase();
  const [items, setItems] = useState<ActaExportable[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [lastDownload, setLastDownload] = useState<DownloadResult | null>(null);
  const [texto, setTexto] = useState("");
  const [estado, setEstado] = useState("");
  const [corte, setCorte] = useState(
    corteInicial === "P1" || corteInicial === "P2" || corteInicial === "P3" || corteInicial === "FINAL" ? corteInicial : "",
  );

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await getActasExportables();
        setItems(response.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar actas exportables.");
      } finally {
        setLoading(false);
      }
    }

    if (user && canAccessReportes(user)) void load();
  }, [user]);

  const formalizadas = useMemo(
    () => items.filter((item) => item.estado_acta === "FORMALIZADO_JEFATURA_ACADEMICA"),
    [items],
  );
  const isDocenteUser = useMemo(
    () => !!user && (user.perfil_principal === "DOCENTE" || user.roles.includes("DOCENTE") || user.cargos_vigentes.some((cargo) => cargo.cargo_codigo === "DOCENTE")),
    [user],
  );
  const misAsignaciones = useMemo(() => {
    const seen = new Set<number>();
    const list: ActaExportable[] = [];
    for (const item of items) {
      if (seen.has(item.asignacion_docente_id)) continue;
      seen.add(item.asignacion_docente_id);
      list.push(item);
    }
    return list;
  }, [items]);

  const filtered = useMemo(() => {
    const query = texto.trim().toLowerCase();
    return formalizadas.filter((item) => {
      const matchesTipo =
        tipoVista === "parcial"
          ? item.tipo_acta === "ACTA_EVALUACION_PARCIAL" && (item.corte_codigo === "P1" || item.corte_codigo === "P2" || item.corte_codigo === "P3")
          : tipoVista === "final"
            ? item.tipo_acta === "ACTA_EVALUACION_FINAL" && item.corte_codigo === "FINAL"
            : true;
      const matchesText = !query || [item.programa_asignatura, item.docente, item.grupo, item.carrera, item.periodo]
        .join(" ")
        .toLowerCase()
        .includes(query);
      const matchesEstado = !estado || item.estado_acta === estado;
      const matchesCorte = !corte || item.corte_codigo === corte;
      return matchesTipo && matchesText && matchesEstado && matchesCorte;
    });
  }, [formalizadas, texto, estado, corte, tipoVista]);

  const estados = Array.from(new Map(formalizadas.map((item) => [item.estado_acta, item.estado_acta_label])).entries());
  const cortes = useMemo(() => {
    const base = Array.from(new Map(formalizadas.map((item) => [item.corte_codigo, item.corte_nombre])).entries());
    if (tipoVista === "parcial") return base.filter(([value]) => value === "P1" || value === "P2" || value === "P3");
    if (tipoVista === "final") return base.filter(([value]) => value === "FINAL");
    return base;
  }, [formalizadas, tipoVista]);
  const renderedAssignments = new Set<number>();

  return (
    <AppShell>
      {!user ? null : !canAccessReportes(user) ? (
        <ErrorMessage message="No tienes permiso para consultar actas exportables desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader
            title="Actas exportables"
            description="Descarga actas PDF/XLSX disponibles según la información académica registrada."
            user={user}
          />
          {tipoVista === "parcial" ? (
            <p className="text-sm text-[#5f6764]">Selecciona el corte para consultar el acta parcial (P1, P2 o P3).</p>
          ) : null}
          {tipoVista === "final" ? (
            <p className="text-sm text-[#5f6764]">Consulta el acta de evaluación final disponible según tu perfil autorizado.</p>
          ) : null}
          {tipoVista === "calificacion-final" ? (
            <p className="text-sm text-[#5f6764]">Exporta la calificación final consolidada de tus asignaciones docentes.</p>
          ) : null}
          {isDocenteUser ? (
            <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
              <h3 className="text-base font-black text-[#152b25]">Acta de calificación final de mis materias</h3>
              <p className="mt-1 text-sm text-[#5f6764]">Exporta la calificación final consolidada de tus asignaciones docentes.</p>
              <div className="mt-4 grid gap-3">
                {misAsignaciones.length === 0 ? (
                  <p className="text-sm text-[#5f6764]">Sin asignaciones disponibles por ahora.</p>
                ) : (
                  misAsignaciones.map((item) => (
                    <div key={`cf-${item.asignacion_docente_id}`} className="rounded-2xl border border-[#eadfce] bg-[#fffaf1] p-3">
                      <p className="text-sm font-black text-[#152b25]">{item.programa_asignatura}</p>
                      <p className="text-xs font-semibold text-[#5f6764]">
                        {item.carrera_clave} · {item.periodo} · Grupo {item.grupo}
                      </p>
                      <div className="mt-3">
                        <ExportFormatMenu
                          pdfAction={() => descargarCalificacionFinalPdf(item.asignacion_docente_id)}
                          xlsxAction={() => descargarCalificacionFinalXlsx(item.asignacion_docente_id)}
                          canPdf
                          canXlsx
                          onDone={(result) => {
                            setDownloadError(null);
                            setLastDownload(result);
                          }}
                          onError={(message) => {
                            setLastDownload(null);
                            setDownloadError(message);
                          }}
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          ) : null}

          <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
            <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_220px_220px]">
              <input
                value={texto}
                onChange={(event) => setTexto(event.target.value)}
                placeholder="Buscar por asignatura, docente, grupo o período..."
                className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c]"
              />
              <select value={estado} onChange={(event) => setEstado(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]">
                <option value="">Todos los estados</option>
                {estados.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
              <select value={corte} onChange={(event) => setCorte(event.target.value)} className="h-12 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-bold outline-none focus:border-[#bc955c]">
                <option value="">Todos los cortes</option>
                {cortes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </div>
          </section>

          <ExportTraceInfo result={lastDownload} />
          <DownloadStatusToast message={downloadError} tone="error" />

          {loading ? <LoadingState label="Cargando actas exportables..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}

          {!loading && !error && filtered.length === 0 ? (
            <EmptyExportsState title="No hay actas exportables para tu perfil." description="No hay actas disponibles con los filtros aplicados." />
          ) : null}

          {!loading && !error && filtered.length > 0 ? (
            <section className="grid gap-4">
              {filtered.map((acta) => {
                const showCalificacionFinal = !renderedAssignments.has(acta.asignacion_docente_id);
                renderedAssignments.add(acta.asignacion_docente_id);
                return (
                  <ActaExportCard
                    key={acta.acta_id}
                    acta={acta}
                    showCalificacionFinal={showCalificacionFinal}
                    onDownloaded={(result) => {
                      setDownloadError(null);
                      setLastDownload(result);
                    }}
                    onError={(message) => {
                      setLastDownload(null);
                      setDownloadError(message);
                    }}
                  />
                );
              })}
            </section>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
