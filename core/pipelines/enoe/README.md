# enoe

## Descripción general

Pipeline ETL de la Encuesta Nacional de Ocupación y Empleo (ENOE) del INEGI. Descarga microdatos sociodemográficos y de empleo (tabla SDEM) a nivel persona para Jalisco, incluyendo condición de actividad económica (PEA/PNEA, ocupación, desocupación), sector y grupo de ocupación, informalidad laboral (metodología TIL1), ingresos, horas trabajadas y prestaciones laborales, disponible desde el primer trimestre de 2005.

## Fuente general

https://www.inegi.org.mx/programas/enoe/15ymas/

## Fuente específica

```shell
ENOE_URL=https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/{anio}/conjunto_de_datos_enoe_{anio}_{trimestre}t_csv.zip
```

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `2026-Q1` |
| Frecuencia de actualización | Trimestral |
| Desagregación | Municipal |
| ¿Tiene update? | Sí |
| Update | Automático |

## Diagrama de entidad relación

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_enoe

| variable | descripción |
|---|---|
| `entidad_id` | Clave de entidad federativa INEGI (siempre 14 = Jalisco) |
| `municipio_id` | Clave de municipio INEGI (variable `mun`/`cve_mun` SDEM, sin FK por variación de nomenclatura entre periodos) |
| `cd_a` | Componente de clave de persona: ciudad o área de levantamiento |
| `con` | Componente de clave de persona: número de conglomerado |
| `v_sel` | Componente de clave de persona: número de vivienda seleccionada |
| `n_hog` | Componente de clave de persona: número de hogar dentro de vivienda |
| `h_mud` | Componente de clave de persona: indicador de mudanza del hogar |
| `n_ent` | Componente de clave de persona: número de entrevista del hogar |
| `n_ren` | Componente de clave de persona: número de renglón (identificador de persona dentro del hogar) |
| `tipo_localidad_id` | FK a catálogo de tamaño de localidad de residencia (variable `t_loc_tri` SDEM) |
| `eda` | Edad en años cumplidos al momento del levantamiento |
| `sex` | Sexo (1=hombre, 2=mujer) |
| `habla_lengua_indigena` | Habla alguna lengua indígena, derivado de `cs_p17 = 1` |
| `n_inf` | Número de hijos nacidos vivos (mujeres; variable `n_hij` SDEM) |
| `estado_civil_id` | FK a catálogo de estado civil o conyugal (variable `e_con` SDEM) |
| `nivel_educativo_id` | FK a catálogo de nivel de instrucción máximo alcanzado (variable `cs_p13_1` SDEM) |
| `cs_p13_2` | Grado cursado dentro del nivel educativo |
| `clase1` | Clasificación de actividad económica: 1=PEA (Población Económicamente Activa), 2=PNEA (variable `clase1` SDEM) |
| `clase2` | Subclasificación de condición de actividad: 1=ocupado, 2=desocupado, 3=PNEA disponible, 4=PNEA no disponible (variable `clase2` SDEM) |
| `clase3` | Subclasificación adicional de condición de actividad (variable `clase3` SDEM) |
| `dur9c` | Horas trabajadas en la semana de referencia agrupadas en 9 categorías (variable `dur9c` SDEM) |
| `hrsocup` | Horas trabajadas en el empleo principal durante la semana de referencia |
| `ingocup` | Ingreso mensual por ocupación en pesos corrientes (variable `ingocup` SDEM) |
| `ma48me1sm` | Múltiplo del salario mínimo mensual correspondiente al ingreso (variable `ma48me1sm` SDEM) |
| `emp_ppal` | Posición en el trabajo principal (variable `emp_ppal` SDEM): obrero, empleador, cuenta propia, etc. |
| `sector_id` | FK a catálogo de sector económico del empleo principal (variable `rama_est1` SDEM, 4 valores primario–terciario) |
| `ocupacion_id` | FK a catálogo de grupo de ocupación principal en 11 categorías (variable `c_ocu11c` SDEM) |
| `situacion_trabajo_id` | FK a catálogo de clasificación informal/formal del empleo principal (variable `tue_ppal` SDEM). Base para metodología TIL1 |
| `seg_soc` | Acceso a seguridad social por el trabajo: 1=con acceso, 2=sin acceso, 3=no especificado (variable `seg_soc` SDEM) |
| `pre_asa` | Prestaciones laborales: 1=con prestaciones, 2=sin prestaciones, 3=no especificado (variable `pre_asa` SDEM) |
| `fac` | Factor de expansión trimestral (variable `fac_tri` SDEM). Pondera microdatos a universo de población |
| `es_pea` | Indicador derivado: pertenece a la PEA (`clase1 = 1`) |
| `es_ocupado` | Indicador derivado: está ocupado (`clase2 = 1`) |
| `es_desocupado` | Indicador derivado: está desocupado dentro de la PEA (`clase2 = 2`) |
| `es_informal` | Indicador derivado según metodología TIL1 INEGI: ocupado (`clase2 = 1`) y en sector informal (`situacion_trabajo_id = 1`) |

## Migraciones

| migración | descripción |
|---|---|
| `V1__foreign_tables.sql` | FDW hacia `cvegeo` (estados y municipios) |
| `V2__catalogs_enoe.sql` | Catálogos: sector, ocupación, situación de trabajo, tipo de localidad, estado civil, nivel educativo |
| `V3__tables_enoe.sql` | Tabla principal `stg_enoe` |
| `V4__views_enoe.sql` | Vistas `v_enoe_jalisco` y `v_enoe_indicadores_municipio` |

## Vistas

- `v_enoe_jalisco` — vista person-level con catálogos decodificados y nombre de municipio vía FDW `cvegeo_municipalities`
- `v_enoe_indicadores_municipio` — indicadores agregados por año/trimestre/municipio: totales y ponderados (factor de expansión), tasas de desocupación e informalidad (TIL1), ingreso promedio

## Variables de entorno

| variable | descripción |
|---|---|
| `ENOE_URL` | URL principal de descarga del ZIP CSV trimestral (template `{anio}`, `{trimestre}`) |
| `ENOE_URL_ALT` | URL alterna ante cambios de nomenclatura del archivo del INEGI |
| `ENOE_URL_C` | URL alterna (variante `conjunto_de_datos_enoe{anio}`, sin guion bajo) |
| `ENOE_URL_N` | URL alterna (variante `enoen`, encuesta nueva) |
| `BOOTSTRAP_START_YEAR` | Año de inicio del bootstrap histórico (`2005`) |
| `BOOTSTRAP_START_TRIMESTRE` | Trimestre de inicio del bootstrap histórico (`1`) |

## Notas metodológicas

### Extract

Descarga el ZIP CSV de la tabla SDEM por año y trimestre desde `ENOE_URL`, con fallback automático a `ENOE_URL_ALT`, `ENOE_URL_C` y `ENOE_URL_N` ante cambios de nomenclatura del archivo entre periodos. Filtra las filas a Jalisco (`entidad_id = 14`) antes de guardar. En modo update, omite los trimestres que ya existen en la base de datos.

### Transform

Castea columnas numéricas y enteras, limpia valores nulos (`NULL_VALUES`), renombra columnas (`RENAME_HEADER`) para unificar nomenclatura entre periodos (ej. `mun`/`cve_mun`, `t_loc`/`t_loc_tri`, `fac`/`fac_tri`), agrega `anio`/`trimestre`, deriva `habla_lengua_indigena` desde `cs_p17`, y calcula los indicadores `es_pea`, `es_ocupado`, `es_desocupado` y `es_informal` (metodología TIL1 del INEGI).

### Load

Upsert de catálogos con `insert_records` e inserción de microdatos en `stg_enoe` con `insert_records`, evitando duplicados por la clave natural de persona (`anio`, `trimestre`, `cd_a`, `entidad_id`, `con`, `v_sel`, `n_hog`, `h_mud`, `n_ent`, `n_ren`). Omite periodos ya cargados por completo.

## Ejecución

**Bootstrap** (carga inicial, histórico desde 2005 T1):

```shell
just flyway-migrate enoe
conda run -n etl python -m core.pipelines.enoe bootstrap
```

**Update** (trimestral, DAG `etl_enoe_update`, schedule `0 3 10 3,6,9,12 *`):

```shell
conda run -n etl python -m core.pipelines.enoe update
```

## Notas adicionales

Alcance geográfico: Jalisco (`entidad_id = 14`). El INEGI publica cada trimestre aproximadamente en el día 70 del trimestre siguiente (10 de marzo, junio, septiembre y diciembre), fecha que usa el DAG de actualización. Entre 2005 y la actualidad el INEGI ha cambiado la nomenclatura de algunas columnas de origen (`mun`→`cve_mun`, `t_loc`→`t_loc_tri`, `fac`→`fac_tri`), resueltas mediante `RENAME_HEADER`.
