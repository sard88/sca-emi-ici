export type GradoEmpleo = {
  clave: string;
  abreviatura: string;
  nombre: string;
  tipo: string;
} | null;

export type Carrera = {
  clave: string;
  nombre: string;
};

export type CargoVigente = {
  cargo_codigo: string;
  cargo: string;
  tipo_designacion: string;
  vigente_desde: string | null;
  vigente_hasta: string | null;
  unidad_organizacional: { clave: string; nombre: string } | null;
  carrera: Carrera | null;
};

export type BackendLink = {
  label: string;
  href: string;
  backend?: boolean;
  perfil?: string;
};

export type AuthenticatedUser = {
  authenticated: true;
  id: number;
  username: string;
  nombre_completo: string;
  nombre_visible: string;
  nombre_institucional: string;
  email: string;
  correo: string;
  grado_empleo: GradoEmpleo;
  roles: string[];
  cargos_vigentes: CargoVigente[];
  perfil_principal: string | null;
  carreras: Carrera[];
  enlaces: BackendLink[];
};

export type AnonymousUser = { authenticated: false };
export type AuthMe = AuthenticatedUser | AnonymousUser;
