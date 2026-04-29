---
name: sqlalchemy-models
description: Genera el archivo schemas.py con los modelos SQLAlchemy 2.x del pipeline, en sincronía con las migraciones Flyway.
---

# Skill: SQLAlchemy Models

## Purpose
Invocar después de aplicar las migraciones Flyway (Fase 2) para generar los modelos ORM que usarán los stages de carga.

## Steps

1. Verificar que `./core/pipelines/{flujo}/attributes.py` exista con `{Flujo}Tables(StrEnum)` (uno por nombre de tabla, usando `auto()`). Si no existe, crearlo antes de continuar.
2. Leer las migraciones de catálogos y la tabla principal para extraer nombres de tablas y definiciones de columnas.
3. Crear la clase `{Flujo}Base(DeclarativeBase)` con el método `columns()` que devuelve los nombres de columna.
4. Crear una clase por cada tabla catálogo (`cat_`) con sus columnas tipadas usando `Mapped` y `mapped_column`.
5. Crear la clase de la tabla principal (`stg_`) con sus columnas y las claves foráneas correspondientes.
6. Importar `{Flujo}Tables as T` desde `attributes.py` y usar `T.NOMBRE_TABLA` en `__tablename__` (nunca strings literales).
7. Definir las relaciones entre modelos con `relationship()` desde `stg_` hacia cada catálogo.
8. Guardar en `./core/pipelines/{flujo}/schemas.py`.

## Template

→ Ver `template.py` en esta carpeta.
