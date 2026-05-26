# Redacción sugerida para Capítulo V según decisión 11B

## Escenario A: cerrar con 11A + pruebas manuales

Texto sugerido:

> La validación del sistema combinó pruebas automáticas backend de reglas de negocio, pruebas E2E por rol orientadas a navegación y control de accesos, y una guía de ejecución manual para recorridos operativos transaccionales.  
> En esta etapa, la automatización E2E se enfocó en disponibilidad funcional por perfil, protección de rutas y estabilidad de experiencia institucional, mientras que las transacciones académicas críticas se sustentaron principalmente con pruebas unitarias e integrales del backend y evidencia manual guiada.
> Asimismo, la edición ordinaria de calificaciones queda restringida por estado del acta; en etapas avanzadas, cualquier ajuste se gestiona como procedimiento excepcional institucional con autorización y trazabilidad.

Evitar afirmar:

- “automatización end-to-end completa de todos los flujos transaccionales”.

## Escenario B: ejecutar 11B reducido

Texto sugerido:

> Además de la cobertura automática de navegación y permisos por rol, se implementó una suite E2E transaccional focalizada en cinco recorridos críticos: captura/publicación de actas por docente, conformidad de discente, validación por jefatura de carrera, formalización por jefatura académica y evidencia de exportación/auditoría.  
> Esta estrategia permitió elevar la evidencia funcional de extremo a extremo en los procesos de mayor impacto académico, manteniendo un alcance controlado y estable para el MVP.
> Se mantiene la restricción de no edición ordinaria en estados avanzados del acta, preservando la consistencia del resultado oficial.

## Escenario C: ejecutar 11B completo

Texto sugerido:

> La validación incluyó automatización E2E transaccional amplia por módulo y perfil, cubriendo operaciones académicas, administrativas, reportes, trayectoria, movimientos, periodos y auditoría.  
> El alcance completo incrementó la trazabilidad funcional de interfaz, complementando la verificación backend y reduciendo la dependencia de ejecución manual para los flujos centrales del sistema.
> En todos los casos, las correcciones de calificaciones posteriores a estados avanzados se tratan fuera del flujo ordinario, bajo mecanismo institucional excepcional.

Observación metodológica:

- En este escenario se debe reportar explícitamente estrategia anti-flaky, costos de mantenimiento y límites de estabilidad.
