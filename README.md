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
  - `ADMIN_SISTEMA`
  - `JEFATURA_CARRERA`
  - `JEFATURA_ACADEMICA`
  - `DOCENTE`
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
