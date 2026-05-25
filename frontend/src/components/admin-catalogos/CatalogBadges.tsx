export function CatalogStatusBadge({ value }: { value: unknown }) {
  const label = value ? String(value) : "Sin estado";
  const normalized = label.toLowerCase();
  const styles = normalized.includes("activo") || normalized.includes("abierto")
    ? "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]"
    : normalized.includes("cerrado") || normalized.includes("bloqueado")
      ? "border-[#e7c3ce] bg-[#fff1f5] text-[#7a123d]"
      : "border-[#d8c5a7] bg-[#fff7e8] text-[#7b4c0c]";

  return <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-black uppercase tracking-[0.12em] ${styles}`}>{label}</span>;
}

export function CatalogBooleanBadge({ value }: { value: unknown }) {
  const active = Boolean(value);
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-black uppercase tracking-[0.12em] ${active ? "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]" : "border-[#e5ded2] bg-white text-[#5f6764]"}`}>
      {active ? "Sí" : "No"}
    </span>
  );
}
