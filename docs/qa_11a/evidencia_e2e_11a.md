# Evidencia E2E y dataset QA 11A

Fecha: 2026-05-25
Rama: `feature/bloque-11a-dataset-qa-e2e`

## Comandos ejecutados

```powershell
git status
git branch --show-current
git log --oneline -n 10
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small --dry-run
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small
docker compose exec -T backend python manage.py test core.tests_qa_seed
docker compose exec -T backend python manage.py test
docker compose build
docker compose up -d
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
npx playwright install chromium
npm run e2e:qa
```

## Resultado observado

- `--dry-run` reportó el universo QA estimado sin escribir datos.
- Primera ejecución real `small`: creó el universo QA inicial.
- Segunda ejecución real `small`: reutilizó registros sin duplicar.
- `core.tests_qa_seed`: 5 pruebas OK.
- `backend python manage.py test`: 466 pruebas OK.
- `docker compose build`: OK.
- `docker compose up -d`: OK.
- `makemigrations --check`: OK, sin cambios detectados.
- `frontend npm run lint`: OK.
- `frontend npm run build`: OK.
- `npm run e2e:qa` desde host local: 21 pruebas OK.

## Playwright

Se agregó configuración y pool E2E por rol. La suite final ejecutada desde host local contra `localhost:3000`/`localhost:8000` reportó 21/21 OK.

## Limitaciones

- Las pruebas E2E no deben versionar capturas, videos, trazas ni descargas.
- Dentro del contenedor, el navegador necesita librerías del sistema y Chromium. Se ajustó `frontend/Dockerfile` con `npx playwright install --with-deps chromium`.
- Para esta corrida final se usó host local, porque reproduce mejor la experiencia real del navegador con `localhost:3000` y `localhost:8000`.
