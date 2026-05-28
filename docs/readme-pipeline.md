# readme-pipeline

Template para el `README.md` de cada pipeline. Reemplaza los valores entre `<>` con la información real del pipeline.

---

```markdown
# <nombre_pipeline>

## Descripción general

<Párrafo describiendo qué datos contiene el pipeline, cuál es la fuente institucional, qué variables cubre y desde qué año está disponible la información.>

## Fuente general

<URL del sitio web principal del proveedor de datos>

## Fuente específica

```shell
<VAR_URL>=<url de descarga directa o endpoint de la API>
```

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `<YYYY>` o `<YYYY-MM>` |
| Frecuencia de actualización | <Anual / Mensual / Trimestral / Quinquenal / Bajo demanda> |
| Desagregación | <Nacional / Estatal / Municipal / Ciudad> |
| ¿Tiene update? | <Sí / No> |
| Update | <Automático / Manual / N/A> |

## Diagrama de entidad relación

![ERD](assets/erd.svg)

## Diccionario de variables

### <nombre_tabla_principal>

| variable | descripción |
|---|---|
| `<columna>` | <Descripción de la columna> |

## Migraciones

| migración | descripción |
|---|---|
| `V1__<nombre>.sql` | <Qué crea o modifica esta migración> |

## Variables de entorno

| variable | descripción |
|---|---|
| `<VAR_NAME>` | <Para qué sirve esta variable> |

## Notas metodológicas

### Extract

<Cómo se obtienen los datos: URL fija, iteración por año/mes, API paginada, descarga manual, etc.>

### Transform

<Qué transformaciones aplica: normalización de texto, resolución de FKs, renombrado de columnas, filtros, etc.>

### Load

<Cómo se insertan los datos: `bulk_insert`, `insert_records`, modo append-only o upsert, tablas destino, etc.>

## Ejecución

**Bootstrap** (carga inicial):

```shell
just flyway-migrate <nombre_pipeline>
conda run -n etl python -m core.pipelines.<nombre_pipeline> bootstrap
```

**Update** (<frecuencia>, DAG `etl_<nombre_pipeline>_update`, schedule `<cron>`):

```shell
conda run -n etl python -m core.pipelines.<nombre_pipeline> update
```

## Notas adicionales

<Consideraciones especiales: cobertura geográfica, cambios de formato entre versiones, datos que requieren limpieza manual, limitaciones conocidas, etc. Omitir esta sección si no hay notas relevantes.>
```
