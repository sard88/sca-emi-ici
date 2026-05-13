# Resumen Bloque 9A - Núcleo común de exportaciones y auditoría

## Objetivo

El Bloque 9A implementa la base común para exportaciones y auditoría de salidas documentales del Sistema de Control Académico EMI - ICI. El bloque no genera todavía PDFs ni Excels finales; únicamente deja preparado el registro de metadatos, el catálogo inicial, los permisos base, las APIs y el admin técnico.

Django se mantiene como fuente de verdad de permisos y reglas. El frontend Next.js queda preparado para consumir APIs en una fase posterior, pero no se implementan pantallas React de reportes en este bloque.

## Alcance implementado

- Modelo `RegistroExportacion`.
- Catálogo inicial de documentos y reportes.
- Servicio común de exportación.
- Servicio de permisos por rol/cargo.
- Normalización segura de nombres de archivo.
- Limpieza de filtros/parámetros para evitar guardar datos sensibles.
- APIs para catálogo, historial propio, auditoría institucional y evento técnico de prueba.
- Admin Django en modo consulta/solo lectura.
- Pruebas automatizadas específicas y suite completa.
- Documentación en README.

## Archivos principales

- `backend/reportes/models.py`
- `backend/reportes/catalogo.py`
- `backend/reportes/services.py`
- `backend/reportes/api_views.py`
- `backend/reportes/api_urls.py`
- `backend/reportes/admin.py`
- `backend/reportes/tests.py`
- `backend/reportes/migrations/0001_initial.py`
- `backend/config/urls.py`

## Modelo RegistroExportacion

El modelo registra metadatos de cada exportación relevante:

- usuario solicitante;
- tipo de documento;
- formato;
- nombre lógico del documento;
- nombre técnico de archivo;
- objeto asociado opcional;
- filtros y parámetros sanitizados;
- rol/cargo de contexto;
- IP y user agent;
- estado de la exportación;
- mensaje de error;
- tamaño y hash futuros;
- fechas de creación y finalización.

Estados:

- `SOLICITADA`
- `GENERADA`
- `FALLIDA`
- `DESCARGADA`

Formatos:

- `PDF`
- `XLSX`
- `CSV`

Tipos de documento:

- `ACTA_EVALUACION_PARCIAL`
- `ACTA_EVALUACION_FINAL`
- `ACTA_CALIFICACION_FINAL`
- `KARDEX_OFICIAL`
- `HISTORIAL_ACADEMICO`
- `REPORTE_ACTAS_ESTADO`
- `REPORTE_ACTAS_PENDIENTES`
- `REPORTE_INCONFORMIDADES`
- `REPORTE_DESEMPENO`
- `REPORTE_SITUACION_ACADEMICA`
- `REPORTE_VALIDACIONES_ACTA`
- `REPORTE_EXPORTACIONES`
- `REPORTE_MOVIMIENTOS_ACADEMICOS`
- `AUDITORIA_EVENTOS`
- `OTRO`

## Catálogo de exportaciones

El catálogo vive en código (`backend/reportes/catalogo.py`) y define para cada documento/reporte:

- código;
- nombre;
- descripción;
- formatos soportados;
- si está implementado;
- si requiere objeto;
- roles sugeridos;
- bloque origen;
- nota de alcance.

En 9A solo queda operable la base de auditoría. Los generadores reales quedan para subbloques posteriores.

## Servicios

### CatalogoExportaciones

Devuelve el catálogo completo o filtrado por usuario autenticado.

### ServicioPermisosExportacion

Evalúa permisos base:

- Admin ve catálogo completo y auditoría.
- Estadística ve catálogo institucional y auditoría.
- Jefatura de carrera ve actas y reportes operativos previstos para su ámbito.
- Jefatura académica/pedagógica ve documentos institucionales autorizados.
- Docente ve actas propias como potencial exportación futura.
- Discente no ve kárdex oficial ni reportes globales.

### ServicioExportacion

Responsabilidades:

- validar usuario autenticado;
- validar tipo/formato;
- validar permiso;
- construir nombre de archivo;
- registrar solicitud;
- marcar como generada;
- marcar como fallida;
- capturar IP y user agent;
- sanitizar filtros/parámetros.

### Utilidades

`construir_nombre_archivo` genera nombres seguros:

- minúsculas;
- sin acentos;
- sin caracteres peligrosos;
- espacios convertidos a guiones;
- extensión acorde al formato.

`limpiar_json_seguro` evita guardar llaves sensibles como:

- password;
- token;
- secret;
- session;
- cookie;
- authorization;
- csrf;
- credenciales.

## Endpoints API

### Catálogo

`GET /api/reportes/catalogo/`

Devuelve elementos visibles para el usuario autenticado con:

- `codigo`
- `nombre`
- `descripcion`
- `formatos_soportados`
- `implementado`
- `disponible`
- `motivo_no_disponible`

### Historial propio o amplio

`GET /api/exportaciones/`

Reglas:

- usuario normal ve sus propias exportaciones;
- Admin/Estadística pueden ver más registros;
- admite filtros por fecha, usuario, tipo, formato y estado.

### Auditoría institucional

`GET /api/auditoria/exportaciones/`

Reglas:

- solo Admin, Estadística o autoridad académica autorizada;
- permite filtros básicos;
- devuelve registros recientes.

### Evento técnico de prueba

`POST /api/exportaciones/registrar-evento-prueba/`

Reglas:

- solo Admin/Estadística;
- registra un evento `OTRO`;
- marca el evento como `GENERADA` sin crear archivo físico;
- sirve para validar 9A sin generar documentos finales.

## Admin Django

`RegistroExportacion` queda visible en admin técnico con:

- `usuario`
- `tipo_documento`
- `formato`
- `nombre_archivo`
- `estado`
- `creado_en`
- `finalizado_en`
- `ip_origen`
- `rol_contexto`
- `cargo_contexto`

Protecciones:

- no permite alta manual;
- no permite edición ordinaria;
- no permite eliminación ordinaria;
- no expone acción masiva de borrado;
- todos los campos son de solo lectura.

## Pruebas automatizadas

Se agregan pruebas para:

1. crear `RegistroExportacion` desde servicio;
2. marcar exportación como `GENERADA`;
3. marcar exportación como `FALLIDA`;
4. consultar exportaciones propias;
5. rechazar usuario anónimo;
6. ocultar kárdex oficial a discente;
7. impedir reportes globales para docente;
8. permitir catálogo institucional a Estadística;
9. permitir catálogo completo a Admin;
10. normalizar nombres de archivo;
11. sanitizar filtros sensibles;
12. proteger admin contra edición/borrado;
13. restringir endpoint técnico a Admin/Estadística;
14. rechazar exportación no autorizada para docente.

## Validaciones ejecutadas

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations reportes
docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test reportes
docker compose exec -T backend python manage.py test
```

Resultados:

- `check`: OK.
- `makemigrations reportes`: creó `reportes.0001_initial`.
- `migrate`: OK.
- `makemigrations --check`: OK.
- `test reportes`: 14 pruebas OK.
- `test`: 314 pruebas OK.

## Fuera de alcance

No se implementó:

- PDF real de actas;
- Excel real de actas;
- kárdex PDF;
- historial exportable;
- reportes de desempeño reales;
- reportes de situación académica reales;
- cuadros de aprovechamiento;
- plantillas Excel de captura;
- importación desde Excel;
- reporte de errores de importación;
- gráficas;
- almacenamiento físico permanente de archivos;
- envío por correo;
- firma electrónica;
- QR o sello digital;
- pantallas React de reportes;
- cambios en actas formalizadas;
- cambios en kárdex;
- cambios en resultados oficiales.

## Pendientes para 9B

- Conectar generadores PDF/Excel reales de actas.
- Definir plantillas oficiales.
- Registrar tamaño y hash real del archivo generado.
- Registrar fallos reales de renderizado/documento.
- Validar permisos por objeto concreto de acta.

## Pendientes para 9C

- Conectar kárdex PDF oficial.
- Mantener regla de no exposición del kárdex oficial a discentes.
- Definir formato institucional del documento.

## Pendientes para 9F/9G/9I

- Implementar agregados reales de reportes operativos.
- Implementar reportes de desempeño.
- Implementar reportes de situación académica.
- Conectar auditoría transversal si se crea bitácora de eventos críticos.

## Pendientes para 10C

- Mostrar catálogo de reportes en portal Next.js.
- Mostrar historial de exportaciones del usuario.
- Mostrar auditoría institucional para Admin/Estadística.
- Integrar estados de disponibilidad y motivos de pendiente.
- Agregar acciones visuales cuando 9B/9C habiliten generación real.

## Cierre

El Bloque 9A queda listo como base común de auditoría documental. No genera documentos finales, pero ya permite registrar, consultar y auditar exportaciones de forma controlada y segura.
