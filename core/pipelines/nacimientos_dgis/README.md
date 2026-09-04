# nacimientos_dgis

## Descripción general

Nacimientos registrados en el **SINAC** (Subsistema de Información sobre Nacimientos) y publicados como datos abiertos por la **DGIS** de la Secretaría de Salud. La fuente es un microdato: una fila por nacimiento. El pipeline se queda sólo con los nacimientos de **madres residentes en Jalisco** y los agrega a un grano de `año × municipio × edad de la madre`, guardando el total de nacimientos y tres conteos sobre la edad del padre.

Sobre esa base agregada la carga calcula dos indicadores municipales: **tasa de fecundidad general** y **fecundidad adolescente e infantil** (madres de 10-14 y de 15-19 años), cruzando contra la población femenina de `conapo` por FDW.

No confundir con el pipeline `defunciones`, que también viene de la DGIS pero cubre mortalidad.

## Fuente general

http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_nacimientos_gobmx.html

## Fuente específica

```shell
SOURCE_URL=http://www.dgis.salud.gob.mx/descargas/datosabiertos/nacimientos/sinac_{year}.zip
```

Un ZIP por año. El extract prueba año por año desde `START_YEAR` hasta el año en curso y trata el `404` como "esa edición todavía no existe".

**El ZIP no siempre trae el CSV al primer nivel.** Las ediciones viejas lo entregan directo; la de 2025 lo envuelve en un segundo ZIP (`sinac_2025.zip` → `.../sinac_2025.zip` → `Nacimientos_2025.csv`). `_extract_csv_bytes` desciende recursivamente hasta encontrar el CSV, así que ambos formatos funcionan sin tocar nada.

Del CSV se leen sólo cinco columnas (`USECOLS`): `ENTIDADRESIDENCIA`, `MUNICIPIORESIDENCIA`, `EDAD`, `EDADPADRE`, `FECHANACIMIENTO`.

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `2025` |
| Frecuencia de actualización | Anual |
| Desagregación | Municipal |
| ¿Tiene update? | Sí |
| Update | Automático |

## Diagrama de entidad relación

![ERD](assets/erd.svg)

```shell
python scripts/generate_erds.py nacimientos_dgis
```

## Diccionario de variables

### stg_nacimientos

Tabla base del pipeline. Grano: `anio × cve_geo × edad_madre` (constraint `uq_nacimientos_anio_geo_edad`). Es `UNLOGGED`: se reconstruye desde la fuente, no se replica.

| variable | descripción |
|---|---|
| `id` | Identificador único de la fila (surrogate) |
| `anio` | Año de nacimiento, tomado de `FECHANACIMIENTO` |
| `cve_geo` | Clave geoestadística del municipio de residencia de la madre (`EEMMM`, calculada como `ENTIDADRESIDENCIA * 1000 + MUNICIPIORESIDENCIA`) |
| `edad_madre` | Edad de la madre al momento del nacimiento |
| `tot_nac` | Total de nacimientos del grupo |
| `nac_padre_conocido` | Nacimientos con edad del padre conocida (no nula y distinta de los centinelas `888` y `999`) |
| `nac_padre_18_mas` | Nacimientos con padre de 18 años o más |
| `nac_padre_25_mas` | Nacimientos con padre de 25 años o más |
| `fecha_actualizacion` | Fecha en que el pipeline transformó la fila |

### stg_tasa_fecundidad

Tabla calculada en SQL a partir de `stg_nacimientos` y `conapo_poblacion`. Grano: `año × municipio`.

| variable | descripción |
|---|---|
| `fecha` | 1 de enero del año del periodo |
| `entidad_id` | Clave de la entidad (`14`, constante) |
| `municipio_id` | Clave del municipio con cero a la izquierda (`CHAR(5)`) |
| `pob_mujeres_15_49` | Mujeres de 15 a 49 años, suma de los siete grupos quinquenales de CONAPO |
| `nacimientos` | Nacimientos del municipio en el año, todas las edades de la madre |
| `tasa_fec_gen` | Tasa de fecundidad general por cada 1,000 mujeres de 15 a 49 años |

### stg_nacimientos_adolescentes

Tabla calculada en SQL. Grano: `año × municipio`. Cubre dos grupos de edad de la madre en paralelo: 10-14 (infantil) y 15-19 (adolescente).

| variable | descripción |
|---|---|
| `fecha` | 1 de enero del año del periodo |
| `entidad_id` / `municipio_id` | Claves de entidad y municipio |
| `nac_madres_10_14` | Nacimientos de madres de 10 a 14 años |
| `tasa_esp_fec_madres_10_14` | Tasa específica por cada 1,000 mujeres de 10 a 14 años |
| `pct_padres_18_mas_madres_10_14` | Porcentaje de esos nacimientos con padre de 18 años o más |
| `pct_edad_padre_sin_dato_madres_10_14` | Porcentaje sin dato de edad del padre |
| `nac_madres_15_19` | Nacimientos de madres de 15 a 19 años |
| `tasa_esp_fec_madres_15_19` | Tasa específica por cada 1,000 mujeres de 15 a 19 años |
| `pct_padres_25_mas_madres_15_19` | Porcentaje de esos nacimientos con padre de 25 años o más |
| `pct_edad_padre_sin_dato_madres_15_19` | Porcentaje sin dato de edad del padre |

Los dos porcentajes de "sin dato" se calculan como `(tot_nac - nac_padre_conocido) / tot_nac`, así que miden cobertura de la variable, no un hecho demográfico.

### Vistas

| objeto | tipo | qué entrega |
|---|---|---|
| `vw_nacimientos` | vista | `stg_nacimientos` con `municipio` y `entidad` resueltos por FDW |
| `vw_tasa_fecundidad` | vista | `stg_tasa_fecundidad` con nombres de municipio y entidad |
| `vw_nacimientos_adolescentes` | vista | `stg_nacimientos_adolescentes` con nombres de municipio y entidad |
| `tasa_fecundidad` | materializada | Tasa de fecundidad general con geometría municipal, lista para publicar |
| `nacimientos_adolescentes` | materializada | Grupo 15-19 con geometría municipal |
| `nacimientos_infantiles` | materializada | Grupo 10-14 con geometría municipal |

Las tres materializadas parten de `cvegeo_municipalities CROSS JOIN` las fechas distintas, así que **siempre traen los 125 municipios por año**, con `0` donde no hubo nacimientos del grupo. Se crean `WITH NO DATA` y las refresca el load.

## Migraciones

| migración | descripción |
|---|---|
| `V1__foreign_tables.sql` | Extensiones `postgres_fdw` y `postgis`, servidores `cvegeo_server` y `conapo_server`, y foreign tables `cvegeo_states`, `cvegeo_municipalities` y `conapo_poblacion` |
| `V2__tables_nacimientos_dgis.sql` | Crea `stg_nacimientos` (`UNLOGGED`) con su constraint único |
| `V3__views_nacimientos_dgis.sql` | Vista `vw_nacimientos` |
| `V4__tables_calculated.sql` | Crea `stg_tasa_fecundidad` y `stg_nacimientos_adolescentes` |
| `V5__views_calculated.sql` | Vistas `vw_tasa_fecundidad` y `vw_nacimientos_adolescentes` |
| `V6__mv_tasa_fecundidad.sql` | Materializada `tasa_fecundidad` con geometría, `WITH NO DATA` |
| `V7__mv_nacimientos_adolescentes.sql` | Materializada `nacimientos_adolescentes` (15-19), `WITH NO DATA` |
| `V8__mv_nacimientos_infantiles.sql` | Materializada `nacimientos_infantiles` (10-14), `WITH NO DATA` |
| `V9__comments.sql` | `COMMENT ON` de tablas, vistas y materializadas con sus columnas |
| `V10__fdw_placeholders_por_nombre_db.sql` | Pasa `conapo_server` a placeholders Flyway (`${fdw_conapo_*}`); en `V1` el `dbname` estaba escrito a mano |

## Variables de entorno

| variable | descripción |
|---|---|
| `DB_*` | Conexión a la base `nacimientos_dgis` |
| `LOG_LEVEL` | Nivel de log del pipeline |
| `SOURCE_URL` | Plantilla de descarga del ZIP anual, con `{year}` |
| `START_YEAR` | Primer año a descargar en bootstrap (por defecto `2020`) |

Los placeholders `${fdw_*}` y `${fdw_conapo_*}` de las migraciones los resuelve la configuración de Flyway, no este `.env`. Ver `docs/flyway.md`.

## Notas metodológicas

### Extract

Una tarea por año, desde `START_YEAR` hasta el año en curso. Descarga el ZIP, desciende hasta el CSV, lee las cinco columnas de `USECOLS` y deja un `sinac_{year}.pkl` en `data/extract/nacimientos_dgis/`. Si el pkl ya existe lo reusa sin volver a descargar. Un `404` devuelve `None` y no falla la tarea.

### Transform

Lee todos los `sinac_*.pkl` del directorio de extract y procesa año por año:

- **Filtro geográfico**: sólo `ENTIDADRESIDENCIA = 14`. El criterio es **residencia de la madre**, no lugar de ocurrencia del parto.
- **Clave municipal**: `cve_geo = entidad * 1000 + municipio`.
- **Año**: se toma de `FECHANACIMIENTO` (`%d/%m/%Y`), no del nombre del archivo.
- **Descarte**: se eliminan las filas sin `anio`, sin `cve_geo` o sin `EDAD`.
- **Edad del padre**: `888` y `999` son centinelas de "no especificado" y se tratan como desconocido, no como edades.
- **Agregación**: `groupby(anio, cve_geo, EDAD)` con el conteo total y las tres banderas de edad del padre sumadas.

El resultado se guarda en `data/transform/nacimientos_dgis/nacimientos.pkl`.

### Load

Cuatro pasos en la misma corrida:

1. En modo `bootstrap`, `TRUNCATE stg_nacimientos RESTART IDENTITY`. En modo `update` no se trunca.
2. `COPY` de las filas agregadas desde un buffer en memoria (`COPY_COLS` fija el orden de las columnas).
3. Repobla las dos tablas calculadas con `DELETE` + `INSERT ... SELECT`, cruzando contra `conapo_poblacion` por `(municipio_id, anio, sexo_id = 2)`.
4. `REFRESH MATERIALIZED VIEW` de las tres materializadas.

Al terminar, `cleanup_pipeline_data` borra los pkl de extract y transform.

## Ejecución

**Bootstrap** (carga inicial de todos los años desde `START_YEAR`):

```shell
just create-db nacimientos_dgis
just flyway-migrate nacimientos_dgis
python dags/etl_nacimientos_dgis.py
```

También como DAG bajo demanda: `etl_nacimientos_dgis_bootstrap`.

**Update** (anual, DAG `etl_nacimientos_dgis_update`, schedule `0 14 1 1 *`, "cada año, el 1 de enero"):

Consulta el `anio` máximo cargado y arranca en el siguiente, así que no vuelve a descargar lo que ya está en la base. Si no hay años nuevos, la corrida no hace nada.

## Notas adicionales

- **El año sale del hecho, no del archivo.** `sinac_{year}.zip` agrupa por año de registro, pero `anio` se deriva de `FECHANACIMIENTO`. Un archivo puede contener nacimientos de años anteriores, y esas filas chocarían contra `uq_nacimientos_anio_geo_edad` en un `update` (que no trunca). Es el punto a vigilar en la primera actualización automática; el `bootstrap` no lo sufre porque limpia la tabla.
- **Las tasas dependen de `conapo`.** El denominador viene por FDW de `conapo.stg_poblacion_mitad_anio` con `sexo_id = 2` (mujeres). Un año sin proyección de CONAPO simplemente no aparece en `stg_tasa_fecundidad` ni en `stg_nacimientos_adolescentes`, porque el cruce es un `JOIN`, no un `LEFT JOIN`. Con `START_YEAR = 2020` el rango cubierto por las proyecciones vigentes alcanza, pero conviene revisarlo al extender la serie hacia atrás.
- **`2019` sí existe en la fuente.** `START_YEAR` está en `2020` por decisión de cobertura, no por un límite del servidor.
- **El último año publicado es parcial.** La DGIS libera la edición del año en curso con avance preliminar; los totales de ese año se mueven en cada actualización.
- **Geografía por FDW.** Municipios y entidades viven en la base `cvegeo` y se consultan por foreign table, según `docs/estandares_datos.md`. `stg_nacimientos` guarda `cve_geo` como entero, sin cero a la izquierda; las tablas calculadas y las materializadas lo emiten como `CHAR(5)` con `LPAD`.
- **Erratas en nombres de columnas de las materializadas.** `nacimientos_madre_adelocente` y `tasa_fecundidad_adolecente` en `nacimientos_adolescentes` están mal escritos. Se conservan tal cual porque ya son contrato de los consumidores publicados.
