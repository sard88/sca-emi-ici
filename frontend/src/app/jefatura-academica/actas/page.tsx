"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ActasFilters } from "@/components/operacion-actas/ActasFilters";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getJefaturaAcademicaActasPendientes, getReporteOperativoActasFormalizadas } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessJefaturaAcademicaActas } from "@/lib/dashboard";
import type { ActaResumen, ReporteOperativoRespuesta } from "@/lib/types";

export default function JefaturaAcademicaActasPage() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const estado = (searchParams.get("estado") || "").toLowerCase();
  const showFormalizadas = estado === "formalizadas";
  const [items, setItems] = useState<ActaResumen[]>([]);
  const [formalizadasReport, setFormalizadasReport] = useState<ReporteOperativoRespuesta | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        if (showFormalizadas) {
          const report = await getReporteOperativoActasFormalizadas(filters);
          setFormalizadasReport(report);
          setItems([]);
        } else {
          const response = await getJefaturaAcademicaActasPendientes(filters);
          setItems(response.items);
          setFormalizadasReport(null);
        }
      } catch (err) {
        const fallback = showFormalizadas
          ? "No fue posible cargar las actas formalizadas desde esta vista."
          : "No fue posible cargar actas para revisión académica.";
        setError(fallback);
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessJefaturaAcademicaActas(user)) void load();
  }, [user, filters, showFormalizadas]);

  const visibleItems = useMemo(() => (showFormalizadas ? [] : items), [items, showFormalizadas]);
  const formalizadasItems = useMemo(() => {
    if (!showFormalizadas || !formalizadasReport?.items) return [];
    return formalizadasReport.items.filter((item) => isOperativeRowFormalizada(item as Record<string, unknown>));
  }, [showFormalizadas, formalizadasReport]);

  return (
    <AppShell>
      {!user ? null : !canAccessJefaturaAcademicaActas(user) ? (
        <ErrorMessage message="No tienes permiso para revisar actas académicas." />
      ) : (
        <div className="space-y-5">
          <PageHeader
            title={showFormalizadas ? "Actas formalizadas" : "Actas para revisión académica"}
            description={showFormalizadas ? "Consulta las actas formalizadas recientemente." : "Consulta las actas disponibles para revisión académica."}
            user={user}
          />
          <p className="text-sm text-[#5f6764]">
            {showFormalizadas ? "Consulta actas formalizadas dentro de tu ámbito autorizado." : "Revisa el estado de las actas según tu ámbito autorizado."}
          </p>

          <div className="rounded-2xl border border-[#eadfce] bg-white/90 p-4">
            <ActasFilters onApply={setFilters} includeEstado={false} />
          </div>

          {loading ? <LoadingState label="Cargando actas..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && showFormalizadas && formalizadasItems.length === 0 ? (
            <EmptyState title={showFormalizadas ? "Sin actas formalizadas por ahora." : "Sin actas pendientes por ahora."} description="Sin información disponible." />
          ) : null}
          {!loading && !error && !showFormalizadas && visibleItems.length === 0 ? (
            <EmptyState title="Sin actas pendientes por ahora." description="Sin información disponible." />
          ) : null}

          {!loading && !error && !showFormalizadas && visibleItems.length > 0 ? (
            <section className="overflow-hidden rounded-2xl border border-[#e7dccb] bg-white/90 shadow-sm">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[#eadfce] text-sm">
                  <thead className="bg-[#f7f0e3]">
                    <tr className="text-left text-xs font-black uppercase tracking-[0.08em] text-[#5f6764]">
                      <th className="px-4 py-3">Corte</th>
                      <th className="px-4 py-3">Grupo</th>
                      <th className="px-4 py-3">Asignatura</th>
                      <th className="px-4 py-3">Período académico</th>
                      <th className="px-4 py-3">Estado</th>
                      <th className="px-4 py-3">Acción</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#f0e7d8] bg-white/95 text-[#152b25]">
                    {visibleItems.map((acta) => (
                      <tr key={acta.acta_id}>
                        <td className="px-4 py-3 font-bold">{acta.corte_label || acta.corte_codigo || "-"}</td>
                        <td className="px-4 py-3">{acta.grupo?.label || acta.grupo?.nombre || "-"}</td>
                        <td className="px-4 py-3">{acta.programa_asignatura?.label || acta.programa_asignatura?.nombre || "-"}</td>
                        <td className="px-4 py-3">{acta.periodo?.label || acta.periodo?.nombre || "-"}</td>
                        <td className="px-4 py-3">
                          <span className="rounded-lg border border-[#d8c5a7] bg-[#fbf5ea] px-2.5 py-1 text-xs font-black text-[#5a3b2a]">
                            {toEstadoVisible(acta.estado_acta_label || acta.estado_acta)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <Link href={`/jefatura-academica/actas/${acta.acta_id}`} className="rounded-lg border border-[#7a123d] bg-[#7a123d] px-3 py-1.5 text-xs font-black text-white hover:bg-[#671033]">
                            Revisar acta
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}

          {!loading && !error && showFormalizadas && formalizadasItems.length > 0 ? (
            <section className="overflow-hidden rounded-2xl border border-[#e7dccb] bg-white/90 shadow-sm">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[#eadfce] text-sm">
                  <thead className="bg-[#f7f0e3]">
                    <tr className="text-left text-xs font-black uppercase tracking-[0.08em] text-[#5f6764]">
                      {(formalizadasReport?.columnas || []).map((columna) => (
                        <th key={columna.key} className="px-4 py-3">
                          {columna.label}
                        </th>
                      ))}
                      <th className="px-4 py-3">Acción</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#f0e7d8] bg-white/95 text-[#152b25]">
                    {formalizadasItems.map((item, index) => {
                      const row = item as Record<string, unknown>;
                      const actaId = getActaIdFromRow(row);
                      return (
                        <tr key={String(actaId || index)}>
                          {(formalizadasReport?.columnas || []).map((columna) => (
                            <td key={`${String(actaId || index)}-${columna.key}`} className="px-4 py-3">
                              {formatValue(row[columna.key])}
                            </td>
                          ))}
                          <td className="px-4 py-3">
                            {actaId ? (
                              <Link href={`/jefatura-academica/actas/${actaId}`} className="rounded-lg border border-[#7a123d] bg-[#7a123d] px-3 py-1.5 text-xs font-black text-white hover:bg-[#671033]">
                                Revisar acta
                              </Link>
                            ) : (
                              <span className="text-xs font-bold text-[#7b6b58]">Sin detalle disponible</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function isEstadoFormalizado(estado: string) {
  const normalized = normalizeToken(estado);
  return normalized.includes("FORMALIZADO") || normalized.includes("FORMALIZADA");
}

function isActaFormalizada(acta: ActaResumen) {
  const candidate = acta as ActaResumen & Record<string, unknown>;
  const fields = [
    acta.estado_acta,
    acta.estado_acta_label,
    String(candidate.estado || ""),
    String(candidate.estado_codigo || ""),
    String(candidate.estado_display || ""),
    String(candidate.fase || ""),
    String(candidate.situacion || ""),
    String(candidate.estado_nombre || ""),
    String(candidate.estadoActual || ""),
  ];
  return fields.some((value) => isEstadoFormalizado(value || ""));
}

function isOperativeRowFormalizada(row: Record<string, unknown>) {
  const candidates = [
    String(row.estado || ""),
    String(row.estado_acta || ""),
    String(row.estado_codigo || ""),
    String(row.estado_display || ""),
    String(row.estado_nombre || ""),
    String(row.estado_actual || ""),
    String(row.fase || ""),
    String(row.situacion || ""),
    String(row.estado_etiqueta || ""),
  ];
  return candidates.some((value) => isEstadoFormalizado(value));
}

function getActaIdFromRow(row: Record<string, unknown>) {
  const candidate =
    row.acta_id ??
    row.id_acta ??
    row.id ??
    row.actaId ??
    row.acta;
  if (typeof candidate === "number") return candidate;
  if (typeof candidate === "string" && candidate.trim()) return candidate.trim();
  return null;
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "Sí" : "No";
  return String(value);
}

function toEstadoVisible(estado: string) {
  const normalized = (estado || "").toUpperCase();
  if (normalized.includes("BORRADOR")) return "En elaboración";
  if (normalized.includes("REMITIDO") && normalized.includes("ACADEM")) return "Pendiente de revisión académica";
  if (normalized.includes("REMITIDO")) return "Pendiente de revisión académica";
  if (normalized.includes("VALIDADO")) return "Validada por carrera";
  if (normalized.includes("FORMALIZADO")) return "Formalizada";
  if (normalized.includes("PUBLICADO")) return "Publicada";
  return estado;
}

function normalizeToken(value: string) {
  return (value || "")
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toUpperCase();
}
