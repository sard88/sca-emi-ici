# Matriz de decisión 11B

Escenarios evaluados:

- **Escenario A**: cerrar con 11A + pruebas manuales guiadas.
- **Escenario B**: ejecutar 11B reducido (flujos críticos transaccionales).
- **Escenario C**: ejecutar 11B completo (automatización amplia por módulos).

| Criterio | 11A + manual | 11B reducido | 11B completo |
|---|---|---|---|
| Suficiencia para tesis | Medio-Alto | Alto | Alto |
| Evidencia funcional automatizada | Medio | Alto | Muy alto |
| Costo técnico | Bajo | Medio | Alto |
| Riesgo de romper estabilidad | Bajo | Medio | Alto |
| Riesgo de pruebas frágiles | Bajo | Medio | Alto |
| Tiempo de mantenimiento | Bajo | Medio | Alto |
| Valor para demo | Medio | Alto | Alto |
| Valor para defensa | Medio-Alto | Alto | Alto |
| Riesgo de sobreafirmación | Medio | Bajo | Bajo |
| Recomendación | Viable con redacción prudente | **Recomendada** | No recomendada por costo/beneficio actual |

## Justificación por escenario

## A) 11A + manual

Ventajas:

- Cierre rápido y estable.
- Sin introducir flakiness adicional.
- Aprovecha fuerte cobertura backend ya existente.

Riesgos:

- La tesis no debería afirmar automatización transaccional completa por UI.
- Dependencia alta en ejecución manual para demostrar recorrido funcional real.

## B) 11B reducido

Ventajas:

- Cierra la brecha más crítica de evidencia funcional por UI.
- Mantiene control de alcance y tiempo.
- Da mejor narrativa de validación end-to-end por rol.

Riesgos:

- Incremento moderado de mantenimiento E2E.
- Requiere cuidar estabilidad de dataset QA y selectores de UI.

## C) 11B completo

Ventajas:

- Máxima cobertura automatizada visible.

Riesgos:

- Esfuerzo alto y posibilidad de inestabilidad por pruebas frágiles.
- Mayor probabilidad de retrasar cierre de tesis.
- Duplicación parcial de valor ya cubierto por tests backend.

## Recomendación final

Ejecutar **11B reducido**.  
Si el tiempo se vuelve crítico, alternativa segura: cerrar con **11A + manual** y redactar límites explícitos en Capítulo V.

