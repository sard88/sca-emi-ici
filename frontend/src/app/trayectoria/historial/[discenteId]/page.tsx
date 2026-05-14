"use client";

import { useParams } from "next/navigation";
import { InstitutionalHistoryDetail } from "@/components/trayectoria-operativa/TrajectoryOperations";

export default function HistorialDetallePage() {
  const params = useParams<{ discenteId: string }>();
  return <InstitutionalHistoryDetail discenteId={params.discenteId} />;
}
