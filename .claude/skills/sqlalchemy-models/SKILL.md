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

```python
from enum import auto
from typing import Optional

from sqlalchemy import ForeignKey, Integer, SmallInteger, String, Date, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.pipelines.{flujo}.attributes import {Flujo}Tables as T


class {Flujo}Base(DeclarativeBase):
    def columns(self) -> list[str]:
        return [c.key for c in self.__table__.columns]


class CatEstadoTramite({Flujo}Base):
    __tablename__ = T.CAT_ESTADO_TRAMITE

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class CatTipoSolicitante({Flujo}Base):
    __tablename__ = T.CAT_TIPO_SOLICITANTE

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class Stg{Flujo}({Flujo}Base):
    __tablename__ = T.STG_{FLUJO}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estado_tramite_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_ESTADO_TRAMITE}.id"), nullable=False
    )
    tipo_solicitante_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_TIPO_SOLICITANTE}.id"), nullable=True
    )
    fecha_actualizacion: Mapped[Date] = mapped_column(Date, nullable=False)

    estado_tramite: Mapped["CatEstadoTramite"] = relationship()
    tipo_solicitante: Mapped[Optional["CatTipoSolicitante"]] = relationship()
```

> **Regla:** `nullable` en los modelos debe coincidir 1:1 con `NOT NULL` en el SQL de la migración.
