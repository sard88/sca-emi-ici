# Defectos detectados 11A

| ID | Severidad | Módulo | Rol | Descripción | Pasos | Esperado | Observado | Estado | Bloque recomendado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11A-DEF-001 | P3 | E2E | Todos | El contenedor frontend requiere dependencias de Playwright/Chromium para ejecutar E2E internamente. Se ajustó el Dockerfile y se validó ejecución desde host local. | `npm run e2e:qa` | Pruebas ejecutadas | 21/21 OK desde host local; contenedor preparado con `npx playwright install --with-deps chromium`. | Cerrado | 11A |

No hay P0/P1 registrados al crear el dataset y la estructura inicial de pruebas.
