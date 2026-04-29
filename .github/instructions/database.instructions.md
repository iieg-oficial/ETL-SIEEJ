---
applyTo: "**/*.sql,**/schemas.py"
---

# Database Instructions

> Aplican a: DB

## Rules

- Homologar tipos de columna: texto → `VARCHAR(n)`, numérico entero → `INT`, decimal → `FLOAT` o `NUMERIC(p,s)`, fecha → `DATE`, fecha-hora → `TIMESTAMP`.
- Homologar nombres de columna a `snake_case` en español, sin espacios, tildes ni caracteres especiales. Usar `normalize_text` como referencia de transformación.
- Tablas catálogo llevan prefijo `cat_`. La tabla principal lleva prefijo `stg_`. No usar otros prefijos.
- Crear tablas únicamente a través de migraciones Flyway versionadas. Validar la aplicación con `just migrate {flujo}` en la BD local de Docker.
- Para consultar o inspeccionar la BD usar `just psql` o los comandos definidos en el `justfile`. No conectar directamente sin pasar por Docker.
- Si hay un error de lógica en una migración ya versionada y aún no aplicada en producción, corregir el script existente; no crear una migración nueva para parchar el error.
- Para referencias a municipios y entidades, usar la BD `cve_geo` a través del Foreign Data Wrapper (FDW) ya configurado. No duplicar estas tablas en el esquema del pipeline.
- Nombres de migración: `V{n}__{flujo}__{descripcion}.sql` (dos guiones bajos entre cada segmento).
- El archivo `schemas.py` del pipeline debe mantenerse en sincronía con las migraciones Flyway. Cada tabla en SQL tiene su modelo SQLAlchemy correspondiente.
- Generar diagrama ER con ERAlchemy2 después de aplicar las migraciones y guardarlo en `./core/pipelines/{flujo}/assets/er_{flujo}.png`.
