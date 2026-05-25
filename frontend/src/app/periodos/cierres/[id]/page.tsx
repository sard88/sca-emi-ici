"use client";

import { useParams } from "next/navigation";
import { ClosureProcessDetail } from "@/components/trayectoria-operativa/TrajectoryOperations";

export default function CierreDetallePage() {
  const params = useParams<{ id: string }>();
  return <ClosureProcessDetail id={params.id} />;
}
