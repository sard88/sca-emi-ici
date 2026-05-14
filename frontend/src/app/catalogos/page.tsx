"use client";

import { AdminCatalogIndex } from "@/components/admin-catalogos/AdminCatalogIndex";
import { canAccessCatalogos, canWriteCatalogos, catalogosResources } from "@/lib/catalogos-config";

export default function CatalogosPage() {
  return (
    <AdminCatalogIndex
      title="Catálogos académicos"
      description="Consulta y operación segura de carreras, planes, antigüedades, periodos, grupos, materias, programas, esquemas y catálogos de trayectoria."
      heroTitle="Estructura académica operable desde el portal"
      heroDescription="Los formularios son una capa visual sobre APIs Django. Las reglas reales de vigencia, compatibilidad y validación permanecen en modelos y servicios backend."
      resources={catalogosResources}
      canRead={canAccessCatalogos}
      canWrite={canWriteCatalogos}
    />
  );
}
