import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";

export function CatalogEmptyState({ title = "No hay registros.", description = "El backend no devolvió registros para los filtros actuales." }: { title?: string; description?: string }) {
  return <EmptyState title={title} description={description} variant="search" />;
}

export function CatalogErrorState({ message }: { message: string }) {
  return <ErrorState description={message} variant={message.includes("permiso") ? "forbidden" : "error"} compact />;
}

export function CatalogLoadingState({ label = "Cargando registros..." }: { label?: string }) {
  return (
    <section className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-6 text-sm font-black text-[#10372e] shadow-sm">
      {label}
    </section>
  );
}
