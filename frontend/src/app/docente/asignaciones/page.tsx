"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { TeacherAssignmentCard } from "@/components/operacion-actas/OperationCards";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDocenteAsignaciones } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDocenteOperacion } from "@/lib/dashboard";
import type { DocenteAsignacion } from "@/lib/types";

export default function DocenteAsignacionesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<DocenteAsignacion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <AppShell>
      {!user ? null : !canAccessDocenteOperacion(user) ? (
        <ErrorMessage message="No tienes permiso para consultar asignaciones docentes desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Mis asignaciones" description="Captura preliminar, resumen académico y actas asociadas a tus grupos." user={user} />
          {loading ? <LoadingState label="Cargando asignaciones..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {!loading && !error && items.length === 0 ? <EmptyState title="No hay asignaciones activas." description="Cuando existan asignaciones docentes activas aparecerán aquí." /> : null}
          <section className="grid gap-4 xl:grid-cols-2">
            {items.map((item) => <TeacherAssignmentCard key={item.asignacion_id} asignacion={item} />)}
          </section>
        </div>
      )}
    </AppShell>
  );
}
