"use client";

import { useState } from "react";
import { formalizarActaJefaturaAcademica, publicarActaDocente, regenerarActaDocente, remitirActaDocente, validarActaJefaturaCarrera } from "@/lib/api";
import type { ActaDetalle, ActaResumen } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { microcopy } from "@/lib/microcopy";
import { uiLabels } from "@/lib/glosario";

export function TeacherActaActionButtons({ acta, onChanged }: { acta: ActaResumen; onChanged: () => void }) {
  return (
    <ActaActionsPanel
      actions={[
        { label: uiLabels.actas.regenerarBorrador, visible: Boolean(acta.acciones?.puede_regenerar), confirm: "Solo se puede regenerar en borrador docente. ¿Continuamos?", run: () => regenerarActaDocente(acta.acta_id) },
        { label: uiLabels.actas.publicar, visible: Boolean(acta.acciones?.puede_publicar), confirm: "El acta será visible para los discentes. ¿Publicar acta?", run: () => publicarActaDocente(acta.acta_id) },
        { label: uiLabels.actas.remitir, visible: Boolean(acta.acciones?.puede_remitir), confirm: `${microcopy.actas.soloLectura} ¿Remitir acta?`, run: () => remitirActaDocente(acta.acta_id) },
      ]}
      onChanged={onChanged}
    />
  );
}

export function HeadValidationActionPanel({ acta, onChanged }: { acta: ActaResumen; onChanged: () => void }) {
  return (
    <ActaActionsPanel
      actions={[
        { label: "Validar acta", visible: Boolean(acta.acciones?.puede_validar_carrera), confirm: "La validación no modifica calificaciones. ¿Validar acta?", run: () => validarActaJefaturaCarrera(acta.acta_id) },
      ]}
      onChanged={onChanged}
    />
  );
}

export function FormalizationActionPanel({ acta, onChanged }: { acta: ActaResumen; onChanged: () => void }) {
  return (
    <ActaActionsPanel
      warning="La formalización convierte el acta en información oficial. Si es acta de evaluación final, actualizará resultados oficiales mediante el servicio backend existente."
      actions={[
        { label: "Formalizar acta", visible: Boolean(acta.acciones?.puede_formalizar), confirm: "Esta acción formaliza el acta. ¿Confirmas?", run: () => formalizarActaJefaturaAcademica(acta.acta_id) },
      ]}
      onChanged={onChanged}
    />
  );
}

type PanelAction = {
  label: string;
  visible: boolean;
  confirm: string;
  run: () => Promise<unknown>;
};

function ActaActionsPanel({ actions, warning, onChanged }: { actions: PanelAction[]; warning?: string; onChanged: () => void }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const visible = actions.filter((action) => action.visible);
  if (!visible.length) return null;

  async function execute(action: PanelAction) {
    if (!window.confirm(action.confirm)) return;
    setBusy(action.label);
    setError(null);
    try {
      await action.run();
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible completar la acción.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <section className="space-y-3 rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      <h3 className="text-base font-black text-[#101b18]">Acciones disponibles</h3>
      {warning ? <p className="rounded-2xl border border-[#efc3c7] bg-[#fff1f2] px-4 py-3 text-sm font-bold text-[#8c1239]">{warning}</p> : null}
      <div className="flex flex-wrap gap-2">
        {visible.map((action) => (
          <Button key={action.label} disabled={Boolean(busy)} onClick={() => void execute(action)}>
            {busy === action.label ? "Procesando..." : action.label}
          </Button>
        ))}
      </div>
      {error ? <ErrorMessage message={error} /> : null}
    </section>
  );
}

export function ActaActionsPanelReadOnly({ data }: { data: ActaDetalle }) {
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      <h3 className="text-base font-black text-[#101b18]">Acciones</h3>
      <p className="mt-1 text-sm text-[#5f6764]">
        {Object.values(data.acciones || {}).some(Boolean) ? "Hay acciones disponibles según el backend." : "No hay acciones disponibles para tu perfil o el estado actual."}
      </p>
    </section>
  );
}
