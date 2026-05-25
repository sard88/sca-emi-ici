# Checklist por perfil 10E

Leyenda:

- OK: validado por pruebas automaticas, build, rutas o endpoints.
- Parcial: requiere sesion/datos QA para confirmacion manual completa.
- Pendiente: queda para demo con credenciales ficticias.

## Admin / superusuario

| Validacion | Estado | Evidencia |
|---|---|---|
| Login | Parcial | `/login` responde 200; flujo con credencial demo no ejecutado por falta de credenciales QA documentadas. |
| Dashboard | OK | `/admin-soporte` y `/dashboard` responden 200; build compila rutas. |
| Administracion usuarios/cargos/unidades | OK | Rutas `/administracion/**` responden 200; tests `usuarios` OK. |
| Catalogos | OK | Rutas `/catalogos/**` responden 200; tests `catalogos` OK. |
| Reportes, kardex y auditoria | OK | Rutas responden 200; tests `reportes` y `auditoria` OK. |
| Django Admin soporte tecnico | Parcial | Servicio backend y admin montado; no se valida login manual. |
| Logout | Parcial | Tests de autenticacion/auditoria cubren logout; no se ejecuta manual. |
| Casos negativos de password | OK | Documentado en 10D-2/10D-3; no se detecta exposicion en build/rutas. |

## Estadistica

| Validacion | Estado | Evidencia |
|---|---|---|
| Dashboard institucional | OK | `/estadistica` responde 200. |
| Actas consulta | OK | `/estadistica/actas` compila en build y responde en listado de rutas cuando aplica. |
| Trayectoria, movimientos y periodos | OK | Rutas principales responden 200; tests `trayectoria`, `relaciones`, `actas` OK. |
| Cierre/apertura | Parcial | Endpoints y tests pasan; flujo manual depende de datos QA sin bloqueantes. |
| Reportes, exportaciones, auditoria | OK | Rutas y tests `reportes`/`auditoria` OK. |
| Casos negativos de cargo | Parcial | Cubierto por permisos backend en tests; no se valida manual con usuario local. |

## Docente

| Validacion | Estado | Evidencia |
|---|---|---|
| Dashboard docente | OK | `/docente` responde 200. |
| Mis asignaciones y captura | OK | `/docente/asignaciones` responde 200; build compila rutas dinamicas; tests `evaluacion` OK. |
| Mis actas | OK | `/docente/actas` responde 200; tests `actas` y `evaluacion` OK. |
| Generar/publicar/remitir | Parcial | Tests backend cubren transiciones; no se ejecuta manual sin datos demo. |
| No ver globales/auditoria/admin | OK | Endpoints anonimos protegidos 401; permisos backend cubiertos por tests. |

## Discente

| Validacion | Estado | Evidencia |
|---|---|---|
| Dashboard discente | OK | `/discente` responde 200. |
| Mi carga academica | OK | `/discente/carga-academica` responde 200; endpoint anonimo protegido 401. |
| Mis actas y detalle propio | OK | `/discente/actas` responde 200; build compila detalle dinamico. |
| Conformidad/inconformidad | Parcial | Tests backend cubren reglas; no se ejecuta manual sin datos demo. |
| Mi historial | OK | `/trayectoria/mi-historial` responde 200; endpoint anonimo protegido 401. |
| No ver otros discentes/globales | OK | Tests de trayectoria/evaluacion y endpoints protegidos. |

## Jefatura de carrera

| Validacion | Estado | Evidencia |
|---|---|---|
| Dashboard | OK | `/jefatura-carrera` responde 200. |
| Actas por validar | OK | Build compila `/jefatura-carrera/actas/[id]`; tests `evaluacion` OK. |
| Reportes de ambito y trayectoria | Parcial | Rutas y tests OK; alcance por ambito requiere usuario QA especifico. |
| No formalizar ni operar fuera de permisos | OK | Permisos backend cubiertos por tests. |

## Jefatura academica

| Validacion | Estado | Evidencia |
|---|---|---|
| Dashboard | OK | `/jefatura-academica` responde 200. |
| Actas por formalizar | OK | Build compila `/jefatura-academica/actas/[id]`; tests `evaluacion` OK. |
| No modificar calificaciones | OK | Tests de actas/evaluacion pasan. |
| Reportes, kardex y auditoria autorizada | Parcial | Rutas OK; permisos por cargo requieren usuario QA. |

## Jefatura pedagogica

| Validacion | Estado | Evidencia |
|---|---|---|
| Dashboard | OK | `/jefatura-pedagogica` responde 200. |
| Reportes operativos/desempeno/trayectoria | OK | Rutas de reportes responden 200; tests reportes OK. |
| Kardex autorizado | Parcial | Ruta `/reportes/kardex` OK; requiere usuario QA para permiso exacto. |
| Sin rutas antiguas Django en dashboard | OK | Validado por configuracion 10D-2/10D-3 y build. |

## Usuario anonimo

| Validacion | Estado | Evidencia |
|---|---|---|
| Puede abrir `/login` | OK | `/login` 200 tras correccion P1. |
| APIs protegidas bloqueadas | OK | Endpoints principales devuelven 401 sin sesion. |
| No ve datos privados por API | OK | `/api/auth/me/` no entrega datos privados; APIs de modulos protegidas. |
