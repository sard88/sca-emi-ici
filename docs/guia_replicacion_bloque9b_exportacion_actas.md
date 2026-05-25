# Guía para replicar Bloque 9B - Exportación de actas PDF/Excel

Esta guía sirve para que otra computadora obtenga la versión actual del Sistema de Control Académico EMI - ICI con el Bloque 9B funcionando, incluyendo:

- exportación de actas en XLSX desde plantillas institucionales;
- exportación de actas en PDF convirtiendo XLSX con LibreOffice;
- auditoría de exportaciones en `RegistroExportacion`;
- migraciones nuevas de `Acta` y `Usuario`;
- plantillas productivas anonimizadas de actas.

## Punto clave

No basta con hacer `git pull` si el contenedor backend ya existía.

Además de traer el código, la otra computadora debe:

- reconstruir la imagen `backend` para instalar LibreOffice;
- recrear el contenedor `backend`;
- aplicar migraciones;
- validar que `soffice` exista dentro del contenedor.

## Caso específico: ya tiene 10B y 9A funcionando

Si la otra computadora ya tiene el proyecto funcionando con:

- Bloque 10B;
- Bloque 9A;
- Docker levantado;
- base de datos operativa;

entonces no necesita reinstalar todo ni restaurar base desde cero.

Solo debe:

1. Traer la rama/cambios de 9B.
2. Reconstruir `backend` para instalar LibreOffice.
3. Recrear el contenedor `backend`.
4. Aplicar migraciones nuevas.
5. Validar XLSX/PDF.

Comandos resumidos:

```bash
cd /ruta/al/repo/sca-emi-ici

git status
git fetch origin
git checkout feature/bloque-9b-exportacion-actas
git pull --ff-only origin feature/bloque-9b-exportacion-actas

docker compose build backend
docker compose up -d --force-recreate backend

docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend sh -lc 'which soffice && soffice --version'
```

Si el Bloque 9B ya fue integrado a `main`, reemplazar la parte de Git por:

```bash
git checkout main
git pull --ff-only origin main
```

No ejecutar:

```bash
docker compose down -v
```

porque eso puede borrar la base de datos local.

## Antes de compartir

Desde esta computadora se debe hacer commit y push de los cambios.

Rama actual de trabajo:

```bash
feature/bloque-9b-exportacion-actas
```

Commit sugerido:

```bash
git status
git add .
git commit -m "feat(reportes): implementar exportacion de actas PDF Excel Bloque 9B"
git push -u origin feature/bloque-9b-exportacion-actas
```

Si el equipo trabaja con Pull Request, abrir PR desde:

```text
feature/bloque-9b-exportacion-actas
```

hacia la rama principal que use el equipo, por ejemplo:

```text
main
```

La otra computadora puede usar la rama directamente o esperar a que se haga merge.

## Archivos privados

Los archivos reales de referencia no se versionan:

```text
docs/referencias_privadas/
```

Esa carpeta está en `.gitignore`.

La otra computadora no necesita esos archivos privados para generar actas. El sistema usa las plantillas productivas anonimizadas versionadas en:

```text
backend/reportes/templates_xlsx/actas/
```

## Requisitos en la otra computadora

- Docker Desktop funcionando.
- Git instalado.
- Acceso al repositorio de GitHub.
- Puertos disponibles:
  - `3000` para frontend;
  - `8000` para backend;
  - `5433` para PostgreSQL local del compose.
- Espacio suficiente en Docker. LibreOffice agrega aproximadamente 400-500 MB a la imagen backend.

## Opción A: Ya existe el repo en la otra computadora

Entrar al repo:

```bash
cd /ruta/al/repo/sca-emi-ici
```

Revisar si hay cambios locales:

```bash
git status
```

Si hay cambios locales importantes, guardarlos antes de actualizar:

```bash
git add .
git commit -m "chore: respaldo cambios locales antes de actualizar"
```

O, si son cambios temporales:

```bash
git stash push -m "respaldo temporal antes de actualizar bloque 9b"
```

Traer la rama del Bloque 9B:

```bash
git fetch origin
git checkout feature/bloque-9b-exportacion-actas
git pull --ff-only origin feature/bloque-9b-exportacion-actas
```

Si el Bloque 9B ya fue integrado a `main`, usar:

```bash
git checkout main
git pull --ff-only origin main
```

## Opción B: Clonar el repo desde cero

```bash
git clone <URL_DEL_REPOSITORIO> sca-emi-ici
cd sca-emi-ici
git checkout feature/bloque-9b-exportacion-actas
```

Si el Bloque 9B ya fue integrado a `main`:

```bash
git checkout main
git pull --ff-only origin main
```

## Variables de entorno

Si no existe `.env`:

```bash
cp .env.example .env
```

Revisar que `.env` tenga al menos:

```env
POSTGRES_DB=sca_emi_ici
POSTGRES_USER=sca_emi_ici
POSTGRES_PASSWORD=sca_emi_ici
POSTGRES_PORT=5433

DJANGO_SECRET_KEY=cambia-esto-por-una-clave-larga
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend

NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Si no existe `frontend/.env.local`:

```bash
cp frontend/.env.example frontend/.env.local
```

No compartir secretos reales por Git.

## Levantar servicios

No usar:

```bash
docker compose down -v
```

porque `-v` borra los volúmenes y puede eliminar la base local.

Construir backend para instalar LibreOffice:

```bash
docker compose build backend
```

Este paso puede tardar bastante la primera vez porque descarga LibreOffice.

Levantar o recrear servicios:

```bash
docker compose up -d db
docker compose up -d --force-recreate backend
docker compose up -d frontend
```

También puede usarse:

```bash
docker compose up -d --build
```

pero para asegurar LibreOffice en backend, el comando importante es:

```bash
docker compose build backend
docker compose up -d --force-recreate backend
```

Verificar estado:

```bash
docker compose ps
```

Debe verse algo parecido a:

```text
sca-emi-ici-db         Up / healthy
sca-emi-ici-backend    Up
sca-emi-ici-frontend   Up
```

## Aplicar migraciones

```bash
docker compose exec -T backend python manage.py migrate
```

Migraciones relevantes de este bloque:

- `evaluacion.0009_acta_probables_causas_reprobacion_and_more`
- `usuarios.0017_usuario_cedula_profesional_and_more`

Validar proyecto:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
```

Resultado esperado:

```text
System check identified no issues
No changes detected
```

## Validar LibreOffice en backend

```bash
docker compose exec -T backend sh -lc 'which soffice && soffice --version'
```

Resultado esperado:

```text
/usr/bin/soffice
LibreOffice 25.2...
```

Si `soffice` no aparece, reconstruir:

```bash
docker compose build --no-cache backend
docker compose up -d --force-recreate backend
```

## Validar exportación XLSX

Primero identificar un acta existente:

```bash
docker compose exec -T backend python manage.py shell -c "from evaluacion.models import Acta; print(list(Acta.objects.values_list('id','corte_codigo','asignacion_docente__grupo_academico__clave_grupo','asignacion_docente__programa_asignatura__materia__nombre')[:10]))"
```

Con sesión iniciada en el navegador, abrir:

```text
http://localhost:8000/api/exportaciones/actas/<ACTA_ID>/xlsx/
```

Ejemplo:

```text
http://localhost:8000/api/exportaciones/actas/5/xlsx/
```

Debe descargar un archivo `.xlsx`.

## Validar exportación PDF

Con sesión iniciada en el navegador, abrir:

```text
http://localhost:8000/api/exportaciones/actas/<ACTA_ID>/pdf/
```

Ejemplo:

```text
http://localhost:8000/api/exportaciones/actas/5/pdf/
```

Debe descargar un archivo `.pdf`.

También puede validarse por shell con un superusuario existente:

```bash
docker compose exec -T backend python manage.py shell -c "from usuarios.models import Usuario; from reportes.actas_services import ServicioExportacionActa; user=Usuario.objects.filter(is_superuser=True).first(); archivo=ServicioExportacionActa(user).exportar_acta_corte(5, 'PDF'); print(archivo.content_type, len(archivo.contenido), archivo.contenido[:5], archivo.registro.estado)"
```

Resultado esperado:

```text
application/pdf <tamano> b'%PDF-' GENERADA
```

## URLs disponibles para actas

Acta por corte, para `P1`, `P2`, `P3` o `FINAL`:

```text
GET /api/exportaciones/actas/<acta_id>/xlsx/
GET /api/exportaciones/actas/<acta_id>/pdf/
```

Acta de Calificación Final consolidada por asignación docente:

```text
GET /api/exportaciones/asignaciones/<asignacion_docente_id>/calificacion-final/xlsx/
GET /api/exportaciones/asignaciones/<asignacion_docente_id>/calificacion-final/pdf/
```

Todas requieren autenticación y permisos.

## Datos necesarios para que las firmas salgan completas

Para el bloque `Evaluó`:

- el usuario docente debe tener capturado `Título profesional`;
- el usuario docente debe tener capturada `Cédula profesional`.

Esto se captura en Django Admin, en el perfil de Usuario.

Para `Revisó`:

- debe existir una `Asignación de cargo` activa/vigente de jefatura de carrera o subsección correspondiente;
- debe estar asociada a la carrera del grupo.

Para `Vo. Bo.`:

- debe existir una `Asignación de cargo` activa/vigente de jefatura académica.

Si esos datos no existen, el acta no inventa nombres y deja el espacio como pendiente o vacío según corresponda.

## Validar auditoría

Entrar a:

```text
http://localhost:8000/admin/reportes/registroexportacion/
```

Debe aparecer un registro por cada descarga o intento de exportación.

Si una exportación falla, revisar `mensaje_error`.

## Pruebas recomendadas

```bash
docker compose exec -T backend python manage.py test reportes
```

Si se quiere validar todo el backend:

```bash
docker compose exec -T backend python manage.py test
```

## Problemas comunes

### Error: No fue posible generar el archivo de acta

Revisar el último error:

```bash
docker compose exec -T backend python manage.py shell -c "from reportes.models import RegistroExportacion; qs=RegistroExportacion.objects.order_by('-id')[:5]; print('\n'.join([f'{r.id} | {r.tipo_documento} | {r.formato} | {r.estado} | {r.mensaje_error}' for r in qs]))"
```

Si aparece que LibreOffice no está disponible:

```bash
docker compose exec -T backend sh -lc 'which soffice || which libreoffice || true'
```

Si no aparece ruta:

```bash
docker compose build backend
docker compose up -d --force-recreate backend
```

Si sigue sin aparecer:

```bash
docker compose build --no-cache backend
docker compose up -d --force-recreate backend
```

### Build muy lento

Es normal la primera vez. `libreoffice-calc` descarga muchos paquetes.

No interrumpir si se ve que sigue descargando paquetes Debian.

### Migraciones pendientes

Si el backend muestra:

```text
You have unapplied migration(s)
```

Ejecutar:

```bash
docker compose exec -T backend python manage.py migrate
```

### Puerto ocupado

Si el puerto `8000`, `3000` o `5433` está ocupado, cerrar el proceso que lo usa o cambiar el puerto en `.env`/`compose.yaml`.

### Base de datos vacía

Si la otra computadora no tiene datos, el sistema funcionará, pero no habrá actas para exportar.

Opciones:

- restaurar un backup de PostgreSQL del proyecto;
- cargar datos por Admin;
- usar una base ya poblada del equipo.

## Resumen corto para la otra persona

Si ya tiene repo y `.env` listo:

```bash
git fetch origin
git checkout feature/bloque-9b-exportacion-actas
git pull --ff-only origin feature/bloque-9b-exportacion-actas

docker compose build backend
docker compose up -d db
docker compose up -d --force-recreate backend
docker compose up -d frontend

docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py check
docker compose exec -T backend sh -lc 'which soffice && soffice --version'
```

Validación rápida:

```text
http://localhost:8000/api/exportaciones/actas/<ACTA_ID>/xlsx/
http://localhost:8000/api/exportaciones/actas/<ACTA_ID>/pdf/
```
