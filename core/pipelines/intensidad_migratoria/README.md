# Pipeline: Intensidad Migratoria

Pipeline ETL para el Índice de Intensidad Migratoria (IIM) publicado por CONAPO.

## Fuentes de datos

| Fuente | Tipo | Nivel geográfico |
|---|---|---|
| IIM 2010 | XLS | Municipio |
| IIM 2020 | CSV | Municipio |
| IIM 2020 | CSV | Entidad |

URLs configuradas en `.env` como `IIM_URL_MUNICIPAL_2010`, `IIM_URL_MUNICIPAL_2020`, `IIM_URL_ESTATAL_2020`. Todas requieren `verify=False`.

## Tablas

```
iim_municipal                          iim_estatal
──────────────────────────────         ──────────────────────────────
id            SERIAL PK                id            SERIAL PK
municipio_id  INTEGER NOT NULL         entidad_id    INTEGER NOT NULL
viv_totales   INTEGER                  viv_totales   INTEGER
por_viv_remesas    FLOAT               por_viv_remesas    FLOAT
por_viv_emigrantes FLOAT               por_viv_emigrantes FLOAT
por_viv_reto  FLOAT                    por_viv_reto  FLOAT
iim_dp2       FLOAT                    iim_dp2       FLOAT
fecha         INTEGER NOT NULL         fecha         INTEGER NOT NULL
UNIQUE (municipio_id, fecha)           UNIQUE (entidad_id, fecha)
```

`municipio_id` usa el código cvegeo de 5 dígitos (EEMMMM). `fecha` = año del censo (2010 o 2020).

## Flujo

- **Extract**: descarga 3 archivos vía HTTPS con SSL deshabilitado, cachea en pkl.
- **Transform**: construye `municipio_id` cvegeo desde `ENT`+`MUN` para 2010, filtra fila nacional (`entidad_id = 0`) en estatal, concatena 2010+2020 en `iim_municipal`.
- **Load**: `bulk_insert` para ambas tablas.

## Vistas

- `view_iim_entidades` — todas las entidades con nombre, lugar por `iim_dp2` ascendente y año.
- `view_iim_municipios_jalisco` — municipios de Jalisco con clave y nombre.

## Periodicidad

Bootstrap único bajo demanda. Sin actualizaciones (publicación decenal).
