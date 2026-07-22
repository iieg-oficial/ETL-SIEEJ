# Estándares y Convenciones de Datos — ETL-SIEEJ

> Referencia centralizada de las convenciones que ya existen, de forma implícita, en los pipelines del repositorio. Antes de este documento vivían dispersas entre `testing-checklist.md`, comentarios de código y el propio SQL de las migraciones.

---

## Índice

1. [Nomenclatura de tablas y vistas](#1-nomenclatura-de-tablas-y-vistas)
2. [La base de datos `cvegeo`](#2-la-base-de-datos-cvegeo)
3. [Tipos de datos estándar para campos comunes](#3-tipos-de-datos-estándar-para-campos-comunes)
4. [Normalización con `core/utils/`](#4-normalización-con-coreutils)

---

## 1. Nomenclatura de tablas y vistas

| Prefijo | Significado | Dónde se crea | Ejemplos |
|---|---|---|---|
| `cat_*` | Catálogos: dimensiones de referencia (listas de valores fijos) | `V2__catalogs*.sql` | `cat_actividades_economicas`, `cat_edad`, `cat_causa_defuncion` |
| `stg_*` | Staging: tabla principal donde `load.py` inserta los datos ya transformados | `V3__tables*.sql` | `stg_efipem`, `stg_enoe`, `stg_ganadera` |
| `vw_*` | Vista normal (`CREATE [OR REPLACE] VIEW`), joins de lectura sobre `stg_*`/`cat_*` | Migraciones posteriores (`V4`, `V5`...) | `vw_asg_imss`, `vw_delitos_serie_historica`, `vw_nacimientos` |
| `mv_*` | Vista materializada (`CREATE MATERIALIZED VIEW`), normalmente para consumo GIS o agregados costosos, con `REFRESH` disparado desde `load.py` | Migraciones de vistas materializadas | `mv_enoe_tasas`, `mv_nacimientos_adolescentes` |

**Excepciones a tener en cuenta:**
- Algunas vistas materializadas de uso GIS (`iieg_gis`) se nombran por el concepto de negocio, sin prefijo `mv_` — ejemplo: `brecha_salarial`, `delitos_fiscalia_feminicidio` en `migrations/asg_imss/sql/V6__vistas_materializadas_asg_imss.sql` y `migrations/fiscalia/sql/`. Si vas a crear una vista materializada nueva para consumo GIS, revisa el pipeline más reciente (`asg_imss` o `conapo`) como referencia antes de decidir si usa prefijo o no.
- No existe un prefijo `ce_view_*`/`ce_vista_*` en el código; si lo ves referenciado en algún lugar, es un error — el estándar real es `vw_*`/`mv_*`.

---

## 2. La base de datos `cvegeo`

`cvegeo` es una base de datos independiente (migración propia en `migrations/cvegeo/`) que centraliza el catálogo geográfico oficial de México (entidades y municipios). Los pipelines **no la copian**: la consultan en tiempo real vía Foreign Data Wrapper (FDW) de PostgreSQL.

### Tablas foráneas expuestas

```sql
CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_states (
    id      INTEGER,
    cve_ent INTEGER,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_states');

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id      INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');
```

Este bloque (`postgres_fdw` + `CREATE SERVER cvegeo_server` + `CREATE USER MAPPING` + las dos `CREATE FOREIGN TABLE`) es el patrón estándar y vive típicamente en `V1__foreign_tables.sql` de cada pipeline que lo necesita (ver `migrations/agropecuario_siap/sql/V1__foreign_tables.sql` como referencia).

### Relación con los pipelines

- `entidad_id` en un pipeline es una FK lógica hacia `cvegeo_states.id`
- `municipio_id` en un pipeline es una FK lógica hacia `cvegeo_municipalities.id`
- No son FKs declaradas a nivel de motor (son tablas foráneas de otra base), por lo que la relación normalmente solo queda documentada en un comentario junto a la columna, ej.:

```python
entidad_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ref. cvegeo_states
municipio_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ref. cvegeo_municipalities
```

- Antes de crear un pipeline nuevo que use geografía, levanta primero la base `cvegeo` (`just create-cvegeo-db user=sieej_user && just flyway-migrate cvegeo`, ver [`docs/nuevo_flujo.md`](nuevo_flujo.md)) y luego agrega el bloque FDW anterior a tu propia migración.

---

## 3. Tipos de datos estándar para campos comunes

| Campo | Tipo típico | Notas |
|---|---|---|
| `anio` | `INTEGER` | La mayoría de pipelines usa `Integer` (ej. `conapo`, `efipem`, `defunciones`). **Excepción:** `delitos_fuero_comun` usa `SmallInteger` — revisa el pipeline análogo antes de asumir `Integer` a ciegas. |
| `entidad_id` | `INTEGER` | FK lógica → `cvegeo_states.id` (ver sección 2). En pipelines con catálogo propio de entidad (ej. `asg_imss`) puede ser una FK real (`ForeignKey(T.CAT_ENTIDAD.id)`) en vez de apuntar directo a `cvegeo`. |
| `municipio_id` | `INTEGER` | FK lógica → `cvegeo_municipalities.id`, misma salvedad que `entidad_id`. |
| `valor*` | **No es un tipo único** — es un patrón de nombre | No existe una columna estándar llamada `valor` con tipo fijo `FLOAT`/`NUMERIC`. El patrón real es un prefijo/sufijo `valor_*` en el nombre de la columna, con tipo que varía según el pipeline: mayormente `Float` (ej. `valor_produccion` en `agropecuario_siap`, `valor_comercio` en `datamexico`, múltiples columnas `valor_*_mdp` en `censos_economicos`), pero `BigInteger` en `efipem.valor`. **Al definir un campo `valor_*` nuevo, elige el tipo según la naturaleza real del dato (moneda/proporción → `Float`; conteo entero grande → `BigInteger`), no asumas un tipo único.** |

---

## 4. Normalización con `core/utils/`

Todo pipeline debe apoyarse en las utilidades comunes en `core/utils/` para limpieza y normalización, en vez de reimplementar lógica ad hoc en cada `transform.py`.

### `lowercase_headers()` — `core/utils/normalize.py`

```python
def lowercase_headers(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = map(str.lower, df.columns)
```

Baja a minúsculas los nombres de columnas del DataFrame extraído, para que coincidan con los nombres definidos en `schemas.py`. Se aplica típicamente al inicio de `transform.py`, justo después de leer el inventario de `extract.py`.

> ⚠️ **Nota de corrección:** en `docs/nuevo_flujo.md` esta función aparece referenciada erróneamente como `normalize_headers`. El nombre real y correcto es **`lowercase_headers`**.

### `list_values_to_null()` — `core/utils/clean.py`

```python
def list_values_to_null(df: pd.DataFrame, rm_list: list = None) -> pd.DataFrame:
    rm_list = rm_list or ["NA", "N/A", "null", "nan", ""]
    ...
```

Convierte a `None` cualquier valor de columnas de texto que (después de limpiar espacios, comillas y espacios no-rompibles) coincida —sin distinguir mayúsculas/minúsculas— con alguno de los valores de `rm_list`, o que quede como cadena vacía.

- **Valores por defecto** si no se pasa `rm_list`: `["NA", "N/A", "null", "nan", ""]`
- **Parámetro `rm_list`**: cada pipeline puede extender esta lista con sus propios valores "sucios" observados en la fuente, definiéndola como constante (`NULL_VALUES`) en su `constants.py`/`consts.py` y pasándola explícitamente:

```python
# core/pipelines/agropecuario_siap/constants.py
NULL_VALUES = [
    "NA", "N/A", "null", "nan", "",
    # ... valores específicos de la fuente
]

# core/pipelines/agropecuario_siap/stages/transform.py
df = list_values_to_null(df, rm_list=NULL_VALUES)
```

Este patrón (`NULL_VALUES` en `constants.py`, importado en `transform.py`) es el estándar en la mayoría de pipelines (`censo_poblacion`, `conapo`, `centros_educativos`, `censos_economicos`, `denue`, entre otros).

---

## Referencias

- [`docs/nuevo_flujo.md`](nuevo_flujo.md) — flujo completo para crear un pipeline nuevo
- [`docs/testing-checklist.md`](testing-checklist.md) — checklist de verificación por pipeline
- [`docs/flyway.md`](flyway.md) — configuración y uso de migraciones
