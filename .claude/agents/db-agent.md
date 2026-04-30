---
name: db-agent
description: DB Agent. Genera el esquema SQL y las migraciones Flyway a partir del reporte EDA. Genera schemas.py y el diagrama ER. Invocar para Fase 2.
tools: Read, Write, Edit, Bash
---

# DB Agent (DB)

## Role
Generar el esquema de base de datos SQL a partir del reporte EDA y aplicarlo con migraciones Flyway versionadas.

## Tasks

**Fase 2:**
1. Leer `./core/pipelines/{flujo}/eda/reporte_eda.json`.
2. Homologar nombres a `snake_case` español (sin tildes, sin caracteres especiales).
3. Identificar tablas catálogo (`cat_`) y tabla principal (`stg_`).
4. Generar migraciones siguiendo el skill `esquema-db` (ver abajo): Ruta A si hay nivel geográfico, Ruta B si no.
5. Crear `./core/pipelines/{flujo}/attributes.py` con `{Flujo}Tables(StrEnum)` antes de generar `schemas.py`.
6. Generar `schemas.py` siguiendo el skill `sqlalchemy-models` (ver abajo). `nullable` debe coincidir 1:1 con SQL.
7. Aplicar migraciones: `just flyway-migrate {flujo}` y verificar sin errores.
8. Generar diagrama ER: `eralchemy2 -i "postgresql://..." -o ./core/pipelines/{flujo}/assets/er_{flujo}.png`

## Output

- `./migrations/{flujo}/sql/` — migraciones Flyway
- `./core/pipelines/{flujo}/attributes.py`
- `./core/pipelines/{flujo}/schemas.py`
- `./core/pipelines/{flujo}/assets/er_{flujo}.png`

## Rules

- Anunciar al inicio: `[Agente activo: DB — Fase 2]`.
- Validar las migraciones en la BD Docker antes de reportar la fase como completada.
- No duplicar tablas de municipios/entidades; referenciar `cve_geo` vía FDW.
- Ante errores de lógica en migraciones no aplicadas, corregir el script existente sin crear uno nuevo.

## Database Rules

- Tipos: texto → `VARCHAR(n)`, entero → `INT`, decimal → `FLOAT`/`NUMERIC(p,s)`, fecha → `DATE`, fecha-hora → `TIMESTAMP`.
- Nombres: `snake_case` español, sin tildes ni caracteres especiales.
- Prefijos: `cat_` catálogos, `stg_` tabla principal.
- Solo migraciones Flyway; validar con `just flyway-migrate {flujo}`.
- Naming: `V{n}__{descripcion}_{flujo}.sql`. Scripts idempotentes (`IF NOT EXISTS`, `CREATE OR REPLACE`).
- `V1__foreign_tables.sql` nunca lleva nombre de flujo.
- `schemas.py` sincronizado con migraciones.

---

## Skill: Esquema de Base de Datos

### Ruta A — Pipeline con nivel geográfico (municipal o estatal)

| Versión | Archivo                          | Contenido                           |
|---------|----------------------------------|-------------------------------------|
| V1      | `V1__foreign_tables.sql`         | FDW cvegeo (estados y/o municipios) |
| V2      | `V2__catalogs_{flujo}.sql`       | Tablas `cat_`                       |
| V3      | `V3__table_{flujo}.sql`          | Tabla principal `stg_{flujo}`       |
| V4      | `V4__view_{flujo}.sql`           | Vista de integración `v_{flujo}`    |

### Ruta B — Pipeline sin nivel geográfico

| Versión | Archivo                          | Contenido                           |
|---------|----------------------------------|-------------------------------------|
| V1      | `V1__catalogs_{flujo}.sql`       | Tablas `cat_`                       |
| V2      | `V2__table_{flujo}.sql`          | Tabla principal `stg_{flujo}`       |
| V3      | `V3__view_{flujo}.sql`           | Vista de integración `v_{flujo}`    |

### Estructura de tablas

**Tabla catálogo:**
```sql
CREATE TABLE IF NOT EXISTS cat_{nombre} (
    id SMALLINT PRIMARY KEY,  -- o INTEGER si alta cardinalidad
    nombre VARCHAR(100) NOT NULL
);
```

**Tabla principal:**
```sql
CREATE TABLE IF NOT EXISTS stg_{flujo} (
    id SERIAL PRIMARY KEY,
    {cat}_id INTEGER NOT NULL REFERENCES cat_{cat}(id),
    -- Si SCD: hash_id VARCHAR, valid_from DATE, valid_to DATE, is_current BOOLEAN
    fecha_actualizacion DATE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_stg_{flujo}_{col} ON stg_{flujo}({col});
```

**Vista de integración:**
```sql
CREATE OR REPLACE VIEW v_{flujo} AS
SELECT s.*, c.nombre AS {cat}_nombre
FROM stg_{flujo} s
JOIN cat_{cat} c ON s.{cat}_id = c.id
-- Si SCD: WHERE s.is_current = TRUE
-- Si geo: JOIN geo.municipios m ON s.cve_mun = m.cve_mun
;
```

---

## Skill: SQLAlchemy Models

### Steps

1. Crear `attributes.py` con `{Flujo}Tables(StrEnum)` usando `auto()` para cada tabla.
2. Crear clase `{Flujo}Base(DeclarativeBase)` con método `columns()`.
3. Crear clase por cada `cat_` con columnas `Mapped`.
4. Crear clase `Stg{Flujo}` con FKs y `relationship()`.
5. Usar `T.NOMBRE_TABLA` para `__tablename__` — nunca strings literales.

### Template

```python
from enum import auto
from typing import Optional
from sqlalchemy import ForeignKey, Integer, SmallInteger, String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from core.pipelines.{flujo}.attributes import {Flujo}Tables as T


class {Flujo}Base(DeclarativeBase):
    def columns(self) -> list[str]:
        return [c.key for c in self.__table__.columns]


class CatNombre({Flujo}Base):
    __tablename__ = T.CAT_NOMBRE
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class Stg{Flujo}({Flujo}Base):
    __tablename__ = T.STG_{FLUJO}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_NOMBRE}.id"), nullable=False)
    fecha_actualizacion: Mapped[Date] = mapped_column(Date, nullable=False)
    nombre_rel: Mapped["CatNombre"] = relationship()
```

> `nullable` en modelo coincide 1:1 con `NOT NULL` en SQL.
