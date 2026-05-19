import type { ReactNode } from "react";
import type { ActaComponente, ActaFilaDetalle, ValidacionActaDTO } from "@/lib/types";
import { ValidationTimeline } from "@/components/trazabilidad";

export function ActaDetailTable({ filas, componentes }: { filas: ActaFilaDetalle[]; componentes: ActaComponente[] }) {
  const orderedComponents = [...componentes].sort((a, b) => (a.orden ?? 0) - (b.orden ?? 0));

  return (
    <section className="rounded-[1.25rem] border border-[#eadfce] bg-white/90 shadow-sm">
      <div className="border-b border-[#eadfce] px-4 py-3">
        <h3 className="text-sm font-black text-[#101b18]">Detalle del acta</h3>
        <p className="text-xs text-[#5f6764]">Detalle académico por discente.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full table-fixed border-collapse text-left text-xs">
          <thead>
            <tr className="bg-[#0b4a3d] text-white">
              <Header>No.</Header>
              <Header>Grado y empleo</Header>
              <Header>Nombre</Header>
              {orderedComponents.map((componente) => (
                <Header key={`head-${componente.id}`}>{componente.nombre}</Header>
              ))}
              <Header>Calificación parcial</Header>
              <Header>Estado</Header>
              <Header>Conformidad</Header>
            </tr>
          </thead>
          <tbody>
            {filas.map((fila, index) => {
              const valuesByComponent = new Map(fila.calificaciones.map((calificacion) => [calificacion.componente_id, calificacion]));
              return (
                <tr key={fila.detalle_id} className="border-b border-[#f0e5d6] odd:bg-white even:bg-[#fffaf1]/70">
                  <Cell className="text-center">{index + 1}</Cell>
                  <Cell className="break-words">{fila.discente?.grado_empleo || "—"}</Cell>
                  <Cell className="max-w-[220px] break-words">
                    {fila.discente ? (
                      <div>
                        <p className="font-black text-[#152b25]">{fila.discente.nombre_institucional || fila.discente.nombre}</p>
                        {fila.discente.situacion_actual_label || fila.discente.situacion_actual ? (
                          <p className="text-xs text-[#5f6764]">{fila.discente.situacion_actual_label || fila.discente.situacion_actual}</p>
                        ) : null}
                      </div>
                    ) : (
                      "Mi resultado"
                    )}
                  </Cell>
                  {orderedComponents.map((componente) => {
                    const calificacion = valuesByComponent.get(componente.id);
                    return (
                      <Cell key={`row-${fila.detalle_id}-${componente.id}`} className="text-center">
                        {formatValue(calificacion?.valor_capturado)}
                        {calificacion?.sustituido_por_exencion ? (
                          <span className="ml-1 rounded-full bg-[#edf8f2] px-1.5 py-0.5 text-[10px] font-black text-[#0b4a3d]">Exención</span>
                        ) : null}
                      </Cell>
                    );
                  })}
                  <Cell className="text-center">{formatValue(fila.resultado_corte)}</Cell>
                  <Cell className="text-center">{fila.completo ? fila.resultado_preliminar : "Incompleto"}</Cell>
                  <Cell className="text-center">{fila.conformidad_vigente?.estado_conformidad_label || "Sin registro"}</Cell>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function ActaComponentsTable({ componentes }: { componentes: ActaComponente[] }) {
  if (!componentes.length) return null;
  const ordered = [...componentes].sort((a, b) => (a.orden ?? 0) - (b.orden ?? 0));

  return (
    <section className="rounded-[1.25rem] border border-[#eadfce] bg-white/90 shadow-sm">
      <div className="border-b border-[#eadfce] px-4 py-3">
        <h3 className="text-sm font-black text-[#101b18]">Componentes</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-[#f7f0e3] text-xs font-black uppercase tracking-[0.08em] text-[#5f6764]">
            <tr>
              <th className="px-3 py-2 text-left">Componente</th>
              <th className="px-3 py-2 text-left">Ponderación</th>
              <th className="px-3 py-2 text-left">Tipo</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#f0e5d6] text-[#263b34]">
            {ordered.map((componente) => (
              <tr key={componente.id}>
                <td className="px-3 py-2">{componente.nombre}</td>
                <td className="px-3 py-2">{formatValue(componente.porcentaje)}%</td>
                <td className="px-3 py-2">{componente.es_examen ? "Examen" : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function ActaValidationTimeline({ validaciones }: { validaciones: ValidacionActaDTO[] }) {
  return <ValidationTimeline validaciones={validaciones} />;
}

function Header({ children }: { children: ReactNode }) {
  return <th className="px-2 py-2 text-[11px] font-black uppercase tracking-[0.06em] align-middle break-words">{children}</th>;
}

function Cell({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <td className={`max-w-[220px] px-2 py-2 align-top text-[#263b34] ${className}`}>{children}</td>;
}

export function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "N/A";
  if (typeof value === "boolean") return value ? "Sí" : "No";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(1);
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}
