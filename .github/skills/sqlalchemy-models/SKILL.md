---
name: sqlalchemy-models
description: Template dummy para generar el schemas.py de un pipeline en SQLAlchemy 2.0 con Mapped/mapped_column.
---

## Cuándo usar

Justo después de definir las migraciones SQL. El `schemas.py` debe reflejar exactamente la estructura de las tablas creadas.

## Reglas

Ver `database-rules.instructions.md` y `bootstrap-update-rules.instructions.md`.

- SQLAlchemy 2.0 (`Mapped`, `mapped_column`, `DeclarativeBase`).
- `id: Mapped[int]` PK en toda tabla.
- FKs `{singular}_id`.
- Tablas principales con `fecha_actualizacion: Date NOT NULL`.
- Nombres de tabla via enum en `attributes.py` (centralizado).
- `nullable` de cada columna **idéntico** al SQL.

## Template — `core/pipelines/{flujo}/attributes.py`

```python
from enum import StrEnum


class Tablas(StrEnum):
    CAT_EJEMPLO = "cat_ejemplo"
    STG_PRINCIPAL = "stg_principal"
```

## Template — `core/pipelines/{flujo}/schemas.py`

```python
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.{flujo}.attributes import Tablas as T


class {Flujo}Base(DeclarativeBase):
    """Base declarativa del pipeline {flujo}."""


class CatEjemplo({Flujo}Base):
    __tablename__ = T.CAT_EJEMPLO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    ejemplo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class StgPrincipal({Flujo}Base):
    __tablename__ = T.STG_PRINCIPAL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cve_geo_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ejemplo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_EJEMPLO}.id"), nullable=False
    )
    valor: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
```

## Variante SCD Tipo 2

Cuando la fuente mezcla nuevos + actualizaciones:

```python
class StgPrincipal({Flujo}Base):
    __tablename__ = T.STG_PRINCIPAL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hash_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(nullable=False, default=True)
    # ... resto de columnas
```

## ERD

Generar con `eralchemy2` y guardar en `core/pipelines/{flujo}/assets/erd.png`:

```python
from eralchemy2 import render_er

from core.pipelines.{flujo}.schemas import {Flujo}Base

render_er({Flujo}Base, "core/pipelines/{flujo}/assets/erd.png")
```
