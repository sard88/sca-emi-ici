# Reporte Bloque 10A - Front institucional base

Fecha de corte: 13 de mayo de 2026  
Rama de trabajo: `feature/bloque-10a-frontend-base`  
Sistema: Sistema de Control Academico EMI - ICI

## 1. Objetivo del Bloque 10A

El Bloque 10A crea la base del frontend institucional moderno del Sistema de Control Academico EMI - ICI, sin reemplazar todavia el backend Django, el Django Admin ni las vistas operativas existentes.

La intencion de este bloque fue construir un portal visual progresivo para validar el acceso por rol/cargo, iniciar la experiencia institucional del sistema y conectar el frontend moderno con el backend Django mediante APIs HTTP/JSON.

## 2. Alcance implementado

Se implemento una arquitectura hibrida:

- Django se mantiene como fuente de verdad funcional y de permisos.
- Django Admin se conserva como respaldo tecnico y operativo.
- Las vistas Django existentes se mantienen disponibles.
- Next.js se agrega como portal visual institucional moderno.
- El frontend consume APIs del backend; no accede directamente a la base de datos.
- No se duplicaron reglas academicas en el frontend.
- No se implemento JWT, MFA, OTP, PDF, Excel ni Bloque 9.

## 3. Estructura frontend creada

Se creo la carpeta `frontend/` con proyecto Next.js y estructura modular:

```text
frontend/
  Dockerfile
  .dockerignore
  .env.example
  package.json
  package-lock.json
  next.config.ts
  tailwind.config.ts
  tsconfig.json
  public/
    brand/
      README.md
      institutions/
      careers/
      login/
  src/
    app/
    components/
    config/
    lib/
```

Stack usado:

- Next.js con App Router.
- React.
- TypeScript.
- Tailwind CSS.
- Componentes propios equivalentes a una base shadcn/ui simple.
- ESLint.
- Docker para desarrollo.

## 4. Rutas frontend creadas

Se agregaron rutas iniciales del portal:

- `/`: redirecciona segun estado de autenticacion.
- `/login`: inicio de sesion institucional.
- `/dashboard`: panel general por rol/cargo.
- `/admin-soporte`: modulo administrador.
- `/estadistica`: modulo estadistica.
- `/docente`: modulo docente.
- `/discente`: modulo discente.
- `/jefatura-carrera`: modulo jefatura de carrera.
- `/jefatura-academica`: modulo jefatura academica.
- `/jefatura-pedagogica`: modulo jefatura pedagogica.
- `/brand-logo/[folder]/[code]`: fallback interno de logos para evitar imagen rota cuando falte un archivo.

## 5. Docker y compose

Se actualizo `compose.yaml` para agregar el servicio `frontend` junto a los servicios existentes:

- `db`: PostgreSQL.
- `backend`: Django.
- `frontend`: Next.js.

El servicio `frontend`:

- construye desde `./frontend`;
- expone `http://localhost:3000`;
- monta el codigo local para desarrollo;
- usa volumen Docker para `node_modules`;
- usa volumen Docker para `.next`;
- ejecuta `npm install && npm run dev`;
- depende de `backend`;
- usa variables `NEXT_PUBLIC_*` controladas por entorno.

URLs esperadas en desarrollo:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Django Admin: `http://localhost:8000/admin/`

## 6. Variables de entorno

Se creo `frontend/.env.example` con:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Sistema de Control Academico EMI - ICI
NEXT_PUBLIC_APP_ENV=MVP intranet
```

Se actualizaron variables backend en `.env.example` para desarrollo local seguro:

```env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
SESSION_COOKIE_NAME=sca_sessionid
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_AGE=28800
SESSION_EXPIRE_AT_BROWSER_CLOSE=False
SESSION_SAVE_EVERY_REQUEST=False
CSRF_COOKIE_NAME=sca_csrftoken
CSRF_COOKIE_SECURE=False
CSRF_COOKIE_SAMESITE=Lax
CSRF_COOKIE_HTTPONLY=True
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Sistema de Control Academico EMI - ICI
NEXT_PUBLIC_APP_ENV=MVP intranet
```

Regla importante:

- No se colocan secretos en variables `NEXT_PUBLIC_` porque son visibles para el navegador.

## 7. APIs backend agregadas para autenticacion

Se agregaron endpoints en Django bajo `/api/auth/`:

- `GET /api/auth/csrf/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`

Archivos principales:

- `backend/usuarios/api_views.py`
- `backend/usuarios/api_urls.py`
- `backend/config/urls.py`

### 7.1 CSRF

`GET /api/auth/csrf/`:

- genera o asegura el token CSRF;
- devuelve JSON con `csrfToken`;
- establece cookie CSRF;
- no desactiva CSRF.

### 7.2 Login

`POST /api/auth/login/`:

- recibe `username` y `password` en JSON;
- autentica con Django Auth;
- rechaza credenciales invalidas con error controlado;
- rechaza usuarios inactivos o con cuenta no activa;
- crea sesion Django con `login(request, user)`;
- devuelve datos minimos del usuario y un token CSRF renovado.

### 7.3 Logout

`POST /api/auth/logout/`:

- cierra sesion Django con `logout(request)`;
- requiere CSRF;
- devuelve JSON de exito.

### 7.4 Usuario actual

`GET /api/auth/me/`:

Si no hay sesion:

```json
{"authenticated": false}
```

Si hay sesion, devuelve:

- `authenticated`
- `id`
- `username`
- `nombre_completo`
- `nombre_visible`
- `nombre_institucional`
- `email`
- `correo`
- `grado_empleo`
- `roles`
- `cargos_vigentes`
- `perfil_principal`
- `carreras`
- `enlaces`

## 8. Seguridad configurada

Se agrego configuracion segura y parametrizable en `backend/config/settings.py`.

### 8.1 Sesiones

- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SECURE` configurable por entorno.
- `SESSION_COOKIE_SAMESITE = "Lax"` por defecto.
- `SESSION_COOKIE_PATH = "/"`
- `SESSION_COOKIE_NAME = "sca_sessionid"` por defecto.
- `SESSION_COOKIE_AGE = 28800` segundos por defecto, equivalente a 8 horas.
- `SESSION_SAVE_EVERY_REQUEST = False` por defecto.

### 8.2 CSRF

- CSRF permanece activo.
- `CSRF_COOKIE_HTTPONLY = True` por defecto.
- El frontend obtiene el token por `/api/auth/csrf/` y lo mantiene en memoria.
- `CSRF_COOKIE_SECURE` configurable por entorno.
- `CSRF_COOKIE_SAMESITE = "Lax"` por defecto.
- `CSRF_TRUSTED_ORIGINS` configurable.

### 8.3 CORS

Se agrego `backend/core/middleware.py` con un middleware CORS explicito:

- permite solo origenes definidos en `CORS_ALLOWED_ORIGINS`;
- permite credenciales;
- no usa comodines;
- responde `OPTIONS` cuando el origen esta permitido.

### 8.4 Hardening basico

- `ALLOWED_HOSTS` configurable.
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = "DENY"`
- `SECURE_REFERRER_POLICY` configurable.
- `SECURE_SSL_REDIRECT` configurable.
- HSTS desactivado en desarrollo local por defecto.

### 8.5 Seguridad frontend

- `fetch` usa `credentials: "include"`.
- No se guarda password.
- No se guarda token en `localStorage`.
- No se implemento JWT en esta fase.
- Logout cierra sesion en backend y limpia estado visual.

## 9. Identidad visual institucional

Se implemento una identidad visual aproximada, sobria e institucional.

Paleta base:

- Guinda institucional: `#611232`
- Guinda acento: `#9F2241`
- Verde institucional / militar: `#235B4E`
- Verde oscuro del portal: `#073F34`
- Verde olivo: `#3A4A32`
- Dorado sobrio: `#D4AF37`
- Dorado institucional: `#BC955C`
- Fondo marfil: `#F8F4EA`
- Gris carbon: `#1F2937`
- Blanco: `#FFFFFF`

Se ajusto el portal para evitar mensajes tecnicos al usuario final en la pantalla de login. La experiencia visible se enfoca en:

- acceso institucional;
- gestion academica;
- seguimiento de calificaciones;
- carga academica;
- actas;
- trayectoria escolar;
- seguridad y confidencialidad institucional.

## 10. Logos y branding

Se preparo la estructura de logos:

```text
frontend/public/brand/
  README.md
  institutions/
    emi.png
    emi-escudo.png
    sedena.png
    udefa.png
  careers/
    ic.png
    ice.png
    ici.png
    ii.png
  login/
    emi-campus.png
```

Se agrego configuracion centralizada en:

- `frontend/src/config/branding.ts`

Instituciones configuradas:

- EMI.
- UDEFA.
- SEDENA.

Carreras configuradas:

- IC - Ingenieria Civil.
- ICE - Ingenieria en Comunicaciones y Electronica.
- ICI - Ingenieria en Computacion e Informatica.
- II - Ingenieria Industrial.

Se agregaron componentes reutilizables:

- `InstitutionLogo`
- `CareerLogo`
- `BrandHeader`
- `InstitutionalSealPlaceholder`
- `LogoWithFallback`

Cuando un logo no existe, se muestra placeholder SVG interno para evitar imagen rota.

## 11. Login institucional

Se rediseño `/login` con estilo institucional inspirado en la referencia visual compartida.

Incluye:

- logos EMI y SEDENA;
- texto “Bienvenido al Sistema de Control Academico EMI”;
- tarjeta de inicio de sesion;
- campos usuario y contraseña;
- boton institucional de inicio;
- mensajes de error claros;
- imagen institucional local del edificio;
- diseno responsivo;
- fondo marfil con detalles graficos sobrios;
- eliminacion del indicador visual de Next.js para demos locales.

Se removieron mensajes tecnicos para usuario final como:

- referencia a cookies HttpOnly;
- referencia a CSRF;
- referencia a JWT;
- texto de backend operativo;
- texto tecnico de arquitectura.

## 12. Layout institucional del portal

Se construyo un shell principal con:

- `AppShell`
- `Sidebar`
- `Topbar`
- `DashboardSidePanel`
- pie institucional

### 12.1 Sidebar

El panel izquierdo incluye:

- logo/escudo EMI;
- texto Escuela Militar de Ingenieria;
- identificadores EMI y UDEFA;
- nombre del sistema;
- acceso a Panel general;
- modulos visibles segun rol/cargo;
- tarjeta de seguridad y confianza.

Regla por perfil:

- ADMIN ve todos los modulos.
- Estadistica ve sus modulos autorizados.
- Docente ve modulos docentes.
- Discente ve modulos discentes.
- Jefaturas ven los modulos asociados a su rol/cargo.

### 12.2 Topbar

El encabezado superior incluye:

- saludo con nombre visible del usuario;
- subtitulo “Panel de control institucional”;
- buscador visual preparado;
- campana de notificaciones preparada;
- caja de usuario/rol con menu desplegable.

El menu de usuario incluye:

- Mi perfil, como opcion futura;
- Panel general;
- Cerrar sesion.

### 12.3 Panel central

El panel central incluye:

- banner verde institucional;
- accesos rapidos segun rol/cargo;
- tarjetas de funcionalidades permitidas;
- banner inferior con los cuatro logos de carreras.

### 12.4 Panel derecho

El panel derecho incluye espacios preparados para:

- actividad reciente;
- calendario institucional;
- eventos proximos.

Actualmente se muestran placeholders controlados, no informacion inventada.

## 13. Dashboard general por rol/cargo

Se implemento logica en:

- `frontend/src/lib/dashboard.ts`

Perfiles contemplados:

- ADMIN / ADMIN_SISTEMA.
- ENCARGADO_ESTADISTICA / ESTADISTICA.
- DOCENTE.
- DISCENTE.
- JEFE_CARRERA / JEFATURA_CARRERA / JEFE_SUB_EJEC_CTR.
- JEFE_ACADEMICO / JEFATURA_ACADEMICA.
- JEFE_PEDAGOGICA / JEFE_SUB_PLAN_EVAL.

Las tarjetas del dashboard se construyen desde los permisos y enlaces definidos, apuntando a rutas actuales del backend cuando la funcionalidad aun no fue migrada a React.

Importante:

- El frontend oculta opciones no autorizadas.
- El backend sigue siendo la autoridad real de permisos.
- El discente no recibe acceso al kardex oficial institucional.

## 14. Componentes frontend base

Se crearon componentes reutilizables:

- `AppShell`
- `Sidebar`
- `Topbar`
- `PageHeader`
- `DashboardCard`
- `DashboardGrid`
- `DashboardSidePanel`
- `GeneralDashboard`
- `ProfilePanel`
- `RoleBadge`
- `StatusBadge`
- `EmptyState`
- `LoadingState`
- `ErrorMessage`
- `Button`
- `Card`
- `Input`
- componentes de branding/logos.

## 15. Ajustes visuales finales realizados

Durante la iteracion visual se realizaron ajustes adicionales:

- Pantalla de login mas cercana a la referencia institucional proporcionada.
- Eliminacion del logo/indicador de Next.js visible en demos locales.
- Responsividad del login y del portal.
- Menu de usuario superior con caja desplegable.
- Separacion y alineacion del panel derecho para dar mas espacio al centro.
- Banner inferior de carreras con solo logos, sin nombres visibles.
- Eliminacion del escudo EMI dentro del banner verde superior del dashboard.
- Homologacion visual de las paginas de modulos para evitar el estilo anterior.
- Separacion entre banner de modulo y tarjetas de opciones.
- Ajuste del banner inferior para que los logos de carreras se vean grandes sin circulo blanco.

## 16. Archivos principales modificados o creados

### Backend

- `backend/config/settings.py`
- `backend/config/urls.py`
- `backend/core/middleware.py`
- `backend/usuarios/api_urls.py`
- `backend/usuarios/api_views.py`
- `backend/usuarios/tests.py`

### Frontend

- `frontend/Dockerfile`
- `frontend/.dockerignore`
- `frontend/.env.example`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/next.config.ts`
- `frontend/tailwind.config.ts`
- `frontend/src/app/*`
- `frontend/src/components/*`
- `frontend/src/config/branding.ts`
- `frontend/src/lib/*`
- `frontend/public/brand/*`

### Infraestructura y documentacion

- `compose.yaml`
- `.env.example`
- `README.md`
- `docs/resumen_bloque10a_front_institucional_base.md`
- `docs/guia_actualizacion_bloque10a_frontend.md`

## 17. Pruebas y validaciones realizadas

Validaciones frontend ejecutadas despues de los ultimos ajustes:

```bash
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
```

Resultado:

- `npm run lint`: correcto.
- `npm run build`: correcto.

Validacion visual realizada en navegador:

- `/login` carga con diseno institucional.
- Login redirige al dashboard con usuario valido.
- `/dashboard` muestra layout institucional.
- Menu de usuario despliega opciones.
- Modulos laterales abren pantallas con estilo homologado.
- Panel derecho muestra placeholders para actividad/calendario/eventos.
- Banner inferior muestra logos de carreras.
- El escudo EMI ya no aparece dentro del banner verde superior.

Pendiente recomendado antes de integrar definitivamente a rama estable:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test
docker compose ps
```

## 18. Que queda pendiente para Bloque 10B o fases posteriores

### 18.1 Buscador superior

Estado actual:

- Se muestra como campo visual preparado.
- No ejecuta busqueda real todavia.

Pendiente:

- Definir entidades buscables por rol.
- Crear API de busqueda global o por modulo.
- Respetar permisos de backend por perfil.
- Mostrar resultados agrupados por tipo: usuarios, discentes, grupos, materias, actas, historial, etc.
- Agregar accesos rapidos desde resultados.

### 18.2 Campana de notificaciones

Estado actual:

- Se muestra icono de notificaciones preparado.
- No consume notificaciones reales.

Pendiente:

- Definir modelo/eventos de notificacion.
- Definir reglas por rol: actas pendientes, remisiones, validaciones, cambios de grupo, cierres de periodo, etc.
- Crear API de notificaciones.
- Marcar como leida/no leida.
- Definir retencion y auditoria.

### 18.3 Actividad reciente

Estado actual:

- Se muestra panel derecho con placeholder.
- No se inventan actividades.

Pendiente:

- Conectar con auditoria o bitacora real del sistema.
- Definir eventos visibles para cada usuario.
- Mostrar acciones recientes propias o institucionales segun rol.
- Filtrar por permisos.
- Considerar paginacion y detalle de evento.

### 18.4 Calendario institucional

Estado actual:

- Se muestra calendario visual del mes actual.
- No esta conectado a eventos academicos reales.

Pendiente:

- Definir fuente de calendario institucional.
- Crear modelo o endpoint de eventos.
- Asociar eventos a periodo escolar, carrera, grupo o rol.
- Mostrar cierres, aperturas, fechas de captura, validacion de actas, entregas, etc.
- Agregar navegacion por mes.

### 18.5 Eventos proximos

Estado actual:

- Se muestra espacio reservado.
- No hay eventos reales.

Pendiente:

- Conectar con calendario institucional.
- Mostrar eventos proximos filtrados por rol/cargo/carrera.
- Definir prioridad y estado.
- Permitir enlace al modulo correspondiente.

### 18.6 Mi perfil

Estado actual:

- Opcion visible en menu de usuario como funcionalidad futura.

Pendiente:

- Crear pantalla de perfil.
- Mostrar datos personales/institucionales.
- Mostrar rol, cargos vigentes, carrera, unidad, grado/empleo.
- Definir si el usuario puede actualizar algun dato o si sera solo lectura.

### 18.7 Accesos rapidos por uso real

Estado actual:

- Se muestran accesos disponibles por rol/cargo.
- El orden no depende aun de uso real.

Pendiente:

- Registrar accesos recientes/frecuentes.
- Ordenar tarjetas por uso del usuario.
- Permitir fijar favoritos si se decide.

### 18.8 Migracion progresiva de pantallas backend al portal

Estado actual:

- Muchas tarjetas enlazan a rutas existentes del backend Django.

Pendiente:

- Migrar progresivamente vistas de consulta y operacion al portal Next.js.
- Mantener Django Admin como respaldo tecnico.
- No duplicar reglas; las operaciones deben seguir validando en backend.

### 18.9 Reportes formales

Estado actual:

- No se implemento Bloque 9.
- No se implementaron PDF ni Excel en el portal.

Pendiente:

- Bloque 9 debe definir reportes oficiales.
- Exportaciones deben respetar reglas institucionales y permisos.

## 19. Consideraciones para despliegue futuro

En desarrollo local se usa HTTP, por eso:

- `SESSION_COOKIE_SECURE=False`
- `CSRF_COOKIE_SECURE=False`
- `SECURE_SSL_REDIRECT=False`
- `SECURE_HSTS_SECONDS=0`

En HTTPS real se debera evaluar:

- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_SSL_REDIRECT=True`
- HSTS solo cuando HTTPS sea estable.
- Cookies `__Host-*` solo si se cumplen condiciones: Secure, Path=/ y sin Domain.

## 20. Cierre funcional de Bloque 10A

El Bloque 10A deja lista la base visual y tecnica del portal institucional moderno:

- frontend Next.js creado;
- Docker actualizado con servicio frontend;
- login institucional conectado con Django;
- dashboard general por rol/cargo;
- modulos iniciales por perfil;
- branding institucional y logos por carrera;
- seguridad base con sesiones Django, cookies y CSRF;
- placeholders claros para funciones futuras;
- backend y Django Admin conservados.

El siguiente paso natural es cerrar commit/push de esta rama y luego avanzar en Bloque 10B con datos reales para busqueda, notificaciones, actividad reciente, calendario y eventos.
