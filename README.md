# Sistema de Control Académico EMI - ICI

Repositorio base del **MVP del Sistema de Control Académico** para la **Escuela Militar de Ingeniería**, acotado en esta fase a la carrera de **Ingeniería en Computación e Informática (ICI)**.

## Objetivo del proyecto

Construir un sistema web para intranet que centralice:

- gestión de calificaciones;
- operación y validación de actas;
- historial académico;
- kárdex oficial derivado;
- reportes operativos y académicos;
- trazabilidad y auditoría de eventos críticos.

El proyecto sustituye el flujo actual basado en hojas de cálculo, documentos impresos y validaciones manuales por un proceso digital controlado por roles.

## Alcance del MVP

Esta primera versión contempla:

- una sola carrera: **ICI**;
- autenticación **local** del sistema;
- operación en **intranet**;
- gestión de periodos, planes, generaciones, grupos, materias y esquemas de evaluación;
- materias con **1, 2 o 3 parciales**, según configuración académica;
- actas por corte y acta final;
- validación jerárquica del acta;
- historial académico completo;
- kárdex oficial como **vista derivada**;
- auditoría **append-only**;
- exportaciones documentales (PDF / Excel) dentro del alcance del MVP.

## Reglas base del dominio

Estas reglas no deben romperse durante el desarrollo:

- La autenticación del MVP es **local al sistema**.
- El MVP **no** implementa OTP/MFA en esta fase.
- La validación base del acta sigue el flujo:
  - docente
  - jefatura de carrera
  - jefatura académica
- Las suplencias o cargos accidentales deben quedar registradas con trazabilidad.
- El docente pierde edición directa del acta al momento de remitirla a validación superior.
- El acta queda en **solo lectura** tras la validación final.
- La fórmula de cálculo final es **45% parciales + 55% evaluación final** como valor por omisión, parametrizable por materia autorizada.
- En materias de **1 parcial**, el examen final es **obligatorio**; no hay exención.
- La exención solo aplica cuando la materia lo permite y tiene **2 o 3 parciales**.
- La conformidad del discente es **informativa y no bloqueante**.
- La marca **EE** corresponde al resultado aprobatorio por extraordinario; no es un estatus del discente.
- El **kárdex oficial** no es una tabla transaccional principal; se construye a partir del historial consolidado.
- La auditoría debe registrar eventos críticos sin sobrescribir silenciosamente la evidencia previa.

## Línea base documental cerrada

Antes de programar, este repositorio debe considerar como baseline documental al menos los siguientes paquetes ya cerrados:

1. Contexto funcional y operativo.
2. Metodología de desarrollo.
3. Requerimientos funcionales, no funcionales y reglas de negocio.
4. Casos de uso.
5. Diagramas UML y de estados.
6. Diagrama entidad-relación.
7. Diagrama de clases.
8. Arquitectura lógica base.

## Estado actual del proyecto

El análisis y diseño de negocio ya están definidos. La siguiente etapa técnica es:

1. cerrar el **stack tecnológico**;
2. definir la **arquitectura de despliegue**;
3. preparar el entorno colaborativo y el esqueleto del proyecto;
4. comenzar la construcción por incrementos.

## Estrategia de construcción sugerida

Se recomienda avanzar por incrementos funcionales:

1. **Calificaciones**
   - catálogos mínimos
   - esquema de evaluación
   - captura y cálculo
2. **Actas**
   - borradores
   - publicación
   - conformidad del discente
   - validación jerárquica
   - cierre
3. **Trayectoria**
   - historial
   - extraordinario
   - baja temporal / reingreso
   - kárdex
   - reportes y auditoría

## Herramientas de colaboración

### Ya definidas

- **GitHub** para repositorio remoto privado.
- **Git** para control de versiones.
- **Visual Studio Code** como IDE.
- **Codex para VS Code** como apoyo de desarrollo.
- **Docker Desktop** como entorno base de contenedores para desarrollo del MVP.

### Pendientes de cierre técnico

- stack de aplicación definitivo;
- arquitectura tecnológica;
- arquitectura de despliegue;
- configuración inicial de contenedores de desarrollo.

## Flujo de trabajo Git recomendado

### Ramas

- `main` → rama estable
- `develop` → integración
- `feature/<nombre>` → desarrollo de funcionalidades
- `fix/<nombre>` → correcciones puntuales

### Reglas mínimas

- No hacer commits directos a `main`.
- Trabajar siempre desde una rama de funcionalidad o corrección.
- Hacer commits pequeños y con mensaje claro.
- Integrar cambios por **pull request**.
- Mantener sincronizada la rama local con `develop`.

### Ejemplo de nombres de rama

- `feature/backend-base`
- `feature/catalogos-academicos`
- `feature/esquema-evaluacion`
- `feature/actas-flujo`
- `feature/historial-kardex`

## Estructura sugerida del repositorio

```text
sca-emi-ici/
├── README.md
├── docs/
│   ├── 00_baseline/
│   ├── 01_metodologia/
│   ├── 02_requerimientos/
│   ├── 03_casos_uso/
│   ├── 04_uml_estados/
│   ├── 05_er/
│   ├── 06_clases/
│   ├── 07_arquitectura_logica/
│   └── 08_stack_y_despliegue/
├── backend/
├── frontend/
├── infra/
│   ├── docker/
│   └── scripts/
├── tests/
├── .gitignore
├── .editorconfig
└── compose.yaml
```

> Nota: `backend/`, `frontend/`, `infra/` y `compose.yaml` pueden ajustarse cuando se cierre el stack de aplicación.

## Requisitos mínimos para desarrollo colaborativo

Cada integrante debe tener instalado:

- Git
- Visual Studio Code
- Extensión de Codex para VS Code
- Docker Desktop
- acceso al repositorio privado en GitHub

## Primeros pasos sugeridos

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd sca-emi-ici
```

### 2. Configurar identidad de Git

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu_correo@ejemplo.com"
```

### 3. Crear y usar una rama de trabajo

```bash
git checkout -b feature/nombre-funcionalidad
```

### 4. Confirmar cambios y subirlos

```bash
git add .
git commit -m "feat: descripcion breve del cambio"
git push -u origin feature/nombre-funcionalidad
```

### 5. Abrir pull request

La integración debe hacerse por GitHub mediante revisión y aprobación.

## Convenciones recomendadas

### Mensajes de commit

Usar un formato simple:

- `feat:` nueva funcionalidad
- `fix:` corrección
- `docs:` cambios en documentación
- `refactor:` reorganización sin cambio funcional
- `test:` pruebas
- `chore:` tareas de soporte

Ejemplos:

- `feat: agrega estructura inicial de backend`
- `docs: agrega baseline documental al repositorio`
- `fix: corrige validacion de esquema de evaluacion`

### Documentación

- Toda decisión importante debe registrarse en `docs/`.
- No dejar reglas de negocio solo en conversaciones o comentarios de código.
- Si un cambio afecta el baseline funcional, debe reflejarse en la documentación correspondiente.

## Criterios de calidad mínimos

Antes de integrar una funcionalidad a `develop`, debería cumplir al menos con esto:

- no rompe reglas de negocio ya cerradas;
- mantiene coherencia con el modelo de datos y el diagrama de clases;
- tiene nombre claro y estructura comprensible;
- incluye actualización documental cuando aplica;
- no introduce dependencias nuevas sin justificación.

## Decisiones tecnológicas pendientes

Este repositorio todavía no fija de forma definitiva:

- framework backend;
- estrategia de frontend;
- motor final de base de datos para desarrollo y despliegue;
- esquema final de despliegue en intranet.

### Rutas candidatas a evaluar

#### Ruta A
- Backend y web administrativa dentro de un mismo framework.
- Menor complejidad inicial.
- Mayor velocidad de construcción.

#### Ruta B
- Backend desacoplado + frontend moderno independiente.
- Mejor experiencia visual y flexibilidad.
- Mayor complejidad de integración.

## Confidencialidad y uso

Este repositorio está orientado a trabajo académico/técnico del **Sistema de Control Académico EMI – ICI**. Su contenido debe tratarse como **privado** y no debe exponerse públicamente sin autorización expresa.

## Siguiente paso inmediato recomendado

1. Crear el repositorio privado.
2. Configurar Git en ambos equipos.
3. Subir este `README.md` y el baseline documental.
4. Definir la estructura inicial del repo.
5. Cerrar el stack de aplicación y la arquitectura de despliegue.
6. Comenzar el desarrollo del primer incremento funcional.

---

**Estado de este README:** versión inicial para arranque del repositorio y trabajo colaborativo.

Proyecto actualizado el 15/04/2026 Clemeente

## Arranque del backend base

### Infraestructura incluida

- `compose.yaml` con servicios `db` (PostgreSQL 16) y `backend` (Django).
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/.dockerignore`
- `.env.example`

### Configuración local

```bash
cp .env.example .env
```

### Levantar servicios y migraciones

```bash
docker compose up -d db
docker compose build backend
docker compose run --rm backend python manage.py makemigrations
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
docker compose up -d backend
```

### Pruebas rápidas

- Healthcheck del backend: `http://localhost:8000/health/`
- Admin de Django: `http://localhost:8000/admin/`
- PostgreSQL local: `localhost:5433`

## Apps base del dominio creadas

- `usuarios` (modelo de usuario personalizado con `AUTH_USER_MODEL`)
- `core`
- `catalogos`
- `relaciones`
- `evaluacion`
- `actas`
- `trayectoria`
- `reportes`
- `auditoria`

## Dev Container (opcional, recomendado)

El repositorio incluye `.devcontainer/devcontainer.json` para abrir VS Code en un entorno reproducible usando el servicio `backend` definido en `compose.yaml`.

En VS Code:

1. Abrir la paleta de comandos.
2. Ejecutar `Dev Containers: Reopen in Container`.

## Bloque 1

Implementacion inicial de autenticacion local, roles y base administrativa del backend Django.

### Incluye

- Modelo `Usuario` personalizado (basado en `AbstractUser`) con campos:
  - `nombre_completo`
  - `correo`
  - `telefono`
  - `estado_cuenta`
- Soporte de roles mediante `django.contrib.auth.models.Group` con creacion automatica de roles base:
  - `ADMIN`
  - `ADMIN_SISTEMA`
  - `JEFE_CARRERA`
  - `JEFATURA_CARRERA`
  - `JEFE_ACADEMICO`
  - `JEFATURA_ACADEMICA`
  - `JEFE_PEDAGOGICA`
  - `ENCARGADO_ESTADISTICA`
  - `ESTADISTICA`
  - `DOCENTE`
  - `DISCENTE`
- Asociacion automatica de permisos Django por rol durante `post_migrate`:
  - Administracion tecnica recibe permisos globales.
  - Jefatura de Carrera opera `AsignacionDocente` y consulta catalogos/carga academica.
  - Estadistica consulta carga academica y opera movimientos academicos.
  - Docente y Discente reciben permisos de consulta acordes a sus vistas temporales.
- Modelo `AsignacionCargo` para cargos institucionales vigentes con:
  - `usuario`
  - `cargo_codigo`
  - `tipo_designacion`
  - `vigente_desde`
  - `vigente_hasta`
  - `activo`
- Formularios y vistas minimas:
  - `login` (`/login/`)
  - `logout` (`/logout/`)
  - `dashboard` (`/dashboard/`)
- Dashboard restringido a usuarios autenticados.
- Endpoint de salud JSON: `/health/`.

### Admin

Se registran en admin:

- `Usuario`
- `AsignacionCargo`

### Migraciones

Ejecutar:

```bash
docker compose run --rm backend python manage.py makemigrations usuarios
docker compose run --rm backend python manage.py migrate
```

## Bloque 2

Implementacion de catalogos academicos minimos para sostener la estructura base del sistema desde admin.

### Modelos creados

- `Carrera`
- `PlanEstudios`
- `Generacion`
- `PeriodoEscolar`
- `GrupoAcademico`
- `Materia`
- `MateriaPlan`

### Relaciones del dominio (Bloque 2)

- `PlanEstudios` pertenece a `Carrera`.
- `Generacion` pertenece a `PlanEstudios`.
- `GrupoAcademico` pertenece a `Generacion` y `PeriodoEscolar`.
- `MateriaPlan` relaciona `Materia` con `PlanEstudios`.

### Campos base incorporados

Se incluyeron campos razonables para:

- identificacion (`clave`, `nombre`)
- vigencia (`vigente_desde`, `vigente_hasta`)
- estado (`estado`)
- asociaciones entre entidades academicas

### Admin

Todos los modelos de Bloque 2 se registraron en Django Admin para alta y mantenimiento:

- `Carrera`
- `PlanEstudios`
- `Generacion`
- `PeriodoEscolar`
- `GrupoAcademico`
- `Materia`
- `MateriaPlan`

### Migraciones

Ejecutar:

```bash
docker compose run --rm backend python manage.py makemigrations catalogos
docker compose run --rm backend python manage.py migrate
```

### Corrección Bloque 2

Se alineo el Bloque 2 al baseline academico aprobado con estos ajustes puntuales:

- `PeriodoEscolar` ahora expone `clave`, `anio_escolar`, `semestre_operativo`, `fecha_inicio`, `fecha_fin`, `estado`.
- `GrupoAcademico` elimina `turno` y conserva estructura con `clave_grupo`, `generacion`, `periodo`, `semestre_numero` (con `cupo_maximo` opcional).
- `MateriaPlan` queda explicita con `plan_estudios`, `materia`, `semestre_numero`, `anio_escolar_numero`, `obligatoria`.

## Bloque 3

Implementacion del esquema de evaluacion y validaciones academicas, sin adelantar actas, trayectoria ni reportes.

### Modelos creados

- `EsquemaEvaluacion`
- `ComponenteEvaluacion`

### Reglas implementadas

- Se permiten esquemas con `1`, `2` o `3` parciales.
- Exencion solo permitida para materias con `2` o `3` parciales (`num_parciales=1` la bloquea).
- En materias de `1` parcial, el examen final es obligatorio.
- Formula base configurable por materia-plan con `peso_parciales` y `peso_final` (45/55 por omision).
- La suma `peso_parciales + peso_final` debe ser exactamente `100`.
- Cada corte (`P1`, `P2`, `P3`, `FINAL`) valida suma de componentes igual a `100`.

### Admin

Se registran ambos modelos en Django admin con soporte para edicion de componentes por esquema:

- `EsquemaEvaluacion`
- `ComponenteEvaluacion`

### Tests minimos incluidos

- Permitir esquemas de 1, 2 y 3 parciales.
- Impedir exencion cuando `num_parciales = 1`.
- Validar sumas de porcentajes por corte iguales a 100.
- Validar pesos 45/55 por omision y persistencia configurable.

### Migraciones

Ejecutar:

```bash
docker compose run --rm backend python manage.py makemigrations evaluacion
docker compose run --rm backend python manage.py migrate
```

### Prueba de sincronización: rol Discente

Se agregó el rol base DISCENTE al sistema de roles (Groups) mediante seed seguro y migración de datos en usuarios, sin cambiar lógica operativa del negocio.

## Bloque 4

Implementacion de relaciones academicas operativas, sin adelantar actas, trayectoria ni reportes.

### Modelos creados

- `Discente`
- `AdscripcionGrupo`
- `AsignacionDocente`
- `InscripcionMateria`
- `MovimientoAcademico`

### Reglas implementadas

- `Discente` se vincula con `Usuario`, `PlanEstudios` y `Antiguedad` (`Generacion` en equivalencia documental), y exige usuario activo con rol `DISCENTE`.
- `AdscripcionGrupo` registra la pertenencia vigente del discente a un grupo academico.
- `AsignacionDocente` vincula docente con rol `DOCENTE`, grupo academico y programa de asignatura; el periodo se deriva desde `GrupoAcademico`.
- `InscripcionMateria` se muestra como `Inscripción a asignatura` y representa el registro interno generado desde la asignacion docente.
- `MovimientoAcademico` conserva cambios de grupo y altas/bajas extemporaneas sin borrar evidencia previa.
- Las relaciones filtran y validan entidades activas.
- Se bloquean asignaciones docentes activas duplicadas para el mismo grupo y programa.
- Se bloquean inscripciones activas duplicadas para el mismo discente y asignacion docente.
- Los cambios de grupo exigen grupo destino.
- Las altas y bajas extemporaneas exigen observaciones minimas.

### Bloque 4 – generación automática de carga académica por grupo

El discente no selecciona materias ni profesor. La escuela registra la adscripcion del discente al grupo y asigna un programa de asignatura a un docente para ese grupo.

Al crear o activar una `AsignacionDocente`, el sistema sincroniza automaticamente las `InscripcionMateria` necesarias para los discentes vigentes del grupo. La sincronizacion es idempotente: si la inscripcion activa ya existe para el discente y la asignacion docente, no se duplica.

Tambien existe una accion administrativa en `AsignacionDocente` para sincronizar manualmente la carga academica cuando se agregan discentes al grupo despues de crear la asignacion.

### Bloque 4: AsignacionDocente operada por Jefatura de Carrera

`AsignacionDocente` queda operada por Jefatura de Carrera (`JEFE_CARRERA` / `JEFATURA_CARRERA`) o por administracion tecnica/superusuario. Estadistica (`ENCARGADO_ESTADISTICA` / `ESTADISTICA`) conserva acceso de consulta y consolidacion, pero no crea ni modifica asignaciones docentes en el flujo ordinario.

### Vistas minimas

Se agregan vistas autenticadas para listar y crear:

- `AsignacionDocente`: `/relaciones/asignaciones-docentes/`
- `MovimientoAcademico`: `/relaciones/movimientos-academicos/`

Las `Inscripciones a asignatura` se listan en `/relaciones/inscripciones-materia/`, pero su creacion ordinaria se genera automaticamente desde `AsignacionDocente` y `AdscripcionGrupo`.

El acceso queda restringido a superusuarios/staff, rol `ADMIN_SISTEMA`, rol `ESTADISTICA` o cargo activo equivalente.

### Admin

Se registran en Django admin:

- `Discente`
- `AdscripcionGrupo`
- `AsignacionDocente`
- `InscripcionMateria`
- `MovimientoAcademico`

### Tests minimos incluidos

- Validaciones de entidades activas.
- Validaciones de roles `DISCENTE` y `DOCENTE`.
- Derivacion de periodo desde grupo academico.
- Duplicados activos de asignacion docente e inscripcion.
- Generacion automatica e idempotente de inscripciones a asignatura.
- Reglas de movimientos academicos.
- Permisos de vistas para anonimo, usuario sin rol y usuario/cargo de estadistica.

### Migraciones

Ejecutar:

```bash
docker compose run --rm backend python manage.py makemigrations relaciones
docker compose run --rm backend python manage.py migrate
```

## Bloque 4.5 – Front temporal de validación por rol

Se agrego un front temporal con Django templates para validar permisos, datos y flujos de los Bloques 1, 2, 3 y 4 sin depender solo de Django Admin.

### Vistas agregadas

- Dashboard por rol/cargo: `/dashboard/`
- Discente - Mi carga academica: `/validacion/discente/carga/`
- Docente - Mis asignaciones: `/validacion/docente/asignaciones/`
- Jefatura de carrera - Asignaciones docentes: `/validacion/jefatura/asignaciones-docentes/`
- Estadistica - Carga academica y movimientos: `/validacion/estadistica/carga/`
- Administrador - enlaces tecnicos: `/validacion/admin/tecnico/`

### Reglas de acceso

- Todas las vistas requieren autenticacion.
- El discente solo consulta su carga academica.
- El docente solo consulta sus asignaciones y discentes asociados.
- Jefatura de Carrera opera `AsignacionDocente` y puede sincronizar carga academica del grupo.
- Estadistica consulta carga academica y movimientos, sin crear ni modificar asignaciones docentes.
- Superusuario conserva acceso tecnico completo.

Este frente es temporal y no reemplaza el frontend final del sistema.

## Bloque 5 - Captura básica y cálculo académico preliminar

Se implementa la captura preliminar de calificaciones para validar el cálculo académico antes de construir el flujo formal de actas.

### Qué se implementó

- Modelo `CapturaCalificacionPreliminar` para registrar valores por `InscripcionMateria`, `ComponenteEvaluacion`, corte académico, usuario capturador y fecha de actualización.
- Servicio `ServicioCalculoAcademico` para calcular resultado por corte, promedio de parciales, exención preliminar, evaluación final, resultado final preliminar y estado preliminar.
- Sustitución del componente de evaluación final por promedio de parciales cuando la exención preliminar aplica.
- Vistas simples con Django templates para captura por corte y resumen de cálculo por asignación docente.
- Registro técnico de capturas preliminares en Django Admin.

### Rutas nuevas

- `GET/POST /evaluacion/docente/asignaciones/<id>/captura/<corte>/`
- `GET /evaluacion/docente/asignaciones/<id>/resumen/`

Desde `/validacion/docente/asignaciones/` se enlazan las acciones de captura y resumen.

### Reglas principales

- La escala válida de captura es 0.0 a 10.0.
- Las materias pueden tener 1, 2 o 3 parciales.
- Materias con 1 parcial no exentan examen final.
- La exención preliminar solo aplica si la materia la permite, tiene 2 o 3 parciales, el promedio de parciales es al menos 9.0 y existe componente de examen en el corte FINAL, mostrado al usuario como evaluación final.
- La fórmula preliminar usa los pesos configurados en `EsquemaEvaluacion`; por omisión se conserva 45/55.
- El resultado final preliminar se muestra redondeado a un decimal.

### Fuera de este bloque

No se crean ni actualizan todavía `Acta`, `DetalleActa`, calificaciones oficiales de acta, conformidad de discente, validación de acta, extraordinarios, historial académico, kárdex, reportes formales ni exportaciones PDF/Excel.

Tampoco se actualizan automáticamente los campos oficiales de `InscripcionMateria`:

- `calificacion_final`
- `codigo_resultado_oficial`
- `codigo_marca`
- `cerrado_en`

### Cómo probar

1. Entrar como docente asignado.
2. Abrir `Mis asignaciones`.
3. Usar `Capturar` para registrar valores por corte.
4. Usar `Resumen` para revisar promedio de parciales, exención, evaluación final, resultado final preliminar y estado preliminar.

Validaciones recomendadas:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py test evaluacion
```

## Bloque 6 - Gestión formal de actas

Se implementa la gestión formal de actas tomando como base la captura preliminar y el servicio de cálculo académico del Bloque 5.

El Bloque 6 no convierte `CapturaCalificacionPreliminar` en acta oficial. La captura preliminar sigue siendo insumo de trabajo del docente, mientras que el acta conserva sus propios registros, estado y snapshots mínimos.

### Modelos creados

- `Acta`: entidad principal del flujo formal por asignación docente y corte académico.
- `DetalleActa`: fila del acta por cada inscripción a asignatura.
- `CalificacionComponente`: snapshot de los componentes usados en cada detalle.
- `ConformidadDiscente`: acuse o conformidad informativa del discente.
- `ValidacionActa`: bitácora de publicación, remisión, validación y formalización.

### Estados del acta

- `BORRADOR_DOCENTE`
- `PUBLICADO_DISCENTE`
- `REMITIDO_JEFATURA_CARRERA`
- `VALIDADO_JEFATURA_CARRERA`
- `FORMALIZADO_JEFATURA_ACADEMICA`
- `ARCHIVADO`

En `BORRADOR_DOCENTE` el docente puede regenerar el acta desde capturas preliminares. Después de publicar, remitir, validar, formalizar o archivar, el backend impide regenerar el acta desde la captura preliminar.

### Snapshot mínimo

El acta guarda evidencia para no depender ciegamente de cambios futuros del esquema vivo:

- versión del esquema;
- peso de parciales;
- peso final;
- umbral de exención;
- nombre del componente;
- porcentaje del componente;
- si el componente era examen;
- valor capturado;
- valor calculado;
- marca de sustitución por exención.

### Rutas principales

- `GET /evaluacion/actas/docente/`
- `POST /evaluacion/docente/asignaciones/<id>/actas/<corte>/crear-borrador/`
- `GET /evaluacion/actas/<id>/`
- `POST /evaluacion/actas/<id>/regenerar/`
- `POST /evaluacion/actas/<id>/publicar/`
- `POST /evaluacion/actas/<id>/remitir/`
- `GET /evaluacion/actas/discente/`
- `GET/POST /evaluacion/actas/discente/detalle/<id>/`
- `GET /evaluacion/actas/jefatura-carrera/pendientes/`
- `POST /evaluacion/actas/<id>/validar-carrera/`
- `GET /evaluacion/actas/jefatura-academica/pendientes/`
- `POST /evaluacion/actas/<id>/formalizar/`
- `GET /evaluacion/actas/estadistica/`

### Reglas principales

- No se permite duplicar actas activas para la misma asignación docente y corte.
- El docente crea, publica y remite sus propias actas.
- El discente solo consulta su detalle publicado y registra conformidad informativa.
- La conformidad del discente no bloquea el flujo.
- Jefatura de carrera valida actas remitidas de su carrera/unidad.
- Jefatura académica formaliza actas previamente validadas y consulta actas ya formalizadas en modo de solo lectura.
- Estadística consulta estados, pero no firma por jefaturas.
- Superusuario conserva soporte técnico.
- Solo al formalizar el acta `FINAL` se actualizan campos oficiales de `InscripcionMateria`.
- Las actas parciales no actualizan `calificacion_final` definitiva.

### Fuera de este bloque

No se implementan todavía:

- historial académico completo;
- kárdex;
- extraordinarios;
- reportes formales;
- exportación PDF/Excel;
- rectificación posterior al cierre;
- MFA/OTP.

### Cómo probar el flujo mínimo

1. Capturar calificaciones preliminares como docente.
2. Crear borrador de acta desde la asignación docente y corte.
3. Publicar el acta para discentes.
4. Registrar conformidad informativa como discente.
5. Remitir el acta a jefatura de carrera.
6. Validar como jefe de subsección de Ejecución y Control/Jefe de carrera.
7. Formalizar como jefatura académica.
8. Consultar el acta en la sección de actas formalizadas de jefatura académica.

Validaciones recomendadas:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py test evaluacion
docker compose exec -T backend python manage.py test
```

## Bloque 7 - Historial académico y trayectoria

Se implementa el módulo inicial de historial académico y trayectoria del discente usando como base resultados oficiales ya consolidados. La fuente oficial del historial son las inscripciones con acta `FINAL` formalizada; las capturas preliminares y actas en borrador no se consideran historial oficial.

### Modelos agregados

- `CatalogoSituacionAcademica`
- `CatalogoResultadoAcademico`
- `EventoSituacionAcademica`
- `Extraordinario`

### Rutas principales

- `GET /trayectoria/mi-historial/`
- `GET /trayectoria/historial/`
- `GET /trayectoria/historial/<id>/`
- `GET/POST /trayectoria/extraordinarios/registrar/`
- `GET/POST /trayectoria/situaciones/registrar/`

### Reglas principales

- El discente consulta solo su propio historial.
- Estadística/Admin puede consultar historiales y registrar extraordinarios o eventos de situación académica.
- Jefaturas consultan historiales según su ámbito.
- El extraordinario requiere resultado ordinario reprobatorio menor a 6.0 y acta `FINAL` formalizada.
- No se permite más de un extraordinario por inscripción.
- Si el extraordinario es aprobado se marca `APROBADO_EXTRAORDINARIO` y `EE`.
- Si el extraordinario es reprobado se registra baja temporal.
- El reingreso cierra la baja temporal abierta.
- La evidencia ordinaria se conserva aunque exista extraordinario.

### Fuera de este bloque

No se implementan todavía kárdex oficial, reportes formales, exportaciones PDF/Excel, rectificación de actas, reapertura de actas ni actas extraordinarias formales complejas.

## Bloque 8 - Kárdex oficial

Se implementa el kárdex oficial como vista derivada del historial académico y de resultados oficiales consolidados. El kárdex no es una tabla transaccional principal y no duplica resultados oficiales.

La fuente del kárdex son las inscripciones con acta `FINAL` formalizada y los campos oficiales de `InscripcionMateria`, incluyendo resultados extraordinarios cuando existan.

### Servicio creado

- `ServicioKardex`: construye el kárdex por discente desde resultados oficiales.
- `construir_kardex_discente`: función de aplicación usada por vistas y pruebas.

### Rutas principales

- `GET /trayectoria/kardex/`
- `GET /trayectoria/kardex/<id>/`

### Reglas principales

- El kárdex no es visible para discentes; queda como consulta institucional.
- Estadística/Admin consulta kárdex de discentes.
- Jefaturas consultan kárdex según su ámbito.
- Capturas preliminares y actas no formalizadas no aparecen.
- Las asignaturas se agrupan por año de formación y se ordenan por semestre.
- El promedio anual usa solo asignaturas numéricas con resultado oficial.
- Las asignaturas no numéricas, como `ACREDITADA` o `EXCEPTUADO`, no se incluyen en el promedio.
- Si una materia fue aprobada por extraordinario, se muestra la marca `EE`.

### Fuera de este bloque

No se implementan todavía exportaciones PDF/Excel, reportes estadísticos, cuadros de aprovechamiento, actas extraordinarias formales, rectificación de actas ni reapertura de actas.

Validaciones recomendadas:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test trayectoria
docker compose exec -T backend python manage.py test
```

## Bloque 8.5 - Cierre y apertura de periodo académico

Se implementa el cierre y apertura de periodo como proceso asistido. El sistema diagnostica primero si un periodo puede cerrarse, revisando actas `FINAL`, actas vivas, resultados oficiales, extraordinarios pendientes, situación académica y adscripciones. Si no existen bloqueantes, el periodo se marca como cerrado y se registra trazabilidad del proceso.

### Modelos agregados

- `ProcesoCierrePeriodo`
- `DetalleCierrePeriodoDiscente`
- `ProcesoAperturaPeriodo`

### Servicios creados

- `ServicioDiagnosticoCierrePeriodo`
- `ServicioCierrePeriodo`
- `ServicioAperturaPeriodo`
- `listar_pendientes_asignacion_docente`

### Rutas principales

- `GET /actas/periodos/`
- `GET /actas/periodos/<id>/diagnostico/`
- `POST /actas/periodos/<id>/cerrar/`
- `GET /actas/cierres/<id>/`
- `GET/POST /actas/apertura/`
- `GET /actas/aperturas/<id>/`
- `GET /actas/pendientes-asignacion-docente/`

### Reglas principales

- No se permite cerrar un periodo con actas `FINAL` faltantes.
- No se permite cerrar con actas vivas pendientes.
- No se permite cerrar con resultados oficiales faltantes.
- No se promueven discentes con extraordinario pendiente.
- No se promueven discentes en baja temporal o baja definitiva.
- La apertura requiere un periodo origen cerrado y un periodo destino existente.
- La apertura crea grupos destino y adscripciones de manera idempotente.
- No se asignan docentes automáticamente.
- Los programas esperados sin docente se muestran como pendientes para jefatura.

### Fuera de este bloque

No se implementan exportaciones PDF/Excel, reportes formales, cuadros de aprovechamiento, rectificación de actas, reapertura de actas, actas extraordinarias formales ni asignación automática de docentes.

Validaciones recomendadas:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test actas
docker compose exec -T backend python manage.py test
```

## Bloque 10A - Front institucional base

Se crea la base del portal visual moderno del Sistema de Control Académico EMI - ICI con Next.js, React, TypeScript y Tailwind CSS. El backend Django continúa como fuente de verdad para reglas académicas, permisos, actas, historial, kárdex y cierre/apertura de periodo.

### Arquitectura

- Frontend Next.js: `http://localhost:3000`
- Backend Django: `http://localhost:8000`
- Django Admin: `http://localhost:8000/admin/`
- PostgreSQL en Docker.

Servicios Docker esperados:

- `db`
- `backend`
- `frontend`

### Frontend

La carpeta `frontend/` contiene:

- Next.js con App Router.
- React y TypeScript.
- Tailwind CSS.
- Componentes base equivalentes compatibles: `Button`, `Card`, `Input`, `AppShell`, `Sidebar`, `Topbar`, `DashboardCard`, `StatusBadge`, `RoleBadge`, estados de carga/error/vacío y componentes de branding.
- Rutas iniciales:
  - `/`
  - `/login`
  - `/dashboard`
  - `/discente`
  - `/docente`
  - `/jefatura-carrera`
  - `/jefatura-academica`
  - `/jefatura-pedagogica`
  - `/estadistica`
  - `/admin-soporte`

### Variables de entorno frontend

Crear archivo local:

macOS/Linux:

```bash
cp frontend/.env.example frontend/.env.local
```

Windows PowerShell:

```powershell
Copy-Item frontend/.env.example frontend/.env.local
```

Variables:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Sistema de Control Académico EMI - ICI
NEXT_PUBLIC_APP_ENV=MVP intranet
```

No se deben colocar secretos en variables `NEXT_PUBLIC_`, porque son visibles para el navegador.

### Variables backend nuevas o ajustadas

```bash
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
```

En HTTPS real se debe activar `SESSION_COOKIE_SECURE=True` y `CSRF_COOKIE_SECURE=True`. No activar `SameSite=None` sin `Secure=True`. No activar HSTS en desarrollo local.

### Autenticación

El Bloque 10A usa sesiones Django con cookies y CSRF:

- `GET /api/auth/csrf/`: genera/devuelve token CSRF y cookie CSRF.
- `POST /api/auth/login/`: valida credenciales, crea sesión Django y devuelve usuario mínimo.
- `POST /api/auth/logout/`: cierra sesión Django.
- `GET /api/auth/me/`: devuelve `authenticated=false` o datos del usuario autenticado.

Reglas de seguridad:

- No JWT en esta fase.
- No MFA/OTP en esta fase.
- No tokens en `localStorage`.
- Cookies de sesión `HttpOnly`.
- CSRF activo; no se desactiva globalmente.
- CORS usa orígenes explícitos y `credentials: include`.

### Identidad visual

Paleta aproximada hasta recibir lineamientos oficiales:

- Guinda: `#611232`
- Guinda acento: `#9F2241`
- Verde institucional/militar: `#235B4E`
- Verde olivo: `#3A4A32`
- Dorado sobrio: `#D4AF37`
- Dorado institucional: `#BC955C`
- Fondo marfil: `#F8F4EA`
- Gris carbón: `#1F2937`

### Logos

Se prepara la estructura:

```text
frontend/public/brand/
  institutions/
  careers/
```

Convenciones principales:

- `frontend/public/brand/institutions/emi.svg` o `.png`
- `frontend/public/brand/institutions/emi-escudo.png`
- `frontend/public/brand/institutions/udefa.svg` o `.png`
- `frontend/public/brand/institutions/sedena.png`
- `frontend/public/brand/careers/ici.svg` o `.png`
- `frontend/public/brand/careers/ice.svg` o `.png`
- `frontend/public/brand/careers/ic.svg` o `.png`
- `frontend/public/brand/careers/ii.svg` o `.png`

No se descargan logos de internet. Si faltan logos, el portal muestra placeholders institucionales limpios mediante la ruta interna `/brand-logo/...`, evitando imagen rota y solicitudes 404 visibles.

### Levantar con Docker

```bash
docker compose build
docker compose up -d
docker compose ps
```

Validaciones recomendadas:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test
docker compose exec -T frontend npm install
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
```

### Alcance conservado

- Django Admin se mantiene.
- Las vistas Django existentes se mantienen como respaldo operativo.
- El frontend enlaza a rutas actuales del backend para funciones aún no migradas.
- No se implementa Bloque 9.
- No se implementan PDF ni Excel.
- No se duplican reglas académicas en React.

## Bloque 10B - Portal con datos vivos

Se implementa la primera capa de datos vivos del portal Next.js creado en el Bloque 10A. El frontend deja de depender solo de placeholders y consume APIs Django para mostrar informacion autorizada por rol/cargo, manteniendo a Django como fuente de verdad funcional y de permisos.

### Alcance implementado

- Dashboard con resumen calculado por usuario autenticado.
- Campana de notificaciones con contador de no leidas, listado, marcar una como leida y marcar todas.
- Actividad reciente basada en eventos existentes del backend, sin datos inventados.
- Calendario institucional con eventos visibles por rol/cargo/carrera/grupo.
- Eventos proximos derivados del calendario institucional.
- Buscador superior con resultados agrupados y filtrados por permisos.
- Ruta `/perfil` con informacion del usuario en solo lectura.
- Accesos rapidos/favoritos por usuario, con fallback estatico por rol cuando no hay favoritos guardados.

### Modelos agregados

- `NotificacionUsuario`: avisos dirigidos a usuarios del portal.
- `EventoCalendarioInstitucional`: eventos del calendario institucional, filtrables por periodo, carrera, grupo y roles destino.
- `AccesoRapidoUsuario`: accesos rapidos persistentes por usuario.

### Servicios agregados

- `portal_context`: resuelve roles, cargos, perfil principal y ambito del usuario.
- `dashboard_resumen`: arma tarjetas del dashboard con datos reales disponibles.
- `actividad_reciente`: consolida eventos recientes desde actas, capturas y movimientos academicos.
- `eventos_mes` y `eventos_proximos`: filtran calendario institucional por permisos.
- `busqueda`: busca usuarios, discentes, grupos, programas, actas y periodos segun permisos.
- `crear_notificacion_usuario`: punto simple para generar notificaciones desde backend.
- `notificar_acta_publicada_para_discentes`: servicio preparado para avisar a discentes cuando un acta publicada aplique.

### APIs nuevas

- `GET /api/dashboard/resumen/`
- `GET /api/dashboard/actividad-reciente/`
- `GET /api/notificaciones/`
- `POST /api/notificaciones/<id>/leer/`
- `POST /api/notificaciones/leer-todas/`
- `GET /api/calendario/mes/?year=YYYY&month=M`
- `GET /api/calendario/proximos/`
- `GET /api/busqueda/?q=texto`
- `GET /api/perfil/me/`
- `GET /api/accesos-rapidos/`
- `POST /api/accesos-rapidos/crear/`
- `DELETE /api/accesos-rapidos/<id>/`

Todas las APIs anteriores requieren autenticacion. Las operaciones de escritura mantienen CSRF y sesiones Django.

### Rutas frontend actualizadas

- `/dashboard`: consume resumen vivo y accesos rapidos.
- `/perfil`: muestra datos del usuario autenticado en solo lectura.
- `Topbar`: integra busqueda, notificaciones y menu de usuario.
- `DashboardSidePanel`: integra actividad reciente, calendario y eventos proximos.

### Seguridad y permisos

- No se implementa JWT.
- No se usan tokens en `localStorage`.
- Se mantienen sesiones Django, cookies y CSRF.
- El backend filtra datos por usuario, rol/cargo y ambito institucional.
- El discente no recibe kárdex oficial en dashboard ni busqueda.
- Las notificaciones solo son visibles para su usuario dueño.
- El calendario filtra eventos visibles y aplicables al contexto del usuario.

### Estados vacios

Cuando no existen registros vivos, el portal muestra mensajes controlados, por ejemplo:

- No hay actividad reciente registrada.
- No hay eventos en el mes.
- No hay eventos proximos registrados.
- No hay resultados para tu perfil.

No se generan metricas ni eventos inventados en el frontend.

### Validaciones ejecutadas

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test core
docker compose exec -T backend python manage.py test
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
docker compose exec -T backend python manage.py migrate
```

### Fuera de este bloque

No se implementa Bloque 9, PDF, Excel, WebSockets, JWT, MFA/OTP, IdP externo, migracion completa de actas a React, migracion completa de captura de calificaciones a React, migracion completa de kárdex a React ni cambio de reglas academicas.

### Pendientes naturales para 10C

- Conectar eventos automaticos completos desde actas, cierre/apertura de periodo y trayectoria hacia notificaciones.
- Permitir administracion operativa del calendario institucional desde pantallas dedicadas.
- Hacer favoritos editables desde el portal visual.
- Implementar resultados de busqueda con rutas React propias conforme se migren modulos.
- Mejorar auditoria fina de actividad reciente si se requiere una bitacora transversal formal.

## Bloque 9A - Núcleo común de exportaciones y auditoría

Se implementa la base común para registrar y auditar salidas documentales del sistema, sin generar todavía documentos PDF/Excel finales. Este bloque prepara la infraestructura para los subbloques posteriores de actas, kárdex y reportes operativos.

### Objetivo

Registrar toda exportación relevante como evidencia de auditoría, centralizar permisos base por rol/cargo y exponer APIs para que el portal pueda consultar catálogo e historial de exportaciones en fases posteriores.

### Modelo principal

Se agrega `RegistroExportacion` en la app `reportes`.

Campos principales:

- `usuario`
- `tipo_documento`
- `formato`
- `nombre_documento`
- `nombre_archivo`
- `objeto_tipo`
- `objeto_id`
- `objeto_repr`
- `filtros_json`
- `parametros_json`
- `rol_contexto`
- `cargo_contexto`
- `ip_origen`
- `user_agent`
- `estado`
- `mensaje_error`
- `tamano_bytes`
- `hash_archivo`
- `creado_en`
- `finalizado_en`

Estados soportados:

- `SOLICITADA`
- `GENERADA`
- `FALLIDA`
- `DESCARGADA`

Formatos previstos:

- `PDF`
- `XLSX`
- `CSV`

### Catálogo de exportaciones

Se crea un catálogo inicial en código con documentos y reportes previstos:

- actas de evaluación parcial;
- actas de evaluación final;
- actas de calificación final;
- kárdex oficial;
- historial académico interno;
- actas por estado;
- actas pendientes de validación;
- inconformidades y conformidades pendientes;
- desempeño académico;
- situación académica;
- validaciones de acta;
- exportaciones realizadas;
- movimientos académicos;
- auditoría de eventos.

En 9A queda implementado el núcleo de catálogo/auditoría. La generación real de documentos queda marcada como pendiente para 9B, 9C, 9F, 9G y 9I.

### Servicios creados

- `CatalogoExportaciones`: expone el catálogo filtrado por permisos.
- `ServicioPermisosExportacion`: define permisos base por rol/cargo.
- `ServicioExportacion`: registra solicitudes, marca exportaciones generadas o fallidas y captura IP/user agent.
- `construir_nombre_archivo`: normaliza nombres de archivo seguros.
- `limpiar_json_seguro`: remueve llaves sensibles de filtros/parámetros antes de auditar.

### APIs creadas

- `GET /api/reportes/catalogo/`
- `GET /api/exportaciones/`
- `GET /api/auditoria/exportaciones/`
- `POST /api/exportaciones/registrar-evento-prueba/`

El endpoint de prueba es técnico, restringido a Admin/Estadística y sirve para validar auditoría sin generar documentos finales.

### Reglas de permisos

- Todas las APIs requieren autenticación.
- Admin/superusuario puede consultar catálogo completo y auditoría.
- Estadística puede consultar catálogo institucional y auditoría de exportaciones.
- Jefatura de carrera ve actas y reportes operativos de su ámbito previsto.
- Jefatura académica/pedagógica ve documentos institucionales autorizados.
- Docente ve únicamente exportaciones potenciales de actas propias.
- Discente no ve kárdex oficial ni reportes globales como exportables.
- El backend valida permisos; el frontend no es fuente de autorización.

### Admin Django

`RegistroExportacion` queda registrado en Django Admin como consulta técnica:

- campos en solo lectura;
- sin alta manual desde admin;
- sin edición ordinaria;
- sin eliminación ordinaria;
- sin acción masiva de borrado.

### Seguridad documental

- No se guardan archivos físicos en 9A.
- No se almacenan payloads completos de documentos.
- No se guardan contraseñas, tokens, cookies, CSRF ni credenciales en `filtros_json` o `parametros_json`.
- El registro es evidencia append-only: si algo debe corregirse, se registra otro evento.
- No se modifican actas formalizadas, kárdex ni reglas académicas.

### Validación

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations reportes
docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test reportes
docker compose exec -T backend python manage.py test
```

Resultados locales:

- `check`: OK.
- `migrate`: OK, `reportes.0001_initial` aplicado.
- `makemigrations --check`: OK, sin cambios pendientes.
- `test reportes`: 14 pruebas OK.
- `test`: 314 pruebas OK.

### Fuera de alcance

No se implementa todavía:

- PDF real de actas;
- Excel real de actas;
- kárdex PDF;
- historial exportable;
- reportes de desempeño reales;
- reportes de situación académica reales;
- importación desde Excel;
- almacenamiento físico permanente de archivos;
- firma electrónica;
- QR o sello digital;
- pantallas React de reportes.

### Relación con siguientes bloques

- 9B conectará generadores reales de actas PDF/Excel usando `ServicioExportacion`.
- 9C podrá conectar kárdex PDF manteniendo la regla de no exposición al discente.
- 9F/9G/9I podrán construir reportes operativos y académicos sobre el catálogo.
- 10C podrá consumir las APIs para mostrar catálogo, historial y estados de exportación en el portal.
