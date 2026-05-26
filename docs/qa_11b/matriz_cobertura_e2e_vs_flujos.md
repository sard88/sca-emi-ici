# Matriz de cobertura E2E vs flujos críticos (11B-0)

Leyenda de cobertura:

- **A**: Cubierto por E2E 11A.
- **B**: Cubierto parcialmente por E2E 11A.
- **C**: Cubierto por pruebas backend.
- **D**: Cubierto por documentación/QA manual.
- **E**: No cubierto con evidencia suficiente.
- **F**: Fuera de alcance MVP.

Severidad de brecha:

- Alta: afecta flujo nuclear o afirmaciones de tesis.
- Media: importante, pero mitigable con backend tests/manual.
- Baja: complementario/usabilidad.

| ID | Flujo | Módulo | Perfil | Cobertura actual | Evidencia | Brecha | Severidad | Recomendación |
|---:|---|---|---|---|---|---|---|---|
| 1 | Login exitoso por perfil | Auth | Todos | A | Spec 00-auth | Sin transacción de negocio | Media | Mantener |
| 2 | Login fallido | Auth | Anónimo | D | Docs 10E/11A | No spec explícito | Media | Incluir en 11B reducido |
| 3 | Logout | Auth | Todos | A | Spec 00-auth | Básico | Baja | Mantener |
| 4 | Anónimo bloqueado rutas | Auth | Anónimo | A | Spec 00 y 11 | Cobertura suficiente | Baja | Mantener |
| 5 | Discente bloqueado reportes globales | Auth | Discente | B | Spec 11 | Assert débil (navega) | Media | Fortalecer assert |
| 6 | Docente bloqueado auditoría global | Auth | Docente | B | Spec 03 | Sin verificación 403/alert robusta | Media | Mejorar en 11B |
| 7 | Jefatura bloqueada fuera de ámbito | Auth | Jefaturas | C | Tests backend permisos | No E2E de ámbito | Media | Manual + backend |
| 8 | Admin acceso soporte | Auth | Admin | B | Spec 01 | No opera mutación | Baja | Manual |
| 9 | Crear usuario | Administración | Admin | C | Tests usuarios | Sin E2E | Media | Manual/11B completo |
| 10 | Editar usuario | Administración | Admin | C | Tests usuarios | Sin E2E | Media | Manual/11B completo |
| 11 | Inactivar usuario | Administración | Admin | C | Tests usuarios | Sin E2E | Media | Manual |
| 12 | Crear grado/empleo | Catálogos | Admin | C | Tests catalogos | Sin E2E | Baja | Manual |
| 13 | Crear unidad organizacional | Catálogos | Admin | C | Tests usuarios/catalogos | Sin E2E | Baja | Manual |
| 14 | Crear asignación de cargo | Administración | Admin | C | Tests usuarios | Sin E2E | Media | Manual |
| 15 | Rechazar cargo institucional a discente | Administración | Admin | C | Tests seed/permisos | Sin E2E | Alta | Incluir en 11B completo |
| 16 | Crear carrera | Catálogos | Admin | C | Tests catalogos | Sin E2E | Baja | Manual |
| 17 | Crear plan | Catálogos | Admin | C | Tests catalogos | Sin E2E | Baja | Manual |
| 18 | Crear antigüedad | Catálogos | Admin | C | Tests catalogos | Sin E2E | Baja | Manual |
| 19 | Crear periodo | Catálogos | Admin | C | Tests catalogos | Sin E2E | Media | Manual |
| 20 | Crear grupo | Catálogos | Admin | C | Tests catalogos/relaciones | Sin E2E | Media | Manual |
| 21 | Crear materia/asignatura | Catálogos | Admin | C | Tests catalogos | Sin E2E | Baja | Manual |
| 22 | Crear programa de asignatura | Catálogos | Admin | C | Tests catalogos | Sin E2E | Baja | Manual |
| 23 | Crear esquema de evaluación | Evaluación | Admin | C | Tests evaluacion | Sin E2E | Media | Manual |
| 24 | Crear componentes evaluación | Evaluación | Admin | C | Tests evaluacion | Sin E2E | Media | Manual |
| 25 | Validar suma componentes 100% | Evaluación | Sistema | C | Tests evaluacion | Sin E2E | Media | Mantener backend |
| 26 | Rechazar exención en 1 parcial | Evaluación | Sistema | C | Tests evaluacion | Sin E2E | Alta | Mantener backend |
| 27 | Crear docente | Relaciones | Admin | C | Tests relaciones | Sin E2E | Baja | Manual |
| 28 | Crear discente | Relaciones | Admin | C | Tests relaciones | Sin E2E | Baja | Manual |
| 29 | Adscribir discente a grupo | Relaciones | Admin | C | Tests relaciones | Sin E2E | Media | Manual |
| 30 | Asignar docente a grupo/asignatura | Relaciones | Jefatura carrera/Admin | C | Tests relaciones | Sin E2E | Alta | 11B completo opcional |
| 31 | Generar inscripciones/carga | Relaciones | Sistema | C | Tests relaciones | Sin E2E | Alta | Manual+backend |
| 32 | Discente ve carga propia | Relaciones | Discente | A | Spec 04 | Sin assert de datos propietarios fuertes | Media | Fortalecer |
| 33 | Docente ve asignaciones propias | Relaciones | Docente | A | Spec 03 | Sin comparar contra ajenas | Media | Fortalecer |
| 34 | Docente no ve asignación ajena | Relaciones | Docente | C | Tests evaluacion/permisos | No E2E | Alta | 11B reducido |
| 35 | Captura P1 | Calificaciones | Docente | C | Tests evaluacion | Sin E2E transaccional | Alta | 11B reducido |
| 36 | Captura P2/P3 | Calificaciones | Docente | C | Tests evaluacion | Sin E2E transaccional | Alta | 11B reducido |
| 37 | Vacío elimina captura | Calificaciones | Docente | C | Tests evaluacion/api | Sin E2E | Alta | 11B reducido |
| 38 | Rechazo valor <0 | Calificaciones | Docente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 39 | Rechazo valor >10 | Calificaciones | Docente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 40 | Resultado por corte | Calificaciones | Docente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 41 | Promedio parciales | Calificaciones | Docente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 42 | Exención cuando aplica | Calificaciones | Docente | C | Tests evaluacion/reportes | Sin E2E | Alta | 11B reducido |
| 43 | Generar borrador acta | Actas | Docente | C | Tests evaluacion/actas | Sin E2E | Alta | 11B reducido |
| 44 | Regenerar borrador | Actas | Docente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 45 | Publicar acta | Actas | Docente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 46 | Discente consulta acta propia | Actas | Discente | B | Spec 04 ruta lista | Sin detalle transaccional | Media | 11B reducido |
| 47 | Discente registra acuse | Actas | Discente | E | Sin evidencia 11A actual | No automatizado | Media | Manual/11B |
| 48 | Discente registra conforme | Actas | Discente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 49 | Inconforme sin comentario rechazado | Actas | Discente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 50 | Inconforme con comentario | Actas | Discente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 51 | Docente remite acta | Actas | Docente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 52 | Conformidad solo lectura tras remisión | Actas | Discente | C | Tests evaluacion | Sin E2E | Alta | 11B reducido |
| 53 | Jefatura carrera valida | Actas | Jefatura carrera | C | Tests evaluacion | Sin E2E transacción | Alta | 11B reducido |
| 54 | Jefatura académica formaliza | Actas | Jefatura académica | C | Tests evaluacion | Sin E2E transacción | Alta | 11B reducido |
| 55 | FINAL formalizada actualiza oficial | Actas | Sistema | C | Tests evaluacion/reportes | Sin E2E | Alta | Mantener backend + 11B reducido |
| 56 | Acta formalizada sin edición ordinaria | Actas | Todos | C | Tests evaluacion/permisos | Sin E2E | Alta | 11B reducido |
| 57 | Estadística solo lectura | Actas | Estadística | B | Spec 02/06/07 navegación | Sin assert de acciones bloqueadas | Media | Fortalecer |
| 58 | Exportar acta PDF | Reportes | Roles autorizados | C | Tests reportes | Sin E2E descarga | Alta | 11B reducido |
| 59 | Exportar acta XLSX | Reportes | Roles autorizados | C | Tests reportes | Sin E2E descarga | Alta | 11B reducido |
| 60 | Exportar acta final | Reportes | Roles autorizados | C | Tests reportes | Sin E2E descarga | Alta | 11B reducido |
| 61 | Exportar calificación final | Reportes | Roles autorizados | C | Tests reportes | Sin E2E descarga | Alta | 11B reducido |
| 62 | Exportar kárdex PDF | Reportes | Roles autorizados | C | Tests reportes | Sin E2E descarga | Media | Manual/11B |
| 63 | Bloquear kárdex a discente | Reportes | Discente | C | Tests permisos/reportes | Sin E2E | Media | Fortalecer |
| 64 | Exportar reporte operativo | Reportes | Estadística/Admin | C | Tests reportes | Sin E2E descarga | Media | Manual/11B |
| 65 | Exportar reporte desempeño | Reportes | Estadística/Admin | C | Tests reportes | Sin E2E descarga | Media | Manual/11B |
| 66 | Exportar reporte trayectoria | Reportes | Estadística/Admin | C | Tests reportes | Sin E2E descarga | Media | Manual/11B |
| 67 | Exportar auditoría XLSX | Auditoría | Admin/Estadística | C | Tests auditoria/reportes | Sin E2E descarga | Alta | 11B reducido |
| 68 | Registrar RegistroExportacion | Auditoría | Sistema | C | Tests reportes/auditoria | Sin E2E | Media | Mantener backend |
| 69 | Mostrar folio técnico | Auditoría/UI | Roles autorizados | B | Docs UX + specs navegación | No assert fuerte | Media | Fortalecer |
| 70 | No versionar descargas | QA | Repo | D | .gitignore + docs | No control automático CI | Baja | Agregar check CI |
| 71 | Registrar extraordinario | Trayectoria | Estadística | C | Tests trayectoria | Sin E2E transacción | Alta | 11B completo opcional |
| 72 | Rechazar extraordinario duplicado | Trayectoria | Sistema | C | Tests trayectoria | Sin E2E | Media | Mantener backend |
| 73 | Rechazar extraordinario sin reprobado | Trayectoria | Sistema | C | Tests trayectoria | Sin E2E | Media | Mantener backend |
| 74 | Registrar baja temporal | Trayectoria | Estadística | C | Tests trayectoria | Sin E2E | Media | Manual |
| 75 | Registrar reingreso | Trayectoria | Estadística | C | Tests trayectoria | Sin E2E | Media | Manual |
| 76 | Registrar baja definitiva | Trayectoria | Estadística | C | Tests trayectoria | Sin E2E | Media | Manual |
| 77 | Consultar historial institucional | Trayectoria | Estadística/Jefaturas | B | Spec 08 navegación | Sin asserts funcionales | Media | Fortalecer |
| 78 | Discente historial propio | Trayectoria | Discente | B | Spec 04 ruta | Sin asserts de propiedad | Media | Fortalecer |
| 79 | Docente no registra extraordinario | Trayectoria | Docente | C | Tests permisos trayectoria | Sin E2E | Media | Manual |
| 80 | Discente no registra situación | Trayectoria | Discente | C | Tests permisos trayectoria | Sin E2E | Media | Manual |
| 81 | Cambio de grupo válido | Movimientos | Estadística | C | Tests relaciones/trayectoria | Sin E2E | Alta | 11B completo opcional |
| 82 | Cerrar adscripción origen | Movimientos | Sistema | C | Tests relaciones | Sin E2E | Media | Mantener backend |
| 83 | Crear adscripción destino | Movimientos | Sistema | C | Tests relaciones | Sin E2E | Media | Mantener backend |
| 84 | Baja inscripciones origen | Movimientos | Sistema | C | Tests relaciones | Sin E2E | Media | Mantener backend |
| 85 | Crear inscripciones destino | Movimientos | Sistema | C | Tests relaciones | Sin E2E | Media | Mantener backend |
| 86 | Bloquear cambio con actas vivas | Movimientos | Sistema | C | Tests relaciones/actas | Sin E2E | Alta | Manual/11B completo |
| 87 | Bloquear origen=destino | Movimientos | Sistema | C | Tests relaciones | Sin E2E | Baja | Mantener backend |
| 88 | Bloquear destino incompatible | Movimientos | Sistema | C | Tests relaciones | Sin E2E | Media | Mantener backend |
| 89 | Docente/discente no crean movimientos | Movimientos | Docente/Discente | C | Tests permisos | Sin E2E | Media | Fortalecer |
| 90 | Diagnóstico cierre con bloqueantes | Periodos | Estadística | C | Tests actas/trayectoria | Sin E2E | Alta | 11B completo opcional |
| 91 | Cierre bloqueado no cambia estado | Periodos | Sistema | C | Tests actas | Sin E2E | Alta | Mantener backend |
| 92 | Diagnóstico sin bloqueantes | Periodos | Estadística | C | Tests actas | Sin E2E | Media | Manual |
| 93 | Cierre exitoso | Periodos | Estadística | C | Tests actas | Sin E2E | Alta | 11B completo opcional |
| 94 | Crear ProcesoCierrePeriodo | Periodos | Sistema | C | Tests actas | Sin E2E | Media | Mantener backend |
| 95 | Crear detalles por discente | Periodos | Sistema | C | Tests actas | Sin E2E | Media | Mantener backend |
| 96 | Apertura con origen cerrado | Periodos | Estadística | C | Tests actas | Sin E2E | Alta | 11B completo opcional |
| 97 | Promover promovibles | Periodos | Sistema | C | Tests actas | Sin E2E | Alta | Mantener backend |
| 98 | No promover egresables >12 | Periodos | Sistema | C | Tests actas | Sin E2E | Media | Mantener backend |
| 99 | No asignar docentes automáticamente | Periodos | Sistema | C | Tests actas/docs | Sin E2E | Media | Mantener backend |
| 100 | Mostrar pendientes asignación docente | Periodos | Estadística/Jefatura | B | Specs 05/09 | Sin assert de contenido | Media | Fortalecer |
| 101 | Bloquear apertura con origen no cerrado | Periodos | Sistema | C | Tests actas | Sin E2E | Media | Mantener backend |
| 102 | Docente/discente no operan periodos | Periodos | Docente/Discente | B | Specs negativos + navegación | Assert parcial | Baja | Fortalecer |
| 103 | Evento login exitoso | Auditoría | Sistema | C | Tests auditoria | Sin E2E | Baja | Mantener backend |
| 104 | Evento login fallido | Auditoría | Sistema | C | Tests auditoria | Sin E2E | Baja | Mantener backend |
| 105 | Evento captura | Auditoría | Sistema | C | Tests evaluacion/auditoria | Sin E2E | Media | Manual/11B |
| 106 | Evento acta publicada | Auditoría | Sistema | C | Tests evaluacion/auditoria | Sin E2E | Media | Manual/11B |
| 107 | Evento conformidad | Auditoría | Sistema | C | Tests evaluacion/auditoria | Sin E2E | Media | Manual/11B |
| 108 | Evento validación | Auditoría | Sistema | C | Tests evaluacion/auditoria | Sin E2E | Media | Manual/11B |
| 109 | Evento formalización | Auditoría | Sistema | C | Tests evaluacion/auditoria | Sin E2E | Media | Manual/11B |
| 110 | Evento extraordinario | Auditoría | Sistema | C | Tests trayectoria/auditoria | Sin E2E | Baja | Mantener backend |
| 111 | Evento movimiento | Auditoría | Sistema | C | Tests relaciones/auditoria | Sin E2E | Baja | Mantener backend |
| 112 | Evento cierre/apertura | Auditoría | Sistema | C | Tests actas/auditoria | Sin E2E | Media | Mantener backend |
| 113 | Evento exportación | Auditoría | Sistema | C | Tests reportes/auditoria | Sin E2E | Alta | 11B reducido |
| 114 | Auditoría sin password/token/CSRF | Auditoría | Admin/Estadística | A | Spec 10 (negativo texto) | Assert simple | Media | Fortalecer |
| 115 | Docente/discente sin auditoría global | Auditoría | Docente/Discente | B | Specs 03/11 | Assert parcial | Media | Fortalecer |
| 116 | Captura docente usable desktop | UX | Docente | D | QA manual 10D/10E | Sin automatización | Baja | Manual |
| 117 | Acta detalle usable | UX | Docente/Jefaturas | D | QA manual 10D | Sin automatización | Baja | Manual |
| 118 | Reportes densos usables | UX | Estadística | D | QA manual 10D | Sin automatización | Baja | Manual |
| 119 | Auditoría usable | UX | Admin/Estadística | D | QA manual 10D | Sin automatización | Baja | Manual |
| 120 | Periodos/diagnóstico usable | UX | Estadística | D | QA manual 10D | Sin automatización | Baja | Manual |

## Resumen cuantitativo

- A: 8
- B: 16
- C: 79
- D: 16
- E: 1
- F: 0

Lectura: el valor central del proyecto está fuertemente cubierto por backend tests y parcialmente por E2E de navegación; la automatización UI transaccional profunda es la principal brecha.

