---
name: esquema-db
description: Genera el esquema SQL y las migraciones Flyway a partir del reporte EDA estandarizado.
---

# Skill: Esquema de Base de Datos

## Purpose
Invocar en la Fase 2 para traducir el análisis exploratorio a un esquema SQL versionado con Flyway.

## Steps

1. Leer `./core/pipelines/{flujo}/eda/reporte_eda.json` para identificar columnas, tipos y columnas candidatas a catálogo.
2. Generar `V1__{flujo}__catalogos.sql` siguiendo `template_v1_catalogos.sql`. Una tabla `cat_` por cada columna con `es_catalogo: true`.
3. Si `geografia.nivel` es `"municipal"` o `"estatal"`, generar `V2__{flujo}__geo.sql` siguiendo `template_v2_geo.sql` para conectar con `cve_geo` vía FDW.
4. Generar `V3__{flujo}__tabla_principal.sql` siguiendo `template_v3_tabla.sql` con la tabla `stg_` y sus claves foráneas a las tablas catálogo.
5. Generar `V4__{flujo}__vista.sql` siguiendo `template_v4_vista.sql` con la vista de integración que une `stg_` con todos los catálogos.
6. Aplicar migraciones: `just migrate {flujo}` (o el alias definido en el `justfile`). Verificar que no haya errores.
7. Generar diagrama ER con ERAlchemy2 y guardar en `./core/pipelines/{flujo}/assets/er_{flujo}.png`.

## Template

→ Ver `template_v1_catalogos.sql`, `template_v2_geo.sql`, `template_v3_tabla.sql`, `template_v4_vista.sql` en esta carpeta.

## References

- Migraciones de referencia: `migrations/fiscalia/sql/`
- Esquema de referencia: `core/pipelines/fiscalia/schemas.py`
