# marginacion

Pipeline ETL para el índice y grado de marginación municipal, por localidad y estatal, publicado por CONAPO.

## Esquema

<img src="assets/erd.png" width="600" height="900">

## Diccionario de variables

### `marginaciones_municipales`

| Variable | Descripción |
|----------|-------------|
| `municipio_id` | Clave INEGI del municipio (referencia a `cvegeo_municipalities`) |
| `grado_marginacion_id` | FK a `grados_marginacion` |
| `pob_total` | Población total |
| `porc_pob15_analfabeta` | % de población de 15 años o más analfabeta |
| `pob15_sin_educ_bas` | % de población de 15 años o más sin educación básica completa |
| `porc_viv_sin_drenaje_ni_excusado` | % de ocupantes en viviendas sin drenaje ni excusado |
| `porc_viv_sin_energia` | % de ocupantes en viviendas sin energía eléctrica |
| `porc_viv_sin_agua_entubada` | % de ocupantes en viviendas sin agua entubada |
| `porc_viv_piso_tierra` | % de ocupantes en viviendas con piso de tierra |
| `prom_ocup_por_cuarto` | Promedio de ocupantes por cuarto |
| `porc_pob_loc_menos5000_hab` | % de población en localidades con menos de 5,000 habitantes |
| `pob_ocup_hasta_2_sal_min` | % de población ocupada con ingresos de hasta 2 salarios mínimos |
| `indice_marginacion` | Índice de marginación calculado por CONAPO |
| `indice_marginacion_normalizado` | Índice de marginación normalizado en escala 0–100 |
| `lugar_contexto_nacional` | Posición del municipio en el ranking nacional por índice de marginación |

### `marginaciones_estatales`

| Variable | Descripción |
|----------|-------------|
| `entidad_id` | Clave INEGI de la entidad federativa (referencia a `cvegeo_states`) |
| `grado_marginacion_id` | FK a `grados_marginacion` |
| `pob_total` | Población total |
| `porc_pob15_analfabeta` | % de población de 15 años o más analfabeta |
| `pob15_sin_educ_bas` | % de población de 15 años o más sin educación básica completa |
| `porc_viv_sin_drenaje_ni_excusado` | % de ocupantes en viviendas sin drenaje ni excusado |
| `porc_viv_sin_energia` | % de ocupantes en viviendas sin energía eléctrica |
| `porc_viv_sin_agua_entubada` | % de ocupantes en viviendas sin agua entubada |
| `porc_viv_piso_tierra` | % de ocupantes en viviendas con piso de tierra |
| `porc_viv_con_hacinamiento` | % de viviendas particulares con hacinamiento |
| `porc_pob_loc_menos5000_hab` | % de población en localidades con menos de 5,000 habitantes |
| `pob_ocup_hasta_2_sal_min` | % de población ocupada con ingresos de hasta 2 salarios mínimos |
| `porc_viv_sin_refrigerador` | % de viviendas particulares habitadas sin refrigerador (calculado desde ITER 2020 de INEGI; nulo para años anteriores) |
| `indice_marginacion` | Índice de marginación calculado por CONAPO |
| `indice_marginacion_normalizado` | Índice de marginación normalizado en escala 0–100 |
| `lugar_contexto_nacional` | Posición de la entidad en el ranking nacional por índice de marginación |

### `marginaciones_localidades`

| Variable | Descripción |
|----------|-------------|
| `localidad_id` | FK a `localidades` |
| `grado_marginacion_id` | FK a `grados_marginacion` |
| `pob_total` | Población total |
| `porc_pob15_analfabeta` | % de población de 15 años o más analfabeta |
| `porc_pob15_sin_educ_basica` | % de población de 15 años o más sin educación básica completa |
| `porc_viv_sin_drenaje_ni_excusado` | % de ocupantes en viviendas sin drenaje ni excusado |
| `porc_viv_sin_energia` | % de ocupantes en viviendas sin energía eléctrica |
| `porc_viv_sin_agua_entubada` | % de ocupantes en viviendas sin agua entubada |
| `porc_viv_piso_tierra` | % de ocupantes en viviendas con piso de tierra |
| `prom_ocup_por_cuarto` | Promedio de ocupantes por cuarto |
| `porc_viv_sin_refrigerador` | % de viviendas sin refrigerador |
| `indice_marginacion` | Índice de marginación calculado por CONAPO |
| `indice_marginacion_normalizado` | Índice de marginación normalizado en escala 0–100 |

## Fuentes

| Nivel | Fuente |
|-------|--------|
| Municipal 2020 | [IMM_{año}.xlsx](https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Municipio/IMM_{año}.xlsx) |
| Municipal 2010, 2015 | [IMM_DP2_{año}.xlsx](https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Municipio/IMM_DP2_{año}.xlsx) |
| Localidad | [IML_{año}.zip](https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Localidad/IML_{año}.zip) |
| Estatal 2010 | [IME_DP2_2010.xlsx](https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Entidad_Federativa/IME_DP2_2010.xlsx) |
| Estatal 2015 | [Base_Indice_de_marginacion_estatal_90-15.csv](https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Entidad_Federativa/Base_Indice_de_marginacion_estatal_90-15.csv) |
| Estatal 2020 | [IME_2020.xls](https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Entidad_Federativa/IME_2020.xls) |
| `porc_viv_sin_refrigerador` | [iter_{01..32}_2020_csv.zip](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/microdatos/iter/iter_{01..32}_2020_csv.zip) |

Municipal y localidad filtrados a Jalisco (`CVE_ENT = 14`). Los registros de totales municipales (`LOC = 9999`) son excluidos. Estatal incluye las 32 entidades federativas.

## Actualización

**Frecuencia:** cada 5 años, al momento de publicación de CONAPO (último: 2020).

**Manual.** CONAPO no ofrece API ni feed automático; los archivos se publican de forma irregular en su portal. El dato de `porc_viv_sin_refrigerador` proviene del Censo de Población y Vivienda de INEGI, que se realiza cada 10 años.

Para incorporar un nuevo año de publicación:

1. Agregar el año a `DATA_YEARS` en `.env`
2. Verificar si los nombres de columna cambiaron en la fuente y actualizar `rename_municipal`, `rename_estatal` y `rename_localidad` en `constants.py`
3. Verificar si el patrón de URL cambió y actualizar `config.py` y `.env.example`
4. Para el año estatal, identificar el nuevo archivo en el portal de CONAPO y actualizar `_fetch_estatal` en `extract.py`
5. Para `porc_viv_sin_refrigerador`, actualizar la URL del ITER en `_fetch_pct_sin_refrigerador_all` cuando se publique el Censo 2030
6. Ejecutar `python dags/etl_marginacion.py`
