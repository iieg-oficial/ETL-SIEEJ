---
name: sqlalchemy-models
description: Genera el archivo schemas.py con los modelos SQLAlchemy 2.x del pipeline, en sincronía con las migraciones Flyway.
---

# Skill: SQLAlchemy Models

## Purpose
Invocar después de aplicar las migraciones Flyway (Fase 2) para generar los modelos ORM que usarán los stages de carga.

## Steps

1. Leer las migraciones `V1`, `V3` (y `V2` si aplica) para extraer nombres de tablas y definiciones de columnas.
2. Crear una clase `Base` con `DeclarativeBase` de SQLAlchemy 2.x.
3. Crear una clase por cada tabla catálogo (`cat_`) con sus columnas tipadas usando `Mapped` y `mapped_column`.
4. Crear la clase de la tabla principal (`stg_`) con sus columnas y las claves foráneas correspondientes.
5. Definir las relaciones entre modelos con `relationship()` desde `stg_` hacia cada catálogo.
6. Agregar una clase de constantes con los nombres de tabla al inicio del archivo (para evitar strings hardcodeados).
7. Guardar en `./core/pipelines/{flujo}/schemas.py`.

## Template

→ Ver `template.py` en esta carpeta.

## References

- Archivo de referencia: `core/pipelines/fiscalia/schemas.py`
- Atributos de referencia: `core/pipelines/fiscalia/attributes/fiscalia.py`
