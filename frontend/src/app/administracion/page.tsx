"use client";

import { AdminCatalogIndex } from "@/components/admin-catalogos/AdminCatalogIndex";
import { adminResources, canReadAdministracion, canWriteAdministracion } from "@/lib/admin-config";

export default function AdministracionPage() {
  return (
    <AdminCatalogIndex
      title="Administración institucional"
      description="Gestiona usuarios, grados, unidades, cargos y roles desde el portal institucional."
      heroTitle="Administración institucional"
      heroDescription="Consulta y administra información de acceso según tu perfil autorizado."
      resources={adminResources}
      canRead={canReadAdministracion}
      canWrite={canWriteAdministracion}
    />
  );
}
