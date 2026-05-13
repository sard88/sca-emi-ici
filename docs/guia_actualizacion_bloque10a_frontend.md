# Guia para obtener y levantar la version Bloque 10A

Fecha de corte: 13 de mayo de 2026  
Rama esperada: `feature/bloque-10a-frontend-base`  
Sistema: Sistema de Control Academico EMI - ICI

## 1. Que debe hacer quien genera los cambios

Para que otra persona pueda obtener esta version, basta con subir el codigo al repositorio GitHub.

No es necesario subir imagenes Docker ni generar un paquete especial si la otra persona tiene Docker Desktop y acceso al repositorio.

Pasos recomendados desde la maquina donde estan los cambios:

```bash
git status
```

Revisar que los cambios correspondan al Bloque 10A.

Despues:

```bash
git add .
git commit -m "feat(frontend): crear base institucional Next.js para Bloque 10A"
git push -u origin feature/bloque-10a-frontend-base
```

Si la rama ya existe en remoto y ya tiene upstream configurado:

```bash
git push
```

## 2. Que NO se debe subir al repo

No subir archivos generados localmente:

- `frontend/node_modules/`
- `frontend/.next/`
- volumenes Docker;
- imagenes Docker generadas;
- archivos `.env` con credenciales reales;
- backups de base de datos salvo que se acuerde explicitamente;
- dumps con informacion sensible sin control.

El repositorio ya contiene:

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/Dockerfile`
- `compose.yaml`

Con eso Docker puede reconstruir el frontend en la otra maquina.

## 3. Que debe hacer la otra persona si ya tiene el repo clonado

Entrar a la carpeta del proyecto:

```bash
cd /ruta/al/sca-emi-ici
```

Guardar o confirmar cualquier cambio local antes de actualizar:

```bash
git status
```

Si no tiene cambios locales importantes:

```bash
git fetch origin
git checkout feature/bloque-10a-frontend-base
git pull origin feature/bloque-10a-frontend-base
```

Si estaba trabajando en otra rama y quiere solo traer la version final cuando se integre a `main` o `develop`, entonces debera hacer pull de esa rama cuando corresponda.

## 4. Que debe hacer si no tiene el repo clonado

```bash
git clone <URL_DEL_REPOSITORIO>
cd sca-emi-ici
git checkout feature/bloque-10a-frontend-base
```

## 5. Variables de entorno necesarias

Debe existir archivo `.env` en la raiz del repo.

Si no existe, crear desde ejemplo:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Revisar que tenga al menos variables de base de datos y configuracion local:

```env
POSTGRES_DB=sca_emi_ici
POSTGRES_USER=sca_emi_ici
POSTGRES_PASSWORD=<password_local>
POSTGRES_PORT=5433
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Sistema de Control Academico EMI - ICI
NEXT_PUBLIC_APP_ENV=MVP intranet
```

Importante:

- No compartir `.env` con secretos reales por Git.
- Las variables `NEXT_PUBLIC_*` son visibles para el navegador; no colocar secretos ahi.

## 6. Variables frontend opcionales

Tambien existe `frontend/.env.example`.

Para desarrollo local fuera de Docker se puede crear:

```bash
cp frontend/.env.example frontend/.env.local
```

En Windows PowerShell:

```powershell
Copy-Item frontend/.env.example frontend/.env.local
```

Con Docker Compose no es estrictamente obligatorio si las variables ya estan en `.env` raiz y `compose.yaml` las inyecta al servicio frontend.

## 7. Levantar los contenedores

Desde la raiz del repo:

```bash
docker compose build
docker compose up -d
```

Verificar servicios:

```bash
docker compose ps
```

Servicios esperados:

- `sca-emi-ici-db`
- `sca-emi-ici-backend`
- `sca-emi-ici-frontend`

URLs esperadas:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Django Admin: `http://localhost:8000/admin/`

## 8. Migraciones backend

Si la base de datos ya existe y esta actualizada, validar:

```bash
docker compose exec -T backend python manage.py migrate
```

En esta fase 10A no deberia crear migraciones de modelos academicos, pero el backend debe estar migrado para que el login y los datos de usuario funcionen.

## 9. Validaciones recomendadas

Backend:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test
```

Frontend:

```bash
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
```

Si `npm run build` reinicia o altera el estado del servidor dev de Next.js, se puede reiniciar el servicio frontend:

```bash
docker compose restart frontend
```

## 10. Validacion manual esperada

Abrir:

```text
http://localhost:3000
```

Resultado esperado:

- si no hay sesion, redirige a `/login`;
- login institucional visible;
- iniciar sesion con usuario valido redirige a `/dashboard`;
- dashboard muestra panel institucional;
- sidebar muestra modulos segun rol/cargo;
- menu de usuario despliega opciones;
- `Cerrar sesion` vuelve al login;
- paginas de modulo conservan estilo verde institucional;
- banner inferior muestra logos de carreras;
- Django Admin sigue disponible en `http://localhost:8000/admin/`.

## 11. Base de datos

Para obtener los cambios de codigo del Bloque 10A no se necesita restaurar base de datos nueva.

Pero para que el portal muestre usuarios, roles, cargos y datos reales, la otra persona necesita una base de datos compatible con los bloques previos.

Opciones:

1. Usar su base local si ya esta migrada y tiene datos.
2. Restaurar un backup acordado del equipo.
3. Crear usuario administrador local para prueba.

Ejemplo si necesita crear superusuario:

```bash
docker compose exec backend python manage.py createsuperuser
```

## 12. Se debe generar algo en Docker?

No es obligatorio generar ni compartir imagen Docker.

Lo normal para colaboracion es:

1. Hacer commit y push del codigo.
2. La otra persona hace pull.
3. La otra persona ejecuta `docker compose build`.
4. La otra persona ejecuta `docker compose up -d`.

Docker generara localmente:

- imagen del backend si aplica;
- imagen del frontend;
- volumen `frontend_node_modules`;
- volumen `frontend_next`;
- volumen `postgres_data`.

Esos artefactos no se suben al repositorio.

Solo tendria sentido publicar imagenes Docker en un registry si el equipo define un flujo de despliegue formal, pero eso no es necesario para este intercambio de desarrollo.

## 13. Problemas comunes

### 13.1 Puerto ocupado

Si `3000`, `8000` o `5433` estan ocupados, Docker puede fallar.

Revisar:

```bash
docker compose ps
```

### 13.2 Cookies o sesion rara despues de cambios

Probar:

```bash
docker compose restart frontend backend
```

Y limpiar cookies de `localhost` si persiste.

### 13.3 Error de CORS o CSRF

Validar `.env`:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Despues reiniciar backend:

```bash
docker compose restart backend
```

### 13.4 El frontend no refleja cambios

Reiniciar frontend:

```bash
docker compose restart frontend
```

Si es necesario reconstruir:

```bash
docker compose build frontend
docker compose up -d frontend
```

## 14. Checklist rapido para la otra persona

```bash
git fetch origin
git checkout feature/bloque-10a-frontend-base
git pull origin feature/bloque-10a-frontend-base
cp .env.example .env
docker compose build
docker compose up -d
docker compose exec -T backend python manage.py migrate
docker compose ps
```

Abrir:

```text
http://localhost:3000
```

## 15. Resumen ejecutivo

Para compartir esta ultima version:

- Si, basta con commit y push al repo.
- No, no se necesita subir `node_modules` ni `.next`.
- No, no se necesita generar imagen Docker para compartir con otra maquina.
- Si, la otra persona debe reconstruir/levantar Docker localmente.
- Si, necesitara una base de datos migrada y con usuarios para probar login y roles.
