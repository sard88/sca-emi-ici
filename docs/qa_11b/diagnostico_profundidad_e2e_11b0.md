# Diagnóstico de profundidad E2E transaccional (Bloque 11B-0)

## Resumen ejecutivo

El Bloque 11A dejó una base sólida de QA (seed integral + evidencia + suite Playwright por rol), pero la cobertura E2E observada es principalmente de **autenticación, navegación y permisos visibles**.  
No hay evidencia de automatización transaccional profunda de extremo a extremo (captura real, remisión, validación, formalización, cierre/apertura con mutaciones verificadas y asserts de datos persistidos).

Conclusión: para tesis, **11A + backend tests + manual guiado** puede ser suficiente si se redacta con precisión; si se desea afirmar automatización funcional integral por rol, conviene **11B reducido**.

## Alcance del diagnóstico

- Revisión documental 10E y 11A.
- Revisión de artefactos Playwright declarados en 11A.
- Contraste contra 120 flujos críticos solicitados.
- Validaciones técnicas no destructivas.
- Emisión de dictamen para decidir entre:
  - A) 11A + manual,
  - B) 11B reducido,
  - C) 11B completo.

## Hallazgos de control de rama y trazabilidad

1. Rama activa durante diagnóstico: `feature/bloque-11b0-diagnostico-e2e-transaccional`.
2. Se detectó que el commit de 11A (`e7918fd`) **no es ancestro de HEAD** en esta rama (`contains_11a_commit=no`).
3. La evidencia 11A existe (documentada y visible en el commit), pero en esta rama no están presentes físicamente los archivos Playwright/seed.
4. Esto implica riesgo de “evidencia en rama distinta” si no se integra antes de cierre final.

## Qué cubre realmente 11A (según evidencia y specs)

### Cobertura fuerte

- Login/logout por rol.
- Bloqueo de anónimo en rutas protegidas.
- Navegación por módulos clave por perfil.
- Verificaciones básicas de no-crash UI.
- Verificaciones básicas de texto/no exposición de patrones sensibles.

### Cobertura limitada (parcial)

- Docente, discente, jefaturas, reportes, periodos: se valida entrada a rutas, pero no secuencias transaccionales completas con mutaciones y aserciones de persistencia.
- Exportaciones: no hay evidencia E2E fuerte de descarga+validación de registro de exportación en la suite mostrada.

### Cobertura no demostrada en E2E

- Captura de calificaciones componente a componente con validaciones de rango y limpieza.
- Flujo completo acta: borrador -> publicar -> remitir -> validar -> formalizar con validaciones de estado en backend.
- Trayectoria/movimientos/cierre-apertura con mutaciones completas verificadas.

## Revisión de specs Playwright 11A

Los 12 specs revisados (`00` a `11`) son mayoritariamente del patrón:

- `loginAs(...)`
- `visitAndCheck(path, headingRegex)`
- asserts de presencia/ausencia de texto

No se observan (en esos archivos):

- secuencias largas de interacción transaccional con formularios complejos,
- asserts de payload funcional persistido,
- validación de transición de estado de negocio por caso.

Dictamen técnico: suite útil como **smoke/regresión de navegación y permisos**, no como automatización transaccional integral.

## Aclaración funcional relevante para tesis

Durante el diagnóstico se confirma una restricción de negocio clave:  
**no existe edición ordinaria de calificaciones cuando el acta ya superó etapas de publicación/remisión/validación/formalización**.

Motivo:

- proteger la integridad del resultado oficial,
- evitar alteraciones fuera de flujo,
- mantener trazabilidad académica y de auditoría.

Implicación para redacción:

- no afirmar “edición posterior libre” de calificaciones,
- describir cualquier corrección posterior como proceso excepcional controlado, no como operación estándar de portal.

## Relación con pruebas backend

La plataforma sí tiene valor alto en pruebas backend (según evidencia 10E/11A):

- reglas de evaluación y actas,
- permisos,
- trayectoria,
- reportes,
- auditoría.

Por tanto, no todo debe duplicarse en E2E UI. El gap real está en demostrar algunos recorridos críticos de negocio desde interfaz.

## Respuesta a preguntas clave

1. ¿Qué cubre 11A?  
Cobertura por rol de login/rutas/permisos visibles + smoke de no-crash.

2. ¿Las Playwright 11A son transaccionales completas?  
No; en su mayoría son navegación y acceso.

3. ¿Qué flujos críticos ya están automatizados?  
Autenticación básica, acceso por rol, bloqueo anónimo/ciertos no autorizados.

4. ¿Qué flujos críticos no están automatizados?  
Cadena transaccional actas, movimientos, cierre/apertura y descargas auditadas con verificación profunda.

5. ¿Qué depende de backend tests?  
La mayor parte de reglas de negocio (cálculo, transiciones, bloqueos, consistencia).

6. ¿Qué valor adicional real aporta 11B?  
Evidencia defendible de “operación real por rol en UI” en flujos críticos.

7. Riesgo si no hacemos 11B  
Sobreafirmar en tesis automatización que hoy es parcial.

8. Riesgo si hacemos 11B completo  
Tiempo alto, fragilidad E2E, mantenimiento y flakiness.

## Validaciones ejecutadas en este bloque (no destructivas)

- `docker compose exec -T backend python manage.py check` -> OK
- `docker compose exec -T backend python manage.py makemigrations --check` -> OK
- `docker compose exec -T frontend npm run lint` -> OK
- `docker compose exec -T frontend npm run build` -> OK
- `docker compose exec -T backend python manage.py seed_demo_qa_integral --size small` -> FAIL (comando no existe en esta rama)
- `docker compose exec -T frontend npm run e2e:qa` -> FAIL (script no existe en esta rama)

Interpretación: el estado de esta rama no contiene integración efectiva de artefactos 11A, aunque sí existe evidencia histórica en otro commit/rama.

## Dictamen recomendado

**Recomendación principal: ejecutar 11B reducido (opción C del usuario / escenario intermedio).**

Justificación:

- Preserva cronograma.
- Evita riesgo alto de un 11B completo.
- Cierra brecha más crítica: demostrar transacciones reales desde UI en el flujo nuclear académico.

### Flujos mínimos para 11B reducido

1. Docente: captura -> borrador -> publicar.  
2. Discente: consulta -> conforme/inconforme con comentario obligatorio.  
3. Jefatura de carrera: validar.  
4. Jefatura académica: formalizar.  
5. Exportación + auditoría asociada.

## Riesgos abiertos (P0/P1 detectados en diagnóstico)

- P1-DIAG-11B0-01: Desalineación de rama (11A no integrado en rama de diagnóstico).  
  Impacto: evidencia incompleta/reproducibilidad afectada.
- P1-DIAG-11B0-02: Declaración “21 E2E OK” no reproducible en rama actual sin reintegrar artefactos.
