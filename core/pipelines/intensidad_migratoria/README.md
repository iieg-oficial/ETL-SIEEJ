# intensidad_migratoria

Pipeline ETL para el Índice de Intensidad Migratoria México–Estados Unidos (IIM) publicado por CONAPO.

## ERD

![ERD](assets/erd.svg)

## Diccionario de variables

### `iim_municipal`

| Variable | Descripción |
|----------|-------------|
| `municipio_id` | Clave INEGI del municipio en formato cvegeo 5 dígitos (referencia a `cvegeo_municipalities`) |
| `viv_totales` | Total de viviendas |
| `por_viv_remesas` | % de viviendas que reciben remesas del exterior |
| `por_viv_emigrantes` | % de viviendas con emigrantes residentes en Estados Unidos |
| `por_viv_reto` | % de viviendas con migrantes de retorno de Estados Unidos |
| `iim_dp2` | Valor del Índice de Intensidad Migratoria (método DP2) |
| `grado_iim` | Grado de intensidad migratoria (Muy bajo, Bajo, Medio, Alto, Muy alto) |
| `lugar_contexto_nacional` | Posición del municipio en el ranking nacional por índice de intensidad migratoria |
| `fecha` | Año de la fuente (2010 o 2020) |

### `iim_estatal`

| Variable | Descripción |
|----------|-------------|
| `entidad_id` | Clave INEGI de la entidad federativa (referencia a `cvegeo_states`) |
| `viv_totales` | Total de viviendas |
| `por_viv_remesas` | % de viviendas que reciben remesas del exterior |
| `por_viv_emigrantes` | % de viviendas con emigrantes residentes en Estados Unidos |
| `por_viv_reto` | % de viviendas con migrantes de retorno de Estados Unidos |
| `iim_dp2` | Valor del Índice de Intensidad Migratoria (método DP2) |
| `grado_iim` | Grado de intensidad migratoria (Muy bajo, Bajo, Medio, Alto, Muy alto) |
| `lugar_contexto_nacional` | Posición de la entidad en el ranking nacional por índice de intensidad migratoria |
| `fecha` | Año de la fuente (2020) |

## Fuentes

| Nivel | Fuente |
|-------|--------|
| Municipal 2010 | [IIM2010_BASEMUN.xls](http://www.conapo.gob.mx/work/models/CONAPO/intensidad_migratoria/base_completa/IIM2010_BASEMUN.xls) |
| Municipal 2020 | [iim_base2020m.csv](https://conapo.segob.gob.mx/work/models/CONAPO/IIM/iim_base2020m.csv) |
| Estatal 2020 | [iim_base2020e.csv](https://conapo.segob.gob.mx/work/models/CONAPO/IIM/iim_base2020e.csv) |

## Actualización

**Frecuencia:** cada 10 años, al momento de publicación de CONAPO con base en el Censo de Población y Vivienda de INEGI (último: 2020).

**Manual.** CONAPO no ofrece API ni feed automático. La siguiente publicación se espera alrededor de 2031, una vez procesados los resultados del Censo 2030.

Para incorporar un nuevo año:

1. Agregar las URLs de los nuevos archivos en `.env` y `config.py`
2. Verificar si los nombres de columna cambiaron y actualizar los dicts en `constants.py`
3. Agregar el procesamiento del nuevo año en `transform.py`
4. Ejecutar `python dags/etl_intensidad_migratoria.py`
