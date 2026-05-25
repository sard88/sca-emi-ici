# Logos institucionales y por carrera

Esta carpeta prepara el portal del Bloque 10A para usar logos oficiales o autorizados. No incluye logos descargados de internet ni imágenes inventadas.

## Estructura

```text
frontend/public/brand/
  institutions/
  careers/
```

## Convención institucional

Preferir SVG. Si no existe SVG, se permite PNG transparente.

- `frontend/public/brand/institutions/emi.svg`
- `frontend/public/brand/institutions/udefa.svg`
- `frontend/public/brand/institutions/gobierno.svg`
- `frontend/public/brand/institutions/sedena.svg`
- `frontend/public/brand/institutions/emi.png`
- `frontend/public/brand/institutions/emi-escudo.png`
- `frontend/public/brand/institutions/udefa.png`
- `frontend/public/brand/institutions/gobierno.png`
- `frontend/public/brand/institutions/sedena.png`

## Recursos de login

- `frontend/public/brand/login/emi-campus.png`

Este recurso se usa como apoyo visual del login institucional.

## Convención por carrera

- `frontend/public/brand/careers/ici.svg`
- `frontend/public/brand/careers/ice.svg`
- `frontend/public/brand/careers/ic.svg`
- `frontend/public/brand/careers/ii.svg`
- `frontend/public/brand/careers/ici.png`
- `frontend/public/brand/careers/ice.png`
- `frontend/public/brand/careers/ic.png`
- `frontend/public/brand/careers/ii.png`

## Reglas

- Usar solo archivos proporcionados por el equipo o autorizados institucionalmente.
- No descargar logos de internet.
- No usar imágenes externas desde URL remota.
- Si falta un logo, el frontend muestra un placeholder limpio con siglas, no una imagen rota.
- El portal sirve logos mediante `/brand-logo/...`; si el archivo esperado no existe, esa ruta devuelve un placeholder SVG para evitar 404 visuales.
- Los colores actuales son aproximados hasta recibir lineamientos oficiales.
