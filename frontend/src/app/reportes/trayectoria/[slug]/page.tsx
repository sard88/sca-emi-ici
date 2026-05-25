"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { TrajectoryReportPage } from "@/components/reportes/trayectoria/TrajectoryReportPage";
import { getReporteTrayectoriaConfig } from "@/lib/reportes-trayectoria";

export default function ReporteTrayectoriaDetallePage() {
  const params = useParams<{ slug: string }>();
  const config = getReporteTrayectoriaConfig(params.slug);

  if (!config) {
    return (
      <AppShell>
        <ErrorMessage message="Reporte de trayectoria no reconocido." />
      </AppShell>
    );
  }

  return <TrajectoryReportPage config={config} />;
}
