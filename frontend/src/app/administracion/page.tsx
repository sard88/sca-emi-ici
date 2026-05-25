"use client";

import { AdminCatalogIndex } from "@/components/admin-catalogos/AdminCatalogIndex";
import { adminResources, canReadAdministracion, canWriteAdministracion } from "@/lib/admin-config";

export default function AdministracionPage() {
  return (
    <AdminCatalogIndex
      title="Administración institucional"
      description="Operación base de usuarios, grados, unidades, cargos y roles visibles desde el portal moderno. Django Admin se conserva como respaldo técnico."
      heroTitle="Administración base sin abandonar Django Admin"
      heroDescription="Estas interfaces consumen APIs Django con sesión y CSRF. El frontend no expone contraseñas ni decide reglas críticas; solo presenta formularios y errores validados por backend."
      resources={adminResources}
      canRead={canReadAdministracion}
      canWrite={canWriteAdministracion}
    />
  );
}
