"use client";

import { useParams } from "next/navigation";
import { AcademicMovementDetail } from "@/components/trayectoria-operativa/TrajectoryOperations";

export default function MovimientoDetallePage() {
  const params = useParams<{ id: string }>();
  return <AcademicMovementDetail id={params.id} />;
}
