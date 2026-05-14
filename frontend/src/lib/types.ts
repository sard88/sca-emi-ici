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

export type DashboardResumenCard = {
  title: string;
  value: number;
  description: string;
  href?: string | null;
  backend?: boolean;
  tone?: "neutral" | "guinda" | "dorado" | "verde";
};

export type PortalQuickAccess = {
  id: number | null;
  label: string;
  url: string;
  description?: string;
  backend?: boolean;
  icono?: string;
};

export type DashboardResumen = {
  perfil: string | null;
  generado_en: string;
  cards: DashboardResumenCard[];
  alertas: Array<{ titulo: string; mensaje: string; prioridad: string }>;
  quick_accesses: PortalQuickAccess[];
};

export type ActividadRecienteItem = {
  id: string;
  tipo: string;
  titulo: string;
  descripcion: string;
  fecha: string | null;
  url?: string;
  backend?: boolean;
};

export type Notificacion = {
  id: number;
  tipo: string;
  tipo_label: string;
  titulo: string;
  mensaje: string;
  url_destino: string;
  prioridad: string;
  prioridad_label: string;
  leida: boolean;
  creada_en: string | null;
  leida_en: string | null;
};

export type NotificacionesResponse = {
  unread_count: number;
  items: Notificacion[];
};

export type EventoCalendario = {
  id: number;
  titulo: string;
  descripcion: string;
  tipo_evento: string;
  tipo_evento_label: string;
  fecha_inicio: string;
  fecha_fin: string | null;
  periodo: string | null;
  carrera: string | null;
  grupo: string | null;
  roles_destino: string[];
  url_destino: string;
};

export type CalendarioMes = {
  year: number;
  month: number;
  dias_con_eventos: string[];
  eventos: EventoCalendario[];
};

export type BusquedaResultado = {
  type: string;
  title: string;
  subtitle: string;
  url: string;
  backend: boolean;
};

export type BusquedaGrupo = {
  label: string;
  items: BusquedaResultado[];
};

export type BusquedaResponse = {
  query: string;
  min_chars: number;
  groups: BusquedaGrupo[];
};

export type PerfilUsuario = AuthenticatedUser & {
  estado_cuenta: string;
  estado_cuenta_label: string;
  ultimo_acceso: string | null;
  last_login: string | null;
  date_joined: string | null;
};

export type ReporteCatalogoItem = {
  codigo: string;
  nombre: string;
  descripcion: string;
  formatos_soportados: string[];
  implementado: boolean;
  disponible: boolean;
  requiere_objeto: boolean;
  roles_sugeridos: string[];
  bloque_origen: string;
  nota: string;
  motivo_no_disponible?: string;
};

export type ExportacionRegistro = {
  id: number;
  usuario: {
    id: number;
    username: string;
    nombre: string;
  };
  tipo_documento: string;
  tipo_documento_label: string;
  formato: string;
  nombre_documento: string;
  nombre_archivo: string;
  objeto_tipo: string;
  objeto_id: string;
  objeto_repr: string;
  rol_contexto: string;
  cargo_contexto: string;
  ip_origen: string | null;
  estado: string;
  estado_label: string;
  mensaje_error: string;
  tamano_bytes: number | null;
  hash_archivo: string;
  creado_en: string | null;
  finalizado_en: string | null;
};

export type ActaExportable = {
  acta_id: number;
  asignacion_docente_id: number;
  tipo_acta: string;
  corte_codigo: string;
  corte_nombre: string;
  estado_acta: string;
  estado_acta_label: string;
  estado_documental: string;
  periodo: string;
  carrera: string;
  carrera_clave: string;
  grupo: string;
  programa_asignatura: string;
  docente: string;
  fecha_publicacion: string | null;
  fecha_remision: string | null;
  fecha_formalizacion: string | null;
  puede_exportar_pdf: boolean;
  puede_exportar_xlsx: boolean;
  url_pdf: string;
  url_xlsx: string;
  es_documento_oficial: boolean;
  motivo_no_disponible: string;
  calificacion_final_disponible: boolean;
  url_calificacion_final_pdf: string;
  url_calificacion_final_xlsx: string;
};

export type KardexExportable = {
  discente_id: number;
  nombre_completo: string;
  grado_empleo: string;
  carrera: Carrera;
  plan_estudios: string;
  antiguedad: string;
  grupo_actual: string;
  periodo_actual: string;
  situacion_actual: string;
  puede_exportar_pdf: boolean;
  url_kardex_pdf: string;
  motivo_no_disponible: string;
};

export type DownloadResult = {
  filename: string;
  registroExportacionId: string | null;
  contentType: string;
  size: number;
};

export type ReporteOperativoCodigo =
  | "actas-estado"
  | "actas-pendientes"
  | "inconformidades"
  | "sin-conformidad"
  | "actas-formalizadas"
  | "validaciones-acta"
  | "exportaciones-realizadas";

export type ReporteOperativoColumna = {
  key: string;
  label: string;
};

export type ReporteOperativoItem = Record<string, unknown>;

export type ReporteOperativoSheet = {
  titulo: string;
  total: number;
  columnas: ReporteOperativoColumna[];
};

export type ReporteOperativoRespuesta = {
  ok: boolean;
  slug: ReporteOperativoCodigo;
  nombre: string;
  total: number;
  filtros: Record<string, string>;
  columnas: ReporteOperativoColumna[];
  items: ReporteOperativoItem[];
  sheets?: ReporteOperativoSheet[];
};

export type ReporteOperativoFiltro = {
  key: string;
  label: string;
  type?: "text" | "select" | "date";
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
};

export type ReporteOperativoConfig = {
  slug: ReporteOperativoCodigo;
  titulo: string;
  descripcion: string;
  ruta: string;
  tipoDocumento: string;
  endpointVistaPrevia: string;
  endpointDescarga: string;
  filtros: ReporteOperativoFiltro[];
  columnasDestacadas: string[];
  rolesSugeridos: string[];
  ayuda: string;
};

export type ReporteDesempenoCodigo =
  | "aprobados-reprobados"
  | "promedios"
  | "distribucion"
  | "exentos"
  | "docentes"
  | "cohorte"
  | "reprobados-nominal"
  | "cuadro-aprovechamiento";

export type ReporteDesempenoColumna = {
  key: string;
  label: string;
};

export type ReporteDesempenoItem = Record<string, unknown>;

export type ReporteDesempenoSheet = {
  titulo: string;
  total: number;
  columnas: ReporteDesempenoColumna[];
};

export type ReporteDesempenoRespuesta = {
  ok: boolean;
  slug: ReporteDesempenoCodigo;
  nombre: string;
  total: number;
  filtros: Record<string, string>;
  columnas: ReporteDesempenoColumna[];
  items: ReporteDesempenoItem[];
  resumen?: Record<string, unknown>;
  sheets?: ReporteDesempenoSheet[];
};

export type ReporteDesempenoFiltro = {
  key: string;
  label: string;
  type?: "text" | "select" | "date";
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
};

export type ReporteDesempenoConfig = {
  slug: ReporteDesempenoCodigo;
  titulo: string;
  descripcion: string;
  ruta: string;
  tipoDocumento: string;
  endpointVistaPrevia: string;
  endpointDescarga: string;
  formatosDisponibles: string[];
  pdfPendiente: boolean;
  filtros: ReporteDesempenoFiltro[];
  columnasDestacadas: string[];
  rolesSugeridos: string[];
  ayuda: string;
  nominal: boolean;
  datosSensibles: boolean;
  privacidad?: string;
};
