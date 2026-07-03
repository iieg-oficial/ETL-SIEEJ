# enoe_microdatos

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_enoe_microdatos

| variable | descripción |
|---|---|
| `anio` | Año de levantamiento de la encuesta (2005-presente) |
| `trimestre` | Trimestre de levantamiento (1-4) |
| `cd_a` | Ciudad o área de levantamiento; parte de la clave natural del registro |
| `entidad_id` | Clave de la entidad federativa (siempre 14 para Jalisco) |
| `con` | Número de control del hogar; parte de la clave natural |
| `v_sel` | Vivienda seleccionada; parte de la clave natural |
| `n_hog` | Número del hogar dentro de la vivienda |
| `h_mud` | Indica si el hogar se mudó (hogar sustituto) |
| `n_ent` | Número de la entrevista dentro del hogar |
| `n_ren` | Número de renglón (persona dentro del hogar) |
| `municipio_id` | Clave del municipio (FK implícita a cvegeo_municipalities) |
| `tipo_localidad_id` | Tamaño de localidad trimestral |
| `ur` | Zona urbano/rural (1=Urbano, 2=Rural) |
| `zona` | Zona geográfica de la encuesta |
| `sex` | Sexo (1=Hombre, 2=Mujer) |
| `eda` | Edad en años cumplidos |
| `nac_dia`, `nac_mes`, `nac_anio` | Fecha de nacimiento (día, mes, año) |
| `e_con` | Estado conyugal (1=Unido, 2=Separado, 3=Divorciado, 4=Viudo, 5=Soltero) |
| `niv_ins` | Nivel de instrucción recodificado |
| `anios_esc` | Años de escolaridad aprobados |
| `clase1` | Condición de actividad (1=PEA, 2=PNEA) |
| `clase2` | Condición de ocupación (1=Ocupado, 2=Desocupado) |
| `clase3` | Condición de ocupación desagregada |
| `seg_soc` | Acceso a servicios de salud por ocupación principal (1=Con, 2=Sin) |
| `rama` | Rama de actividad económica (1 dígito SCIAN adaptado ENOE) |
| `rama_est2` | Rama de actividad económica estrato 2 (versiones históricas) |
| `scian` | Clave de subsector SCIAN de la actividad principal |
| `hrsocup` | Horas trabajadas en la semana de referencia (ocupación principal) |
| `ingocup` | Ingreso mensual por trabajo (pesos corrientes) |
| `ing_x_hrs` | Ingreso por hora trabajada (pesos corrientes) |
| `salario` | Salario mínimo general diario de referencia |
| `tue1`, `tue2`, `tue3` | Componentes de la tasa de informalidad laboral (TIL1) |
| `tue_ppal` | Trabajo informal en ocupación principal (1=Informal, 2=Formal) |
| `emp_ppal` | Características de la empresa en la ocupación principal |
| `trans_ppal` | Tipo de transacción en la ocupación principal |
| `sub_o` | Subocupación (1=Subocupado, 2=No subocupado) |
| `fac` | Factor de expansión trimestral |
| `fac_men` | Factor de expansión mensual |
| `sector_id` | FK a `cat_enoe_sector` — derivado de rama_est1 |
| `ocupacion_id` | FK a `cat_enoe_ocupacion` — derivado de c_ocu11c |
| `situacion_trabajo_id` | FK a `cat_enoe_situacion_trabajo` — derivado de pos_ocu |
| `p3b` | COE1 — Número de trabajadores en el establecimiento (codificado por rangos) |
| `p3i` | COE1 — Tiene contrato escrito (1=Sí indefinido, 2=Sí temporal, 3=No) |
| `p10b` | COE2 — Razón por la que no trabajó la semana de referencia |
| `es_pea` | TRUE si la persona pertenece a la Población Económicamente Activa (clase1=1) |
| `es_ocupado` | TRUE si la persona está ocupada (clase2=1) |
| `es_desocupado` | TRUE si la persona está desocupada (clase2=2) |
| `es_informal` | TRUE si el trabajo principal es informal (clase2=1 & tue_ppal=1) |

### cat_enoe_sector

| variable | descripción |
|---|---|
| `id` | Identificador del sector (0=No aplica, 1=Primario, 2=Secundario, 3=Terciario, 4=No especificado) |
| `descripcion` | Nombre del sector económico |

### cat_enoe_ocupacion

| variable | descripción |
|---|---|
| `id` | Identificador del grupo de ocupación (0-11) |
| `descripcion` | Descripción del grupo ocupacional (ej. Profesionales técnicos y trabajadores del arte) |

### cat_enoe_situacion_trabajo

| variable | descripción |
|---|---|
| `id` | Identificador de la situación (0=No aplica, 1=Subordinados remunerados, 2=Empleadores, 3=Cuenta propia, 4=Sin pago, 5=No especificado) |
| `descripcion` | Descripción de la situación en el trabajo |

## Fuentes

| nivel | archivo | variable de entorno |
|---|---|---|
| Microdatos 2023+ | ENOE microdatos trimestral (ZIP) | `MICRODATOS_URL` |
| Microdatos 2021-2022 | ENOE_N microdatos (ZIP, no publicados) | `MICRODATOS_URL_ENOE_N` |
| Microdatos 2005-2020 | ENOE microdatos legacy (ZIP) | `MICRODATOS_URL_LEGACY` |

Dentro de cada ZIP: SDEM (diseño muestral + sociodemográfico), COE1 (características empresariales), COE2 (variables complementarias).

Fuente oficial: https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/

## Actualización

Frecuencia: Trimestral (marzo, junio, septiembre, diciembre)

Tipo: Automática vía DAG `etl_enoe_microdatos_incremental` (cron `0 0 10 3,6,9,12 *`)

Justificación: INEGI publica ENOE trimestral. Jalisco (entidad_id=14) incluye municipios de Jalisco únicamente. Los períodos 2020 T2-T4, 2021 T1-T4 y 2022 T1-T4 no están disponibles (pausa COVID-19 / ETOE). Bootstrap disponible desde 2005 T1 hasta trimestre corriente.

## Vistas materializadas

Tres vistas con diferentes niveles de agregación:

| Vista | Granularidad | Filas aprox. |
|---|---|---|
| `mv_enoe_microdatos` | 1 fila = 1 persona encuestada (microdatos con joins resueltos) | ~1,090,806 |
| `mv_enoe_tasas` | 1 fila = municipio × trimestre | ~3,250 |
| `mv_enoe_tasas_jalisco` | 1 fila = trimestre (estado completo) | 74 |

> **Nota estadística**: ENOE no es representativa a nivel municipio. El diseño muestral opera por `cd_a` (ciudad/área). Por ejemplo, `cd_a = 2` corresponde a la Zona Metropolitana de Guadalajara (Guadalajara, Zapopan, Tlaquepaque, Tonalá, Tlajomulco de Zúñiga, El Salto). Para valores que coincidan con cifras oficiales INEGI usar `mv_enoe_tasas_jalisco`.

Las vistas `mv_enoe_tasas` y `mv_enoe_tasas_jalisco` incluyen las 11 tasas y poblaciones base desagregadas por sexo con sufijos `_h` (hombres, `sex=1`) y `_m` (mujeres, `sex=2`). Ejemplo: `td_h`, `td_m`, `pea_h`, `pea_m`.

## Tasas INEGI — metodología

Las 11 tasas siguen la metodología de *ENOE. Conociendo la base de datos* (INEGI, 2023).

### Criterio general poblacional

Aplica a todas las tasas:

```
r_def = 0          -- entrevista completa
c_res IN (1, 3)    -- residente habitual o nuevo residente
eda BETWEEN 15 AND 98
```

### Poblaciones base

Las poblaciones se obtienen sumando el factor de expansión trimestral (`fac` = FAC_TRI). **Nunca contar registros — siempre sumar `fac`.**

| Población | Criterio adicional |
|---|---|
| P15yMAS | Sin filtro adicional |
| PEA | `clase1 = 1` |
| PD | `clase2 = 2` |
| PO | `clase2 = 1` |
| PONA | `clase2 = 1 AND ambito1 <> 1` |

### Fórmulas de las 11 tasas

| # | Tasa | Columna | Fórmula |
|---|---|---|---|
| I | Tasa de Participación | `tp` | PEA / P15yMAS × 100 |
| II | Tasa de Desocupación | `td` | PD / PEA × 100 |
| III | Tasa de Ocupación Parcial y Desocupación | `topd` | (PD + O<15hrs) / PEA × 100 |
| IV | Tasa de Presión General | `tprg` | (PD + POBOT) / PEA × 100 |
| V | Tasa de Trabajo Asalariado | `tta` | PASA / PO × 100 |
| VI | Tasa de Subocupación | `tsub` | PSUB_O / PO × 100 |
| VII | Tasa de Condiciones Críticas de Ocupación | `tcco` | PCCO / PO × 100 |
| VIII | Tasa de Ocupación en el Sector Informal 1 | `tosi1` | POSI / PO × 100 |
| IX | Tasa de Informalidad Laboral 1 | `til1` | POI / PO × 100 |
| X | Tasa de Ocupación en el Sector Informal 2 | `tosi2` | POSI / PONA × 100 |
| XI | Tasa de Informalidad Laboral 2 | `til2` | POINA / PONA × 100 |

Donde:
- **O<15hrs**: `clase2=1 AND dur9c=2`
- **POBOT**: `clase2=1 AND tpg_p8a=1`
- **PASA**: `clase2=1 AND remune2c=1`
- **PSUB_O**: `clase2=1 AND sub_o=1`
- **PCCO**: `clase2=1 AND tcco IN (1,2,3)`
- **POSI**: `clase2=1 AND tue2=5`
- **POI**: `clase2=1 AND emp_ppal=1`
- **POINA**: `clase2=1 AND emp_ppal=1 AND ambito1<>1`
