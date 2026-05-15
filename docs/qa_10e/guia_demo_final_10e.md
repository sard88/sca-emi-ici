# Guia de demo final 10E

## Preparacion

1. Levantar ambiente:

   ```bash
   docker compose up -d
   docker compose ps
   ```

2. Verificar salud interna si el host local no responde desde sandbox:

   ```bash
   docker compose exec -T backend python manage.py check
   docker compose exec -T frontend npm run lint
   ```

3. Usar un dataset ficticio. No usar datos reales ni subir PDF/XLSX generados al repositorio.

## Recorrido sugerido

1. **Login institucional**
   - Abrir `/login`.
   - Iniciar sesion con usuario demo autorizado.
   - Mostrar dashboard de perfil.

2. **Admin / Estadistica**
   - Abrir `/administracion` y `/catalogos`.
   - Mostrar carrera, plan, antiguedad, periodo, grupo, materia base, programa de asignatura y esquema.
   - Remarcar que Django conserva validaciones.

3. **Docente**
   - Abrir `/docente/asignaciones`.
   - Entrar a una asignacion.
   - Mostrar captura por corte y resumen.
   - Generar o revisar borrador de acta.
   - Publicar y remitir solo si el dataset demo esta preparado.

4. **Discente**
   - Abrir `/discente/carga-academica`.
   - Abrir `/discente/actas`.
   - Registrar acuse/conformidad/inconformidad con comentario en datos ficticios.
   - Mostrar aviso de conformidad informativa y solo lectura despues de remision.

5. **Jefatura de carrera**
   - Abrir `/jefatura-carrera/actas`.
   - Revisar timeline de validacion.
   - Validar acta remitida si corresponde.

6. **Jefatura academica**
   - Abrir `/jefatura-academica/actas`.
   - Revisar aviso de formalizacion.
   - Formalizar solo acta validada y preparada para demo.

7. **Reportes y exportaciones**
   - Abrir `/reportes`.
   - Mostrar agrupacion por documentos oficiales, reportes, exportaciones y auditoria.
   - Exportar acta/kardex/reporte solo con datos ficticios.
   - Confirmar folio tecnico.

8. **Trayectoria y movimientos**
   - Abrir `/trayectoria/mi-historial` o `/trayectoria/historial/<discenteId>`.
   - Mostrar historial academico interno y aviso de que no sustituye al kardex.
   - Mostrar movimiento o cambio de grupo preparado.

9. **Periodos**
   - Abrir `/periodos`.
   - Ejecutar o mostrar diagnostico de cierre.
   - Si hay bloqueantes, demostrar que el cierre no procede.
   - Si el dataset esta listo, mostrar cierre/apertura y pendientes de asignacion docente.

10. **Auditoria**
    - Abrir `/reportes/auditoria`.
    - Mostrar eventos criticos y drawer de detalle.
    - Confirmar que no se exponen payloads sensibles completos.

## Cierre de demo

- Mostrar `docs/qa_10e/resumen_bloque10e_qa_integral.md`.
- Indicar que no hay P0/P1 abiertos.
- Mencionar P2 diferidos: dataset demo formal, QA visual responsive con capturas y tests frontend automatizados.
