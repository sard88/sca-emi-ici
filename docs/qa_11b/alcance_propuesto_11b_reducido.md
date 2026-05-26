# Alcance propuesto 11B reducido

## Objetivo

Automatizar únicamente los flujos transaccionales más críticos para respaldar defensa técnica sin ampliar innecesariamente el alcance.

## Flujos a automatizar

1. **Docente**
   - Abrir asignación real QA.
   - Capturar P1 (valores válidos e inválidos).
   - Guardar captura.
   - Generar/re-generar borrador.
   - Publicar acta.

2. **Discente**
   - Abrir detalle de acta propia publicada.
   - Registrar `CONFORME`.
   - Registrar `INCONFORME` sin comentario (esperar rechazo).
   - Registrar `INCONFORME` con comentario (éxito).

3. **Jefatura de carrera**
   - Consultar acta remitida de su ámbito.
   - Validar acta.

4. **Jefatura académica**
   - Consultar acta validada por carrera.
   - Formalizar acta.
   - Verificar estado final y bloqueo de edición ordinaria.

5. **Exportación + auditoría**
   - Disparar al menos una exportación autorizada.
   - Verificar descarga no vacía.
   - Verificar evidencia de evento/folio técnico en UI o endpoint auxiliar autorizado.

## Casos negativos mínimos

- Docente no puede operar asignación ajena.
- Discente no puede registrar conformidad tras remisión.
- Jefatura carrera no valida fuera de ámbito.
- Jefatura académica no formaliza acta no validada.

## Datos QA mínimos requeridos

- 1 asignación docente activa con discentes inscritos.
- Acta en borrador/publicada/remitida/validada según etapa.
- Usuarios `qa_*` por rol.
- Dataset seed idempotente y estable.

## Esfuerzo estimado

- Diseño y hardening de pruebas: medio.
- Mantenimiento posterior: medio-bajo.
- Riesgo de flakiness: medio (controlable con selectores robustos y precondiciones).

## Resultado esperado

Conjunto pequeño de specs con evidencia transaccional real que complemente 11A sin convertir el bloque en un proyecto de automatización total.

