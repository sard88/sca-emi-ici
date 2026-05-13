import { EmptyState } from "@/components/states/EmptyState";

export function EmptyExportsState({
  title = "No hay exportaciones registradas.",
  description = "Cuando generes documentos autorizados, aparecerán en esta sección.",
}: {
  title?: string;
  description?: string;
}) {
  return <EmptyState title={title} description={description} />;
}
