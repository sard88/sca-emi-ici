# Resumen Bloque 10D-3 - Terminologia, microcopy, estados vacios e iconografia

## Objetivo

El Bloque 10D-3 normaliza lenguaje visible, ayudas contextuales, estados vacios, errores, avisos sensibles e iconografia del portal Next.js sin modificar reglas academicas, flujos funcionales, permisos backend, modelos ni migraciones.

## Glosario aplicado

Se agrego `frontend/src/lib/glosario.ts` con terminos institucionales para UI:

- Discente, Docente, Asignatura, Materia, Programa de asignatura.
- Antiguedad, Periodo academico y Ano de formacion.
- Kardex oficial e Historial academico interno.
- Acta, Evaluacion final, Resultado final preliminar y Calificacion final.
- Conformidad, Inconformidad, Bitacora, Registro de exportacion y Auditoria institucional.

El criterio aplicado mantiene `Materia` para el catalogo base y usa `Asignatura` en operacion, reportes, actas, carga academica y trayectoria.

## Componentes creados o ajustados

- `frontend/src/lib/microcopy.ts`: mensajes reutilizables de acceso, estados vacios, historial, kardex, actas, auditoria, reportes, catalogos, periodos y privacidad.
- `frontend/src/components/ui/EmptyState.tsx`: estados vacios con variantes `default`, `search`, `restricted`, `noData`, `pending` y `success`.
- `frontend/src/components/ui/ErrorState.tsx`: errores visuales con variantes `error`, `forbidden`, `validation`, `network` y `notFound`.
- `frontend/src/components/ui/SensitiveInfoNotice.tsx`: avisos de informacion academica sensible.
- `frontend/src/components/ui/icons.tsx`: iconografia SVG centralizada para modulos, estados y acciones principales.
- `frontend/src/components/states/EmptyState.tsx` y `frontend/src/components/states/ErrorMessage.tsx`: wrappers actualizados para reutilizar los componentes comunes.

## Pantallas y archivos actualizados

- Sidebar y tarjetas de dashboard usan iconos centralizados y etiquetas institucionales.
- Dashboards por perfil ajustan textos visibles de seguimiento, reportes, trayectoria, kardex y auditoria.
- Reportes operativos, desempeno y trayectoria normalizan periodo academico, antiguedad, asignatura e historial academico interno.
- Catalogos mantienen `Materias` para el catalogo base y usan `Materia / asignatura base` en programas de asignatura.
- Trayectoria operativa reemplaza labels tecnicos como `Discente ID`, `Inscripcion materia ID`, `Situacion codigo` y booleanos crudos por textos legibles.
- Actas normalizan botones academicos: publicar, remitir, validar, formalizar y regenerar borrador.
- Reportes/kardex y reportes/exportaciones ajustan ayudas y estados vacios.

## Estados vacios y errores

Los estados vacios distinguen:

- sin datos;
- sin resultados por filtros;
- acceso restringido;
- configuracion pendiente;
- proceso completado.

Los errores visuales evitan JSON crudo y mensajes tecnicos. Los mensajes con `permiso` se muestran como acceso restringido.

## Iconografia

No se agregaron dependencias nuevas. La iconografia manual existente se centralizo en `frontend/src/components/ui/icons.tsx` para evitar mezclar estilos entre sidebar, dashboard, estados vacios y avisos.

## Privacidad

Se homologaron avisos para informacion academica sensible, historial interno, kardex, auditoria y reportes nominales. El bloque no expone matricula militar por defecto, payloads sensibles, JSON tecnico ni datos de otros discentes.

## Ajustes backend

No hubo cambios backend, modelos, permisos, migraciones ni APIs.

## Validaciones

Comandos ejecutados durante el bloque:

- `docker compose exec -T frontend npm run lint`
- `docker compose exec -T frontend npm run build`
- `docker compose exec -T backend python manage.py check`
- `docker compose exec -T backend python manage.py makemigrations --check`
- `docker compose exec -T backend python manage.py test`

## Limitaciones

- No se realizo rediseño completo ni QA responsive fino.
- No se cambiaron identificadores tecnicos, rutas, nombres de tipos ni modelos aunque conserven `Kardex`, `MateriaPlan` o `InscripcionMateria`.
- Algunos filtros nominales siguen como texto libre hasta que exista endpoint seguro y especifico.

## Pendientes

- 10E: QA responsive fino, densidad de tablas largas y mejoras visuales profundas.
- Post-10D: filtros en cascada completa, asignacion docente en portal, consulta pedagogica especifica y restablecimiento de contraseña.
