import { EmptyState, type EmptyStateVariant } from "@/components/ui/EmptyState";

export function EmptyExportsState({
  title = "No hay exportaciones registradas.",
  description = "Cuando generes documentos autorizados, aparecerán en esta sección.",
  variant = "noData",
}: {
  title?: string;
  description?: string;
  variant?: EmptyStateVariant;
}) {
  return <EmptyState title={title} description={description} variant={variant} />;
}
