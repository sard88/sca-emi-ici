# Backlog post 10E

Este backlog consolida pendientes no bloqueantes detectados o confirmados durante QA 10E. No forman parte del MVP cerrado ni deben resolverse como correccion urgente salvo decision posterior.

## QA y datos demo

- Crear fixture o management command QA idempotente, explicito de desarrollo, con usuarios ficticios por perfil y flujo docente-discente-jefaturas-estadistica.
- Documentar credenciales demo ficticias fuera de repositorios publicos o mediante mecanismo seguro local.
- Automatizar recorrido E2E con navegador para login, permisos y flujo academico principal.

## Frontend y responsive

- Agregar suite frontend de componentes/rutas si se adopta framework de pruebas.
- Generar capturas responsive desktop 1440, laptop 1366, tablet 768 y movil 390 para rutas criticas.
- Afinar tablas densas, filtros y formularios largos si la revision visual con usuarios detecta friccion.

## Funcionalidades futuras ya fuera de 10E

- Filtros en cascada completos periodo -> carrera -> grupo -> asignatura.
- Asignacion docente en portal.
- Consulta pedagogica especifica si se define alcance formal.
- Acceso granular a auditoria por ambito de jefatura de carrera.
- Restablecimiento formal de contraseña.
- Importacion Excel.
- Kardex Excel.
- PDF de cuadro de aprovechamiento.
- Rectificacion/reapertura de actas, si se aprueba como bloque futuro.

## Despliegue operativo

- Manual de instalacion productiva.
- Variables y secretos por ambiente.
- Estrategia de backup/restauracion.
- Configuracion HTTPS, dominio, correo y almacenamiento de archivos.
- Politica de retencion de auditoria/exportaciones.
