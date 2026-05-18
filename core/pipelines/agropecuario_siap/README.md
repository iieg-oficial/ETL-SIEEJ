# Pipeline: agropecuario_siap

Pipeline ETL para la descarga y carga de datos agrícolas del SIAP (Servicio de Información Agroalimentaria y Pesquera).

## ERD

![ERD](assets/erd.svg)

## Fuente de datos

- **Organismo:** SIAP — Secretaría de Agricultura y Desarrollo Rural
- **URL:** `https://nube.agricultura.gob.mx/index.php?view=10AE434F-A2158368-A120BC5A-EDF4AFAA&ANIO={anio}`
- **Formato:** CSV (encoding latin-1)
- **Parámetro iterable:** año (`anio`), desde 2003 en adelante
- **Frecuencia de actualización:** anual

## Tablas generadas

| Tabla | Descripción | Filas aprox. |
|---|---|---|
| `stg_agricola` | Producción agrícola por municipio, cultivo, ciclo y modalidad | ~30,000/año |
| `cat_cultivos` | Catálogo de cultivos agrícolas | ~300 |
| `cat_unidades_medida` | Unidades de medida de producción | ~6 |
| `cat_modalidades` | Modalidades hídricas (Riego, Temporal) | 2 |
| `cat_ciclos` | Ciclos productivos (Otoño-Invierno, Primavera-Verano, Perenne) | 3 |
| `cat_ctrs_apoyo_des_rural` | Centros de Apoyo al Desarrollo Rural | ~20 |
| `cat_distritos_des_rural` | Distritos de Desarrollo Rural | ~190 |

## DAGs

- **`etl_agropecuario_siap_bootstrap`** — Carga inicial completa (2003 a END_DATE). Schedule: None (on-demand)
- **`etl_agropecuario_siap_update`** — Actualización incremental desde el último año en DB. Schedule: `@yearly`

## Variables de entorno

| Variable | Descripción |
|---|---|
| `SIAP_URL` | URL template de la API (con `{anio}`) |
| `START_DATE` | Año de inicio del bootstrap (default: 2003) |
| `END_DATE` | Año fin del bootstrap (default: 2024) |
| `DB_*` | Conexión a PostgreSQL |

## Instrucciones para actualizar

1. Crear o actualizar `.env` en `core/pipelines/agropecuario_siap/`
2. Ejecutar flyway: `just flyway-reset agropecuario_siap` (solo si es primer deploy)
3. Para carga inicial: activar DAG `etl_agropecuario_siap_bootstrap` en Airflow
4. Para actualización anual: el DAG `etl_agropecuario_siap_update` se ejecuta automáticamente con schedule `@yearly`

## Vista disponible

- `view_agricola_jalisco` — datos agrícolas filtrados para Jalisco (cve_ent = 14) con nombres de municipio, entidad, cultivo, ciclo, modalidad, etc.
