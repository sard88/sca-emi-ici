"use client";

import { useParams } from "next/navigation";
import { ExtraordinaryDetail } from "@/components/trayectoria-operativa/TrajectoryOperations";

export default function ExtraordinarioDetallePage() {
  const params = useParams<{ id: string }>();
  return <ExtraordinaryDetail id={params.id} />;
}
