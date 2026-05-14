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

  return (
    <AppShell>
      {!user ? null : !canAccessEstadisticaActas(user) ? (
        <ErrorMessage message="No tienes permiso para consultar actas operativas." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Consulta operativa de actas" description="Consulta general en solo lectura para Estadística/Admin." user={user} />
          <ActasFilters onApply={setFilters} />
          {loading ? <LoadingState label="Cargando actas..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyState title="No hay actas para los filtros seleccionados." description="Ajusta los filtros o consulta más tarde." /> : null}
          <section className="grid gap-4 xl:grid-cols-2">
            {items.map((acta) => <ActaListCard key={acta.acta_id} acta={acta} href={`/estadistica/actas/${acta.acta_id}`} />)}
          </section>
        </div>
      )}
    </AppShell>
  );
}
