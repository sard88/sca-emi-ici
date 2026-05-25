import { EmptyState } from "@/components/states/EmptyState";

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
          ? "Ajusta el nombre, carrera, situación académica o ID interno e intenta nuevamente."
          : "El backend no devolvió discentes autorizados para exportar kárdex oficial."
      }
    />
  );
}
