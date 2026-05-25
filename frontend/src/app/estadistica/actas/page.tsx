"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ActasFilters } from "@/components/operacion-actas/ActasFilters";
import { ActaListCard } from "@/components/operacion-actas/OperationCards";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getEstadisticaActas } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessEstadisticaActas } from "@/lib/dashboard";
import type { ActaResumen } from "@/lib/types";

export default function EstadisticaActasPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<ActaResumen[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        setItems((await getEstadisticaActas(filters)).items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar actas.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessEstadisticaActas(user)) void load();
  }, [user, filters]);

  const formalizadas = items.filter(isActaFormalizadaPorJefaturaAcademica);

  return (
    <AppShell>
      {!user ? null : !canAccessEstadisticaActas(user) ? (
        <ErrorMessage message="No tienes permiso para consultar actas vivas." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Actas vivas" description="Consulta las actas formalizadas por jefatura académica disponibles para seguimiento institucional." user={user} />
          <ActasFilters onApply={setFilters} />
          {loading ? <LoadingState label="Cargando actas..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && formalizadas.length === 0 ? <EmptyState title="Sin actas formalizadas para mostrar." description="Sin información disponible." /> : null}
          <section className="grid gap-4 xl:grid-cols-2">
            {formalizadas.map((acta) => <ActaListCard key={acta.acta_id} acta={acta} href={`/estadistica/actas/${acta.acta_id}`} />)}
          </section>
        </div>
      )}
    </AppShell>
  );
}

function isActaFormalizadaPorJefaturaAcademica(acta: ActaResumen) {
  const rawStates = [
    acta.estado_acta,
    acta.estado_acta_label,
    (acta as unknown as Record<string, unknown>).estado,
    (acta as unknown as Record<string, unknown>).estado_codigo,
    (acta as unknown as Record<string, unknown>).estado_display,
    (acta as unknown as Record<string, unknown>).estado_nombre,
    (acta as unknown as Record<string, unknown>).estadoActual,
    (acta as unknown as Record<string, unknown>).fase,
    (acta as unknown as Record<string, unknown>).situacion,
  ];

  const normalizedStates = rawStates.map(normalizeState).filter(Boolean);

  const isFormalizedState = normalizedStates.some((value) =>
    value === "FORMALIZADO" ||
    value === "FORMALIZADA" ||
    value === "FORMALIZADO JEFATURA ACADEMICA" ||
    value === "FORMALIZADA JEFATURA ACADEMICA" ||
    value === "FORMALIZADO POR JEFATURA ACADEMICA" ||
    value === "FORMALIZADA POR JEFATURA ACADEMICA",
  );

  if (isFormalizedState) return true;
  return Boolean(acta.formalizada_en);
}

function normalizeState(value: unknown) {
  if (typeof value !== "string") return "";
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toUpperCase();
}
