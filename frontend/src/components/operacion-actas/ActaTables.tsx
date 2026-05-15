import type { ReactNode } from "react";
import type { ActaComponente, ActaFilaDetalle, ValidacionActaDTO } from "@/lib/types";
import { ValidationTimeline } from "@/components/trazabilidad";

export function ActaDetailTable({ filas }: { filas: ActaFilaDetalle[] }) {
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 shadow-sm">
      <div className="border-b border-[#eadfce] p-4">
        <h3 className="text-base font-black text-[#101b18]">Detalle del acta</h3>
        <p className="text-sm text-[#5f6764]">No se muestra matrícula militar por defecto.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead>
            <tr className="bg-[#0b4a3d] text-white">
              <Header>Discente</Header>
              <Header>Componentes</Header>
              <Header>Resultado corte</Header>
              <Header>Promedio parciales</Header>
              <Header>Final preliminar</Header>
              <Header>Estado</Header>
              <Header>Conformidad</Header>
            </tr>
          </thead>
          <tbody>
            {filas.map((fila) => (
              <tr key={fila.detalle_id} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                <Cell>
                  {fila.discente ? (
                    <div>
                      <p className="font-black text-[#152b25]">{fila.discente.nombre_institucional || fila.discente.nombre}</p>
                      <p className="text-xs text-[#5f6764]">{fila.discente.situacion_actual_label || fila.discente.situacion_actual}</p>
                    </div>
                  ) : (
                    "Mi resultado"
                  )}
                </Cell>
                <Cell>
                  <div className="space-y-1">
                    {fila.calificaciones.map((calificacion) => (
                      <p key={`${fila.detalle_id}-${calificacion.componente_id}`} className="whitespace-nowrap">
                        <span className="font-bold">{String(calificacion.nombre)}:</span>{" "}
                        {formatValue(calificacion.valor_capturado)}
                        {calificacion.sustituido_por_exencion ? <span className="ml-2 rounded-full bg-[#edf8f2] px-2 py-0.5 text-xs font-black text-[#0b4a3d]">Exención</span> : null}
                      </p>
                    ))}
                  </div>
                </Cell>
                <Cell>{formatValue(fila.resultado_corte)}</Cell>
                <Cell>{formatValue(fila.promedio_parciales)}</Cell>
                <Cell>{formatValue(fila.resultado_final_preliminar)}</Cell>
                <Cell>{fila.completo ? fila.resultado_preliminar : "Incompleto"}</Cell>
                <Cell>{fila.conformidad_vigente?.estado_conformidad_label || "Sin registro"}</Cell>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function ActaComponentsTable({ componentes }: { componentes: ActaComponente[] }) {
  if (!componentes.length) return null;
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/90 p-4 shadow-sm">
      <h3 className="text-base font-black text-[#101b18]">Componentes</h3>
      <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {componentes.map((componente) => (
          <div key={componente.id} className="rounded-2xl border border-[#eadfce] bg-[#fffaf1] p-4">
            <p className="text-sm font-black text-[#152b25]">{componente.nombre}</p>
            <p className="mt-1 text-xs text-[#5f6764]">{formatValue(componente.porcentaje)}% {componente.es_examen ? "· Examen" : ""}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export function ActaValidationTimeline({ validaciones }: { validaciones: ValidacionActaDTO[] }) {
  return <ValidationTimeline validaciones={validaciones} />;
}

function Header({ children }: { children: ReactNode }) {
  return <th className="whitespace-nowrap px-4 py-3 text-xs font-black uppercase tracking-[0.08em]">{children}</th>;
}

function Cell({ children }: { children: ReactNode }) {
  return <td className="max-w-[360px] px-4 py-3 align-top text-[#263b34]">{children}</td>;
}

export function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "boolean") return value ? "Sí" : "No";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(1);
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}
