# asg_imss

Pipeline ETL de Asegurados, Salarios y Grupos de cotización del IMSS. Descarga mensual desde el portal de datos abiertos del IMSS, con 12 catálogos normalizados y una tabla de hechos append-only filtrada a Jalisco.

## ERD

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_asg_imss

| Columna | Descripción |
|---|---|
| `fecha_corte` | Último día del mes al que corresponde el registro |
| `asegurados` | Total de asegurados en el patrón |
| `no_trabajadores` | Número de trabajadores registrados |
| `ta` | Trabajadores asegurados totales |
| `teu` | Trabajadores eventuales urbanos |
| `tec` | Trabajadores eventuales del campo |
| `tpu` | Trabajadores permanentes urbanos |
| `tpc` | Trabajadores permanentes del campo |
| `ta_sal` | Suma de salarios de trabajadores asegurados totales |
| `teu_sal` | Suma de salarios de eventuales urbanos |
| `tec_sal` | Suma de salarios de eventuales del campo |
| `tpu_sal` | Suma de salarios de permanentes urbanos |
| `tpc_sal` | Suma de salarios de permanentes del campo |
| `masa_sal_ta` | Masa salarial de trabajadores asegurados totales |
| `masa_sal_teu` | Masa salarial de eventuales urbanos |
| `masa_sal_tec` | Masa salarial de eventuales del campo |
| `masa_sal_tpu` | Masa salarial de permanentes urbanos |
| `masa_sal_tpc` | Masa salarial de permanentes del campo |

## Fuentes

| Nivel | Archivo | Variable de entorno |
|---|---|---|
| Catálogos | `diccionario_de_datos_1.xlsx` | `ASG_IMSS_CATALOG_URL` |
| Mensual | `asg-{YYYY-MM-DD}.csv` | `ASG_IMSS_DATA_URL` |

## Actualización

Frecuencia mensual. El IMSS publica los datos de cada mes durante la primera semana del mes siguiente. La actualización es automática vía el DAG `etl_asg_imss_update`, programado para el día 10 de cada mes. El bootstrap cubre el historial completo desde enero de 2015.
