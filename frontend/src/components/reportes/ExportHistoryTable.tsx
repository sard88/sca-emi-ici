import type { ExportacionRegistro } from "@/lib/types";
import { ExportStatusBadge } from "./ExportStatusBadge";

export function ExportHistoryTable({ items, showUser = false }: { items: ExportacionRegistro[]; showUser?: boolean }) {
  return (
    <div className="overflow-hidden rounded-[1.5rem] border border-[#eadfce] bg-white/88 shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-[#fff7e8] text-xs font-black uppercase tracking-[0.14em] text-[#7b5a2b]">
            <tr>
              <th className="px-4 py-3">Folio</th>
              {showUser ? <th className="px-4 py-3">Usuario</th> : null}
              <th className="px-4 py-3">Documento</th>
              <th className="px-4 py-3">Formato</th>
              <th className="px-4 py-3">Estado</th>
              <th className="px-4 py-3">Archivo</th>
              <th className="px-4 py-3">Fecha</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#f0e2cf]">
            {items.map((item) => (
              <tr key={item.id} className="align-top">
                <td className="px-4 py-4 font-black text-[#7a123d]">#{item.id}</td>
                {showUser ? <td className="px-4 py-4 font-bold text-[#152b25]">{item.usuario.nombre || item.usuario.username}</td> : null}
                <td className="px-4 py-4">
                  <p className="font-black text-[#152b25]">{item.tipo_documento_label || item.nombre_documento}</p>
                  <p className="mt-1 text-xs text-[#66716c]">{item.objeto_repr || "Sin objeto asociado"}</p>
                </td>
                <td className="px-4 py-4 font-black text-[#5f4525]">{item.formato}</td>
                <td className="px-4 py-4"><ExportStatusBadge estado={item.estado} label={item.estado_label} /></td>
                <td className="max-w-[18rem] px-4 py-4 text-xs font-semibold text-[#5f6764]">{item.nombre_archivo}</td>
                <td className="px-4 py-4 text-xs font-semibold text-[#5f6764]">{formatDateTime(item.creado_en)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function formatDateTime(value: string | null) {
  if (!value) return "Sin fecha";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}
