"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { formatValue } from "@/components/operacion-actas/ActaTables";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { getDocenteResumen } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canAccessDocenteOperacion } from "@/lib/dashboard";
import type { ResumenCalculoAcademico } from "@/lib/types";

export default function DocenteResumenPage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [data, setData] = useState<ResumenCalculoAcademico | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        setData(await getDocenteResumen(params.id));
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar el resumen.");
      } finally {
        setLoading(false);
      }
    }
    if (user && canAccessDocenteOperacion(user)) void load();
  }, [user, params.id]);

  return (
    <AppShell showRightPanel={false}>
      {!user ? null : !canAccessDocenteOperacion(user) ? (
        <ErrorMessage message="No tienes permiso para consultar este resumen." />
      ) : (
        <div className="space-y-6">
          <PageHeader title="Resumen de cálculo académico" description="Vista derivada del ServicioCalculoAcademico. No modifica datos." user={user} />
          <Link className="inline-flex rounded-xl border border-[#d8c5a7] px-4 py-2 text-sm font-black text-[#6f4a16]" href={`/docente/asignaciones/${params.id}`}>
            Volver a la asignación
          </Link>
          {loading ? <LoadingState label="Cargando resumen..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          {data ? (
            <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 shadow-sm">
              <div className="overflow-x-auto">
                <table className="min-w-full border-collapse text-left text-sm">
                  <thead>
                    <tr className="bg-[#0b4a3d] text-white">
                      {["Discente", "P1", "P2", "P3", "Final", "Promedio parciales", "Exención", "Final preliminar", "Estado"].map((header) => (
                        <th key={header} className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((item) => (
                      <tr key={item.inscripcion_id} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                        <td className="px-4 py-3 font-black text-[#152b25]">{item.discente.nombre_institucional || item.discente.nombre}</td>
                        {["P1", "P2", "P3", "FINAL"].map((corte) => (
                          <td key={corte} className="px-4 py-3 text-[#263b34]">{formatValue((item.cortes as Record<string, { resultado?: unknown }> | undefined)?.[corte]?.resultado)}</td>
                        ))}
                        <td className="px-4 py-3">{formatValue(item.promedio_parciales)}</td>
                        <td className="px-4 py-3">{formatValue(item.exencion_aplica)}</td>
                        <td className="px-4 py-3">{formatValue(item.calificacion_final_preliminar)}</td>
                        <td className="px-4 py-3">{formatValue(item.resultado_preliminar)}</td>
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
