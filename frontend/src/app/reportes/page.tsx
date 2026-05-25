"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { LoadingState } from "@/components/states/LoadingState";
import { ReportCatalogCard } from "@/components/reportes/ReportCatalogCard";
import { ExportHistoryTable } from "@/components/reportes/ExportHistoryTable";
import { getExportaciones, getReportesCatalogo } from "@/lib/api";
import { canAccessAuditoriaExportaciones, canAccessKardexPdf, canAccessReportes, canAccessReportesOperativos } from "@/lib/dashboard";
import { canAccessReporteOperativo, reportesOperativos } from "@/lib/reportes-operativos";
import { useAuth } from "@/lib/auth";
import type { AuthenticatedUser, ExportacionRegistro, ReporteCatalogoItem } from "@/lib/types";

export default function ReportesPage() {
  const { user } = useAuth();
  const [catalogo, setCatalogo] = useState<ReporteCatalogoItem[]>([]);
  const [exportaciones, setExportaciones] = useState<ExportacionRegistro[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [catalogoResponse, exportacionesResponse] = await Promise.all([
          getReportesCatalogo(),
          getExportaciones({ limit: "6" }),
        ]);
        setCatalogo(catalogoResponse.items);
        setExportaciones(exportacionesResponse.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar reportes y exportaciones.");
      } finally {
        setLoading(false);
      }
    }

    if (user && canAccessReportes(user)) void load();
  }, [user]);

  return (
    <AppShell>
      {!user ? null : !canAccessReportes(user) ? (
        <ErrorMessage message="No tienes permiso para consultar reportes y exportaciones desde el portal." />
      ) : (
        <div className="space-y-6">
          <PageHeader
            title="Reportes y exportaciones"
            description="Consulta el catálogo documental disponible, descarga actas autorizadas y revisa la trazabilidad de tus exportaciones."
            user={user}
          />

          <section className="grid gap-4 md:grid-cols-3">
            <QuickLink title="Actas exportables" description="PDF/XLSX de actas de corte y calificación final." href="/reportes/actas" />
            {canAccessReportesOperativos(user) ? (
              <QuickLink title="Reportes operativos" description="Actas, validaciones y exportaciones realizadas en XLSX." href="/reportes/operativos" />
            ) : null}
            {canAccessKardexPdf(user) ? (
              <QuickLink title="Kárdex oficial" description="PDF institucional desde ServicioKardex, con auditoría documental." href="/reportes/kardex" />
            ) : null}
            <QuickLink title="Historial de exportaciones" description="Descargas recientes y folios técnicos." href="/reportes/exportaciones" />
            {canAccessAuditoriaExportaciones(user) ? (
              <QuickLink title="Auditoría institucional" description="Consulta ampliada de salidas documentales." href="/reportes/auditoria" />
            ) : (
              <QuickLink title="Reportes futuros" description="Reportes analíticos y kárdex Excel quedarán para subbloques posteriores." />
            )}
          </section>

          {loading ? <LoadingState label="Cargando catálogo documental..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}

          {!loading && !error ? (
            <>
              <section>
                <div className="mb-4">
                  <h3 className="text-lg font-black text-[#101b18]">Catálogo de reportes</h3>
                  <p className="mt-1 text-sm text-[#5f6764]">
                    Las actas PDF/XLSX ya están integradas. Los reportes todavía no implementados se muestran como pendientes sin inventar información.
                  </p>
                </div>
                {catalogo.length > 0 ? (
                  <div className="grid gap-4 xl:grid-cols-2">
                    {catalogo.map((item) => (
                      <ReportCatalogCard
                        key={item.codigo}
                        item={item}
                        actionHref={actionHrefForCatalogItem(item, user)}
                        actionLabel={actionLabelForCatalogItem(item)}
                      />
                    ))}
                  </div>
                ) : (
                  <EmptyState title="Sin catálogo disponible" description="El backend no devolvió reportes para tu perfil." />
                )}
              </section>

              <section>
                <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <h3 className="text-lg font-black text-[#101b18]">Últimas exportaciones</h3>
                    <p className="mt-1 text-sm text-[#5f6764]">Trazabilidad reciente registrada por el núcleo de auditoría del Bloque 9A.</p>
                  </div>
                  <Link href="/reportes/exportaciones" className="text-sm font-black text-[#7a123d]">Ver historial completo</Link>
                </div>
                {exportaciones.length > 0 ? (
                  <ExportHistoryTable items={exportaciones} showUser={canAccessAuditoriaExportaciones(user)} />
                ) : (
                  <EmptyState title="No hay exportaciones registradas." description="Cuando generes documentos autorizados, aparecerán en esta sección." />
                )}
              </section>
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function actionHrefForCatalogItem(item: ReporteCatalogoItem, user: AuthenticatedUser) {
  if (item.codigo === "KARDEX_OFICIAL" && canAccessKardexPdf(user)) return "/reportes/kardex";
  if (!canAccessReportesOperativos(user)) return undefined;
  return reportesOperativos.find((config) => config.tipoDocumento === item.codigo && canAccessReporteOperativo(user, config))?.ruta;
}

function actionLabelForCatalogItem(item: ReporteCatalogoItem) {
  if (item.codigo === "KARDEX_OFICIAL") return "Exportar kárdex PDF";
  if (reportesOperativos.some((config) => config.tipoDocumento === item.codigo)) return "Ver reporte operativo";
  return "Abrir módulo";
}

function QuickLink({ title, description, href }: { title: string; description: string; href?: string }) {
  const className = "block rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-[#bc955c]";
  const content = (
    <>
      <p className="text-sm font-black text-[#7a123d]">{title}</p>
      <p className="mt-2 text-sm leading-6 text-[#5f6764]">{description}</p>
    </>
  );
  if (!href) return <div className={className}>{content}</div>;
  return <Link href={href} className={className}>{content}</Link>;
}
