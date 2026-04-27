---
name: eda-source
description: Proceso y formato de salida del análisis exploratorio (EDA) de una fuente CSV/Excel/API para alimentar el diseño de un pipeline SIEEJ. Define los criterios de detección de tipo, nulos, cardinalidad y el schema JSON que se entrega a los agentes `db` y `etl`.
argument-hint: <archivo_o_path> [nombre_pipeline]
---

# Skill: EDA de Fuente de Datos

Proceso y contrato de salida del análisis exploratorio. Úsalo cuando analices una fuente nueva para producir el input estructurado que consumen los siguientes agentes (`db` → `etl` → `docs`).

## Proceso de análisis

### 1. Lectura inicial

```python
import pandas as pd

# Excel: explorar hojas y header
xl = pd.ExcelFile("archivo.xlsx")
print("Hojas:", xl.sheet_names)
df = pd.read_excel(xl, sheet_name=0, nrows=50)

# CSV: detectar encoding y separador
df = pd.read_csv("archivo.csv", nrows=50, encoding="utf-8")
```

Detectar: nº de hojas, fila del header, nº de columnas, nº aproximado de registros, encoding, separador.

### 2. Perfilado por columna

```python
for col in df.columns:
    n_unique = df[col].nunique(dropna=True)
    null_pct = df[col].isna().mean() * 100
    sample = df[col].dropna().head(5).tolist()
    print(f"{col}: n={n_unique} nulls={null_pct:.1f}% sample={sample}")
```

### 3. Clasificación de tipo

| Tipo | Criterio |
|---|---|
| `numeric` | Todos los valores convertibles a `int`/`float`, sin texto libre |
| `date` | Patrones `DD/MM/YYYY`, `MM/YYYY`, `YYYY`, ISO 8601 |
| `boolean` | Cardinalidad ≤ 2 con valores Sí/No, True/False, 1/0, X/- |
| `geo_state` / `geo_municipality` | Nombres INEGI de entidad/municipio |
| `geo_coordinates` | Pares lat/lon o UTM |
| `categorical` | Cardinalidad < 50 con texto repetido → **candidato a catálogo** |
| `text` | Cardinalidad alta, descripciones largas |
| `id` | Valores únicos por fila (UUID, folio, código) |

### 4. Nulos y valores especiales

Strings que representan nulos: `"NO APLICA"`, `"NA"`, `"N/A"`, `"null"`, `"nan"`, `"NULL"`, `"S/D"`, `"NE"`, `"No aplica"`, `""`. Reportar también `NaN` reales.

### 5. Llave natural y estrategia de actualización

- Columna (o combinación) que identifica unívocamente cada registro.
- El `record_hash` solo aplica cuando la fuente entrega **archivos acumulativos mixtos** (viejos sin cambios + nuevos + existentes modificados). En ese caso, el hash permite (a) filtrar en O(1) las filas cuyo contenido ya está vigente y (b) detectar cambios para versionar. Ejemplo: `core/pipelines/repd/`.
- Decisión:
  - Llave estable **y** campos pueden cambiar entre cargas → **`scd2`** (requiere `HASH_FIELDS`).
  - Llave única **y** archivo solo agrega registros nuevos → **`upsert`**.
  - Archivo reemplaza todo en cada carga → **`bootstrap_only`**.
  - Sin llave natural clara → **`insert_only`** con deduplicación por hash de contenido.

### 6. Georreferencia (si aplica)

- Verificar compatibilidad de nombres con `cvegeo.municipalities` (columnas `nomgeo`, `nom_ent`).
- Recomendar normalización a UPPERCASE para el match.
- Identificar valores que no deben resolverse (ej: "EXTRANJERO", "SE IGNORA") → `SKIP_MUNICIPALITY_VALUES`.

### 7. Estrategia de DAGs

| Frecuencia | Modo |
|---|---|
| ≤ 3 meses | `bootstrap_and_update` — dual DAG |
| > 3 meses o única | `bootstrap_only` — solo DAG bootstrap |

Combinado con comportamiento de la fuente:

| Comportamiento | Estrategia |
|---|---|
| `sobreescribe` | `bootstrap_only` (re-ingestar todo) |
| `solo_nuevos` + llave estable | `upsert` |
| `mixto` (cambian registros existentes) | `scd2` |

---

## Contrato de salida (JSON)

Este es el output que consumen los agentes `db` y `etl`. No se puede omitir ningún campo obligatorio.

```json
{
  "pipeline_name": "{nombre}",
  "source": {
    "format": "Excel|CSV|API|Drive",
    "url_or_path": "...",
    "sheet_name": "DATOS",
    "header_row": 0,
    "encoding": "utf-8",
    "separator": ",",
    "approx_rows": 37000,
    "columns_count": 18
  },
  "columns": [
    {
      "original_name": "Nombre Original",
      "suggested_name": "nombre_interno",
      "type": "categorical|numeric|date|boolean|geo_state|geo_municipality|geo_coordinates|text|id",
      "nullable": true,
      "null_pct": 12.5,
      "cardinality": 7,
      "sample_values": ["val1", "val2"],
      "is_catalog_candidate": true,
      "catalog_table_name": "stg_{nombre}_cat_{col}",
      "max_length": 60,
      "notes": "observaciones"
    }
  ],
  "natural_key": ["columna_llave"],
  "update_strategy": "bootstrap_only|upsert|scd2|insert_only",
  "cvegeo_required": true,
  "cvegeo_columns": {
    "state": "col_estado",
    "municipality": "col_municipio",
    "skip_values": ["SE IGNORA", "EXTRANJERO"]
  },
  "constants": {
    "PIPELINE_NAME": "{nombre}",
    "NULL_VALUES": ["NO APLICA", "NA", "N/A", "null", "nan", ""],
    "COLUMN_RENAME_MAP": {"Nombre Original": "nombre_interno"},
    "DATE_COLUMNS": ["col_fecha"],
    "CATALOG_COLUMNS": ["col_cat1", "col_cat2"],
    "HASH_FIELDS": ["campo1", "campo2"]
  },
  "catalog_tables": [
    {
      "column": "col_cat",
      "table_name": "stg_{nombre}_cat_{col}",
      "max_length": 60,
      "sample_values": ["val1", "val2"]
    }
  ],
  "dag_schedule": {
    "mode": "bootstrap_only|bootstrap_and_update",
    "update_cron": "0 3 1 * *",
    "reasoning": "Explicación breve"
  },
  "preprocessing_notes": [
    "Header en fila 13 (index 12)",
    "Fechas en formato MM/YYYY",
    "Municipios requieren UPPER para match con cvegeo"
  ]
}
```

### Reglas del JSON

- `suggested_name` debe ser `snake_case` ASCII sin acentos.
- `max_length` se calcula como `max(len(v))` de los valores únicos, redondeado al múltiplo de 10 superior.
- `HASH_FIELDS` solo presente si `update_strategy == "scd2"`.
- `cvegeo_columns` solo presente si `cvegeo_required == true`.
- `catalog_tables` debe contener **solo** las columnas con `is_catalog_candidate: true`.

## Presentación al usuario (antes de continuar con DB)

Resumen ejecutivo que complementa al JSON:

1. Nº de registros y columnas de la fuente.
2. Lista de catálogos que se van a crear (nombre + valores ejemplo).
3. Llave natural propuesta.
4. Estrategia de update + cron sugerido.
5. Alertas de preprocessing (headers especiales, encoding, valores raros).

## Referencias

- `core/pipelines/repd/consts.py` — constantes completas (patrón SCD2).
- `core/pipelines/fiscalia/consts.py` — catálogos mixtos.
- `core/utils/clean.py`, `normalize.py`, `parse_datetime.py` — utilidades de transformación disponibles.
