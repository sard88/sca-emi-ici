# Checklist por modulo 10E

| Modulo | Estado | Validacion | Observaciones |
|---|---|---|---|
| Autenticacion | OK parcial | `/login` 200; `/api/auth/csrf/` 200; APIs protegidas 401 anonimo; tests `usuarios` OK. | Login manual requiere credenciales QA documentadas. |
| Dashboard | OK | `/dashboard` y dashboards por perfil responden 200; build compila. | Accesos por perfil validados por configuracion y tests. |
| Administracion | OK | `/administracion`, usuarios, cargos y unidades responden 200; tests `usuarios` OK. | No se validan cambios manuales con usuario real. |
| Catalogos | OK | Rutas principales responden 200; tests `catalogos` OK. | `Materia` se conserva en catalogo base. |
| Calificaciones | OK parcial | Tests `evaluacion` OK; rutas docente compiladas. | Captura manual requiere datos QA. |
| Actas | OK parcial | Tests `actas` y `evaluacion` OK; rutas de docente, estadistica y jefaturas compilan. | Flujo visual completo requiere datos QA. |
| Reportes | OK | Rutas responden 200; tests `reportes` OK. | Descargas reales no ejecutadas sin usuario/datos demo. |
| Kardex | OK parcial | `/reportes/kardex` 200; tests `reportes` OK. | Exportacion manual PDF requiere discente QA autorizado. |
| Trayectoria | OK parcial | Rutas responden 200; tests `trayectoria` OK. | Historial manual por discente requiere ID QA. |
| Movimientos | OK parcial | Rutas responden 200; tests `relaciones` OK. | Cambio de grupo manual requiere dataset QA. |
| Periodos | OK parcial | Rutas responden 200; tests `actas`/`trayectoria` OK. | Cierre/apertura real requiere periodo QA sin bloqueantes. |
| Auditoria | OK | `/reportes/auditoria` 200; tests `auditoria` OK; endpoints anonimos 401. | Eventos manuales se validan en demo con datos ficticios. |
| Docker Compose | OK | Build, up, ps y config OK. | Se corrigio limpieza de `.next` para evitar chunks stale. |
| Responsive | Parcial | Build/rutas sin fallos; no hay evidencia visual por viewport. | Queda como P2 en backlog post-10E. |
| Privacidad | OK parcial | APIs protegidas 401 anonimo; tests y docs 9K/10D cubren sanitizacion. | Auditoria visual manual requiere perfil autorizado. |
