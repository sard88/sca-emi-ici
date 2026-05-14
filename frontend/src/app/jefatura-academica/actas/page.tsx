"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ActasFilters } from "@/components/operacion-actas/ActasFilters";
import { ActaListCard } from "@/components/operacion-actas/OperationCards";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getJefaturaAcademicaActasPendientes } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessJefaturaAcademicaActas } from "@/lib/dashboard";
import type { ActaResumen } from "@/lib/types";

export default function JefaturaAcademicaActasPage() {
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
        setItems((await getJefaturaAcademicaActasPendientes(filters)).items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar actas por formalizar.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessJefaturaAcademicaActas(user)) void load();
  }, [user, filters]);

  return (
    <AppShell>
      {!user ? null : !canAccessJefaturaAcademicaActas(user) ? (
        <ErrorMessage message="No tienes permiso para formalizar actas." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Actas por formalizar" description="Cola de actas validadas por jefatura de carrera." user={user} />
          <ActasFilters onApply={setFilters} includeEstado={false} />
          {loading ? <LoadingState label="Cargando actas..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyState title="No hay actas pendientes de formalización." description="Cuando jefatura de carrera valide un acta aparecerá aquí." /> : null}
          <section className="grid gap-4 xl:grid-cols-2">
            {items.map((acta) => <ActaListCard key={acta.acta_id} acta={acta} href={`/jefatura-academica/actas/${acta.acta_id}`} />)}
          </section>
        </div>
      )}
    </AppShell>
  );
}
