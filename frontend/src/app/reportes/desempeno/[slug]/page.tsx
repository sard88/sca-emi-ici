"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { PerformanceReportPage } from "@/components/reportes/desempeno/PerformanceReportPage";
import { getReporteDesempenoConfig } from "@/lib/reportes-desempeno";

export default function ReporteDesempenoDetallePage() {
  const params = useParams<{ slug: string }>();
  const config = getReporteDesempenoConfig(params.slug);

  if (!config) {
    return (
      <AppShell>
        <ErrorMessage message="Reporte de desempeño no reconocido." />
      </AppShell>
    );
  }

  return <PerformanceReportPage config={config} />;
}
