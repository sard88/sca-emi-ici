# Resumen de Cambios del Proyecto (hasta commit `11b8ff4`)

## Alcance del resumen
Este documento resume **solo cambios ya commiteados** en la rama:

- `feature/bloque-10d3-terminologia-microcopy-ui`

Último commit considerado:

- `11b8ff4` — *Ajusta acciones de actas y exportación docente*

## Línea de commits aplicada
1. `eb87d44` — Corrige reserva de columna derecha en layout principal  
2. `7010297` — Mejora distribución de tarjetas en pantallas anchas  
3. `09f2c69` — Mejora presentación del dashboard institucional  
4. `d455f93` — Branding institucional y ajustes de dashboard  
5. `b5cf24e` — Simplifica vistas del discente y agrega historial académico  
6. `c99940d` — Mejora navegación y vistas docentes  
7. `a52ed9b` — Mejora vistas y navegación de jefatura de carrera  
8. `9057396` — Ajusta jefatura académica y limpia textos técnicos en frontend  
9. `cc2cb5f` — Limpia textos y navegación frontend en administración/reportes  
10. `010231a` — Mejora vistas y navegación de estadística  
11. `270ac75` — Habilita consolidado por materia con exportación XLSX  
12. `11b8ff4` — Ajusta acciones de actas y exportación docente  

---

## Cambios funcionales relevantes por bloque

## 1) Layout base y dashboard institucional
- Se corrigió la reserva de columna derecha vacía en layout principal.
- Se mejoró distribución de tarjetas en pantallas amplias.
- Se aplicaron ajustes de presentación institucional en dashboard (compactación y claridad visual).
- Se ajustó branding institucional en dashboard sin alterar rutas/permisos reales.

## 2) Discente
- Se simplificó lenguaje visible para enfoque académico no técnico.
- Se añadieron/ajustaron vistas de historial académico para discente.
- Se corrigieron enlaces internos de tarjetas del dashboard discente a rutas frontend válidas.

## 3) Docente
- Se corrigió navegación de tarjetas del dashboard docente.
- Se separaron mejor acciones docentes (asignaciones, actas, captura, consulta).
- Se mejoró presentación de detalle de acta docente (tablas y secciones más claras).
- Se ocultaron accesos no pertinentes para docente (según visibilidad frontend ya disponible).

## 4) Jefatura de carrera
- Se ajustaron accesos y navegación para evitar rutas erróneas/403 en frontend.
- Se limpiaron textos técnicos visibles.
- Se filtró actividad reciente para mostrar eventos relevantes al rol.

## 5) Jefatura académica
- Se ajustó navegación para actas pendientes vs formalizadas.
- Se agregó soporte de vista formalizada por parámetro (`estado=formalizadas`) en frontend.
- Se eliminaron mensajes técnicos visibles y se unificó microcopy institucional.

## 6) Administración y reportes (limpieza transversal)
- Se removieron textos de implementación técnica visibles al usuario final.
- Se corrigieron casos de navegación a rutas no válidas/404 en frontend.
- Se mantuvieron restricciones de permisos reales sin cambios de backend de seguridad.

## 7) Estadística
- Se mejoró navegación y visibilidad de módulos de estadística/reportes.
- Se alineó “Actas vivas” a criterio de actas formalizadas.
- Se creó/ajustó vista frontend para actas de estadística y periodos, manteniendo lógica segura.

## 8A) Backend consolidado por materia/grupo (JSON oficial)
- Se implementó endpoint backend para consolidado:
  - `GET /api/reportes/desempeno/consolidado-materia/`
- Fuente de datos oficial:
  - Solo actas con estado `FORMALIZADO_JEFATURA_ACADEMICA`.
- Incluye por discente:
  - `P1`, `P2`, `P3`, `PP`, `EF`, `PF`, etc.
- Incluye resumen:
  - `extraordinarios`, `media_aritmetica`, `moda`, `desviacion_estandar`, `reprobados`.

## 8B) Frontend consolidado de desempeño
- Se integró el reporte “Consolidado por materia y grupo” en `Reportes > Desempeño`.
- Se conectó a endpoint oficial JSON.
- Se habilitó exportación XLSX del consolidado.

## 8C) Catálogo de reportes + actas por corte
- En catálogo:
  - `Acta de evaluación parcial` -> `/reportes/actas?tipo=parcial`
  - `Acta de evaluación final` -> `/reportes/actas?tipo=final&corte=FINAL`
  - `Acta de calificación final`:
    - Docente -> `/reportes/actas?tipo=calificacion-final`
    - Otros perfiles autorizados -> `/reportes/desempeno/consolidado-materia`
- En `/reportes/actas`:
  - Parcial soporta cortes `P1/P2/P3`.
  - Final soporta `FINAL`.
  - Listado filtrado solo a estado `FORMALIZADO_JEFATURA_ACADEMICA`.
  - Se añadió sección docente para exportar calificación final de **sus** asignaciones.

---

## Reglas funcionales críticas ya aplicadas
1. Para cálculos y consolidado institucional:
   - Solo actas `FORMALIZADO_JEFATURA_ACADEMICA`.
2. No mezclar:
   - Evaluación final (`EF`) con calificación final (`PF`).
3. Docente:
   - Puede exportar calificación final de su asignación (propia materia/grupo), validado por backend.
4. No depender de enlaces backend directos en UI:
   - Evitar `localhost:8000`, admin Django, endpoints crudos visibles como navegación.

---



## Archivos clave tocados en los últimos bloques (referencia rápida)
- Backend:
  - `backend/reportes/api_urls.py`
  - `backend/reportes/api_views.py`
  - `backend/reportes/reportes_desempeno.py`
- Frontend:
  - `frontend/src/app/reportes/page.tsx`
  - `frontend/src/app/reportes/actas/page.tsx`
  - `frontend/src/lib/reportes-desempeno.ts`
  - `frontend/src/lib/api.ts`
  - `frontend/src/lib/types.ts`
  - (más archivos de dashboard/layout/reportes según bloques previos)

---

## Estado de rama
- Rama: `feature/bloque-10d3-terminologia-microcopy-ui`
- Remoto: actualizado (push sin cambios pendientes de commits).

