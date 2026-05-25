"use client";

import { useState } from "react";
import { registrarConformidadDiscente } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/states/ErrorMessage";

export function StudentConformityForm({ detalleId, disabled, onDone }: { detalleId: number; disabled?: boolean; onDone: () => void }) {
  const [tipo, setTipo] = useState("ACUSE");
  const [comentario, setComentario] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (tipo === "INCONFORME" && !comentario.trim()) {
      setError("El comentario es obligatorio cuando registras inconformidad.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await registrarConformidadDiscente(detalleId, { tipo_conformidad: tipo, comentario });
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible registrar la conformidad.");
    } finally {
      setSaving(false);
    }
  }

  if (disabled) {
    return (
      <div className="rounded-2xl border border-[#d8c5a7] bg-[#fffaf1] px-4 py-3 text-sm font-bold text-[#6f4a16]">
        La conformidad quedó en solo lectura después de remitir el acta.
      </div>
    );
  }

  return (
    <section className="space-y-4 rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      <div>
        <h3 className="text-base font-black text-[#101b18]">Conformidad informativa</h3>
        <p className="text-sm text-[#5f6764]">Si registras inconformidad, el comentario es obligatorio.</p>
      </div>
      <select className="w-full rounded-xl border border-[#e7dcc9] bg-white px-3 py-2.5 text-sm font-semibold text-[#152b25]" value={tipo} onChange={(event) => setTipo(event.target.value)}>
        <option value="ACUSE">Acuse de recibo</option>
        <option value="CONFORME">Conforme</option>
        <option value="INCONFORME">Inconforme</option>
      </select>
      <textarea
        rows={4}
        className="w-full rounded-xl border border-[#e7dcc9] bg-white px-3 py-2.5 text-sm text-[#152b25] outline-none focus:border-[#7a123d]"
        placeholder="Comentario"
        value={comentario}
        onChange={(event) => setComentario(event.target.value)}
      />
      <Button disabled={saving} onClick={() => void submit()}>
        {saving ? "Registrando..." : "Registrar conformidad"}
      </Button>
      {error ? <ErrorMessage message={error} /> : null}
    </section>
  );
}
