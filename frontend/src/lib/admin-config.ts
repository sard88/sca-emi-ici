import type { AdminCatalogResourceConfig, AuthenticatedUser } from "./types";

const adminRoles = ["ADMIN", "ADMIN_SISTEMA"];
const institutionalRoles = [
  "ADMIN",
  "ADMIN_SISTEMA",
  "ENCARGADO_ESTADISTICA",
  "ESTADISTICA",
  "JEFE_ACADEMICO",
  "JEFATURA_ACADEMICA",
  "JEFE_PEDAGOGICA",
  "JEFE_SUB_PLAN_EVAL",
  "JEFE_CARRERA",
  "JEFATURA_CARRERA",
  "JEFE_SUB_EJEC_CTR",
];

export const adminResources: AdminCatalogResourceConfig[] = [
  {
    slug: "usuarios",
    titulo: "Usuarios",
    descripcion: "Administración base de usuarios, roles, grado/empleo y estado de cuenta.",
    ruta: "/administracion/usuarios",
    endpoint: "/api/admin/usuarios/",
    categoria: "administracion",
    tableColumns: [
      { key: "username", label: "Usuario" },
      { key: "nombre_visible", label: "Nombre" },
      { key: "rol", label: "Rol" },
      { key: "estado_cuenta_label", label: "Estado", type: "status" },
      { key: "is_active", label: "Activo", type: "boolean" },
    ],
    formFields: [
      { key: "username", label: "Usuario", required: true },
      { key: "nombre_completo", label: "Nombre completo", required: true },
      { key: "correo", label: "Correo", type: "text" },
      { key: "telefono", label: "Teléfono" },
      { key: "titulo_profesional", label: "Título profesional" },
      { key: "cedula_profesional", label: "Cédula profesional" },
      { key: "grado_empleo_id", label: "Grado/empleo", type: "relation", relationEndpoint: "/api/admin/grados-empleos/" },
      { key: "rol", label: "Rol", type: "relation", relationEndpoint: "/api/admin/roles/", relationLabelKey: "name", relationValueKey: "name", required: true },
      {
        key: "estado_cuenta",
        label: "Estado de cuenta",
        type: "select",
        options: [
          { value: "activo", label: "Activo" },
          { value: "inactivo", label: "Inactivo" },
          { value: "bloqueado", label: "Bloqueado" },
        ],
      },
      { key: "password", label: "Contraseña temporal", type: "password", help: "Solo se usa al crear usuario; no se muestra después." },
    ],
    filters: [{ key: "q", label: "Buscar", placeholder: "Usuario, nombre o correo" }],
    ayuda: "No se exponen hashes ni contraseñas. La edición de contraseña queda fuera salvo password temporal al crear.",
    permiteCrear: true,
    permiteEditar: true,
    permiteInactivar: true,
  },
  {
    slug: "grados-empleos",
    titulo: "Grado y empleo",
    descripcion: "Catálogo institucional de grados, empleos y tratamientos visibles.",
    ruta: "/administracion/grados-empleos",
    endpoint: "/api/admin/grados-empleos/",
    categoria: "administracion",
    tableColumns: [
      { key: "clave", label: "Clave" },
      { key: "abreviatura", label: "Abreviatura" },
      { key: "nombre", label: "Nombre" },
      { key: "tipo_label", label: "Tipo" },
      { key: "activo", label: "Activo", type: "boolean" },
    ],
    formFields: [
      { key: "clave", label: "Clave", required: true },
      { key: "abreviatura", label: "Abreviatura", required: true },
      { key: "nombre", label: "Nombre", required: true },
      {
        key: "tipo",
        label: "Tipo",
        type: "select",
        options: [
          { value: "MILITAR_ACTIVO", label: "Militar activo" },
          { value: "MILITAR_RETIRADO", label: "Militar retirado" },
          { value: "CIVIL", label: "Civil" },
          { value: "OTRO", label: "Otro" },
        ],
      },
      { key: "activo", label: "Activo", type: "boolean" },
    ],
    filters: [{ key: "q", label: "Buscar", placeholder: "Clave, abreviatura o nombre" }],
    permiteCrear: true,
    permiteEditar: true,
    permiteInactivar: true,
  },
  {
    slug: "unidades",
    titulo: "Unidades organizacionales",
    descripcion: "Secciones, subsecciones y estructura institucional por carrera cuando aplique.",
    ruta: "/administracion/unidades",
    endpoint: "/api/admin/unidades-organizacionales/",
    categoria: "administracion",
    tableColumns: [
      { key: "clave", label: "Clave" },
      { key: "nombre", label: "Nombre" },
      { key: "tipo_unidad_label", label: "Tipo" },
      { key: "padre", label: "Padre", type: "relation" },
      { key: "activo", label: "Activo", type: "boolean" },
    ],
    formFields: [
      { key: "clave", label: "Clave", required: true },
      { key: "nombre", label: "Nombre", required: true },
      {
        key: "tipo_unidad",
        label: "Tipo",
        type: "select",
        options: [
          { value: "SECCION", label: "Sección" },
          { value: "SUBSECCION", label: "Subsección" },
        ],
      },
      { key: "padre_id", label: "Unidad padre", type: "relation", relationEndpoint: "/api/admin/unidades-organizacionales/" },
      { key: "carrera_id", label: "Carrera", type: "relation", relationEndpoint: "/api/catalogos/carreras/" },
      { key: "orden", label: "Orden", type: "number" },
      { key: "activo", label: "Activo", type: "boolean" },
    ],
    filters: [{ key: "q", label: "Buscar", placeholder: "Clave, nombre o carrera" }],
    permiteCrear: true,
    permiteEditar: true,
    permiteInactivar: true,
  },
  {
    slug: "cargos",
    titulo: "Asignaciones de cargo",
    descripcion: "Designaciones institucionales vigentes y accidentales con validación backend.",
    ruta: "/administracion/cargos",
    endpoint: "/api/admin/asignaciones-cargo/",
    categoria: "administracion",
    tableColumns: [
      { key: "usuario", label: "Usuario", type: "relation" },
      { key: "cargo_label", label: "Cargo" },
      { key: "tipo_designacion_label", label: "Designación" },
      { key: "unidad_organizacional", label: "Unidad", type: "relation" },
      { key: "activo", label: "Activo", type: "boolean" },
    ],
    formFields: [
      { key: "usuario_id", label: "Usuario", type: "relation", relationEndpoint: "/api/admin/usuarios/", required: true },
      {
        key: "cargo_codigo",
        label: "Cargo",
        type: "select",
        options: [
          { value: "JEFE_ACADEMICO", label: "Jefe académico" },
          { value: "JEFE_PEDAGOGICA", label: "Jefe de Pedagógica" },
          { value: "JEFE_SUB_PLAN_EVAL", label: "Jefe de subsección de Planeación y Evaluación" },
          { value: "JEFE_SUB_EJEC_CTR", label: "Jefe de subsección de Ejecución y Control" },
          { value: "DOCENTE", label: "Docente" },
        ],
      },
      {
        key: "tipo_designacion",
        label: "Tipo de designación",
        type: "select",
        options: [
          { value: "titular", label: "Titular" },
          { value: "accidental", label: "Accidental" },
        ],
      },
      { key: "unidad_organizacional_id", label: "Unidad organizacional", type: "relation", relationEndpoint: "/api/admin/unidades-organizacionales/" },
      { key: "carrera_id", label: "Carrera", type: "relation", relationEndpoint: "/api/catalogos/carreras/" },
      { key: "vigente_desde", label: "Vigente desde", type: "date" },
      { key: "vigente_hasta", label: "Vigente hasta", type: "date" },
      { key: "activo", label: "Activo", type: "boolean" },
    ],
    filters: [{ key: "q", label: "Buscar", placeholder: "Usuario, cargo o unidad" }],
    ayuda: "El backend valida rol compatible, cargo/unidad, titular único y traslapes.",
    permiteCrear: true,
    permiteEditar: true,
    permiteInactivar: true,
  },
  {
    slug: "roles",
    titulo: "Roles",
    descripcion: "Consulta de grupos Django disponibles para asignación controlada.",
    ruta: "/administracion/roles",
    endpoint: "/api/admin/roles/",
    categoria: "administracion",
    tableColumns: [{ key: "name", label: "Rol" }],
    formFields: [],
    filters: [{ key: "q", label: "Buscar", placeholder: "Nombre del rol" }],
    ayuda: "Solo lectura en este bloque. La edición de grupos Django permanece en Django Admin.",
    permiteCrear: false,
    permiteEditar: false,
    permiteInactivar: false,
    soloLectura: true,
  },
];

export function getAdminResource(slug: string) {
  return adminResources.find((item) => item.slug === slug);
}

export function canAccessAdministracion(user: AuthenticatedUser) {
  const values = roleValues(user);
  return values.some((role) => adminRoles.includes(role));
}

export function canReadAdministracion(user: AuthenticatedUser) {
  const values = roleValues(user);
  return values.some((role) => institutionalRoles.includes(role));
}

export function canWriteAdministracion(user: AuthenticatedUser) {
  return canAccessAdministracion(user);
}

function roleValues(user: AuthenticatedUser) {
  return [user.perfil_principal ?? "", ...user.roles, ...user.cargos_vigentes.map((cargo) => cargo.cargo_codigo)];
}
