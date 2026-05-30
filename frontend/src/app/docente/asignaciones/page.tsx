"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDocenteAsignacionDetalle, getDocenteAsignaciones } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDocenteOperacion } from "@/lib/dashboard";
import type { DiscenteMinimo, DocenteAsignacion } from "@/lib/types";

export default function DocenteAsignacionesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<DocenteAsignacion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openDiscentesFor, setOpenDiscentesFor] = useState<number | null>(null);
  const [loadingDiscentesFor, setLoadingDiscentesFor] = useState<number | null>(null);
  const [discentesByAsignacion, setDiscentesByAsignacion] = useState<Record<number, DiscenteMinimo[]>>({});

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await getDocenteAsignaciones();
        setItems(data.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar tus asignaciones.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessDocenteOperacion(user)) void load();
  }, [user]);

  async function handleVerDiscentes(asignacionId: number) {
    if (openDiscentesFor === asignacionId) {
      setOpenDiscentesFor(null);
      return;
    }

    setOpenDiscentesFor(asignacionId);
    if (discentesByAsignacion[asignacionId]) return;

    setLoadingDiscentesFor(asignacionId);
    try {
      const detalle = await getDocenteAsignacionDetalle(asignacionId);
      const discentes = (detalle.discentes || []).map((item) => item.discente).filter(Boolean);
      setDiscentesByAsignacion((prev) => ({ ...prev, [asignacionId]: discentes }));
    } catch {
      setDiscentesByAsignacion((prev) => ({ ...prev, [asignacionId]: [] }));
    } finally {
      setLoadingDiscentesFor(null);
    }
  }

  return (
    <AppShell>
      {!user ? null : !canAccessDocenteOperacion(user) ? (
        <ErrorMessage message="No tienes permiso para consultar asignaciones docentes desde el portal." />
      ) : (
        <div className="space-y-5">
          <PageHeader
            title="Mis asignaciones y captura"
            description="Consulta tus asignaciones académicas, grupos y estudiantes inscritos."
            user={user}
          />

          {loading ? <LoadingState label="Cargando asignaciones..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyState title="No hay asignaciones activas." description="Sin registros por ahora." /> : null}

          {!loading && !error && items.length > 0 ? (
            <section className="overflow-hidden rounded-2xl border border-[#e7dccb] bg-white/90 shadow-sm">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[#eadfce]">
                  <thead className="bg-[#f7f0e3]">
                    <tr className="text-left text-xs font-black uppercase tracking-[0.08em] text-[#5f6764]">
                      <th className="px-4 py-3">Grupo</th>
                      <th className="px-4 py-3">Programa de asignatura</th>
                      <th className="px-4 py-3">Año de formación</th>
                      <th className="px-4 py-3">Período académico</th>
                      <th className="px-4 py-3">Discentes</th>
                      <th className="px-4 py-3">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#f0e7d8] bg-white/95 text-sm text-[#152b25]">
                    {items.map((item) => {
                      const grupo = item.grupo?.label || item.grupo?.nombre || "-";
                      const programa = item.programa_asignatura?.label || item.programa_asignatura?.nombre || "-";
                      const periodo = item.periodo?.label || item.periodo?.nombre || "-";
                      const anio = item.semestre ? `Semestre ${item.semestre}` : "-";
                      const discentes = item.num_discentes ?? 0;
                      const detalleId = item.asignacion_id;
                      const actasHref = `/docente/actas?asignacion=${encodeURIComponent(String(detalleId))}`;

                      return (
                        <tr key={item.asignacion_id} className="align-top">
                          <td className="px-4 py-3 font-bold">{grupo}</td>
                          <td className="px-4 py-3">{programa}</td>
                          <td className="px-4 py-3">{anio}</td>
                          <td className="px-4 py-3">{periodo}</td>
                          <td className="px-4 py-3">{discentes}</td>
                          <td className="px-4 py-3">
                            <div className="flex flex-wrap gap-2">
                              {detalleId ? (
                                <>
                                  <button
                                    type="button"
                                    onClick={() => handleVerDiscentes(detalleId)}
                                    className="rounded-lg border border-[#d8c5a7] bg-white px-3 py-1.5 text-xs font-black text-[#5a3b2a] hover:bg-[#fbf5ea]"
                                  >
                                    Ver discentes
                                  </button>
                                  <Link href={`/docente/asignaciones/${detalleId}/captura/P1`} className="rounded-lg border border-[#0b4a3d] bg-[#0b4a3d] px-3 py-1.5 text-xs font-black text-white hover:bg-[#0a4035]">
                                    Capturar calificaciones
                                  </Link>
                                </>
                              ) : (
                                <span className="rounded-lg border border-[#dfd6c7] bg-[#f8f5ef] px-3 py-1.5 text-xs font-bold text-[#7b6b58]">
                                  Disponible próximamente
                                </span>
                              )}
                              <Link href={actasHref} className="rounded-lg border border-[#7a123d] bg-[#7a123d] px-3 py-1.5 text-xs font-black text-white hover:bg-[#671033]">
                                Ver actas
                              </Link>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {openDiscentesFor ? (
                <div className="border-t border-[#eadfce] bg-[#fffaf1] p-4">
                  <h3 className="text-sm font-black text-[#152b25]">Discentes inscritos</h3>
                  {loadingDiscentesFor === openDiscentesFor ? (
                    <p className="mt-2 text-sm text-[#5f6764]">Cargando discentes...</p>
                  ) : (discentesByAsignacion[openDiscentesFor] || []).length === 0 ? (
                    <p className="mt-2 text-sm text-[#5f6764]">Sin discentes registrados para esta asignación.</p>
                  ) : (
                    <div className="mt-3 overflow-x-auto">
                      <table className="min-w-full divide-y divide-[#eadfce] rounded-xl border border-[#eadfce] bg-white">
                        <thead className="bg-[#f7f0e3]">
                          <tr className="text-left text-xs font-black uppercase tracking-[0.08em] text-[#5f6764]">
                            <th className="px-3 py-2">No.</th>
                            <th className="px-3 py-2">Grado y empleo</th>
                            <th className="px-3 py-2">Nombre</th>
                            <th className="px-3 py-2">Situación</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#f0e7d8] text-sm text-[#152b25]">
                          {(discentesByAsignacion[openDiscentesFor] || []).map((discente, index) => (
                            <tr key={discente.id ?? index}>
                              <td className="px-3 py-2">{index + 1}</td>
                              <td className="px-3 py-2">{discente.grado_empleo || "—"}</td>
                              <td className="px-3 py-2 font-medium">{discente.nombre_institucional || discente.nombre || "—"}</td>
                              <td className="px-3 py-2">{discente.situacion_actual_label || discente.situacion_actual || "—"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ) : null}
            </section>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
