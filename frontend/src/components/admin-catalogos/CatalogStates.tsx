export function CatalogEmptyState({ title = "No hay registros.", description = "El backend no devolvió registros para los filtros actuales." }: { title?: string; description?: string }) {
  return (
    <section className="rounded-[1.5rem] border border-dashed border-[#d8c5a7] bg-white/72 p-8 text-center shadow-sm">
      <p className="text-lg font-black text-[#152b25]">{title}</p>
      <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-[#5f6764]">{description}</p>
    </section>
  );
}

export function CatalogErrorState({ message }: { message: string }) {
  return (
    <section className="rounded-[1.5rem] border border-[#e7c3ce] bg-[#fff7f9] p-5 text-sm font-bold leading-6 text-[#7a123d] shadow-sm">
      {message}
    </section>
  );
}

export function CatalogLoadingState({ label = "Cargando registros..." }: { label?: string }) {
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-6 text-sm font-black text-[#10372e] shadow-sm">
      {label}
    </section>
  );
}
