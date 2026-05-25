# Resumen Bloque 9C - Kárdex oficial PDF

## Objetivo

El Bloque 9C implementa la exportación PDF del kárdex oficial institucional del Sistema de Control Académico EMI - ICI.

La exportación se construye como una salida documental derivada del `ServicioKardex` existente del Bloque 8. No se crea una tabla `KardexOficial`, no se convierte el kárdex en entidad transaccional y no se modifica ningún dato académico oficial.

La estrategia documental sigue el patrón validado en Bloque 9B:

- plantilla XLSX productiva;
- llenado con `openpyxl`;
- valores cerrados, sin fórmulas;
- conversión a PDF con LibreOffice headless;
- auditoría con `RegistroExportacion`.

## Alcance implementado

Se implementó:

- plantilla XLSX productiva anonimizada para kárdex;
- contexto documental del kárdex desde `ServicioKardex`;
- exportador interno XLSX;
- exportador PDF basado en LibreOffice;
- servicio de exportación con permisos y auditoría;
- endpoint de descarga PDF;
- catálogo de exportaciones actualizado;
- pruebas automatizadas;
- documentación técnica.

No se implementa kárdex Excel descargable en este bloque.

## Archivos modificados o creados

### Backend

- `backend/reportes/api_urls.py`
- `backend/reportes/api_views.py`
- `backend/reportes/catalogo.py`
- `backend/reportes/services.py`
- `backend/reportes/tests.py`
- `backend/reportes/kardex_context.py`
- `backend/reportes/kardex_services.py`
- `backend/reportes/utils_calificaciones.py`
- `backend/reportes/exportadores/actas_pdf.py`
- `backend/reportes/exportadores/kardex_pdf.py`
- `backend/reportes/exportadores/libreoffice_utils.py`
- `backend/reportes/templates_xlsx/kardex/kardex_oficial_template.xlsx`

### Documentación

- `README.md`
- `docs/resumen_bloque9c_kardex_pdf.md`

## Plantilla XLSX

La plantilla productiva queda en:

- `backend/reportes/templates_xlsx/kardex/kardex_oficial_template.xlsx`

La plantilla contiene:

- encabezado institucional;
- título de kárdex oficial;
- datos generales del discente;
- tabla por año, semestre, clave, asignatura, calificación, letra, marca y observaciones;
- secciones de promedios;
- leyendas;
- certificación;
- espacio de firma.

La plantilla está anonimizada y no contiene datos personales reales, matrículas reales ni calificaciones reales.

## Servicios creados

### Contexto documental

Archivo:

- `backend/reportes/kardex_context.py`

Responsabilidades:

- invocar `ServicioKardex.construir_por_discente`;
- preparar datos generales del discente;
- preparar carrera, plan de estudios y antigüedad;
- agrupar materias por año de formación y semestre;
- convertir calificaciones numéricas a texto documental;
- preservar resultados no numéricos;
- marcar `EE` cuando exista extraordinario;
- calcular promedio general derivado cuando hay datos numéricos;
- resolver autoridad certificadora cuando existe cargo institucional vigente;
- preparar leyendas, certificación y lugar/fecha.

### Exportador PDF

Archivo:

- `backend/reportes/exportadores/kardex_pdf.py`

Responsabilidades:

- cargar la plantilla XLSX;
- poblar celdas con datos del contexto;
- expandir filas si la trayectoria supera el espacio base;
- conservar estilos, bordes, merges, orientación, márgenes y área de impresión;
- generar XLSX temporal interno;
- convertir a PDF mediante LibreOffice headless.

### Utilidad común de LibreOffice

Archivo:

- `backend/reportes/exportadores/libreoffice_utils.py`

Responsabilidades:

- centralizar la conversión XLSX a PDF;
- respetar `LIBREOFFICE_BINARY`;
- manejar errores de conversión;
- limpiar temporales;
- permitir reutilización por actas y kárdex.

El exportador de actas del Bloque 9B fue ajustado para reutilizar esta utilidad común y evitar duplicación.

### Servicio de exportación de kárdex

Archivo:

- `backend/reportes/kardex_services.py`

Responsabilidades:

- cargar el discente;
- validar permisos;
- registrar solicitud en `RegistroExportacion`;
- generar el PDF;
- marcar exportación como `GENERADA` o `FALLIDA`;
- calcular tamaño y hash SHA-256;
- devolver bytes, MIME type, nombre de archivo y registro de auditoría.

## Endpoint creado

### Kárdex oficial PDF

`GET /api/exportaciones/kardex/<discente_id>/pdf/`

Requiere autenticación y permisos.

Devuelve:

- `Content-Type: application/pdf`
- `Content-Disposition: attachment`
- `X-Registro-Exportacion-Id`

El nombre de archivo sigue una convención segura, por ejemplo:

```text
kardex-oficial_ici-discente-12_20260513-153000.pdf
```

El nombre no incluye nombre completo ni matrícula militar.

## Catálogo de exportaciones

Se actualizó `KARDEX_OFICIAL` en el catálogo de reportes/exportaciones.

Estado:

- PDF implementado;
- XLSX pendiente;
- requiere objeto `discente_id`;
- disponible solo para perfiles institucionales autorizados;
- oculto para discentes.

## Reglas de permisos

El backend conserva la autoridad real.

### Permitidos

- Admin/superusuario.
- Encargado de Estadística.
- Jefatura académica.
- Jefatura pedagógica.
- Jefatura de carrera, para discentes de su ámbito.

### No permitidos

- Discente, incluso sobre su propio kárdex.
- Docente, salvo que en un futuro exista permiso institucional explícito.
- Usuarios anónimos.
- Usuarios sin cargo o rol autorizado.

## Reglas de privacidad

Se aplican estas restricciones:

- el discente no puede exportar kárdex oficial;
- no se incluye matrícula militar por defecto;
- el nombre del archivo no contiene nombres ni matrícula;
- no se guarda el contenido del kárdex en `RegistroExportacion`;
- no se guardan materias ni calificaciones completas en filtros o parámetros de auditoría;
- el PDF sí contiene calificaciones, pero solo se entrega a usuarios autorizados.

## Calificación en letra

Se agregó utilidad documental en:

- `backend/reportes/utils_calificaciones.py`

Ejemplos:

- `10.0` -> `10.0 (DIEZ PUNTO CERO)`
- `9.5` -> `9.5 (NUEVE PUNTO CINCO)`
- `8.0` -> `8.0 (OCHO PUNTO CERO)`
- `6.0` -> `6.0 (SEIS PUNTO CERO)`

Los resultados no numéricos no se fuerzan a calificación.

## EE y extraordinario

Cuando una materia fue aprobada por extraordinario:

- se muestra la calificación aprobatoria vigente;
- se muestra marca `EE`;
- no se usa la calificación ordinaria reprobatoria como resultado final del kárdex oficial;
- la evidencia ordinaria queda en historial académico, no en el documento oficial derivado.

La leyenda incluida es:

```text
EE: Examen Extraordinario.
```

## Promedios

El promedio anual se toma del `ServicioKardex` cuando está disponible.

Si el promedio general se deriva en el contexto documental:

- solo considera materias numéricas oficiales;
- excluye resultados no numéricos;
- usa la calificación vigente cuando hay extraordinario aprobado;
- muestra un decimal;
- no modifica datos persistidos.

## Certificación y firma

El documento incluye sección de certificación y espacio de firma.

La autoridad certificadora se intenta resolver desde cargos vigentes:

- jefatura académica;
- jefatura pedagógica.

Si no hay autoridad configurada, el documento muestra:

```text
Pendiente de designación
```

No se inventan nombres.

## Auditoría

Cada exportación registra `RegistroExportacion` con:

- usuario;
- tipo `KARDEX_OFICIAL`;
- formato `PDF`;
- nombre del documento;
- nombre de archivo;
- objeto exportado;
- rol y cargo de contexto;
- IP y user agent cuando están disponibles;
- estado;
- tamaño;
- hash SHA-256;
- fecha de creación y finalización.

Si la generación falla, la exportación queda como `FALLIDA` y el error se reporta de forma controlada.

## Pruebas automatizadas agregadas

Se agregaron o ajustaron pruebas para:

- exportar kárdex PDF como Estadística;
- exportar kárdex PDF como Admin;
- permitir a jefatura de carrera exportar kárdex de su ámbito;
- bloquear jefatura de carrera fuera de su ámbito;
- bloquear discente;
- bloquear docente;
- registrar `RegistroExportacion` tipo `KARDEX_OFICIAL`;
- registrar estado `FALLIDA` ante error de generación;
- validar nombre de archivo sin datos sensibles;
- validar `Content-Type: application/pdf`;
- validar encabezado `X-Registro-Exportacion-Id`;
- validar catálogo con kárdex PDF implementado para roles autorizados;
- confirmar que no existe modelo transaccional `KardexOficial`;
- confirmar que la exportación no modifica actas ni inscripciones;
- validar marca `EE` en contexto documental;
- validar exclusión de materias no numéricas en promedio;
- validar calificación con letra.

## Validaciones ejecutadas

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations
docker compose exec -T backend python manage.py migrate
docker compose exec -T backend python manage.py makemigrations --check
docker compose exec -T backend python manage.py test reportes
docker compose exec -T backend python manage.py test trayectoria
docker compose exec -T backend python manage.py test
```

Resultados locales:

- `check`: OK.
- `makemigrations`: OK, sin cambios detectados.
- `migrate`: OK, sin migraciones pendientes.
- `makemigrations --check`: OK.
- `test reportes`: 43 pruebas OK.
- `test trayectoria`: 25 pruebas OK.
- `test`: 343 pruebas OK.

No se ejecutó lint/build de frontend porque este bloque no modificó código del portal Next.js.

## Validación manual esperada

1. Ingresar como Estadística o Admin.
2. Llamar `GET /api/exportaciones/kardex/<discente_id>/pdf/`.
3. Confirmar descarga de PDF.
4. Confirmar que el documento abre correctamente.
5. Confirmar que agrupa materias por año y semestre.
6. Confirmar calificación numérica y letra.
7. Confirmar marca `EE` cuando aplica.
8. Confirmar leyendas y certificación.
9. Revisar en Django Admin el `RegistroExportacion` generado.
10. Intentar descarga como discente y confirmar bloqueo.

## Limitaciones

La plantilla se basa en una propuesta institucional derivada de la referencia visual disponible. No pretende ser idéntica milimétricamente al formato físico definitivo hasta contar con un escaneo editable u oficial.

La autoridad certificadora final debe validarse institucionalmente.

La integración visual completa del botón de kárdex en el portal queda pendiente para un bloque posterior.

## Pendientes

Para 9C posterior o 10C-2:

- integrar botón visual de descarga de kárdex PDF en el portal;
- definir autoridad certificadora oficial;
- ajustar plantilla si la institución entrega formato editable definitivo;
- evaluar kárdex Excel si se autoriza;
- agregar folio institucional si se define una regla oficial;
- agregar QR o sello digital en bloque futuro, no en 9C;
- integrar almacenamiento permanente si se requiere evidencia documental histórica.

## Fuera de alcance

No se implementó:

- kárdex Excel descargable;
- historial académico PDF/Excel;
- reportes operativos de actas;
- reportes de desempeño;
- reportes de situación académica;
- cuadro de aprovechamiento;
- importación Excel;
- gráficas;
- firma electrónica;
- QR;
- sello digital;
- envío por correo;
- acceso de discente al kárdex;
- modelo `KardexOficial`;
- modificación de actas;
- modificación de inscripciones;
- modificación de historial.
