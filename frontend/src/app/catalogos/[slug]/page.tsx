"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { CatalogResourcePage } from "@/components/admin-catalogos/CatalogResourcePage";
import { canAccessCatalogos, canWriteCatalogos, getCatalogoResource } from "@/lib/catalogos-config";

export default function CatalogoResourcePage() {
  const params = useParams<{ slug: string }>();
  const config = getCatalogoResource(params.slug);

  if (!config) {
    return (
      <AppShell>
        <ErrorMessage message="Catálogo académico no reconocido." />
      </AppShell>
    );
  }

  return <CatalogResourcePage config={config} backHref="/catalogos" canRead={canAccessCatalogos} canWrite={canWriteCatalogos} />;
}
