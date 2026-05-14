"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { OperativeReportPage } from "@/components/reportes/operativos/OperativeReportPage";
import { getReporteOperativoConfig } from "@/lib/reportes-operativos";

export default function ReporteOperativoDetallePage() {
  const params = useParams<{ slug: string }>();
  const config = getReporteOperativoConfig(params.slug);

  if (!config) {
    return (
      <AppShell>
        <ErrorMessage message="Reporte operativo no reconocido." />
      </AppShell>
    );
  }

  return <OperativeReportPage config={config} />;
}
