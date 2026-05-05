---
name: cvegeo-integration
description: Integración de un pipeline SIEEJ con la base de datos `cvegeo` vía FDW. Cubre la migración SQL, el setup con `just`, la resolución de municipios en `load.py` y los patrones de relación. Úsalo cuando un pipeline requiera georreferenciar entidades/municipios INEGI.
argument-hint: <pipeline>
---

# Skill: Integración cvegeo (FDW)

Fuente única para conectar un pipeline a la base `cvegeo` del IIEG, que contiene las claves oficiales INEGI de entidades federativas y municipios.

## Arquitectura

```
BD del pipeline ({pipeline})           BD cvegeo
+-----------------------------+        +---------------------------+
| stg_{pipeline}_datos        |        | public.municipalities     |
|   municipio_id ─────────────┼──FDW──>| id, cvegeo, cve_ent,      |
|                             |        | cve_mun, nomgeo, nom_ent  |
+-----------------------------+        +---------------------------+

Resolución: (estado_upper, municipio_upper) → municipio_id
```

La tabla en la BD del pipeline es **foreign** (FDW via `postgres_fdw`). No se duplica el catálogo; las consultas se resuelven cruzando con joins.

## 1. Migración SQL

Colocar en `migrations/{pipeline}/sql/V2__cvegeo.sql` (antes de la tabla principal que referencia `municipio_id`):

```sql
-- =======================================================================
-- V2__cvegeo.sql  |  Pipeline: {pipeline}
-- Foreign Data Wrapper hacia la BD cvegeo del IIEG.
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS cvegeo_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'localhost', port '5432', dbname 'cvegeo');

-- Las credenciales reales se inyectan al correr la migración con flyway.conf
CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
    SERVER cvegeo_server
    OPTIONS (user '', password '');

CREATE FOREIGN TABLE IF NOT EXISTS public.cvegeo_municipalities (
    id      INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR
) SERVER cvegeo_server
    OPTIONS (schema_name 'public', table_name 'municipalities');
```

Luego, la tabla principal referencia `municipio_id INTEGER` **sin FK formal** (el planificador FDW no soporta FKs entre servers). La integridad se garantiza en el loader.

## 2. Setup inicial con `just`

Una sola vez por entorno de desarrollo, antes del primer `flyway-migrate` del pipeline que usa cvegeo:

```bash
# Levantar postgres-dev si no está corriendo
just build-dev user=sieej_user pass=mi_pass db={pipeline}

# Crear la BD cvegeo y poblarla (si no existe)
just create-cvegeo-db user=sieej_user
just flyway-migrate cvegeo

# Migrar el pipeline (que incluye V2__cvegeo.sql)
just flyway-config {pipeline}   # editar migrations/{pipeline}/flyway.conf con credenciales
just flyway-migrate {pipeline}
```

## 3. Configuración en `consts.py`

```python
# Valores que NO deben resolverse contra cvegeo (se insertan como NULL)
SKIP_MUNICIPALITY_VALUES = frozenset({
    "SE IGNORA",
    "EXTRANJERO",
    "NO ESPECIFICADO",
})

# Columnas a resolver: (col_municipio, col_estado, col_id_destino)
MUNICIPALITY_COLUMNS = [
    ("disappearance_municipality", "disappearance_state_name", "disappearance_municipality_id"),
    ("location_municipality",     "location_state_name",     "location_municipality_id"),
]
```

## 4. Normalización en `transform.py`

Antes de buscar en el cache, normalizar estado y municipio a UPPERCASE sin acentos:

```python
from core.utils.normalize import uppercase_col

for _, state_col, _ in MUNICIPALITY_COLUMNS:
    if state_col in df.columns:
        uppercase_col(df, state_col)

for muni_col, _, _ in MUNICIPALITY_COLUMNS:
    if muni_col in df.columns:
        uppercase_col(df, muni_col)
```

## 5. Resolución de IDs en `load.py`

```python
from core.utils.bulk_ops import get_cvegeo_mapping

# En source() o al inicio de action()
with self.db.get_session() as session:
    # Cache de (estado_upper, municipio_upper) → municipio_id
    self._municipality_cache = get_cvegeo_mapping(session)

# Resolución por columna
def _resolve_municipality_ids(self, df: pd.DataFrame) -> pd.DataFrame:
    for muni_col, state_col, id_col in MUNICIPALITY_COLUMNS:
        def resolve(row) -> Optional[int]:
            muni = row.get(muni_col)
            state = row.get(state_col)
            if not muni or muni in SKIP_MUNICIPALITY_VALUES:
                return None
            return self._municipality_cache.get((state, muni))

        df[id_col] = df.apply(resolve, axis=1)

        # Reportar unmatched
        unmatched = df[df[id_col].isna() & df[muni_col].notna() &
                       ~df[muni_col].isin(SKIP_MUNICIPALITY_VALUES)]
        if not unmatched.empty:
            self.logger.warning(
                f"{len(unmatched)} municipios sin match en {muni_col}"
            )
    return df
```

## 6. Vista analítica

En `V4__vista.sql` hacer el join con `cvegeo_municipalities` para exponer nombres humanos:

```sql
CREATE OR REPLACE VIEW public.vw_{pipeline}_datos AS
SELECT
    d.id,
    d.llave_natural,
    d.fecha_dato,
    m.nomgeo   AS municipio,
    m.nom_ent  AS entidad,
    m.cve_ent,
    m.cve_mun,
    m.cvegeo
FROM public.stg_{pipeline}_datos d
LEFT JOIN public.cvegeo_municipalities m ON m.id = d.municipio_id;
```

## 7. Variables de entorno

En Docker, el FDW apunta a `host.docker.internal:5432/cvegeo`. Ajustar `OPTIONS (host ...)` en la migración o reemplazar en un `V{n+1}__fdw_docker.sql` específico si es necesario.

## Pitfalls comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `relation "cvegeo_municipalities" does not exist` | FDW no creado | Ejecutar V2__cvegeo.sql |
| `password authentication failed for user` | USER MAPPING vacío | Editar el USER MAPPING con credenciales reales tras correr Flyway |
| `server "cvegeo_server" does not exist` | `create-cvegeo-db` no se ejecutó | `just create-cvegeo-db` + `just flyway-migrate cvegeo` |
| Muchos municipios sin match | Falta UPPER o hay acentos | Aplicar `uppercase_col` en transform |
| Colisión de municipios entre estados | Match solo por nombre | Usar tupla compuesta `(estado, municipio)` |

## Referencias

- `migrations/repd/sql/V1__catalogos_repd.sql` — FDW + catálogos (canónico).
- `core/pipelines/repd/stages/load.py` — `_load_municipality_cache` y `_resolve_municipality_ids`.
- `core/utils/bulk_ops.py` — `get_cvegeo_mapping()`.
- `migrations/cvegeo/sql/` — BD base cvegeo (ya existe; no reimplementar).
