# Resumen Bloque 10B - Portal con datos vivos

## Objetivo

El Bloque 10B convierte el portal institucional del Bloque 10A en una interfaz conectada a datos reales del backend Django. El objetivo es que el dashboard, la campana de notificaciones, la actividad reciente, el calendario, los eventos proximos, el buscador superior, el perfil y los accesos rapidos funcionen con informacion autorizada por rol/cargo.

Django sigue siendo la fuente de verdad para reglas de negocio, permisos y operacion academica. El frontend Next.js solo consume APIs HTTP/JSON y no duplica reglas academicas.

## Alcance funcional implementado

- Dashboard con tarjetas calculadas por perfil principal.
- Notificaciones por usuario con lectura individual y lectura masiva.
- Actividad reciente derivada de actas, capturas preliminares y movimientos academicos.
- Calendario institucional con eventos filtrados por visibilidad, rol/cargo, carrera y grupo.
- Eventos proximos derivados del calendario institucional.
- Buscador superior con resultados agrupados y permisos por perfil.
- Perfil del usuario autenticado en solo lectura.
- Accesos rapidos persistentes por usuario y fallback por rol/cargo.
- Estados vacios controlados cuando no existen registros.

## Archivos backend principales

- `backend/core/models.py`
- `backend/core/admin.py`
- `backend/core/api_views.py`
- `backend/core/api_urls.py`
- `backend/core/portal_services.py`
- `backend/core/notification_services.py`
- `backend/core/tests.py`
- `backend/core/migrations/0001_initial.py`
- `backend/config/urls.py`

## Modelos creados

### NotificacionUsuario

Representa avisos dirigidos a un usuario del portal.

Campos principales:

- `usuario`
- `tipo`
- `titulo`
- `mensaje`
- `url_destino`
- `prioridad`
- `leida`
- `creada_en`
- `leida_en`

Reglas:

- La notificacion no se borra al marcarla como leida.
- Cada usuario consulta solo sus propias notificaciones.
- Se registra en Django Admin para soporte.

### EventoCalendarioInstitucional

Representa eventos visibles en calendario institucional.

Campos principales:

- `titulo`
- `descripcion`
- `tipo_evento`
- `fecha_inicio`
- `fecha_fin`
- `periodo`
- `carrera`
- `grupo`
- `roles_destino`
- `url_destino`
- `visible`
- `creado_por`
- `creado_en`

Reglas:

- `fecha_fin` no puede ser anterior a `fecha_inicio`.
- Si el evento esta ligado a grupo, debe coincidir con el periodo y carrera configurados.
- La visibilidad se filtra por contexto del usuario.

### AccesoRapidoUsuario

Representa favoritos o accesos rapidos personalizados del usuario.

Campos principales:

- `usuario`
- `etiqueta`
- `url`
- `icono`
- `orden`
- `activo`
- `creado_en`

Reglas:

- Evita duplicar un acceso activo con la misma URL para el mismo usuario.
- Si no existen favoritos, el portal usa accesos rapidos por rol/cargo.

## Servicios creados

### portal_context

Construye el contexto de seguridad del portal para un usuario autenticado:

- roles Django Groups;
- cargos vigentes;
- perfil principal;
- carreras del ambito del usuario;
- grupos relacionados;
- perfiles de discente activos.

Este contexto se usa para filtrar dashboard, busqueda, calendario, actas, asignaciones e inscripciones.

### dashboard_resumen

Devuelve tarjetas con informacion real disponible segun perfil:

- Admin: usuarios activos, cargos vigentes, periodos activos y notificaciones.
- Docente: asignaciones activas y estados de actas propias.
- Discente: asignaturas activas, actas publicadas, conformidades pendientes e historial propio.
- Jefatura de carrera: actas por validar, grupos activos, asignaciones docentes y periodos.
- Jefatura academica: actas por formalizar, actas formalizadas y periodos.
- Estadistica: periodos, actas vivas, cierres registrados y kárdex institucional.

### actividad_reciente

Consolida eventos recientes desde fuentes existentes:

- actas visibles;
- capturas preliminares visibles;
- movimientos academicos visibles.

No inventa actividad. Si no hay registros, el frontend muestra estado vacio.

### eventos_mes y eventos_proximos

Filtran `EventoCalendarioInstitucional` con estas reglas:

- Solo eventos `visible=True`.
- Admin, estadistica y jefaturas de consulta amplia tienen visibilidad extendida.
- Discente y docente reciben eventos generales o aplicables por rol/carrera/grupo.
- Jefatura de carrera recibe eventos de su ambito cuando se puede inferir.

### busqueda

Devuelve resultados agrupados por tipo y filtrados por permisos:

- Usuarios.
- Discentes.
- Grupos.
- Programas de asignatura.
- Actas.
- Periodos.
- Kárdex institucional solo para perfiles autorizados.

El discente no recibe kárdex oficial ni datos de otros discentes.

### Servicios de notificacion

Se agregan servicios mínimos para preparar integraciones futuras:

- `crear_notificacion_usuario`.
- `notificar_acta_publicada_para_discentes`.

Estos servicios permiten que bloques posteriores conecten eventos reales sin duplicar logica en el frontend.

## Endpoints creados

### Dashboard

- `GET /api/dashboard/resumen/`
- `GET /api/dashboard/actividad-reciente/`

### Notificaciones

- `GET /api/notificaciones/`
- `POST /api/notificaciones/<id>/leer/`
- `POST /api/notificaciones/leer-todas/`

### Calendario

- `GET /api/calendario/mes/?year=YYYY&month=M`
- `GET /api/calendario/proximos/`

### Busqueda

- `GET /api/busqueda/?q=texto`

### Perfil

- `GET /api/perfil/me/`

### Accesos rapidos

- `GET /api/accesos-rapidos/`
- `POST /api/accesos-rapidos/crear/`
- `DELETE /api/accesos-rapidos/<id>/`

## Cambios frontend

### Topbar

Se integra:

- buscador superior con minimo de 2 caracteres;
- resultados agrupados;
- contador de notificaciones no leidas;
- menu desplegable de notificaciones;
- marcar una notificacion como leida;
- marcar todas como leidas;
- enlace real a `/perfil` desde el menu de usuario.

### DashboardSidePanel

Se reemplazan placeholders por APIs:

- actividad reciente desde `/api/dashboard/actividad-reciente/`;
- calendario mensual desde `/api/calendario/mes/`;
- eventos proximos desde `/api/calendario/proximos/`.

Cuando no hay datos, muestra estados vacios institucionales.

### GeneralDashboard

Se integra `/api/dashboard/resumen/` para mostrar tarjetas vivas y accesos rapidos reales. Si el backend no devuelve datos, mantiene estado vacio claro o fallback por rol/cargo.

### Perfil

Se crea `/perfil` con informacion de solo lectura:

- nombre completo;
- usuario;
- correo;
- estado de cuenta;
- grado/empleo;
- rol principal;
- roles;
- cargos vigentes;
- carreras asociadas.

No permite editar datos personales, cambiar contrasena ni modificar cargos.

### API frontend

Se extiende `frontend/src/lib/api.ts` con funciones para:

- resumen del dashboard;
- actividad reciente;
- notificaciones;
- calendario;
- eventos proximos;
- busqueda;
- perfil;
- accesos rapidos.

## Reglas de seguridad

- Todas las APIs nuevas requieren autenticacion.
- Las mutaciones usan CSRF.
- Se mantienen sesiones Django y cookies.
- No se implementa JWT.
- No se usa `localStorage` para tokens.
- No se expone kárdex oficial a discentes.
- No se confia solo en frontend para ocultar elementos.
- El backend filtra por rol/cargo y ambito.

## Datos vivos y estados vacios

El portal no inventa datos. Cuando no existen registros, se muestra un mensaje controlado:

- actividad reciente vacia;
- calendario sin eventos;
- eventos proximos sin registros;
- busqueda sin resultados para el perfil;
- dashboard sin datos vivos.

## Validaciones ejecutadas

Comandos ejecutados dentro de Docker:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test core
docker compose exec -T backend python manage.py test
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
docker compose exec -T backend python manage.py migrate
```

Resultados:

- `manage.py check`: OK.
- `makemigrations --check`: OK, sin cambios pendientes.
- `manage.py test core`: 7 pruebas OK.
- `manage.py test`: 300 pruebas OK.
- `npm run lint`: OK.
- `npm run build`: OK.
- `migrate`: `core.0001_initial` aplicado correctamente en la base local Docker.

## Fuera de alcance

No se implementa en este bloque:

- Bloque 9.
- PDF.
- Excel.
- reportes formales.
- WebSockets o tiempo real.
- JWT.
- MFA/OTP.
- IdP externo.
- migracion completa de captura de calificaciones a React.
- migracion completa de actas a React.
- migracion completa de kárdex a React.
- cambio de reglas academicas.
- eliminacion de Django Admin.
- eliminacion de vistas Django existentes.

## Pendientes para 10C

- Conectar senales completas desde actas, cierre/apertura de periodo y trayectoria para generar notificaciones automaticas.
- Crear pantallas operativas para administrar calendario institucional desde el portal.
- Permitir que el usuario gestione favoritos visualmente desde Next.js.
- Crear rutas React propias para resultados de busqueda conforme se migren modulos funcionales.
- Incorporar una bitacora transversal formal si se requiere actividad reciente auditada a nivel institucional.
- Mejorar filtros por carrera/unidad cuando se consolide el ambito multi-carrera.

## Criterio de cierre

El Bloque 10B queda funcionalmente cerrado porque:

- el dashboard consume datos del backend;
- la campana de notificaciones funciona por usuario;
- la actividad reciente usa fuentes reales;
- calendario y eventos proximos consumen modelo institucional;
- el buscador respeta permisos basicos;
- el perfil existe en solo lectura;
- los accesos rapidos tienen persistencia inicial;
- no se rompio login/logout;
- Django Admin y vistas actuales se conservan;
- backend y frontend validan correctamente.
