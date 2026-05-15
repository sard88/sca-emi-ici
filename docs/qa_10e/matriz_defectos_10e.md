# Matriz de defectos 10E

| ID | Severidad | Modulo | Perfil | Descripcion | Pasos para reproducir | Resultado esperado | Resultado observado | Estado | Bloque recomendado | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|
| 10E-P1-001 | P1 | Docker Compose / Frontend | Anonimo | `/login` devolvia 500 despues de `docker compose build` + `docker compose up -d` por chunk faltante en `.next/server`. | Rebuild de Compose, recrear frontend, consultar `/login` desde contenedor frontend. | `/login` responde HTML 200. | Error `Cannot find module './5873.js'` en volumen persistente `.next`. | Corregido | 10E | `compose.yaml` limpia contenido de `.next` antes de `next dev`; regresion final `53/53` rutas OK. |
| 10E-ENV-001 | N/A | Ambiente local | N/A | `curl` desde host sandbox no conecta a puertos publicados aunque Compose muestra servicios arriba. | `curl -I http://localhost:8000/health/` y `curl -I http://localhost:3000/login`. | Respuesta HTTP desde host. | `curl: (7) Failed to connect`. | No reproducible como defecto de app | N/A | Desde contenedores: backend `/health/` 200 y frontend `/login` 200. |
| 10E-P2-001 | P2 | QA manual / Datos demo | Todos | No se localizaron credenciales QA/demo ni fixture idempotente de datos demo en el repositorio. | Buscar scripts de seed/fixture/management commands y documentacion de credenciales. | Datos ficticios disponibles para validar flujo completo manual. | No hay comando QA evidente ni credenciales documentadas. | Diferido | Bloque 11 / preparacion demo | Mantener guia manual; no crear datos reales ni fixture nuevo en 10E. |
| 10E-P2-002 | P2 | Frontend QA | Todos | No existe suite automatizada frontend adicional a lint/build. | `npm test --if-present`. | Tests frontend si el proyecto los define. | No hay script `test`. | Diferido | Bloque 11 / QA automatizado | Lint/build pasan; rutas principales verificadas por fetch. |
| 10E-P2-003 | P2 | Responsive | Todos | Validacion responsive visual no fue automatizada con capturas por falta de suite/browser QA configurado y datos demo autenticados. | Intentar cubrir rutas responsive solo con build/fetch. | Evidencia visual desktop/tablet/movil. | Se valida compilacion y disponibilidad de rutas, no screenshot visual por perfil. | Diferido | Bloque 11 / QA visual | Registrar como pendiente no bloqueante; no hay P0/P1 responsive detectado por build/rutas. |

## Resumen

- P0 abiertos: 0.
- P1 abiertos: 0.
- P1 corregidos: 1.
- P2/P3 diferidos: 3.
