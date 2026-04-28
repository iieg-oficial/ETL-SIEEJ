---
name: eda-reporte
description: Plantilla JSON estandarizada para reportes de Análisis Exploratorio de Datos (EDA) consumidos por los agentes DB y ETL.
---

## Cuándo usar

Al cierre de cada script EDA en `core/pipelines/{flujo}/eda/`. El output JSON es el contrato que consumen `db-agent` y `etl-agent`.

## Ubicación del reporte

```
core/pipelines/{flujo}/eda/reporte_{nombre}.json
```

Donde `{nombre}` describe la fuente o nivel (ej: `reporte_municipal_2024.json`).

## Esquema JSON

```json
{
  "pipeline": "{flujo}",
  "source": {
    "name": "Nombre humano de la fuente",
    "publisher": "INEGI / Secretaría / etc.",
    "url": "https://...",
    "format": "csv | xlsx | zip | api | json",
    "encoding": "utf-8 | iso-8859-1",
    "frequency": "anual | mensual | on-demand | ...",
    "iterable": true,
    "iterable_param": "year | entidad | null"
  },
  "files": [
    {
      "name": "archivo.csv",
      "rows": 12345,
      "columns": 30,
      "header_rows_to_skip": 0,
      "footer_rows_to_skip": 0
    }
  ],
  "schema": {
    "columns": [
      {
        "source_name": "NOM_ENT",
        "proposed_name": "entidad",
        "dtype": "string | int | float | date | datetime | bool",
        "nullable": false,
        "unique_values": 32,
        "sample": ["Aguascalientes", "Baja California"],
        "is_key": false,
        "is_geo": true,
        "is_date": false,
        "is_catalog_candidate": true,
        "notes": "Catálogo natural; FK a cve_geo"
      }
    ]
  },
  "geo_level": "nacional | estatal | municipal | localidad | mixto",
  "nulls": {
    "raw_tokens": ["NA", "N/A", "S/D", "ND", "--"],
    "by_column": {
      "col_x": 12,
      "col_y": 0
    }
  },
  "catalog_candidates": [
    {
      "proposed_table": "cat_tipo_centro",
      "source_column": "TIPO_CENTRO",
      "values": ["Primaria", "Secundaria", "Bachillerato"]
    }
  ],
  "main_tables": [
    {
      "proposed_table": "stg_centros",
      "primary_keys_source": ["CCT"],
      "fact_columns": ["alumnos", "docentes"]
    }
  ],
  "update_strategy": {
    "variant": "append | scd2",
    "monitored_columns": ["alumnos", "docentes"],
    "rationale": "La fuente sustituye registros previos al actualizar matrícula."
  },
  "open_questions": [
    "¿La fuente publica la columna XYZ en todos los años?"
  ]
}
```

## Reglas

- Todos los campos del esquema son requeridos. Si no aplica, usar `null` (no omitir).
- `proposed_name` ya en snake_case en español, sin acentos.
- `iterable=false` ⇒ `iterable_param=null`.
- `update_strategy.variant` debe alinear con el skill `bootstrap-update-rules`.
- `open_questions` se discuten con el usuario antes de pasar a la Fase 2.
