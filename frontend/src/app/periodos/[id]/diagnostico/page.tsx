"use client";

import { useParams } from "next/navigation";
import { ClosureDiagnosticPanel } from "@/components/trayectoria-operativa/TrajectoryOperations";

export default function DiagnosticoCierrePage() {
  const params = useParams<{ id: string }>();
  return <ClosureDiagnosticPanel periodoId={params.id} />;
}
