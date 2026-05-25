import type { ReporteDesempenoItem } from "@/lib/types";

type GroupedRange = {
  range: string;
  groups: Array<{
    group: string;
    rows: ReporteDesempenoItem[];
  }>;
};

export function PerformanceHonorRollPreview({ items }: { items: ReporteDesempenoItem[] }) {
  const sections = groupByRangeAndGroup(items);

  if (items.length === 0) {
    return (
      <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm">
        <h3 className="text-base font-black text-[#101b18]">Cuadro de aprovechamiento académico</h3>
        <p className="mt-2 text-sm text-[#5f6764]">Sin información disponible.</p>
      </section>
    );
  }

  return (
    <section className="rounded-[1.5rem] border border-[#d8c5a7] bg-[#fffaf1] shadow-sm">
      <div className="border-b border-[#eadfce] px-5 py-4">
        <p className="text-xs font-black uppercase tracking-[0.2em] text-[#9f6a22]">Vista previa institucional</p>
        <h3 className="mt-2 text-lg font-black text-[#101b18]">Cuadro de aprovechamiento académico</h3>
        <p className="mt-1 text-sm text-[#5f6764]">Consulta de discentes agrupados por rango de aprovechamiento.</p>
      </div>

      <div className="space-y-5 p-4">
        {sections.map((section) => (
          <article key={section.range} className="overflow-hidden rounded-2xl border border-[#d8c5a7] bg-white/90">
            <div className="bg-[#073f34] px-4 py-3 text-white">
              <h4 className="text-sm font-black uppercase tracking-[0.12em]">{section.range}</h4>
            </div>
            <div className="space-y-4 p-4">
              {section.groups.map((group) => (
                <div key={`${section.range}-${group.group}`} className="overflow-hidden rounded-xl border border-[#eadfce]">
                  <div className="flex items-center justify-between border-b border-[#eadfce] bg-[#fff7e8] px-4 py-2">
                    <p className="text-xs font-black uppercase tracking-[0.14em] text-[#7b4c0c]">Grupo {group.group}</p>
                    <p className="text-xs font-bold text-[#5f6764]">{group.rows.length} registros</p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full border-collapse text-left text-sm">
                      <thead>
                        <tr className="bg-[#f7efe2] text-[#152b25]">
                          <th className="px-3 py-2 text-xs font-black uppercase">Grupo</th>
                          <th className="px-3 py-2 text-xs font-black uppercase">No.</th>
                          <th className="px-3 py-2 text-xs font-black uppercase">Grado y empleo</th>
                          <th className="px-3 py-2 text-xs font-black uppercase">Nombre</th>
                          <th className="px-3 py-2 text-right text-xs font-black uppercase">Promedio</th>
                        </tr>
                      </thead>
                      <tbody>
                        {group.rows.map((row, index) => (
                          <tr key={`${group.group}-${index}-${value(row, "nombre_discente")}`} className="border-t border-[#f0e5d6]">
                            <td className="px-3 py-2 font-bold text-[#263b34]">{group.group}</td>
                            <td className="px-3 py-2 text-[#263b34]">{value(row, "lugar") || index + 1}</td>
                            <td className="px-3 py-2 text-[#263b34]">{value(row, "grado") || "N/A"}</td>
                            <td className="max-w-[360px] px-3 py-2 font-semibold text-[#152b25]">{value(row, "nombre_discente") || "N/A"}</td>
                            <td className="px-3 py-2 text-right font-black text-[#7a123d]">{value(row, "promedio") || "N/A"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function groupByRangeAndGroup(items: ReporteDesempenoItem[]): GroupedRange[] {
  const ranges = new Map<string, Map<string, ReporteDesempenoItem[]>>();
  for (const item of items) {
    const range = value(item, "rango_aprovechamiento") || "Sin rango";
    const group = value(item, "grupo") || "Sin grupo";
    if (!ranges.has(range)) ranges.set(range, new Map());
    const groups = ranges.get(range)!;
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group)!.push(item);
  }

  return Array.from(ranges.entries()).map(([range, groups]) => ({
    range,
    groups: Array.from(groups.entries()).map(([group, rows]) => ({
      group,
      rows: [...rows].sort((a, b) => Number(value(a, "lugar") || 0) - Number(value(b, "lugar") || 0)),
    })),
  }));
}

function value(item: ReporteDesempenoItem, key: string) {
  const raw = item[key];
  if (raw === null || raw === undefined) return "";
  return String(raw);
}
