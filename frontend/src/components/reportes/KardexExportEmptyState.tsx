import { EmptyState } from "@/components/ui/EmptyState";

export function KardexExportEmptyState({
  filtered = false,
}: {
  filtered?: boolean;
}) {
  return (
    <EmptyState
      title={filtered ? "No hay discentes que coincidan con la búsqueda." : "No hay kárdex exportables para tu perfil."}
      description={
        filtered
          ? "Ajusta el nombre, carrera o situación académica e intenta nuevamente."
          : "No hay discentes disponibles para exportación con los filtros aplicados."
      }
      variant={filtered ? "search" : "restricted"}
    />
  );
}
