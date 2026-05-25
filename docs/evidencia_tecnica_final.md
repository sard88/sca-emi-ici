# Evidencia tecnica final

Fecha de ejecucion: 2026-05-25 15:26:32 -06:00
Rama: release/tesis-mvp
Commit base al iniciar validacion: 5662084
Tag en commit base: tesis-mvp-v1.0

Nota: corrida final posterior a correcciones menores necesarias para compilacion frontend en Next.js.

## Estado inicial
```text
M frontend/src/app/docente/actas/page.tsx
 M frontend/src/app/jefatura-academica/actas/page.tsx
 M frontend/src/app/periodos/page.tsx
 M frontend/src/app/reportes/actas/page.tsx
?? docs/evidencia_tecnica_final.md
?? docs/respaldo_frontend/
```

## docker compose build

Comando:
```powershell
docker compose build
```

Salida:
```text
 Image newproject-backend Building 
 Image newproject-frontend Building 
#1 [internal] load local bake definitions
#1 reading from stdin 997B done
#1 DONE 0.0s

#2 [frontend internal] load build definition from Dockerfile
#2 transferring dockerfile: 179B done
#2 DONE 0.0s

#3 [backend internal] load build definition from Dockerfile
#3 transferring dockerfile: 446B done
#3 DONE 0.0s

#4 [backend internal] load metadata for docker.io/library/python:3.12-slim
#4 DONE 0.0s

#5 [backend internal] load .dockerignore
#5 transferring context: 184B done
#5 DONE 0.0s

#6 [backend internal] load build context
#6 transferring context: 15.60kB 0.0s done
#6 DONE 0.0s

#7 [backend 1/6] FROM docker.io/library/python:3.12-slim@sha256:520153e2deb359602c9cffd84e491e3431d76e7bf95a3255c9ce9433b76ab99a
#7 resolve docker.io/library/python:3.12-slim@sha256:520153e2deb359602c9cffd84e491e3431d76e7bf95a3255c9ce9433b76ab99a 0.0s done
#7 DONE 0.0s

#8 [backend 5/6] RUN pip install --no-cache-dir -r requirements.txt
#8 CACHED

#9 [backend 4/6] COPY requirements.txt .
#9 CACHED

#10 [backend 2/6] WORKDIR /app
#10 CACHED

#11 [backend 3/6] RUN apt-get update     && apt-get install -y --no-install-recommends libreoffice-calc fonts-dejavu     && rm -rf /var/lib/apt/lists/*
#11 CACHED

#12 [backend 6/6] COPY . .
#12 CACHED

#13 [backend] exporting to image
#13 exporting layers done
#13 exporting manifest sha256:1060b556af06d3079d255fa876a8972fdabd744e8cd64a9b86f4d76c52362601 done
#13 exporting config sha256:e0e7465a910e118fa5cb77be05c1fac1435887265c67a68bf157135da97b0cd2 done
#13 exporting attestation manifest sha256:4eb4a2d73b9bf9f589dd8994817aec0bce02caa708bdc0aff6d86dd1cbf8bbba 0.0s done
#13 exporting manifest list sha256:b83b8459ab90300daf88fa55f921c7fc5d9b837f1dc25a257a9164f6073bb7a4 done
#13 naming to docker.io/library/newproject-backend:latest done
#13 unpacking to docker.io/library/newproject-backend:latest 0.0s done
#13 DONE 0.1s

#14 [backend] resolving provenance for metadata file
#14 DONE 0.0s

#15 [frontend internal] load metadata for docker.io/library/node:22-bookworm-slim
#15 DONE 0.6s

#16 [frontend internal] load .dockerignore
#16 transferring context: 88B done
#16 DONE 0.0s

#17 [frontend 1/5] FROM docker.io/library/node:22-bookworm-slim@sha256:7af03b14a13c8cdd38e45058fd957bf00a72bbe17feac43b1c15a689c029c732
#17 resolve docker.io/library/node:22-bookworm-slim@sha256:7af03b14a13c8cdd38e45058fd957bf00a72bbe17feac43b1c15a689c029c732 0.0s done
#17 DONE 0.0s

#18 [frontend internal] load build context
#18 transferring context: 167.61kB 0.0s done
#18 DONE 0.0s

#19 [frontend 3/5] COPY package*.json ./
#19 CACHED

#20 [frontend 2/5] WORKDIR /app
#20 CACHED

#21 [frontend 4/5] RUN npm install
#21 CACHED

#22 [frontend 5/5] COPY . .
#22 DONE 0.1s

#23 [frontend] exporting to image
#23 exporting layers 0.4s done
#23 exporting manifest sha256:8cb79b74bdc2128dc39b6b550602675e2a98fb2d972048937c679bfe85c16f34 done
#23 exporting config sha256:c31f7a8da48971932057f581786fe945dc848c3bc7d2c71babc29c36496afdd5 done
#23 exporting attestation manifest sha256:0d28f8959fed829369ffc4f62fa9728e8d73d1c6662f75ee3dddd83da7b79304 0.0s done
#23 exporting manifest list sha256:8ee8f2d6d6dce8b9e51d53fab3274f7c89dd584502adb8e20b614a07da575486 done
#23 naming to docker.io/library/newproject-frontend:latest done
#23 unpacking to docker.io/library/newproject-frontend:latest 0.1s done
#23 DONE 0.6s

#24 [frontend] resolving provenance for metadata file
#24 DONE 0.0s
 Image newproject-backend Built 
 Image newproject-frontend Built 
```

Codigo de salida: 0

## docker compose up -d

Comando:
```powershell
docker compose up -d
```

Salida:
```text
 Container sca-emi-ici-db Running 
 Container sca-emi-ici-backend Recreate 
 Container sca-emi-ici-backend Recreated 
 Container sca-emi-ici-frontend Recreate 
 Container sca-emi-ici-frontend Recreated 
 Container sca-emi-ici-db Waiting 
 Container sca-emi-ici-db Healthy 
 Container sca-emi-ici-backend Starting 
 Container sca-emi-ici-backend Started 
 Container sca-emi-ici-frontend Starting 
 Container sca-emi-ici-frontend Started 
```

Codigo de salida: 0

## docker compose ps

Comando:
```powershell
docker compose ps
```

Salida:
```text
NAME                   IMAGE                 COMMAND                  SERVICE    CREATED         STATUS                  PORTS
sca-emi-ici-backend    newproject-backend    "python manage.py ru…"   backend    3 seconds ago   Up Less than a second   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
sca-emi-ici-db         postgres:16           "docker-entrypoint.s…"   db         12 days ago     Up 5 hours (healthy)    0.0.0.0:5433->5432/tcp, [::]:5433->5432/tcp
sca-emi-ici-frontend   newproject-frontend   "docker-entrypoint.s…"   frontend   3 seconds ago   Up Less than a second   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
```

Codigo de salida: 0

## backend manage.py check

Comando:
```powershell
docker compose exec -T backend python manage.py check
```

Salida:
```text
System check identified no issues (0 silenced).
```

Codigo de salida: 0

## backend makemigrations --check

Comando:
```powershell
docker compose exec -T backend python manage.py makemigrations --check
```

Salida:
```text
No changes detected
```

Codigo de salida: 0

## backend tests

Comando:
```powershell
docker compose exec -T backend python manage.py test
```

Salida:
```text
Found 461 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.............................................................................................................................................................................................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 461 tests in 231.003s
System.Management.Automation.RemoteException
OK
Destroying test database for alias 'default'...
```

Codigo de salida: 0

## frontend npm run lint

Comando:
```powershell
docker compose exec -T frontend npm run lint
```

Salida:
```text

> sca-emi-ici-frontend@0.1.0 lint
> eslint . --max-warnings=0

```

Codigo de salida: 0

## frontend npm run build

Comando:
```powershell
docker compose exec -T frontend npm run build
```

Salida:
```text

> sca-emi-ici-frontend@0.1.0 build
> next build

   ▲ Next.js 15.5.18

   Creating an optimized production build ...
 ✓ Compiled successfully in 19.8s
   Linting and checking validity of types ...
   Collecting page data ...
   Generating static pages (0/47) ...
   Generating static pages (11/47) 
   Generating static pages (23/47) 
   Generating static pages (35/47) 
 ✓ Generating static pages (47/47)
   Finalizing page optimization ...
   Collecting build traces ...

Route (app)                                        Size  First Load JS
┌ ○ /                                             658 B         107 kB
├ ○ /_not-found                                   996 B         103 kB
├ ○ /admin-soporte                              2.85 kB         132 kB
├ ○ /administracion                             4.51 kB         133 kB
├ ƒ /administracion/[slug]                      2.22 kB         139 kB
├ ƒ /administracion/[slug]/[id]                 2.23 kB         139 kB
├ ƒ /brand-logo/[folder]/[code]                   126 B         103 kB
├ ○ /catalogos                                  2.91 kB         134 kB
├ ƒ /catalogos/[slug]                             416 B         139 kB
├ ƒ /catalogos/[slug]/[id]                        427 B         139 kB
├ ○ /dashboard                                   5.3 kB         134 kB
├ ○ /discente                                   2.85 kB         132 kB
├ ○ /discente/actas                              2.1 kB         138 kB
├ ƒ /discente/actas/[detalleId]                 3.59 kB         140 kB
├ ○ /discente/carga-academica                   2.41 kB         138 kB
├ ○ /discente/historial-academico               2.78 kB         132 kB
├ ○ /docente                                    2.85 kB         132 kB
├ ○ /docente/actas                              1.91 kB         134 kB
├ ƒ /docente/actas/[id]                         2.85 kB         142 kB
├ ○ /docente/asignaciones                       3.96 kB         133 kB
├ ƒ /docente/asignaciones/[id]                  4.17 kB         133 kB
├ ƒ /docente/asignaciones/[id]/captura/[corte]  3.47 kB         132 kB
├ ƒ /docente/asignaciones/[id]/resumen          2.34 kB         138 kB
├ ○ /estadistica                                2.85 kB         132 kB
├ ○ /estadistica/actas                          2.04 kB         134 kB
├ ƒ /estadistica/actas/[id]                     3.75 kB         140 kB
├ ○ /jefatura-academica                         2.85 kB         132 kB
├ ○ /jefatura-academica/actas                   2.24 kB         134 kB
├ ƒ /jefatura-academica/actas/[id]              2.16 kB         141 kB
├ ○ /jefatura-carrera                           2.85 kB         132 kB
├ ○ /jefatura-carrera/actas                     1.55 kB         134 kB
├ ƒ /jefatura-carrera/actas/[id]                2.15 kB         141 kB
├ ○ /jefatura-pedagogica                        2.85 kB         132 kB
├ ○ /login                                      4.25 kB         123 kB
├ ○ /movimientos-academicos                       180 B         145 kB
├ ƒ /movimientos-academicos/[id]                  289 B         145 kB
├ ○ /movimientos-academicos/cambio-grupo          180 B         145 kB
├ ○ /movimientos-academicos/nuevo                 180 B         145 kB
├ ○ /perfil                                     2.58 kB         131 kB
├ ○ /periodos                                   3.35 kB         132 kB
├ ƒ /periodos/[id]/diagnostico                    296 B         145 kB
├ ○ /periodos/apertura                            180 B         145 kB
├ ○ /periodos/aperturas                           179 B         145 kB
├ ƒ /periodos/aperturas/[id]                      290 B         145 kB
├ ○ /periodos/cierres                             180 B         145 kB
├ ƒ /periodos/cierres/[id]                        291 B         145 kB
├ ○ /periodos/pendientes-asignacion-docente       180 B         145 kB
├ ○ /reportes                                   8.11 kB         141 kB
├ ○ /reportes/actas                             5.58 kB         134 kB
├ ○ /reportes/auditoria                         4.42 kB         140 kB
├ ○ /reportes/desempeno                          1.6 kB         135 kB
├ ƒ /reportes/desempeno/[slug]                  5.65 kB         139 kB
├ ○ /reportes/exportaciones                     2.79 kB         139 kB
├ ○ /reportes/kardex                            4.89 kB         134 kB
├ ○ /reportes/operativos                        1.49 kB         134 kB
├ ƒ /reportes/operativos/[slug]                 4.54 kB         137 kB
├ ○ /reportes/trayectoria                        1.8 kB         135 kB
├ ƒ /reportes/trayectoria/[slug]                5.32 kB         139 kB
├ ○ /trayectoria                                  180 B         145 kB
├ ○ /trayectoria/extraordinarios                  178 B         145 kB
├ ƒ /trayectoria/extraordinarios/[id]             290 B         145 kB
├ ○ /trayectoria/extraordinarios/nuevo            180 B         145 kB
├ ○ /trayectoria/historial                        180 B         145 kB
├ ƒ /trayectoria/historial/[discenteId]           298 B         145 kB
├ ○ /trayectoria/mi-historial                     179 B         145 kB
├ ○ /trayectoria/situaciones                      180 B         145 kB
├ ƒ /trayectoria/situaciones/[id]                 289 B         145 kB
└ ○ /trayectoria/situaciones/nuevo                179 B         145 kB
+ First Load JS shared by all                    102 kB
  ├ chunks/1255-b28ea36bf0cdbd65.js             46.2 kB
  ├ chunks/4bd1b696-f785427dddbba9fb.js         54.2 kB
  └ other shared chunks (total)                 1.93 kB


○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand

```

Codigo de salida: 0

## Resumen de resultados

| Validacion | Codigo de salida | Resultado |
|---|---:|---|
| docker compose build | 0 | OK |
| docker compose up -d | 0 | OK |
| docker compose ps | 0 | OK |
| backend manage.py check | 0 | OK |
| backend makemigrations --check | 0 | OK |
| backend tests | 0 | OK |
| frontend npm run lint | 0 | OK |
| frontend npm run build | 0 | OK |

Fecha de finalizacion: 2026-05-25 15:31:49 -06:00

## Estado final
```text
M frontend/src/app/docente/actas/page.tsx
 M frontend/src/app/jefatura-academica/actas/page.tsx
 M frontend/src/app/periodos/page.tsx
 M frontend/src/app/reportes/actas/page.tsx
?? docs/evidencia_tecnica_final.md
?? docs/respaldo_frontend/
```

