import { StatusBadge } from "./StatusBadge";

export function RoleBadge({ value }: { value?: string | null }) {
  if (!value) return <StatusBadge>Sin rol principal</StatusBadge>;
  return <StatusBadge tone="success">{value.replaceAll("_", " ")}</StatusBadge>;
}
