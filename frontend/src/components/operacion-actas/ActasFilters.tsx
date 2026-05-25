"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export type ActasFilterValues = {
  periodo?: string;
  carrera?: string;
  grupo?: string;
  docente?: string;
  corte?: string;
  estado?: string;
};

export function ActasFilters({ onApply, includeEstado = true }: { onApply: (values: Record<string, string>) => void; includeEstado?: boolean }) {
  const [values, setValues] = useState<ActasFilterValues>({});

  function update(key: keyof ActasFilterValues, value: string) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  function clean() {
    const params: Record<string, string> = {};
    Object.entries(values).forEach(([key, value]) => {
      const text = String(value || "").trim();
      if (text) params[key] = text;
    });
    return params;
  }

  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        <Input placeholder="Periodo" value={values.periodo || ""} onChange={(event) => update("periodo", event.target.value)} />
        <Input placeholder="Carrera" value={values.carrera || ""} onChange={(event) => update("carrera", event.target.value)} />
        <Input placeholder="Grupo" value={values.grupo || ""} onChange={(event) => update("grupo", event.target.value)} />
        <Input placeholder="Docente" value={values.docente || ""} onChange={(event) => update("docente", event.target.value)} />
        <select className="rounded-xl border border-[#e7dcc9] bg-white px-3 py-2.5 text-sm font-semibold text-[#152b25]" value={values.corte || ""} onChange={(event) => update("corte", event.target.value)}>
          <option value="">Todos los cortes</option>
          <option value="P1">P1</option>
          <option value="P2">P2</option>
          <option value="P3">P3</option>
          <option value="FINAL">Final</option>
        </select>
        {includeEstado ? (
          <select className="rounded-xl border border-[#e7dcc9] bg-white px-3 py-2.5 text-sm font-semibold text-[#152b25]" value={values.estado || ""} onChange={(event) => update("estado", event.target.value)}>
            <option value="">Todos los estados</option>
            <option value="BORRADOR_DOCENTE">Borrador</option>
            <option value="PUBLICADO_DISCENTE">Publicado</option>
            <option value="REMITIDO_JEFATURA_CARRERA">Remitido</option>
            <option value="VALIDADO_JEFATURA_CARRERA">Validado</option>
            <option value="FORMALIZADO_JEFATURA_ACADEMICA">Formalizado</option>
          </select>
        ) : null}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button onClick={() => onApply(clean())}>Aplicar filtros</Button>
        <Button className="bg-[#73614d] hover:bg-[#5e4d3d]" onClick={() => { setValues({}); onApply({}); }}>
          Limpiar
        </Button>
      </div>
    </section>
  );
}
