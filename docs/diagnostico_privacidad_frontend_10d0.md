# Diagnóstico de privacidad frontend - Bloque 10D-0

## Resumen

No se detectaron contraseñas, tokens, cookies o CSRF expuestos como contenido visible. El frontend sí maneja CSRF en `frontend/src/lib/api.ts`, pero como mecanismo técnico de sesión. El mayor riesgo de privacidad está en pantallas con datos académicos sensibles, historiales internos, comentarios de inconformidad y auditoría, donde debe mantenerse la segmentación backend y mejorar el copy/visibilidad por perfil.

## Hallazgos

| Hallazgo | Perfil afectado | Ruta | Severidad | Recomendación |
|---|---|---|---|---|
| Auditoría institucional mezcla tab de exportaciones con eventos críticos bajo una misma función visual. | Jefatura pedagógica | `/reportes/auditoria` | P1 | Separar permiso de eventos y exportaciones; evitar que una autoridad vea una pestaña que backend niega. |
| Tabla de eventos críticos muestra usuario, módulo, evento, objeto y resumen. | Admin, Estadística, autoridades | `/reportes/auditoria` | P2 | Mantener sin `metadatos_json`/`cambios_json` por defecto; detalle solo si hay necesidad institucional. |
| Historial interno muestra resultados, eventos, extraordinarios y movimientos. | Admin, Estadística, jefaturas | `/trayectoria/historial/[discenteId]` | P2 | Mantener aviso de privacidad y evitar rutas enlazadas a perfiles no autorizados. |
| Diagnóstico de cierre lista discentes y motivos. | Admin, Estadística, jefaturas autorizadas | `/periodos/[id]/diagnostico` | P2 | Confirmar que backend limita ámbito; no mostrar a Docente/Discente. |
| Comentario de inconformidad se captura completo. | Discente | `/discente/actas/[detalleId]` | P2 | Correcto para la entidad de conformidad; no replicar comentario completo en auditoría ni reportes generales. |
| Reporte de inconformidades indica que el comentario se muestra a perfiles autorizados. | Admin, Estadística, jefaturas | `/reportes/operativos/inconformidades` | P2 | Revisar si el reporte debe truncar/ocultar comentario por defecto. |
| Formularios de trayectoria piden ID interno y advierten no usar matrícula militar. | Admin, Estadística | `/trayectoria/**/nuevo`, `/movimientos-academicos/**`, `/periodos/apertura` | P1 | Sustituir por selectores/buscadores autorizados; evita captura de matrícula o nombre sensible en campos libres. |
| Kárdex exportable muestra `discente_id` y carrera. | Admin, Estadística, jefaturas | `/reportes/kardex` | P2 | Aceptable si backend filtra; no mostrar matrícula militar por defecto. |
| Login maneja contraseña en estado de componente y la envía a `/api/auth/login/`. | Usuario autenticable | `/login` | P3 | Correcto para login; no loguear ni reflejar contraseña. |
| Administración de usuarios incluye contraseña temporal. | Admin | `/administracion/usuarios` | P2 | Mantener solo en creación/restablecimiento; ocultar en edición ordinaria para claridad. |
| Buscador/topbar puede abrir URLs backend dinámicas. | Todos | Topbar | P2 | Asegurar que resultados no expongan rutas antiguas ni objetos fuera del perfil. |

## Reglas que deben preservarse

1. No mostrar matrícula militar por defecto.
2. Discente solo debe ver datos propios.
3. Docente no debe ver auditoría global ni reportes globales.
4. Auditoría general solo para Admin, Estadística y autoridades autorizadas.
5. Comentarios completos de inconformidad no deben viajar a bitácora ni listados generales sin justificación.
6. Payloads sensibles (`password`, tokens, cookies, CSRF, `metadatos_json`, `cambios_json`) no deben aparecer en tablas principales.

## Recomendaciones para 10D-1

| Prioridad | Acción |
|---|---|
| P1 | Separar permisos visuales de auditoría de eventos vs exportaciones. |
| P1 | Reemplazar campos de ID manual en operaciones críticas por selectores/buscadores. |
| P1 | Ocultar acciones de periodo a perfiles de consulta. |
| P2 | Truncar o separar comentarios sensibles en reportes operativos. |
| P2 | Mantener avisos de privacidad solo donde realmente hay datos sensibles, sin saturar pantallas comunes. |
