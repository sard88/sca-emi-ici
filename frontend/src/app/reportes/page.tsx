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
import {
  canAccessAuditoria,
  canAccessAuditoriaExportaciones,
  canAccessKardexPdf,
  canAccessReportes,
  canAccessReportesDesempeno,
  canAccessReportesOperativos,
  canAccessReportesTrayectoria,
} from "@/lib/dashboard";
import { canAccessReporteDesempeno, reportesDesempeno } from "@/lib/reportes-desempeno";
import { canAccessReporteOperativo, reportesOperativos } from "@/lib/reportes-operativos";
import { canAccessReporteTrayectoria, reportesTrayectoria } from "@/lib/reportes-trayectoria";
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
        const [catalogoResponse, exportacionesResponse] = await Promise.all([getReportesCatalogo(), getExportaciones({ limit: "6" })]);
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

  const isJefaturaCarrera = user ? isJefaturaCarreraRole(user) : false;
  const isJefaturaAcademica = user ? isJefaturaAcademicaRole(user) : false;

  return (
    <AppShell>
      {!user ? null : !canAccessReportes(user) ? (
        <ErrorMessage message="No tienes permiso para consultar reportes." />
      ) : (
        <div className="space-y-5">
          <PageHeader title="Reportes y exportaciones" description="Consulta reportes y documentos disponibles según tu perfil autorizado." user={user} />

          <div className="space-y-5">
            <QuickSection
              title="Documentos oficiales y académicos"
              intent="Consultar y exportar documentos autorizados."
              links={[
                { title: "Actas PDF/XLSX", description: "Consultar y exportar actas de corte y calificación final.", href: "/reportes/actas" },
                canAccessKardexPdf(user) && !isJefaturaCarrera && !isJefaturaAcademica ? { title: "Kárdex oficial PDF", description: "Exportar Kárdex institucional autorizado.", href: "/reportes/kardex" } : null,
              ]}
            />

            <QuickSection
              title="Reportes institucionales"
              intent="Analizar operación, desempeño y trayectoria."
              links={[
                canAccessReportesOperativos(user) ? { title: "Reportes operativos", description: "Consultar actas, validaciones, pendientes e inconformidades.", href: "/reportes/operativos" } : null,
                canAccessReportesDesempeno(user) ? { title: "Desempeño académico", description: "Consultar resultados oficiales, promedios y aprovechamiento.", href: "/reportes/desempeno" } : null,
                canAccessReportesTrayectoria(user) ? { title: "Reportes de trayectoria", description: "Consultar extraordinarios, bajas, reingresos, movimientos e historial académico.", href: "/reportes/trayectoria" } : null,
              ]}
            />

            {!isJefaturaCarrera && !isJefaturaAcademica ? (
              <QuickSection
                title="Exportaciones"
                intent="Revisar archivos generados."
                links={[{ title: canAccessAuditoriaExportaciones(user) ? "Exportaciones institucionales" : "Mis exportaciones", description: "Consulta descargas realizadas.", href: "/reportes/exportaciones" }]}
              />
            ) : null}

            {!isJefaturaCarrera && !isJefaturaAcademica ? (
              <QuickSection
                title="Auditoría"
                intent="Consulta institucional autorizada."
                links={[canAccessAuditoria(user) ? { title: "Auditoría institucional", description: "Consulta eventos disponibles según tu perfil.", href: "/reportes/auditoria" } : null]}
              />
            ) : null}
          </div>

          {loading ? <LoadingState label="Cargando catálogo documental..." /> : null}
          {error ? <ErrorMessage message={error} /> : null}

          {!loading && !error ? (
            <>
              <section>
                <div className="mb-4">
                  <h3 className="text-lg font-black text-[#101b18]">Catálogo de reportes</h3>
                  <p className="mt-1 text-sm text-[#5f6764]">Consulta reportes disponibles según tu perfil autorizado.</p>
                </div>
                {catalogo.length > 0 ? (
                  <div className="grid gap-4 xl:grid-cols-2 2xl:grid-cols-3">
                    {catalogo.map((item) => (
                      <ReportCatalogCard key={item.codigo} item={item} actionHref={actionHrefForCatalogItem(item, user)} actionLabel={actionLabelForCatalogItem(item)} />
                    ))}
                  </div>
                ) : (
                  <EmptyState title="Sin catálogo disponible" description="No hay reportes disponibles para tu perfil en este momento." variant="noData" />
                )}
              </section>

              {!isJefaturaCarrera && !isJefaturaAcademica ? (
                <section>
                  <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                      <h3 className="text-lg font-black text-[#101b18]">Últimas exportaciones</h3>
                      <p className="mt-1 text-sm text-[#5f6764]">Consulta las descargas recientes disponibles para tu perfil.</p>
                    </div>
                    <Link href="/reportes/exportaciones" className="text-sm font-black text-[#7a123d]">
                      Ver historial completo
                    </Link>
                  </div>
                  {exportaciones.length > 0 ? <ExportHistoryTable items={exportaciones} showUser={canAccessAuditoriaExportaciones(user)} /> : <EmptyState title="Aún no hay exportaciones" description="Sin información disponible." variant="noData" />}
                </section>
              ) : null}
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}

function isJefaturaCarreraRole(user: AuthenticatedUser) {
  return (
    user.perfil_principal === "JEFE_CARRERA" ||
    user.roles.includes("JEFE_CARRERA") ||
    user.roles.includes("JEFATURA_CARRERA") ||
    user.roles.includes("JEFE_SUB_EJEC_CTR") ||
    user.cargos_vigentes.some((cargo) => ["JEFE_CARRERA", "JEFATURA_CARRERA", "JEFE_SUB_EJEC_CTR"].includes(cargo.cargo_codigo))
  );
}

function isJefaturaAcademicaRole(user: AuthenticatedUser) {
  return (
    user.perfil_principal === "JEFE_ACADEMICO" ||
    user.roles.includes("JEFE_ACADEMICO") ||
    user.roles.includes("JEFATURA_ACADEMICA") ||
    user.cargos_vigentes.some((cargo) => ["JEFE_ACADEMICO", "JEFATURA_ACADEMICA"].includes(cargo.cargo_codigo))
  );
}

function actionHrefForCatalogItem(item: ReporteCatalogoItem, user: AuthenticatedUser) {
  if (item.codigo === "KARDEX_OFICIAL" && canAccessKardexPdf(user) && !isJefaturaAcademicaRole(user)) return "/reportes/kardex";
  const desempeno = reportesDesempeno.find((config) => config.tipoDocumento === item.codigo && canAccessReporteDesempeno(user, config));
  if (desempeno) return desempeno.ruta;
  const trayectoria = reportesTrayectoria.find((config) => config.tipoDocumento === item.codigo && canAccessReporteTrayectoria(user, config));
  if (trayectoria) return trayectoria.ruta;
  if (!canAccessReportesOperativos(user)) return undefined;
  return reportesOperativos.find((config) => config.tipoDocumento === item.codigo && canAccessReporteOperativo(user, config))?.ruta;
}

function actionLabelForCatalogItem(item: ReporteCatalogoItem) {
  if (item.codigo === "KARDEX_OFICIAL") return "Exportar kárdex PDF";
  if (reportesDesempeno.some((config) => config.tipoDocumento === item.codigo)) return "Ver reporte de desempeño";
  if (reportesTrayectoria.some((config) => config.tipoDocumento === item.codigo)) return "Ver reporte de trayectoria";
  if (reportesOperativos.some((config) => config.tipoDocumento === item.codigo)) return "Ver reporte operativo";
  return "Abrir módulo";
}

type QuickLinkItem = { title: string; description: string; href?: string } | null;

function QuickSection({ title, intent, links }: { title: string; intent: string; links: QuickLinkItem[] }) {
  const visibleLinks = links.filter(Boolean) as Array<NonNullable<QuickLinkItem>>;
  if (visibleLinks.length === 0) return null;
  return (
    <section>
      <div className="mb-3">
        <h3 className="text-lg font-black text-[#101b18]">{title}</h3>
        <p className="mt-1 text-sm text-[#5f6764]">{intent}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {visibleLinks.map((item) => (
          <QuickLink key={item.title} {...item} />
        ))}
      </div>
    </section>
  );
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
  return (
    <Link href={href} className={className}>
      {content}
    </Link>
  );
}
