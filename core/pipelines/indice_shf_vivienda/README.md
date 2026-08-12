# indice_shf_vivienda

Índice SHF de Precios de la Vivienda en México. Serie trimestral desde el primer trimestre de
2005, con año base 2017 = 100.

![ERD](assets/erd.svg)

La fuente reparte la geografía en tres columnas mutuamente excluyentes (`Global`, `Estado`,
`Municipio`): cuando una trae valor, las otras van vacías. El pipeline la parte en una tabla por
nivel, y así ninguna columna queda con nulos estructurales.

## Diccionario de variables

### `cat_serie_global`

| Columna | Descripción |
|---|---|
| `nombre` | Nombre de la serie tal como lo publica SHF: `Nacional`, `Nueva`, `Usada`, `Casa sola`, `Casa en condominio - depto.`, `Económica - Social`, `Media - Residencial` y 8 zonas metropolitanas. |
| `tipo` | Concepto que agrupa a la serie: `nacional`, `condicion`, `tipo_vivienda`, `segmento` o `zona_metropolitana`. SHF mezcla los cinco en una sola columna; esta clasificación permite consultarlos por separado sin parsear el nombre. |

### `stg_indice_shf_vivienda_global`

| Columna | Descripción |
|---|---|
| `serie_global_id` | Serie a la que corresponde la medición. Referencia a `cat_serie_global.id`. |
| `fecha` | Primer día del trimestre de referencia (T1 = 01-01, T2 = 04-01, T3 = 07-01, T4 = 10-01). |
| `trimestre` | Trimestre de referencia (1 a 4). |
| `indice` | Valor del índice de precios de la vivienda, con año base 2017 = 100. |

### `stg_indice_shf_vivienda_estatal`

| Columna | Descripción |
|---|---|
| `cve_ent` | Clave de la entidad federativa (1 a 32) del INEGI. Referencia lógica a `cvegeo_states.cve_ent`. |
| `fecha` | Primer día del trimestre de referencia. |
| `trimestre` | Trimestre de referencia (1 a 4). |
| `indice` | Valor del índice, con año base 2017 = 100. |

### `stg_indice_shf_vivienda_municipal`

| Columna | Descripción |
|---|---|
| `cvegeo` | Clave geoestadística del municipio (`cve_ent * 1000 + cve_mun`). Referencia lógica a `cvegeo_municipalities.cvegeo`. |
| `cve_ent` | Entidad a la que pertenece el municipio. Se conserva porque la fuente identifica al municipio solo por nombre y hay nombres repetidos entre entidades: `Benito Juárez` (Ciudad de México y Quintana Roo) y `Juárez` (Chihuahua y Nuevo León). |
| `fecha` | Primer día del trimestre de referencia. |
| `trimestre` | Trimestre de referencia (1 a 4). |
| `indice` | Valor del índice, con año base 2017 = 100. |

SHF publica una selección de municipios, no los 2,469 del país: 74 en la edición del 2T 2026, de
los cuales 4 son de Jalisco (Guadalajara, Zapopan, San Pedro Tlaquepaque y Tlajomulco de Zúñiga).

## Fuentes

| Nivel | Archivo | Variable de entorno |
|---|---|---|
| Global, estatal y municipal | `Indice_SHF_datos_abiertos_{n}_trim_{año}.xlsx`, hoja única `Indice SHF datos abiertos` | `SHF_URL` |

Página de origen: <https://www.gob.mx/shf/archivo/documentos> → "Índice SHF de Precios de la
Vivienda en México".

## Vistas

| Vista | Contenido |
|---|---|
| `vw_indice_shf_vivienda_global` | Series sin desglose geográfico, con nombre y tipo resueltos. |
| `vw_indice_shf_vivienda_estatal` | Serie por entidad, con el nombre oficial del INEGI. |
| `vw_indice_shf_vivienda_municipal` | Serie por municipio, con nombres de municipio y entidad. |
| `vw_indice_shf_vivienda_jalisco` | Corte de Jalisco: sus 4 municipios, la entidad y la serie `ZM Guadalajara`, apilados con una columna `nivel`. |

## Migraciones

| Archivo | Contenido |
|---|---|
| `V1__foreign_tables.sql` | `postgres_fdw` hacia `cvegeo`: `cvegeo_states` y `cvegeo_municipalities`. |
| `V2__catalogs_indice_shf_vivienda.sql` | `cat_serie_global`. |
| `V3__tables_indice_shf_vivienda.sql` | Las tres tablas `stg_` con sus restricciones únicas. |
| `V4__views_indice_shf_vivienda.sql` | Las cuatro vistas. |

## Variables de entorno

| Variable | Descripción |
|---|---|
| `SHF_URL` | URL directa del XLSX. Cambia en cada publicación. |
| `DOWNLOAD_TIMEOUT` | Segundos de espera de la descarga. |
| `CHUNK_SIZE` | Tamaño de lote del upsert. |

## Actualización

**Trimestral y manual.** Solo existe el DAG `etl_indice_shf_vivienda_bootstrap`, con
`schedule=None`.

Cada publicación de SHF reemite la serie completa desde 2005, así que no hay carga incremental que
construir: la corrida completa es la actualización. Y la URL no admite plantilla — carga el id de
archivo asignado por el CMS (`file/1097035/`) y el trimestre en el nombre
(`_2_trim_2026.xlsx`), y ambos cambian cada vez, igual que el bienio en el slug de la página que
la contiene. Por eso el DAG no tiene calendario: se actualiza `SHF_URL` en el `.env` y se dispara
a mano. El upsert hace que repetir la corrida sea inofensivo.

Si la URL queda obsoleta, el extract falla con un `FileNotFoundError` que nombra la página de
origen: gob.mx responde 200 con una página de reto de su WAF, así que el status code no distingue
una descarga buena de un rechazo y la validación es sobre la firma del archivo.

## Notas metodológicas

- **Año base 2017 = 100.** No es un trimestre base: el promedio de los cuatro trimestres de 2017
  da exactamente 100.00 en las 121 series.
- **La columna `Consecutivo` se descarta**: es el número de renglón del Excel y se reinicia en
  cada publicación.
- **22 municipios se publican con un espacio al final** del nombre (`"Jesús María "`,
  `"Zihuatanejo de Azueta "`). Sin recortarlo, el nombre no cruza contra `cvegeo`.
- **SHF usa nombres de uso común para tres entidades** donde el Marco Geoestadístico usa el
  oficial: `Coahuila`, `Michoacán` y `Veracruz`. Se resuelven con `ENTITY_NAME_ALIASES` en
  `mappings.py`; ahí se agrega cualquier otro nombre que la carga reporte sin resolver.
- **La carga aborta si un nombre no resuelve su clave**, en vez de insertar la fila con `NULL`:
  la clave es la identidad del registro y perderla en silencio deja filas imposibles de atribuir.

## Ejecución

```bash
just create-db indice_shf_vivienda
just flyway-migrate indice_shf_vivienda
python dags/etl_indice_shf_vivienda.py
```
