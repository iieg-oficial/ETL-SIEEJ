# Refactor: Legacy SQLAlchemy + Alembic → ETL-SIEEJ Stack

Lee el archivo `refactor/$ARGUMENTS.txt` con la herramienta Read antes de continuar. Ese archivo contiene el código de otra repo que usa una versión anterior de SQLAlchemy (estilo clásico 1.x) con migraciones en Alembic. Tu tarea es refactorizarlo al flujo actual del proyecto, siguiendo todas las reglas definidas en CLAUDE.md y los archivos de reglas en `.claude/rules/`.

Lee estas instrucciones completamente antes de empezar.

---

## Paso 1: Analizar el código recibido

Antes de escribir nada, identifica:

1. **Modelos ORM** — tablas, columnas, tipos, relaciones, constraints
2. **Migraciones Alembic** — qué tablas se crean, en qué orden, con qué FKs
3. **Queries / lógica de negocio** — cómo se insertan, actualizan o consultan datos
4. **Dependencias externas** — librerías, conexiones, configuración

Pregunta al usuario si hay algo que no quede claro del código recibido antes de continuar.

---

## Paso 2: Leer referencias del proyecto

Lee antes de escribir cualquier archivo:

- `core/pipelines/establecimientos_de_salud/schemas.py`
- `core/pipelines/establecimientos_de_salud/attributes/establecimientos.py`
- `core/pipelines/centros_educativos/schemas.py`
- `core/pipelines/centros_educativos/attributes/centros_educativos.py`
- `migrations/establecimientos_de_salud/sql/V1__foreign_tables.sql`
- `migrations/centros_educativos/sql/V1__foreign_tables.sql`

---

## Paso 3: Refactorizar schemas

Convierte los modelos SQLAlchemy 1.x al estilo 2.0 con `Mapped` y `mapped_column`:

**Antes (1.x):**
```python
class MyTable(Base):
    __tablename__ = 'my_table'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

**Después (2.0):**
```python
class MyTable(MyPipelineBase):
    __tablename__ = T.MY_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
```

Reglas obligatorias:
- Usar `Mapped` y `mapped_column` — nunca el estilo `Column(...)` suelto
- Usar `Text` en lugar de `String` para columnas de texto
- Heredar del `Base` específico del pipeline, no de un `Base` global
- Nombres de tablas mediante enum `T.TABLE_NAME` definido en `attributes.py`
- Tablas en minúsculas, sin acentos, sin ñ (→ ni), con guiones bajos, en plural
- FKs: `nombre_tabla_singular_id` → `ForeignKey(f"{T.TABLA}.id")`
- Tabla principal con `fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)` salvo que haya catálogo de periodos

Crear:
- `core/pipelines/{pipeline}/attributes.py` o `attributes/` (folder form si hay múltiples enums)
- `core/pipelines/{pipeline}/schemas.py`

---

## Paso 4: Convertir migraciones Alembic → Flyway

Alembic usa scripts Python con `upgrade()`/`downgrade()`. Flyway usa SQL plano versionado.

Estructura de archivos a crear en `migrations/{pipeline}/sql/`:

| Archivo | Contenido |
|---|---|
| `V1__foreign_tables.sql` | postgres_fdw + tablas foráneas (cvegeo) |
| `V2__catalogs_{pipeline}.sql` | Tablas catálogo / secundarias |
| `V3__tables_{pipeline}.sql` | Tablas principales con FKs |
| `V4__views_{pipeline}.sql` | Vistas que joinean con cvegeo |

Reglas:
- SQL puro, sin lógica Python
- El orden de `V1`, `V2`, `V3` debe respetar dependencias de FKs
- Verificar que nullable en SQL coincida con el schema SQLAlchemy
- La vista en `V4` es siempre requerida

Lee las migraciones de referencia antes de escribir:
- `migrations/establecimientos_de_salud/sql/`
- `migrations/centros_educativos/sql/`

Crear también:
- `migrations/{pipeline}/flyway.conf`
- `migrations/{pipeline}/flyway.conf.example`

---

## Paso 5: Adaptar lógica de negocio

Si el código original tiene lógica de inserción, actualización o consulta:

- Reemplazar `session.add()` / `session.bulk_insert_mappings()` por los utilitarios del proyecto:
  - `insert_records` — inserts simples
  - `upsert_records` — upserts con conflict_keys
  - `count_records` — conteo de registros
  - `sync_id_sequence` — sincronizar secuencia SERIAL tras insert con IDs manuales
- Reemplazar queries en estilo 1.x (`session.query(Model).filter(...)`) por estilo 2.0 (`select(Model).where(...)`)

Lee antes:
- `core/utils/bulk_ops.py`
- `core/utils/mappings.py`

---

## Paso 6: Verificación

Revisar:
- [ ] Todos los modelos usan `Mapped` y `mapped_column`
- [ ] Nombres de tablas en plural, minúsculas, sin acentos
- [ ] FKs con nombre correcto (`tabla_singular_id`)
- [ ] Migraciones SQL en orden correcto de dependencias
- [ ] Nullable en SQL coincide con el schema
- [ ] SERIAL `id` excluido de listas de INSERT
- [ ] `sync_id_sequence` llamado tras catálogos con IDs manuales
- [ ] No hay imports de Alembic ni SQLAlchemy 1.x en el código resultante
- [ ] Sin docstrings, sin comentarios, sin emojis

---

## Paso 7: Preguntar al usuario

Al terminar, preguntar:
- "¿Hay alguna tabla o relación del código original que no haya quedado clara?"
- "¿Se necesita adaptar también el extract/transform/load o solo schemas y migraciones?"
