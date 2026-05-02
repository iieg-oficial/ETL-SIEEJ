---
paths:
  - "core/pipelines/**"
  - "migrations/**/*.sql"
---

# Database Rules

## Version

Use SQLAlchemy 2.0 with the new mapping style (Mapped, mapped_column). Do not use the classic SQLAlchemy 1.x style.

## Table naming

- Lowercase only
- No accents; replace ñ with ni
- Underscores instead of spaces
- Plural form
- No prefixes or suffixes

## Primary keys

Every table must have an `id` column as unique identifier:

```python
class TiposSostenimiento(CentrosEducativosBase):
    __tablename__ = T.TIPOS_SOSTENIMIENTO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tipo_sostenimiento: Mapped[str] = mapped_column(Text, nullable=False)
```

## Foreign keys

Columns referencing other tables must be named `{singular_table_name}_id`:

```python
class Colonias(CentrosEducativosBase):
    __tablename__ = T.COLONIAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    colonia: Mapped[str] = mapped_column(Text, nullable=False)
    localidad_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.LOCALIDADES}.id"), nullable=False)
```

## Summary

| Element | Rule | Example |
|---|---|---|
| Table names | Lowercase, no accents, ñ → ni, underscores, plural | `tipos_sostenimiento`, `municipios` |
| Foreign keys | singular_table_name + `_id` | `localidad_id`, `municipio_id` |
| Primary key | `id` | `id: Mapped[int]` |
| Data content | Accents allowed | `"Tláquepaque"` |
| Proper names | `title()` in Python | `"san pedro tlaquepaque"` → `"San Pedro Tlaquepaque"` |
| Descriptions | Capitalize first letter | `"Clave de municipio"` |
