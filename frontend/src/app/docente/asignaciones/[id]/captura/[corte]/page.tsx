"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { GradeCaptureGrid } from "@/components/operacion-actas/GradeCaptureGrid";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDocenteCaptura } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDocenteOperacion } from "@/lib/dashboard";
import type { CapturaPreliminarCorte } from "@/lib/types";

export default function DocenteCapturaCortePage() {
  const params = useParams<{ id: string; corte: string }>();
  const { user } = useAuth();
  const [data, setData] = useState<CapturaPreliminarCorte | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        setData(await getDocenteCaptura(params.id, params.corte));
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar la captura.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessDocenteOperacion(user)) void load();
  }, [user, params.id, params.corte]);

  return (
    <AppShell showRightPanel={false}>
      {!user ? null : !canAccessDocenteOperacion(user) ? (
        <ErrorMessage message="No tienes permiso para capturar calificaciones." />
      ) : (
        <div className="space-y-6">
          <PageHeader title={`Captura ${String(params.corte).toUpperCase()}`} description="Captura preliminar por componente. La validación real permanece en Django." user={user} />
          <Link className="inline-flex rounded-xl border border-[#d8c5a7] px-4 py-2 text-sm font-black text-[#6f4a16]" href={`/docente/asignaciones/${params.id}`}>
            Volver a la asignación
          </Link>
          {loading ? <LoadingState label="Cargando captura..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {data ? <GradeCaptureGrid initialData={data} onSaved={setData} /> : null}
        </div>
      )}
    </AppShell>
  );
}
