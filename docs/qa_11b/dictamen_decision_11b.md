# Dictamen de decisión 11B

## Decisión recomendada

**Ejecutar 11B reducido**.

## Aclaración de alcance sobre edición de calificaciones

En el estado actual del sistema, **no existe un flujo ordinario de “editar calificaciones” en etapas avanzadas del acta** (remitida, validada o formalizada).  
Esto es intencional por control académico: una vez que el acta avanza en la cadena institucional, la captura queda bloqueada para preservar consistencia, trazabilidad y oficialidad del resultado.

Por lo tanto:

- Correcciones en etapas avanzadas deben tratarse como **procedimiento excepcional institucional**.
- Ese procedimiento requiere autorización de jefatura y evidencia de auditoría (antes/después, motivo, responsable).
- No debe presentarse en tesis como funcionalidad operativa estándar de usuario final.

## Razón técnica

1. 11A aporta buena base de QA por roles, pero la suite E2E observable es principalmente de navegación/permisos.
2. Las reglas de negocio transaccionales están mayormente cubiertas por tests backend (alto valor), pero falta evidencia UI transaccional de los flujos más críticos.
3. 11B completo tiene costo alto y riesgo de fragilidad que no compensa para cierre de tesis MVP.

## Riesgo de no hacer 11B

- Riesgo medio de sobreafirmación en tesis si se declara “automatización E2E integral”.
- Mitigable si se redacta como:
  - automatización E2E de disponibilidad/permisos por rol,
  - más pruebas backend de reglas de negocio,
  - más pruebas manuales guiadas para recorridos transaccionales.

## Riesgo de hacer 11B completo

- Riesgo alto de tiempo, flakes y mantenimiento.
- Puede comprometer estabilidad y cronograma de cierre.

## Condición previa obligatoria

Antes de ejecutar cualquier 11B, integrar/confirmar en la rama de trabajo los artefactos reales de 11A (seed y Playwright), porque en esta rama de diagnóstico no quedaron disponibles operativamente.

## Resultado esperado del 11B reducido

Con 5 flujos transaccionales automatizados (docente, discente, jefatura carrera, jefatura académica, exportación+audiotría), la evidencia quedaría suficiente y defendible sin sobredimensionar alcance.
