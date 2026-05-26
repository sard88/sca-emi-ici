# Guía de ejecución QA integral 11A

## Preparación

```powershell
docker compose up -d
docker compose ps
```

## Dataset

```powershell
$env:DEMO_QA_PASSWORD="definir-en-local"
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small
docker compose exec -T backend python manage.py seed_demo_qa_integral --size small
```

La segunda ejecución valida idempotencia. No debe duplicar datos QA.

## Backend

```powershell
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test usuarios
docker compose exec -T backend python manage.py test catalogos
docker compose exec -T backend python manage.py test relaciones
docker compose exec -T backend python manage.py test evaluacion
docker compose exec -T backend python manage.py test actas
docker compose exec -T backend python manage.py test trayectoria
docker compose exec -T backend python manage.py test reportes
docker compose exec -T backend python manage.py test auditoria
docker compose exec -T backend python manage.py test core.tests_qa_seed
docker compose exec -T backend python manage.py test
```

## Frontend

```powershell
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
```

## E2E

```powershell
$env:E2E_QA_PASSWORD=$env:DEMO_QA_PASSWORD
docker compose exec -T frontend npm run e2e:qa
```

Si se ejecuta desde host local:

```powershell
cd frontend
npx playwright install chromium
npm run e2e:qa
```

No versionar `frontend/playwright-report/`, `frontend/test-results/`, descargas, capturas, videos ni trazas.
