"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ActasFilters } from "@/components/operacion-actas/ActasFilters";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDocenteActas } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDocenteOperacion } from "@/lib/dashboard";
import type { ActaResumen } from "@/lib/types";

export default function DocenteActasPage() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const estado = (searchParams.get("estado") || "").toLowerCase();
  const [items, setItems] = useState<ActaResumen[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        setItems((await getDocenteActas(filters)).items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar tus actas.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessDocenteOperacion(user)) void load();
  }, [user, filters]);

  const filteredItems = useMemo(() => items.filter((acta) => matchEstado(estado, acta)), [items, estado]);
  const heading = getHeadingByEstado(estado);

  return (
    <AppShell>
      {!user ? null : !canAccessDocenteOperacion(user) ? (
        <ErrorMessage message="No tienes permiso para consultar actas docentes." />
      ) : (
        <div className="space-y-5">
          <PageHeader title={heading.title} description={heading.description} user={user} />
          <ActasFilters onApply={setFilters} />
          {loading ? <LoadingState label="Cargando actas..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && filteredItems.length === 0 ? (
            <EmptyState title="No hay actas para los filtros seleccionados." description="Sin información disponible." />
          ) : null}

          {!loading && !error && filteredItems.length > 0 ? (
            <section className="overflow-hidden rounded-2xl border border-[#e7dccb] bg-white/90 shadow-sm">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-[#eadfce]">
                  <thead className="bg-[#f7f0e3]">
                    <tr className="text-left text-xs font-black uppercase tracking-[0.08em] text-[#5f6764]">
                      <th className="px-4 py-3">Corte</th>
                      <th className="px-4 py-3">Grupo</th>
                      <th className="px-4 py-3">Programa de asignatura</th>
                      <th className="px-4 py-3">Período académico</th>
                      <th className="px-4 py-3">Estado</th>
                      <th className="px-4 py-3">Actualización</th>
                      <th className="px-4 py-3">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#f0e7d8] bg-white/95 text-sm text-[#152b25]">
                    {filteredItems.map((acta) => (
                      <tr key={acta.acta_id} className="align-top">
                        <td className="px-4 py-3 font-bold">{acta.corte_label || acta.corte_codigo || "-"}</td>
                        <td className="px-4 py-3">{acta.grupo?.label || acta.grupo?.nombre || "-"}</td>
                        <td className="px-4 py-3">{acta.programa_asignatura?.label || acta.programa_asignatura?.nombre || "-"}</td>
                        <td className="px-4 py-3">{acta.periodo?.label || acta.periodo?.nombre || "-"}</td>
                        <td className="px-4 py-3">
                          <span className="rounded-lg border border-[#d8c5a7] bg-[#fbf5ea] px-2.5 py-1 text-xs font-black text-[#5a3b2a]">
                            {humanEstado(acta.estado_acta, acta.estado_acta_label)}
                          </span>
                        </td>
                        <td className="px-4 py-3">{formatDate(acta.actualizado_en || acta.creado_en)}</td>
                        <td className="px-4 py-3">
                          <Link href={`/docente/actas/${acta.acta_id}`} className="rounded-lg border border-[#7a123d] bg-[#7a123d] px-3 py-1.5 text-xs font-black text-white hover:bg-[#671033]">
                            Ver acta
                          </Link>
                        </td>
                      </tr>
                    ))}
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

function matchEstado(filter: string, acta: ActaResumen) {
  if (!filter) return true;
  const estado = (acta.estado_acta || "").toUpperCase();
  const label = (acta.estado_acta_label || "").toUpperCase();

  if (filter === "borrador") {
    return estado.includes("BORRADOR") || label.includes("BORRADOR");
  }
  if (filter === "publicadas") {
    return (
      estado.includes("PUBLICADO") ||
      estado.includes("FORMALIZADO") ||
      estado.includes("ARCHIVADO") ||
      label.includes("PUBLICADO") ||
      label.includes("FORMALIZADO") ||
      label.includes("ARCHIVADO")
    );
  }
  if (filter === "remitidas") {
    return estado.includes("REMITIDO") || label.includes("REMITIDO");
  }
  return true;
}

function getHeadingByEstado(filter: string) {
  if (filter === "borrador") {
    return {
      title: "Borradores de actas",
      description: "Revisa las actas en captura y continúa su gestión.",
    };
  }
  if (filter === "publicadas") {
    return {
      title: "Actas publicadas",
      description: "Consulta las actas publicadas y su seguimiento.",
    };
  }
  if (filter === "remitidas") {
    return {
      title: "Actas remitidas",
      description: "Consulta las actas remitidas a jefatura.",
    };
  }
  return {
    title: "Mis actas",
    description: "Revisa las actas asociadas a tus materias y su estado actual.",
  };
}

function humanEstado(estado: string | undefined, label: string | undefined) {
  const key = (estado || "").toUpperCase();
  if (key.includes("BORRADOR")) return "En captura";
  if (key.includes("PUBLICADO")) return "Publicada";
  if (key.includes("REMITIDO")) return "En revisión";
  if (key.includes("VALIDADO")) return "Validada";
  if (key.includes("FORMALIZADO") || key.includes("ARCHIVADO")) return "Finalizada";
  return label || "Pendiente";
}

function formatDate(value: string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium" }).format(new Date(value));
}
