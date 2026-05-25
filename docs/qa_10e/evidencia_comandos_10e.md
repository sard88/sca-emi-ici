# Evidencia de comandos 10E

Fecha: 2026-05-15  
Rama: `feature/bloque-10e-qa-integral-demo`  
Base inicial: `620f44b`

## Control de rama

| Comando | Resultado | Observacion |
|---|---|---|
| `git status --short --branch` | OK | Rama base limpia en `feature/bloque-10d3-terminologia-microcopy-ui`. |
| `git checkout -b feature/bloque-10e-qa-integral-demo` | OK | Rama 10E creada sobre base con 10D-3 y 10D-4. |

## Docker Compose

| Comando | Resultado | Observacion |
|---|---|---|
| `docker compose ps` | OK | `db`, `backend` y `frontend` arriba; `db` saludable. |
| `docker compose build` | OK | Imagen backend y frontend construidas. Frontend: `npm install` dentro de imagen, 0 vulnerabilidades reportadas. |
| `docker compose up -d` | OK | Servicios recreados y levantados. |
| `docker compose ps` | OK | `db` healthy; backend y frontend `Up`. |
| `curl -I http://localhost:8000/health/` | No concluyente por entorno | El host del sandbox no conecto a puertos publicados aunque Compose mostraba puertos expuestos. |
| `curl -I http://localhost:3000/login` | No concluyente por entorno | Misma restriccion de host local del sandbox. |
| `docker compose exec -T backend python ... urllib /health/` | OK | `200 application/json` desde dentro del contenedor backend. |
| `docker compose exec -T frontend node ... fetch /login` | OK tras correccion | `200 text/html; charset=utf-8`. |
| `docker compose config --quiet` | OK | Sintaxis Compose valida tras correccion de comando frontend. |

## Backend

| Comando | Resultado | Observacion |
|---|---|---|
| `docker compose exec -T backend python manage.py check` | OK | Sin issues. |
| `docker compose exec -T backend python manage.py makemigrations --check` | OK | `No changes detected`. |
| `docker compose exec -T backend python manage.py showmigrations` | OK | Migraciones principales marcadas `[X]`. |
| `docker compose exec -T backend python manage.py test usuarios` | OK | 92 tests. |
| `docker compose exec -T backend python manage.py test catalogos` | OK | 71 tests. |
| `docker compose exec -T backend python manage.py test relaciones` | OK | 39 tests. |
| `docker compose exec -T backend python manage.py test evaluacion` | OK | 86 tests. |
| `docker compose exec -T backend python manage.py test actas` | OK | 27 tests. |
| `docker compose exec -T backend python manage.py test trayectoria` | OK | 58 tests. |
| `docker compose exec -T backend python manage.py test reportes` | OK | 74 tests. |
| `docker compose exec -T backend python manage.py test auditoria` | OK | 7 tests. |
| `docker compose exec -T backend python manage.py test core` | OK | 7 tests. |
| `docker compose exec -T backend python manage.py test` | OK | 461 tests en 218.454s. |

## Frontend

| Comando | Resultado | Observacion |
|---|---|---|
| `docker compose exec -T frontend npm run lint` | OK | ESLint sin warnings. |
| `docker compose exec -T frontend npm run build` | OK | Next build compila 46 paginas/rutas. |
| `docker compose exec -T frontend npm test --if-present` | OK sin suite | No existe script `test`; `--if-present` termina sin ejecutar pruebas adicionales. |

## Rutas frontend

Consulta desde contenedor frontend con `fetch("http://127.0.0.1:3000" + ruta)`.

Resultado final: `TOTAL_OK=53/53`.

Rutas cubiertas:

- `/`, `/login`, `/dashboard`, `/perfil`.
- Perfiles: `/admin-soporte`, `/estadistica`, `/docente`, `/discente`, `/jefatura-carrera`, `/jefatura-academica`, `/jefatura-pedagogica`.
- Administracion y catalogos: `/administracion`, `/administracion/usuarios`, `/administracion/cargos`, `/administracion/unidades`, `/catalogos`, `/catalogos/carreras`, `/catalogos/planes`, `/catalogos/antiguedades`, `/catalogos/periodos`, `/catalogos/grupos`, `/catalogos/materias`, `/catalogos/programas-asignatura`, `/catalogos/esquemas-evaluacion`, `/catalogos/situaciones-academicas`, `/catalogos/resultados-academicos`.
- Docente/discente: `/docente/asignaciones`, `/docente/actas`, `/discente/carga-academica`, `/discente/actas`, `/trayectoria/mi-historial`.
- Trayectoria/movimientos/periodos: `/trayectoria`, `/trayectoria/historial`, `/trayectoria/extraordinarios`, `/trayectoria/extraordinarios/nuevo`, `/trayectoria/situaciones`, `/trayectoria/situaciones/nuevo`, `/movimientos-academicos`, `/movimientos-academicos/nuevo`, `/movimientos-academicos/cambio-grupo`, `/periodos`, `/periodos/cierres`, `/periodos/apertura`, `/periodos/aperturas`, `/periodos/pendientes-asignacion-docente`.
- Reportes: `/reportes`, `/reportes/actas`, `/reportes/kardex`, `/reportes/operativos`, `/reportes/desempeno`, `/reportes/trayectoria`, `/reportes/exportaciones`, `/reportes/auditoria`.

## Seguridad anonima basica

Consulta desde backend sin sesion:

| Endpoint | Resultado |
|---|---|
| `/health/` | `200 application/json` |
| `/api/auth/csrf/` | `200 application/json` |
| `/api/auth/me/` | `200 application/json` |
| `/api/dashboard/resumen/` | `401 application/json` |
| `/api/catalogos/carreras/` | `401 application/json` |
| `/api/reportes/catalogo/` | `401 application/json` |
| `/api/exportaciones/` | `401 application/json` |
| `/api/auditoria/eventos/` | `401 application/json` |
| `/api/docente/asignaciones/` | `401 application/json` |
| `/api/discente/carga-academica/` | `401 application/json` |
| `/api/trayectoria/mi-historial/` | `401 application/json` |
| `/api/relaciones/movimientos/` | `401 application/json` |
| `/api/periodos/` | `401 application/json` |

`/api/auth/me/` responde 200 como endpoint de estado de sesion; no entrega datos privados sin autenticacion.
