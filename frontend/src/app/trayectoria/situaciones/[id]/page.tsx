"use client";

import { useParams } from "next/navigation";
import { AcademicSituationDetail } from "@/components/trayectoria-operativa/TrajectoryOperations";

export default function SituacionDetallePage() {
  const params = useParams<{ id: string }>();
  return <AcademicSituationDetail id={params.id} />;
}
