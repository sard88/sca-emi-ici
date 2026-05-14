# Matriz campos frontend/backend - Bloque 10D-0

## Resumen

Los formularios de administración y catálogos ya usan `select`, `boolean`, `date`, `number` y `relation`. El principal problema no es que todo sea texto libre, sino que los selectores relacionales son genéricos: `RelationSelect` carga `page_size=100&limit=100` sin filtros de activos, ámbito, rol compatible ni dependencia entre campos.

Los formularios de trayectoria, movimientos y apertura/cierre son más básicos: `TrajectoryOperations.tsx` usa un `FormPage` genérico con `TextField`, por lo que IDs internos, códigos y booleanos se capturan como texto libre.

## Matriz de campos

| Módulo | Recurso/formulario | Campo | Tipo backend | Validación backend | Representación frontend actual | Representación recomendada | ¿Faltante en frontend? | ¿Sobrante en frontend? | Prioridad | Observación |
|---|---|---|---|---|---|---|---:|---:|---|---|
| Administración | Usuarios | `username` | texto único | requerido | texto | texto | No | No | P3 | Correcto. |
| Administración | Usuarios | `nombre_completo` | texto | requerido | texto | texto | No | No | P3 | Correcto. |
| Administración | Usuarios | `correo` | email/texto | opcional | texto | email | No | No | P2 | Podría usar tipo email. |
| Administración | Usuarios | `grado_empleo_id` | FK | grado existente | relation select genérico | select filtrado activos | No | No | P1 | Hoy puede incluir inactivos. |
| Administración | Usuarios | `rol` | grupo/rol | requerido | relation select de roles | select por roles permitidos | No | No | P1 | Evitar roles técnicos no asignables desde portal. |
| Administración | Usuarios | `password` | contraseña temporal | crear/cambiar | password | password solo en alta o flujo explícito de restablecimiento | No | Parcial | P2 | En edición se omite si está vacío, pero visualmente aparece. |
| Administración | Grado/empleo | `tipo` | choices | catálogo cerrado | select | select | No | No | P3 | Correcto. |
| Administración | Unidades | `tipo_unidad` | choices | SECCION/SUBSECCION | select | select | No | No | P3 | Correcto. |
| Administración | Unidades | `padre_id` | FK | unidad existente | relation select genérico | select jerárquico activos, excluir sí misma en edición | No | No | P1 | Falta filtro contextual. |
| Administración | Unidades | `carrera_id` | FK | carrera existente | relation select genérico | select de carreras activas | No | No | P1 | Puede traer carreras inactivas. |
| Administración | Asignaciones cargo | `usuario_id` | FK usuario | usuario compatible | relation select genérico | buscador de usuario activo filtrable por rol | No | No | P1 | Riesgo UX de elegir usuarios incompatibles. |
| Administración | Asignaciones cargo | `cargo_codigo` | choices | cargo permitido | select | select | No | No | P3 | Correcto. |
| Administración | Asignaciones cargo | `tipo_designacion` | choices | titular/accidental | select | select | No | No | P3 | Correcto. |
| Administración | Asignaciones cargo | `unidad_organizacional_id` | FK | unidad compatible | relation select genérico | select activo filtrado por tipo/cargo | No | No | P1 | Backend valida, pero UX permite errores evitables. |
| Administración | Asignaciones cargo | `vigente_desde/hasta` | fecha | traslapes | date | date | No | No | P3 | Correcto. |
| Catálogos | Carreras | `estado` | choices | activo/inactivo | select | select | No | No | P3 | Correcto. |
| Catálogos | Planes | `carrera_id` | FK | carrera existente | relation select genérico | select carreras activas | No | No | P1 | Falta filtro por activo. |
| Catálogos | Antigüedades | `plan_estudios_id` | FK | plan existente | relation select genérico | select planes activos, idealmente filtrado por carrera | No | No | P1 | Falta dependencia carrera-plan. |
| Catálogos | Periodos | `periodo_academico` | choices | 1/2 | select | select | No | No | P3 | Correcto. |
| Catálogos | Periodos | `estado` | choices | planificado/activo/cerrado/inactivo | select | select | No | No | P3 | Correcto. |
| Catálogos | Grupos | `antiguedad_id` | FK | antigüedad existente | relation select genérico | select activo filtrado por plan/carrera | No | No | P1 | Falta cascada. |
| Catálogos | Grupos | `periodo_id` | FK | periodo existente | relation select genérico | select de periodos activos/planificados según operación | No | No | P1 | Puede incluir cerrados/inactivos. |
| Catálogos | Grupos | `semestre_numero` | entero | rango académico | number | select o stepper con rango | No | No | P2 | Evita semestre inválido antes del backend. |
| Catálogos | Materias | `creditos` | calculado | horas x 0.0625 | readOnly | solo lectura/calculado visible | No | No | P3 | Correcto. |
| Catálogos | Programa asignatura | `plan_estudios_id` | FK | plan existente | relation select genérico | select plan activo | No | No | P1 | Falta activo/dependencia. |
| Catálogos | Programa asignatura | `materia_id` | FK | materia existente | relation select genérico | select materia activa | No | No | P1 | Falta activo. |
| Catálogos | Programa asignatura | `anio_formacion` | calculado | derivado de semestre | readOnly | solo lectura | No | No | P3 | Correcto. |
| Catálogos | Programa asignatura | `obligatoria` | regla institucional | backend conserva | boolean readOnly | solo lectura o retirar del form | No | Parcial | P2 | Está read-only, pero en alta puede confundir. |
| Catálogos | Esquema evaluación | `programa_asignatura_id` | FK | programa existente | relation select genérico | select programa activo con materia/plan visible | No | No | P1 | Label genérico puede ser poco claro. |
| Catálogos | Esquema evaluación | `num_parciales` | choices | 1-3 | select | select | No | No | P3 | Correcto. |
| Catálogos | Esquema evaluación | `peso_parciales/peso_final/umbral_exencion` | número | reglas de esquema | number | number con límites/ayuda | No | No | P2 | Falta validación visual de porcentajes. |
| Catálogos | Componentes evaluación | corte/peso/tipo | estructurado | suma y cortes | panel específico | editor estructurado con validaciones visibles | No | No | P2 | Revisar UX en 10D-2. |
| Evaluación | Captura preliminar | valores por discente/componente | grilla | backend valida acta avanzada y esquema | grilla numérica | grilla full width | No | No | P3 | Layout correcto; no guardar payloads en auditoría. |
| Actas | Publicar/remitir/validar/formalizar | observación | texto | opcional | textarea/botón según acción | mantener, con confirmación | No | No | P3 | No modificar reglas. |
| Conformidad | Inconformidad | `comentario` | texto requerido si INCONFORME | requerido por backend/frontend | textarea | textarea con aviso de privacidad | No | No | P2 | No debe replicarse completo en auditoría ni listados globales. |
| Trayectoria | Registrar extraordinario | `inscripcion_materia_id` | FK | inscripción elegible | texto libre ID | buscador/select de inscripciones elegibles | No | No | P1 | Alto error operativo por captura manual. |
| Trayectoria | Registrar extraordinario | `calificacion` | número | rango/calificación | texto/number genérico | number con rango | No | No | P1 | Debe validar visualmente antes de enviar. |
| Trayectoria | Registrar situación | `discente_id` | FK | discente permitido | texto libre ID | buscador de discente por ámbito | No | No | P1 | No usar matrícula militar. |
| Trayectoria | Registrar situación | `situacion_codigo` | choices/catálogo | BAJA_TEMPORAL, BAJA_DEFINITIVA, REINGRESO | texto libre | select de situación académica activa | No | No | P1 | El texto libre invita errores de código. |
| Trayectoria | Registrar situación | `periodo_id` | FK | periodo existente | texto libre ID | select periodo activo/cerrado según caso | No | No | P1 | Falta selector. |
| Movimientos | Registrar movimiento | `tipo_movimiento` | choices | tipos soportados | texto libre | select | No | No | P1 | Especialmente para no romper cambio de grupo. |
| Movimientos | Cambio de grupo | `discente_id` | FK | ámbito/estado | texto libre ID | buscador/select | No | No | P1 | Debe evitar captura por matrícula. |
| Movimientos | Cambio de grupo | `grupo_origen_id/grupo_destino_id` | FK | grupo compatible | texto libre ID | selects dependientes por periodo/carrera | No | No | P1 | Backend bloquea, pero UX puede prevenir. |
| Periodos | Apertura | `periodo_origen_id` | FK | origen cerrado | texto libre ID | select de periodos cerrados elegibles | No | No | P1 | Acción crítica. |
| Periodos | Apertura | `periodo_destino_id` | FK | destino compatible | texto libre ID | select de periodos destino planificados/activos elegibles | No | No | P1 | Acción crítica. |
| Periodos | Diagnóstico cierre | clasificaciones de discentes | derivado | solo lectura | tabla full width | tabla full width con columnas mínimas | No | No | P2 | Muestra nombres; permitido solo perfiles autorizados. |
| Reportes | Filtros | carrera/periodo/grupo/discente | filtros backend | opcionales/ámbito | texto ID/nombre en varios reportes | selects/buscadores según dato | No | No | P2 | Menor que formularios mutables, pero mejora mucho la UX. |
| Auditoría | Eventos críticos | `evento_codigo` | choice/código | exacto | texto libre uppercase | select/autocomplete de eventos | No | No | P2 | Evita filtros sin resultados. |

## Reglas transversales recomendadas

1. Selectores FK deben filtrar activos por defecto y permitir incluir inactivos solo en edición histórica si el registro ya los usa.
2. Selectores FK operativos deben ser buscadores paginados, no listas de 100 elementos.
3. Campos calculados (`creditos`, `anio_formacion`, resultados derivados) deben quedar solo lectura o fuera del formulario.
4. Acciones críticas de trayectoria, movimientos y periodos deben dejar de pedir IDs manuales en 10D-1.
5. El backend sigue validando todo; el frontend solo reduce errores previsibles.
