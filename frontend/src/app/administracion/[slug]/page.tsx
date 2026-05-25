"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { CatalogResourcePage } from "@/components/admin-catalogos/CatalogResourcePage";
import { canReadAdministracion, canWriteAdministracion, getAdminResource } from "@/lib/admin-config";

export default function AdministracionResourcePage() {
  const params = useParams<{ slug: string }>();
  const config = getAdminResource(params.slug);

  if (!config) {
    return (
      <AppShell>
        <ErrorMessage message="Recurso de administración no reconocido." />
      </AppShell>
    );
  }

  return <CatalogResourcePage config={config} backHref="/administracion" canRead={canReadAdministracion} canWrite={canWriteAdministracion} />;
}
