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

export type BitacoraEventoCritico = {
  id: number;
  creado_en: string | null;
  usuario: {
    id: number | null;
    username: string;
    nombre: string;
  };
  rol_contexto: string;
  cargo_contexto: string;
  modulo: string;
  modulo_label: string;
  evento_codigo: string;
  evento_nombre: string;
  severidad: string;
  severidad_label: string;
  resultado: string;
  resultado_label: string;
  objeto_tipo: string;
  objeto_id: string;
  objeto_repr: string;
  estado_anterior: string;
  estado_nuevo: string;
  resumen: string;
  ip_origen: string | null;
  ruta: string;
  metodo_http: string;
  request_id: string;
  correlacion_id: string;
};

export type BitacoraEventosResponse = {
  ok: boolean;
  total: number;
  page: number;
  page_size: number;
  items: BitacoraEventoCritico[];
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

export type ReporteTrayectoriaCodigo =
  | "extraordinarios"
  | "situacion-actual"
  | "bajas-temporales"
  | "bajas-definitivas"
  | "reingresos"
  | "egresables"
  | "situacion-agregado"
  | "movimientos-academicos"
  | "cambios-grupo"
  | "historial-interno"
  | "historial-interno-discente";

export type ReporteTrayectoriaColumna = {
  key: string;
  label: string;
};

export type ReporteTrayectoriaItem = Record<string, unknown>;

export type ReporteTrayectoriaSheet = {
  titulo: string;
  total: number;
  columnas: ReporteTrayectoriaColumna[];
};

export type ReporteTrayectoriaRespuesta = {
  ok: boolean;
  slug: ReporteTrayectoriaCodigo;
  nombre: string;
  total: number;
  filtros: Record<string, string>;
  columnas: ReporteTrayectoriaColumna[];
  items: ReporteTrayectoriaItem[];
  resumen?: Record<string, unknown>;
  sheets?: ReporteTrayectoriaSheet[];
};

export type ReporteTrayectoriaFiltro = {
  key: string;
  label: string;
  type?: "text" | "select" | "date";
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
};

export type ReporteTrayectoriaConfig = {
  slug: ReporteTrayectoriaCodigo;
  titulo: string;
  descripcion: string;
  ruta: string;
  tipoDocumento: string;
  endpointVistaPrevia: string;
  endpointDescarga: string;
  formatosDisponibles: string[];
  pdfPendiente: boolean;
  filtros: ReporteTrayectoriaFiltro[];
  columnasDestacadas: string[];
  rolesSugeridos: string[];
  ayuda: string;
  nominal: boolean;
  agregado: boolean;
  datosSensibles: boolean;
  privacidad?: string;
  requiereDiscenteId?: boolean;
};

export type ResourceListResponse = {
  ok: boolean;
  total: number;
  page: number;
  page_size: number;
  items: ResourceItem[];
};

export type ResourceDetailResponse = {
  ok: boolean;
  item: ResourceItem;
};

export type ResourceItem = Record<string, unknown> & {
  id: number;
  label?: string;
  activo?: boolean;
};

export type ResourceFieldType = "text" | "textarea" | "number" | "date" | "select" | "relation" | "boolean" | "password";

export type ResourceFieldOption = {
  value: string;
  label: string;
};

export type ResourceFormField = {
  key: string;
  label: string;
  type?: ResourceFieldType;
  required?: boolean;
  readOnly?: boolean;
  placeholder?: string;
  help?: string;
  options?: ResourceFieldOption[];
  relationEndpoint?: string;
  relationLabelKey?: string;
  relationValueKey?: string;
};

export type ResourceTableColumn = {
  key: string;
  label: string;
  type?: "text" | "boolean" | "status" | "date" | "relation";
};

export type AdminCatalogResourceConfig = {
  slug: string;
  titulo: string;
  descripcion: string;
  ruta: string;
  endpoint: string;
  categoria: "administracion" | "catalogos";
  tableColumns: ResourceTableColumn[];
  formFields: ResourceFormField[];
  filters?: ResourceFormField[];
  ayuda?: string;
  permiteCrear: boolean;
  permiteEditar: boolean;
  permiteInactivar: boolean;
  soloLectura?: boolean;
};

export type EstadoActa =
  | "BORRADOR_DOCENTE"
  | "PUBLICADO_DISCENTE"
  | "REMITIDO_JEFATURA_CARRERA"
  | "VALIDADO_JEFATURA_CARRERA"
  | "FORMALIZADO_JEFATURA_ACADEMICA"
  | "ARCHIVADO";

export type CorteAcademico = "P1" | "P2" | "P3" | "FINAL";

export type UsuarioMinimo = {
  id: number;
  username?: string;
  nombre: string;
  nombre_institucional?: string;
  grado_empleo?: string;
  label?: string;
};

export type CatalogoMinimo = {
  id: number;
  clave?: string;
  nombre?: string;
  label?: string;
  [key: string]: unknown;
};

export type DiscenteMinimo = {
  id: number;
  usuario_id?: number;
  nombre: string;
  nombre_institucional?: string;
  grado_empleo?: string;
  situacion_actual?: string;
  situacion_actual_label?: string;
};

export type DocenteAsignacion = {
  id: number;
  asignacion_id: number;
  docente: UsuarioMinimo;
  periodo: CatalogoMinimo;
  carrera: CatalogoMinimo;
  grupo: CatalogoMinimo;
  semestre: number;
  programa_asignatura: CatalogoMinimo;
  materia: CatalogoMinimo;
  num_discentes: number | null;
  activo: boolean;
  estado_operativo: string;
  urls?: Record<string, string>;
};

export type ActaComponente = {
  id: number;
  componente_id?: number;
  corte_codigo?: CorteAcademico | string;
  corte_label?: string;
  nombre: string;
  porcentaje?: number | null;
  es_examen?: boolean;
  orden?: number;
};

export type CapturaPreliminarValor = {
  componente_id: number;
  valor: number | string | null;
};

export type CapturaPreliminarFila = {
  inscripcion_id: number;
  discente: DiscenteMinimo;
  valores: CapturaPreliminarValor[];
};

export type CapturaPreliminarCorte = {
  ok: boolean;
  asignacion: DocenteAsignacion;
  esquema: Record<string, unknown>;
  corte: CorteAcademico | string;
  componentes: ActaComponente[];
  filas: CapturaPreliminarFila[];
  resultados_corte: Array<Record<string, unknown>>;
  captura_bloqueada: boolean;
  acta_bloqueante: ActaResumen | null;
  guardados?: number;
  limpiados?: number;
  errores_calculo?: string[];
};

export type CapturaPreliminarPayload = {
  valores: Array<{ inscripcion_id: number; componente_id: number; valor: string | number | null }>;
};

export type ResumenCalculoAcademico = {
  ok: boolean;
  asignacion: DocenteAsignacion;
  items: Array<Record<string, unknown> & { inscripcion_id: number; discente: DiscenteMinimo }>;
  total: number;
  errores_calculo?: string[];
};

export type ConformidadDiscenteDTO = {
  id: number;
  estado_conformidad: "ACUSE" | "CONFORME" | "INCONFORME" | string;
  estado_conformidad_label: string;
  comentario?: string;
  vigente: boolean;
  registrado_en: string | null;
  invalidado_en: string | null;
};

export type ValidacionActaDTO = {
  id: number;
  etapa_validacion: string;
  etapa_validacion_label: string;
  accion: string;
  accion_label: string;
  usuario: UsuarioMinimo | null;
  cargo?: string;
  cargo_codigo?: string;
  unidad_organizacional?: string;
  carrera?: string;
  fecha_hora: string | null;
  ip_origen?: string | null;
  comentario?: string;
};

export type AccionActaDisponible = {
  puede_regenerar?: boolean;
  puede_publicar?: boolean;
  puede_remitir?: boolean;
  puede_validar_carrera?: boolean;
  puede_formalizar?: boolean;
  solo_lectura?: boolean;
};

export type ActaResumen = {
  id: number;
  acta_id: number;
  asignacion_docente_id: number;
  periodo: CatalogoMinimo;
  carrera: CatalogoMinimo;
  grupo: CatalogoMinimo;
  semestre?: number;
  programa_asignatura: CatalogoMinimo;
  materia: CatalogoMinimo;
  docente: UsuarioMinimo;
  corte_codigo: CorteAcademico | string;
  corte_label: string;
  estado_acta: EstadoActa | string;
  estado_acta_label: string;
  es_final: boolean;
  solo_lectura: boolean;
  es_documento_oficial: boolean;
  publicada_en: string | null;
  remitida_en: string | null;
  formalizada_en: string | null;
  creado_en: string | null;
  actualizado_en: string | null;
  total_discentes?: number | null;
  url_pdf?: string;
  url_xlsx?: string;
  acciones?: AccionActaDisponible;
};

export type ActaFilaDetalle = {
  id: number;
  detalle_id: number;
  discente?: DiscenteMinimo;
  resultado_corte: number | null;
  promedio_parciales: number | null;
  resultado_final_preliminar: number | null;
  resultado_preliminar: string;
  exencion_aplica: boolean;
  completo: boolean;
  calificaciones: Array<Record<string, unknown> & { componente_id: number; nombre: string }>;
  conformidad_vigente: ConformidadDiscenteDTO | null;
};

export type ActaDetalle = {
  ok: boolean;
  acta: ActaResumen;
  componentes: ActaComponente[];
  filas: ActaFilaDetalle[];
  validaciones: ValidacionActaDTO[];
  acciones: AccionActaDisponible;
  exportaciones?: { pdf?: string; xlsx?: string };
  avisos?: Record<string, unknown>;
};

export type DocenteAsignacionDetalle = {
  ok: boolean;
  item: DocenteAsignacion;
  esquema: Record<string, unknown> | null;
  componentes: ActaComponente[];
  cortes: string[];
  discentes: Array<{ inscripcion_id: number; discente: DiscenteMinimo }>;
  actas: ActaResumen[];
};

export type ActasListResponse = {
  ok: boolean;
  total: number;
  items: ActaResumen[];
};

export type AsignacionesListResponse = {
  ok: boolean;
  total: number;
  items: DocenteAsignacion[];
};

export type DiscenteActasResponse = {
  ok: boolean;
  total: number;
  items: Array<Record<string, unknown> & { acta_id: number; detalle_id: number }>;
};

export type DiscenteActaDetalle = {
  ok: boolean;
  acta: ActaResumen;
  detalle: ActaFilaDetalle;
  puede_registrar_conformidad: boolean;
  historial_conformidad: ConformidadDiscenteDTO[];
};

export type HistorialResultadoDTO = Record<string, unknown> & {
  inscripcion_id?: number;
  tipo_resultado?: string;
  calificacion?: number | null;
  codigo_resultado?: string;
  codigo_marca?: string;
};

export type HistorialEventoDTO = Record<string, unknown> & {
  id: number;
  situacion?: CatalogoMinimo;
  fecha_inicio?: string | null;
  fecha_fin?: string | null;
  motivo?: string;
};

export type HistorialMovimientoDTO = Record<string, unknown> & {
  id: number;
  tipo_movimiento?: string;
  tipo_movimiento_label?: string;
  fecha_movimiento?: string | null;
};

export type ExtraordinarioDTO = Record<string, unknown> & {
  id: number;
  discente?: DiscenteMinimo | Record<string, unknown>;
  fecha_aplicacion?: string | null;
  calificacion?: number | null;
  aprobado?: boolean;
  codigo_marca?: string;
};

export type ExtraordinarioPayload = {
  inscripcion_materia_id: string | number;
  fecha_aplicacion?: string;
  calificacion: string | number;
  observaciones?: string;
};

export type SituacionAcademicaDTO = Record<string, unknown> & {
  id: number;
  discente?: DiscenteMinimo | Record<string, unknown>;
  situacion?: CatalogoMinimo | Record<string, unknown>;
  periodo?: CatalogoMinimo | null;
  fecha_inicio?: string | null;
  fecha_fin?: string | null;
  motivo?: string;
};

export type SituacionAcademicaPayload = {
  discente_id: string | number;
  situacion_codigo?: string;
  situacion_id?: string | number;
  periodo_id?: string | number;
  fecha_inicio?: string;
  fecha_fin?: string;
  motivo?: string;
  observaciones?: string;
};

export type MovimientoAcademicoDTO = Record<string, unknown> & {
  id: number;
  discente?: DiscenteMinimo | Record<string, unknown>;
  periodo?: CatalogoMinimo | null;
  tipo_movimiento?: string;
  tipo_movimiento_label?: string;
  grupo_origen?: CatalogoMinimo | null;
  grupo_destino?: CatalogoMinimo | null;
  fecha_movimiento?: string | null;
  observaciones?: string;
  impacto?: Record<string, unknown>;
};

export type MovimientoAcademicoPayload = {
  discente_id: string | number;
  periodo_id: string | number;
  tipo_movimiento: string;
  grupo_origen_id?: string | number;
  grupo_destino_id?: string | number;
  fecha_movimiento?: string;
  observaciones?: string;
};

export type CambioGrupoPayload = Omit<MovimientoAcademicoPayload, "tipo_movimiento">;

export type HistorialAcademicoDTO = {
  ok: boolean;
  discente: DiscenteMinimo | Record<string, unknown>;
  resultados: HistorialResultadoDTO[];
  extraordinarios: ExtraordinarioDTO[];
  eventos: HistorialEventoDTO[];
  movimientos: HistorialMovimientoDTO[];
  vista_propia?: boolean;
  es_kardex_oficial?: boolean;
  aviso_privacidad?: string;
};

export type HistorialSearchResponse = {
  ok: boolean;
  total: number;
  page: number;
  page_size: number;
  items: Array<DiscenteMinimo & { url_detalle?: string } & Record<string, unknown>>;
};

export type TrayectoriaListResponse<T> = {
  ok: boolean;
  total: number;
  page?: number;
  page_size?: number;
  items: T[];
};

export type AccionPeriodoDisponible = {
  puede_diagnosticar?: boolean;
  puede_cerrar?: boolean;
  puede_usarse_como_origen_apertura?: boolean;
  puede_usarse_como_destino_apertura?: boolean;
};

export type PeriodoOperativoDTO = CatalogoMinimo & {
  anio_escolar?: string;
  periodo_academico?: number;
  fecha_inicio?: string | null;
  fecha_fin?: string | null;
  estado?: string;
  estado_label?: string;
  acciones?: AccionPeriodoDisponible;
};

export type BloqueanteCierreDTO = string | Record<string, unknown>;

export type DiagnosticoCierrePeriodoDTO = {
  ok: boolean;
  periodo: PeriodoOperativoDTO;
  puede_cerrar: boolean;
  bloqueantes: BloqueanteCierreDTO[];
  advertencias: BloqueanteCierreDTO[];
  resumen: Record<string, number>;
  resumen_por_grupo?: Record<string, unknown>;
  discentes_promovibles?: Array<Record<string, unknown>>;
  discentes_pendientes_extraordinario?: Array<Record<string, unknown>>;
  discentes_baja_temporal?: Array<Record<string, unknown>>;
  discentes_baja_definitiva?: Array<Record<string, unknown>>;
  discentes_egresables?: Array<Record<string, unknown>>;
};

export type DetalleCierreDiscenteDTO = Record<string, unknown> & {
  id: number;
  clasificacion?: string;
  clasificacion_label?: string;
  promovible?: boolean;
  requiere_extraordinario?: boolean;
};

export type ProcesoCierrePeriodoDTO = Record<string, unknown> & {
  id: number;
  periodo?: PeriodoOperativoDTO;
  estado?: string;
  estado_label?: string;
  ejecutado_en?: string | null;
  resumen?: Record<string, unknown>;
  detalles?: DetalleCierreDiscenteDTO[];
};

export type ProcesoAperturaPeriodoDTO = Record<string, unknown> & {
  id: number;
  periodo_origen?: PeriodoOperativoDTO;
  periodo_destino?: PeriodoOperativoDTO;
  estado?: string;
  estado_label?: string;
  ejecutado_en?: string | null;
  resumen?: Record<string, unknown>;
};

export type PendienteAsignacionDocenteDTO = Record<string, unknown> & {
  grupo?: CatalogoMinimo;
  periodo?: PeriodoOperativoDTO;
  carrera?: CatalogoMinimo;
  plan?: CatalogoMinimo;
  programa_asignatura?: CatalogoMinimo;
  materia?: CatalogoMinimo;
  estado?: string;
  accion_sugerida?: string;
};
