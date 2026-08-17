# Banco de indicadores (fase previa al MCP)

> Documento de diseño. Implementado en [`core/indicadores/`](../core/indicadores/README.md);
> el MCP (fase 2) sigue pendiente.

## Contexto

Queremos exponer los datos del ETL-SIEEJ a agentes de IA vía MCP, pero entregar "la base
de datos completa" no es viable: son **33 bases de datos PostgreSQL separadas** (una por
pipeline), ~198 archivos de migración y ~135 vistas con esquemas heterogéneos. Una IA que
reciba eso escribe SQL malo, cruza `municipio_id` con el patrón equivocado (hay tres
conviviendo, ver [`estandares_datos.md`](estandares_datos.md) §2) e inventa indicadores
que no existen.

La solución es invertir el orden: primero un **banco de indicadores curado** —consultas
pre-hechas, parametrizadas y descritas en lenguaje natural— y después un MCP que
simplemente lo envuelve. Este documento cubre **solo el banco**. El MCP es fase 2.

**Resultado esperado:** un catálogo versionado en git donde agregar un indicador es
escribir un archivo YAML, y un módulo Python que lo lee, valida y ejecuta devolviendo
datos ya agregados en un formato único.

## Decisiones tomadas

| Decisión | Elección |
|---|---|
| Qué devuelve el MCP | Datos ya agregados; la IA nunca ve ni escribe SQL |
| Dónde vive el catálogo | YAML versionado en el repo (revisable en PR) |
| De dónde lee | Directo a la BD de cada pipeline, reusando `core/db.py` |
| Dónde vive el SQL | Inline en el YAML, con parámetros nombrados |
| Formato de salida | Formato largo único para todos los indicadores |
| Alcance v1 | Piloto: empleo, seguridad, pobreza (~12 indicadores) |

## Contrato de salida (formato largo)

Toda consulta devuelve **exactamente** estas columnas, sin excepción:

| Columna | Tipo | Nota |
|---|---|---|
| `cve_geo` | `text` | `'00'` nacional, `'14'` entidad, `'14039'` municipio — siempre con `LPAD` |
| `nombre_geo` | `text` | Nombre oficial (`nomgeo` / `nom_ent`) |
| `periodo` | `text` | ISO: `2024`, `2024-Q1`, `2024-03` |
| `valor` | `numeric` | |
| `categoria` | `text` \| `NULL` | Desagregación opcional: sexo, tipo de delito, actividad |

Nombre del indicador, unidad, fuente y definición **no se repiten por fila**: viven en el
YAML y el MCP los adjunta como metadata de la respuesta.

## Archivos a crear

```
core/indicadores/
├── __init__.py
├── modelo.py          # Pydantic: Indicador, Parametro, Cobertura
├── registro.py        # carga + valida YAMLs, resuelve conexión, ejecuta
├── __main__.py        # CLI: listar / describir / ejecutar
├── README.md          # plantilla del YAML y cómo agregar un indicador
└── catalogo/
    ├── empleo/*.yaml
    ├── seguridad/*.yaml
    └── pobreza/*.yaml
tests/indicadores/
├── test_catalogo.py   # sin BD
└── test_ejecucion.py  # con BD (opt-in)
```

Sin dependencias nuevas: `PyYAML`, `pydantic`, `sqlalchemy` y `pandas` ya están en
`requirements.txt`.

## Formato del YAML

```yaml
id: tasa_desocupacion_municipal
nombre: Tasa de desocupación municipal
tema: empleo
definicion: >
  Porcentaje de la población económicamente activa que se encuentra desocupada,
  estimado a nivel municipal para todos los municipios del país.
unidad: porcentaje
fuente: INEGI — Indicadores del Mercado Laboral Municipal (ILMM)
pipeline: ilmm                 # ← determina a qué BD se conecta
origen: vw_tasa_desocupacion   # vista/MV de la que lee (trazabilidad)
nivel: municipal               # nacional | estatal | municipal
periodicidad: anual
cobertura:
  geografica: Nacional
  temporal: "2017-2024"
notas: |
  La vista de origen expone también el error estándar; el banco no lo devuelve
  porque rompería el formato largo.
  No comparable con la tasa estatal de la ENOE: distinto diseño muestral.
parametros:
  - nombre: cve_geo
    tipo: str
    requerido: false
    descripcion: Clave INEGI de 5 dígitos del municipio (ej. 14039). Omitir para todos.
  - nombre: anio_min
    tipo: int
    requerido: false
    descripcion: Año inicial de la serie. Omitir para la serie completa.
sql: |
  SELECT
      clave_municipio::text          AS cve_geo,
      nombre::text                   AS nombre_geo,
      EXTRACT(YEAR FROM fecha)::text AS periodo,
      valor::numeric                 AS valor,
      NULL::text                     AS categoria
  FROM vw_tasa_desocupacion
  WHERE (CAST(:cve_geo AS text) IS NULL
         OR clave_municipio = CAST(:cve_geo AS text))
    AND (CAST(:anio_min AS integer) IS NULL
         OR EXTRACT(YEAR FROM fecha) >= CAST(:anio_min AS integer))
  ORDER BY cve_geo, periodo
```

### Dos reglas obligatorias del SQL

1. **Filtros opcionales con `(:param IS NULL OR condición)`.** Un solo SQL cubre todas las
   combinaciones de filtros sin construcción dinámica de cadenas → sin inyección posible.
   Los parámetros siempre van como binds de SQLAlchemy `text()`.
2. **Siempre `CAST(:param AS tipo)`.** Un bind `NULL` sin cast hace que PostgreSQL falle
   con *"could not determine data type of parameter"*. Aplica en **cada** aparición del
   parámetro, no solo en la primera.

## `registro.py` — API

```python
listar(tema=None, nivel=None) -> list[dict]    # metadata sin sql, para descubrimiento
obtener(id: str) -> Indicador                  # metadata completa
ejecutar(id: str, **params) -> list[dict]      # datos en formato largo
```

- Carga y valida todos los YAML al importar (`lru_cache`); ids duplicados, SQL que no
  empiece con `SELECT`/`WITH`, SQL que no proyecte las cinco columnas, o desajuste entre
  `parametros` y los `:binds` del SQL revientan ahí, no en producción.
- Conexión: `BaseConfig` con `extra="ignore"` leyendo `env_path(ind.pipeline)`
  (`core/config.py`) → `Database(ind.pipeline, cfg.database_url)` (`core/db.py`), cacheada
  por pipeline. El `extra="ignore"` no es opcional: el `.env` de cada pipeline trae sus
  propias variables (URLs de fuente, tamaños de lote) y `BaseConfig` a secas las rechaza.
- `ejecutar` valida los params contra el modelo Pydantic, rellena con `None` los no
  provistos, envuelve el SQL en `SELECT * FROM (...) LIMIT 5001` y ejecuta con
  `execution_options(postgresql_readonly=True)` para que un agente no pueda escribir ni
  traerse una serie completa por accidente. Se pide una fila de más a propósito: si llegan
  más de 5000, `ejecutar` lanza un error nombrando los parámetros con los que acotar, en vez
  de devolver una serie truncada que el agente reportaría como completa.

Extracción de binds para la validación (evita los `::` de los casts de PostgreSQL):

```python
BINDS = re.compile(r"(?<!:):([a-zA-Z_][a-zA-Z0-9_]*)")
```

## Indicadores del piloto

Los tres temas cubren a propósito las tres formas de tabla del repo: serie ya larga
(`ilmm`), ancha por mes (`delitos_fuero_comun`) y ancha por concepto
(`pobreza_multidimensional`). Si el formato largo aguanta las tres, aguanta los 33.

### Empleo

| id | Pipeline | Origen | Notas de mapeo |
|---|---|---|---|
| `tasa_desocupacion_municipal` | `ilmm` | `vw_tasa_desocupacion` | La MV ya trae `clave_municipio` a 5 dígitos (`LPAD` en el JOIN a `cvegeo_municipalities`) y `nombre`; solo renombrar. No expone `cvegeo` ni `nom_municipio` |
| `ocupacion_informal_municipal` | `ilmm` | `vw_ocupacion_informal` | Igual que el anterior |
| `tasa_desocupacion_jalisco` | `enoe_microdatos` | `mv_enoe_tasas_jalisco` | Columna `td`. `cve_geo` fijo `'14'`, `periodo = anio \|\| '-Q' \|\| trimestre` |
| `tasa_informalidad_laboral_jalisco` | `enoe_microdatos` | `mv_enoe_tasas_jalisco` | Columna `til1` |
| `tasa_subocupacion_jalisco` | `enoe_microdatos` | `mv_enoe_tasas_jalisco` | Columna `tsub` |

**Ojo:** `mv_enoe_tasas` (la versión municipal) agrupa por `entidad_id` pero **no lo
expone en el SELECT**, solo `municipio_id` (= `cve_mun`, 3 dígitos). No se puede formar
una `cve_geo` de 5 dígitos a partir de ella, así que no se cataloga. Su índice único
`(anio, trimestre, municipio_id)` también colisionaría entre estados — vale la pena
levantar un issue aparte.

### Seguridad — `delitos_fuero_comun`

Vista base `vw_delitos_serie_historica`, que ya desapila los 12 meses:
`anio, cve_municipio (5 díg. con LPAD), clave_ent, entidad, municipio,
bien_juridico_afectado, tipo_delito, subtipo_delito, modalidad, mes, conteo`.

| id | Origen | Notas de mapeo |
|---|---|---|
| `homicidio_doloso_municipal` | `vw_homicidio_doloso` | `subtipo_delito = 'Homicidio doloso'` |
| `feminicidio_municipal` | `vw_feminicidio` | `tipo_delito = 'Feminicidio'` y `subtipo <> 'Tentativa de feminicidio'` |
| `incidencia_delictiva_municipal` | `vw_delitos_serie_historica` | Parámetro `tipo_delito` → columna `categoria` |

`mes` viene como nombre en español; convertir con
`array_position(ARRAY['Enero',...,'Diciembre'], mes)` para armar `periodo = 'YYYY-MM'`.

### Pobreza — `pobreza_multidimensional`

Vista `vw_pobreza_multidimencional` (sic, con la errata en el nombre real):
`cve_mun VARCHAR(5)`, `nombre_municipio`, `cve_ent VARCHAR(2)`, `nombre_entidad`, `anio
SMALLINT` (2010, 2015, 2020) y ~30 columnas anchas `*_porcentaje` / `*_personas`.

| id | Columna origen |
|---|---|
| `pobreza_municipal` | `pobreza_porcentaje` |
| `pobreza_extrema_municipal` | `pobreza_ext_porcentaje` |
| `rezago_educativo_municipal` | `rez_edu_porcentaje` |
| `carencia_acceso_salud_municipal` | `car_salud_porcentaje` |

Requieren **unpivot**: cada indicador es un `SELECT` de una columna distinta de la misma
vista. `cve_geo = cve_mun` (ya viene a 5 dígitos), `periodo = anio::text`.

## Verificación

**Sin base de datos** — `pytest tests/indicadores/test_catalogo.py`:

- Todos los YAML validan contra el modelo Pydantic (`extra="forbid"`).
- `id` único en todo el catálogo; `pipeline` existe en `core/pipelines/`.
- Cada `parametro` declarado aparece como `:nombre` en el `sql`, y viceversa.
- El `sql` empieza con `SELECT` o `WITH` (nada de DDL/DML en el catálogo).
- El `sql` proyecta las cinco columnas del contrato de salida.

**Con base de datos** — `pytest tests/indicadores/test_ejecucion.py` (marcado
`@pytest.mark.integration`, requiere el `.env` de los pipelines piloto):

- Cada indicador se ejecuta y devuelve filas; los que rebasan el límite sin filtros se acotan
  en el fixture (`ACOTAR`).
- Las columnas devueltas son exactamente `cve_geo, nombre_geo, periodo, valor, categoria`.
- `cve_geo` no es nulo y tiene 2 o 5 caracteres.
- El filtro opcional por municipio filtra de verdad, no se ignora.

**Manual:**

```bash
python -m core.indicadores listar --tema empleo
python -m core.indicadores describir tasa_desocupacion_municipal
python -m core.indicadores ejecutar tasa_desocupacion_municipal -p cve_geo=14039
```

## Trampas conocidas

- **`municipio_id` tiene tres patrones de JOIN** ([`estandares_datos.md`](estandares_datos.md) §2).
  El SQL del YAML es responsable de normalizar a `cve_geo` de 5 dígitos con `LPAD`; nunca
  asumir el patrón de otro pipeline.
- **Las vistas materializadas necesitan `REFRESH`.** El campo `origen` deja rastro de
  cuál, pero el refresh sigue siendo responsabilidad del `load.py` del pipeline
  (`core/utils/views.py`). El banco solo lee.
- **Los `COMMENT ON` existentes** (17 archivos en `migrations/*/sql/V*__comments_*.sql`)
  son la mejor materia prima para redactar `definicion` y `notas`: copiar de ahí, no
  inventar.
- **Algunos README de pipeline están desfasados** respecto a las migraciones — el de
  `ilmm`, por ejemplo, describe tablas `ilmm`/`ilmm_indicador` que no existen; el esquema
  real es `stg_ilmm` + `cat_ilmm_estimador`. Vale la regla de
  [`architecture.md`](architecture.md) §5: **las migraciones son la fuente de verdad**.
- El banco **no toca los pipelines**: no se modifican `schemas.py`, migraciones ni DAGs.

## Fuera de alcance (fase 2)

El servidor MCP, que vive en otro repositorio. Serán tres tools (`listar_indicadores`,
`describir_indicador`, `consultar_indicador`) que delegan 1:1 en `registro.py`. Nada del
diseño anterior cambia al agregarlo — por eso el banco va primero.

Las reglas de negocio que ese proyecto debe respetar están en
[`contrato_banco_indicadores.md`](contrato_banco_indicadores.md), escrito para leerse sin
abrir este repo.
