import { ErrorState, type ErrorStateVariant } from "@/components/ui/ErrorState";

export function ErrorMessage({ message, variant }: { message: string; variant?: ErrorStateVariant }) {
  const resolvedVariant = variant ?? (message.toLowerCase().includes("permiso") ? "forbidden" : "error");
  return <ErrorState description={message} variant={resolvedVariant} compact />;
}
