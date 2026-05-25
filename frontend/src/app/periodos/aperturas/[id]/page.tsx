"use client";

import { useParams } from "next/navigation";
import { OpeningProcessDetail } from "@/components/trayectoria-operativa/TrajectoryOperations";

export default function AperturaDetallePage() {
  const params = useParams<{ id: string }>();
  return <OpeningProcessDetail id={params.id} />;
}
