"use client";

import { useMemo, useState } from "react";
import type { CapturaPreliminarCorte } from "@/lib/types";
import { guardarDocenteCaptura } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/states/ErrorMessage";

export function GradeCaptureGrid({ initialData, onSaved }: { initialData: CapturaPreliminarCorte; onSaved: (data: CapturaPreliminarCorte) => void }) {
  const initialValues = useMemo(() => {
    const values: Record<string, string> = {};
    initialData.filas.forEach((fila) => {
      fila.valores.forEach((valor) => {
        values[keyFor(fila.inscripcion_id, valor.componente_id)] = valor.valor === null || valor.valor === undefined ? "" : String(valor.valor);
      });
    });
    return values;
  }, [initialData]);

  const [values, setValues] = useState<Record<string, string>>(initialValues);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function save() {
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const payload = {
        valores: initialData.filas.flatMap((fila) =>
          initialData.componentes.map((componente) => ({
            inscripcion_id: fila.inscripcion_id,
            componente_id: componente.id,
            valor: values[keyFor(fila.inscripcion_id, componente.id)] ?? "",
          })),
        ),
      };
      const response = await guardarDocenteCaptura(initialData.asignacion.asignacion_id, String(initialData.corte), payload);
      setMessage(`Captura guardada. Registros actualizados: ${response.guardados ?? 0}. Registros limpiados: ${response.limpiados ?? 0}.`);
      onSaved(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible guardar la captura.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="space-y-4 rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      {initialData.captura_bloqueada ? (
        <div className="rounded-2xl border border-[#efc3c7] bg-[#fff1f2] px-4 py-3 text-sm font-bold text-[#8c1239]">
          Captura bloqueada por acta avanzada. La información queda en solo lectura.
        </div>
      ) : (
        <div className="rounded-2xl border border-[#d8c5a7] bg-[#fffaf1] px-4 py-3 text-sm font-bold text-[#6f4a16]">
          Captura preliminar: los valores oficiales solo se consolidan al formalizar acta FINAL.
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead>
            <tr className="bg-[#0b4a3d] text-white">
              <th className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">Discente</th>
              {initialData.componentes.map((componente) => (
                <th key={componente.id} className="px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">
                  {componente.nombre} ({componente.porcentaje}%)
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {initialData.filas.map((fila) => (
              <tr key={fila.inscripcion_id} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                <td className="min-w-[260px] px-4 py-3 font-black text-[#152b25]">{fila.discente.nombre_institucional || fila.discente.nombre}</td>
                {initialData.componentes.map((componente) => (
                  <td key={`${fila.inscripcion_id}-${componente.id}`} className="px-4 py-3">
                    <input
                      disabled={initialData.captura_bloqueada || saving}
                      inputMode="decimal"
                      min="0"
                      max="10"
                      step="0.1"
                      value={values[keyFor(fila.inscripcion_id, componente.id)] ?? ""}
                      onChange={(event) => setValues((current) => ({ ...current, [keyFor(fila.inscripcion_id, componente.id)]: event.target.value }))}
                      className="w-24 rounded-xl border border-[#e7dcc9] bg-white px-3 py-2 text-sm font-bold text-[#152b25] outline-none focus:border-[#7a123d]"
                      placeholder="Vacío"
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap gap-3">
        <Button disabled={initialData.captura_bloqueada || saving} onClick={() => void save()}>
          {saving ? "Guardando..." : "Guardar captura"}
        </Button>
      </div>
      {message ? <div className="rounded-2xl border border-[#b7d9c9] bg-[#edf8f2] px-4 py-3 text-sm font-bold text-[#0b4a3d]">{message}</div> : null}
      {error ? <ErrorMessage message={error} /> : null}
    </section>
  );
}

function keyFor(inscripcionId: number, componenteId: number) {
  return `${inscripcionId}:${componenteId}`;
}
