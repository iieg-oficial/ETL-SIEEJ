# Contrato del banco de indicadores

> **Para quién es este documento.** Para quien construya la **api/MCP** que expone los datos
> del ETL-SIEEJ a agentes de IA, en un repositorio distinto a éste. Es autocontenido: describe
> todas las reglas de negocio del banco sin que haga falta leer el código de ETL-SIEEJ.
>
> El diseño interno y por qué se tomó cada decisión están en
> [`banco_indicadores.md`](banco_indicadores.md). La implementación de referencia vive en
> [`core/indicadores/`](../core/indicadores/README.md) — unas 150 líneas de Python.

---

## Índice

1. [Qué es el banco y qué no es](#1-qué-es-el-banco-y-qué-no-es)
2. [Contrato de salida](#2-contrato-de-salida)
3. [Anatomía del YAML](#3-anatomía-del-yaml)
4. [Reglas obligatorias del SQL](#4-reglas-obligatorias-del-sql)
5. [Temporalidad y geografía](#5-temporalidad-y-geografía)
6. [Resolución de la conexión](#6-resolución-de-la-conexión)
7. [Seguridad y límites](#7-seguridad-y-límites)
8. [Validaciones al cargar el catálogo](#8-validaciones-al-cargar-el-catálogo)
9. [Especificación del MCP](#9-especificación-del-mcp)
10. [Errores](#10-errores)
11. [Cómo consumir el catálogo desde otro repo](#11-cómo-consumir-el-catálogo-desde-otro-repo)

---

## 1. Qué es el banco y qué no es

El ETL-SIEEJ son **33 bases de datos PostgreSQL separadas** (una por pipeline), ~198 archivos
de migración y ~135 vistas con esquemas heterogéneos. Darle eso a un modelo produce SQL malo,
cruces equivocados de `municipio_id` (hay tres patrones conviviendo, ver
[`estandares_datos.md`](estandares_datos.md) §2) e indicadores inventados.

El banco invierte el orden: **primero un catálogo curado** de consultas pre-hechas,
parametrizadas y descritas en lenguaje natural; **después** una capa que lo expone.

| El banco **sí** | El banco **no** |
|---|---|
| Devuelve datos ya agregados, listos para citar | Genera SQL, ni deja que el agente lo escriba |
| Describe cada indicador en lenguaje natural | Expone el esquema de las bases |
| Lee de las vistas y vistas materializadas de cada pipeline | Escribe, refresca MVs ni toca los pipelines |
| Se amplía escribiendo un YAML | Se amplía escribiendo código |

**El agente nunca ve el SQL.** El campo `sql` del YAML es un detalle de implementación del
servidor; no viaja en ninguna respuesta.

**El banco solo lee.** Refrescar una vista materializada sigue siendo responsabilidad del
`load.py` del pipeline que la publica. Si los datos están viejos, el problema está aguas
arriba, no aquí.

---

## 2. Contrato de salida

Toda consulta, sin excepción, devuelve **exactamente estas cinco columnas, en este orden**:

| # | Columna | Tipo SQL | Descripción |
|:-:|---|---|---|
| 1 | `cve_geo` | `text` | Clave INEGI. `'00'` nacional, `'14'` entidad (2 díg.), `'14039'` municipio (5 díg.). Siempre con `LPAD`, nunca numérica |
| 2 | `nombre_geo` | `text` | Nombre oficial de la geografía (`nomgeo` / `nom_ent`) |
| 3 | `periodo` | `text` | ISO ascendente-ordenable: `2024`, `2024-Q1`, `2024-03` |
| 4 | `valor` | `numeric` | El dato. Su unidad está en la metadata, no en la fila |
| 5 | `categoria` | `text` \| `NULL` | Desagregación opcional: sexo, tipo de delito, actividad económica. `NULL` cuando el indicador no desagrega |

**Nombre del indicador, unidad, fuente y definición no se repiten por fila.** Viven en la
metadata del YAML y la api los adjunta una sola vez al sobre de la respuesta. Repetirlos por
fila multiplicaría el costo en tokens del agente sin agregar información.

Ese formato único es lo que hace intercambiables 33 esquemas distintos: el agente aprende
cinco columnas una vez y sirven para todos los indicadores presentes y futuros.

> **Ausencia de fila ≠ cero.** Varias vistas de origen descartan ceros y nulos. Un periodo sin
> fila no distingue "cero eventos" de "sin dato". Si el indicador tiene esa trampa, va dicha en
> su campo `notas`, y la api debe entregar `notas` junto con los datos.

---

## 3. Anatomía del YAML

Un indicador es **un archivo YAML**. Ruta obligatoria:

```
catalogo/<tema>/<id>.yaml
```

con dos invariantes que se validan: **el nombre de la carpeta es el `tema`** y **el nombre del
archivo (sin extensión) es el `id`**.

### Campos

| Campo | Tipo | Oblig. | Reglas |
|---|---|:-:|---|
| `id` | `str` | ✅ | Único en todo el catálogo. `snake_case`. Es la clave pública que usa el agente |
| `nombre` | `str` | ✅ | Título legible, para mostrar |
| `tema` | `str` | ✅ | Igual al nombre de la carpeta. Es la faceta de descubrimiento (`empleo`, `seguridad`, `pobreza`, …) |
| `definicion` | `str` | ✅ | Qué mide, en una o dos frases. Materia prima: los `COMMENT ON` de las migraciones |
| `unidad` | `str` | ✅ | `porcentaje`, `personas`, `carpetas de investigación`, … |
| `fuente` | `str` | ✅ | Institución y programa. Ej. `INEGI — Indicadores del Mercado Laboral Municipal (ILMM)` |
| `pipeline` | `str` | ✅ | Determina **a qué base se conecta** (§6). Debe existir como pipeline |
| `origen` | `str` | ✅ | Vista o MV de la que lee. Solo trazabilidad; no se usa para construir el query |
| `nivel` | enum | ✅ | `nacional` \| `estatal` \| `municipal` |
| `periodicidad` | `str` | ✅ | `anual`, `trimestral`, `mensual`, `quinquenal`, … |
| `cobertura.geografica` | `str` | ✅ | Ej. `Nacional`, `Jalisco` |
| `cobertura.temporal` | `str` | ✅ | Ej. `"2017-2024"`, `"2015-actual"`. Entre comillas: es texto, no un rango |
| `notas` | `str` | ➖ | Trampas, no comparabilidad, qué **no** es el indicador. Se entrega al agente |
| `parametros` | lista | ➖ | Ver abajo. Vacía si el indicador no filtra |
| `sql` | `str` | ✅ | El query. **Nunca se expone** (§7) |

### `parametros[]`

| Campo | Tipo | Reglas |
|---|---|---|
| `nombre` | `str` | Debe aparecer como bind `:nombre` en el `sql`, y viceversa — el calce es exacto en ambas direcciones |
| `tipo` | enum | `str` \| `int`. Nada más. El valor recibido se coacciona con ese constructor |
| `requerido` | `bool` | Por defecto `false` |
| `descripcion` | `str` | Se le muestra al agente. Debe incluir un ejemplo y decir qué pasa si se omite |

**Validación estricta de esquema.** Los modelos prohíben campos extra (`extra="forbid"` en
Pydantic): una llave mal escrita revienta al cargar, no se ignora en silencio.

### Ejemplo completo

```yaml
id: tasa_desocupacion_municipal
nombre: Tasa de desocupación municipal
tema: empleo
definicion: >
  Porcentaje de la población económicamente activa que se encuentra desocupada,
  estimado a nivel municipal para todos los municipios del país.
unidad: porcentaje
fuente: INEGI — Indicadores del Mercado Laboral Municipal (ILMM)
pipeline: ilmm
origen: vw_tasa_desocupacion
nivel: municipal
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

---

## 4. Reglas obligatorias del SQL

### 4.1 Filtros opcionales con `(:param IS NULL OR condición)`

Un **solo** SQL cubre todas las combinaciones de filtros. Nunca se arma el query concatenando
cadenas, ni se agregan cláusulas `WHERE` según qué parámetros llegaron.

```sql
WHERE (CAST(:cve_geo AS text) IS NULL OR clave_municipio = CAST(:cve_geo AS text))
  AND (CAST(:anio_min AS integer) IS NULL OR anio >= CAST(:anio_min AS integer))
```

Los parámetros ausentes se mandan como `NULL` y la condición se neutraliza sola. Como no hay
construcción dinámica de SQL, **no existe superficie de inyección**: los valores viajan
siempre como binds del driver.

### 4.2 `CAST(:param AS tipo)` en *cada* aparición

No solo en la primera. Un bind `NULL` sin cast hace que PostgreSQL falle con
*"could not determine data type of parameter $1"*, porque no puede inferir el tipo de un `NULL`
suelto.

### 4.3 Proyectar las cinco columnas con `AS`

Las cinco columnas de §2 deben aparecer literalmente como `AS cve_geo`, `AS nombre_geo`,
`AS periodo`, `AS valor`, `AS categoria`. Cuando una no aplica, se emite constante tipada:

```sql
'14'::text   AS cve_geo,      -- indicador estatal fijo
NULL::text   AS categoria     -- indicador sin desagregación
```

### 4.4 Solo lectura

El SQL debe empezar con `SELECT` o `WITH`. Nada de DDL ni DML en el catálogo.

### 4.5 Extracción de binds

Para validar el calce `parametros` ↔ `:binds` hay que extraer los binds del SQL con un regex
que **ignore los casts de PostgreSQL**:

```python
BINDS = re.compile(r"(?<!:):([a-zA-Z_][a-zA-Z0-9_]*)")
```

El lookbehind negativo `(?<!:)` es lo que impide que `valor::numeric` se lea como un bind
llamado `numeric`. Sin él, toda validación de parámetros da falsos positivos.

---

## 5. Temporalidad y geografía

Es lo que el agente pregunta siempre: *"dame X en el municipio Y para el periodo Z"*, igual
que en el visor del INEGI. El banco lo resuelve **dentro del SQL de cada YAML**, no en la capa
que lo envuelve.

### 5.1 Construcción de `periodo`

`periodo` es siempre `text`, y el formato depende de la forma de la fuente:

| Periodicidad | Formato | Construcción típica |
|---|---|---|
| Anual | `2024` | `EXTRACT(YEAR FROM fecha)::text` o `anio::text` |
| Trimestral | `2024-Q1` | `anio::text \|\| '-Q' \|\| trimestre::text` |
| Mensual | `2024-03` | `anio::text \|\| '-' \|\| LPAD(<mes>::text, 2, '0')` |
| Quinquenal | `2020` | `anio::text` |

Caso real que conviene conocer: el SESNSP publica el mes **como nombre en español**, así que
el YAML lo convierte a número dentro del SQL:

```sql
anio::text || '-' || LPAD(array_position(
    ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio',
          'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
    mes)::text, 2, '0')  AS periodo
```

El formato es lexicográficamente ordenable, así que ordenar por `periodo` como texto ordena
cronológicamente.

### 5.2 Filtrado temporal

**Un solo parámetro convencional: `anio_min` (`int`, opcional).** Recorta la serie por el
extremo inferior.

Deliberadamente **no** existen en v1: `anio_max`, rangos de fechas, ni filtro por `periodo`
exacto. El agente pide la serie y la recorta él; el catálogo no crece en superficie. Si se
agregan, deben agregarse como parámetro nuevo en los YAML — no como lógica en la api.

### 5.3 Filtrado geográfico

**Un solo parámetro convencional: `cve_geo` (`str`, opcional)**, la clave INEGI de 5 dígitos
del municipio. Omitirlo devuelve todos.

La columna de origen **cambia según el pipeline** (`clave_municipio`, `cve_mun`,
`cve_municipio`, …) porque conviven tres patrones de `municipio_id` en el repo. **El YAML
absorbe esa heterogeneidad**: normaliza a `cve_geo` de 5 dígitos con `LPAD` y expone siempre el
mismo nombre de parámetro. La api nunca debe intentar adivinar la columna.

Los indicadores de nivel `estatal` o `nacional` normalmente **no declaran `cve_geo`**: emiten
la clave como constante (`'14'::text AS cve_geo`). Que un parámetro exista o no es información
que el agente obtiene de la metadata, no que deba suponer.

---

## 6. Resolución de la conexión

Cada pipeline tiene **su propia base de datos**. El campo `pipeline` del YAML es lo que decide
a cuál conectarse:

```
YAML.pipeline  →  core/pipelines/<pipeline>/.env  →  DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
               →  postgresql://<user>:<password>@<host>:<port>/<db>
```

Reglas:

- **Un pool por pipeline, cacheado.** No abrir una conexión por consulta ni un pool global
  único: cada indicador puede vivir en una base distinta.
- **Ignorar las variables desconocidas del `.env`.** El `.env` de cada pipeline trae sus
  propias variables (URLs de fuente, tamaños de lote, credenciales de API). Un cargador de
  settings estricto las rechazaría y tumbaría el arranque. En la implementación de referencia
  esto es `extra="ignore"`; no es opcional.
- **`.env` ausente ⇒ el indicador no es consultable.** No es un error de catálogo: el YAML es
  válido, simplemente esa base no está configurada en este despliegue. La api debe reportarlo
  como indicador temporalmente no disponible, no como catálogo roto.
- **Los pools no se cierran.** La implementación de referencia cachea el `Database` por vida de
  proceso, lo cual es inocuo en un CLI. **Un servidor MCP es un proceso largo**: dimensionar el
  pool y considerar `pool_pre_ping` / `pool_recycle` (la referencia usa `pool_pre_ping=True`,
  `pool_recycle=3600`).

---

## 7. Seguridad y límites

Cinco garantías que la api **debe** preservar. Perder cualquiera convierte el banco en una
consola SQL abierta a un modelo de lenguaje.

| # | Garantía | Cómo |
|:-:|---|---|
| 1 | El agente nunca ve el SQL | La metadata que sale al exterior es el YAML **sin** el campo `sql` |
| 2 | El agente nunca escribe SQL | La única entrada libre son los valores de los parámetros declarados |
| 3 | Los valores viajan como binds | Nunca interpolación de cadenas. Ver §4.1 |
| 4 | La transacción es de solo lectura | `SET TRANSACTION READ ONLY` (en SQLAlchemy: `execution_options(postgresql_readonly=True)`) |
| 5 | El resultado está acotado | El SQL del catálogo se envuelve en `SELECT * FROM (…) _banco LIMIT <LIMITE>` |

### El límite falla ruidoso, no trunca en silencio

`LIMITE = 5000`. Devolver 5000 filas de una serie de 40000 y no decirlo es peor que fallar: el
agente reporta como completa una serie cortada.

Por eso se piden `LIMITE + 1` filas y, si llegan más de `LIMITE`, **se lanza un error** que
nombra los parámetros disponibles para acotar:

```
incidencia_delictiva_municipal: la consulta excede 5000 filas;
acota con ['anio_min', 'cve_geo', 'tipo_delito']
```

Ese mensaje es accionable: el agente reintenta con un filtro. La api debe propagarlo tal cual.

---

## 8. Validaciones al cargar el catálogo

Todas corren **al cargar el catálogo**, no al servir una consulta. Un catálogo inválido debe
impedir el arranque del servidor; nunca degradar en un error en producción frente al usuario.

| Validación | Error |
|---|---|
| El YAML valida contra el esquema, sin campos extra | `campo desconocido '<x>'` |
| `id` único en todo el catálogo | `id duplicado '<id>'` |
| Nombre de archivo (sin extensión) == `id` | `el id no coincide con el nombre del archivo` |
| Nombre de carpeta == `tema` | `el tema no coincide con la carpeta` |
| `pipeline` existe | `el pipeline '<p>' no existe` |
| `sql` empieza con `SELECT` o `WITH` | `el sql debe empezar con SELECT o WITH` |
| `sql` proyecta las 5 columnas con `AS` | `el sql no proyecta las columnas [...]` |
| `{parametros} == {binds del sql}` (exacto, ambas direcciones) | `desajuste entre parametros y binds del sql (declarados sin usar: [...], usados sin declarar: [...])` |

En tiempo de consulta solo quedan dos, sobre los parámetros recibidos:

- Parámetro no declarado ⇒ error. No se ignora.
- Parámetro `requerido` ausente ⇒ error.
- Parámetro opcional ausente ⇒ se manda `NULL` (que es lo que neutraliza el filtro, §4.1).
- Parámetro presente ⇒ se coacciona al `tipo` declarado (`"2020"` → `2020`).

---

## 9. Especificación del MCP

Tres tools. Cada una delega 1:1 en el banco; **no hay lógica de negocio en esta capa**.

| Tool | Entrada | Salida |
|---|---|---|
| `listar_indicadores` | `tema?`, `nivel?` | Lista de metadata, sin `sql` |
| `describir_indicador` | `id` | Metadata completa, sin `sql` |
| `consultar_indicador` | `id`, `parametros?` | Sobre con metadata + filas |

### 9.1 `listar_indicadores`

Descubrimiento. Es lo primero que llama el agente.

```json
{
  "type": "object",
  "properties": {
    "tema":  {"type": "string", "description": "Filtra por tema, ej. 'empleo'. Omitir para todos."},
    "nivel": {"type": "string", "enum": ["nacional", "estatal", "municipal"]}
  },
  "additionalProperties": false
}
```

Respuesta: `array` de objetos metadata (§3 sin `sql`).

```json
[
  {
    "id": "tasa_desocupacion_municipal",
    "nombre": "Tasa de desocupación municipal",
    "tema": "empleo",
    "definicion": "Porcentaje de la población económicamente activa que se encuentra desocupada...",
    "unidad": "porcentaje",
    "fuente": "INEGI — Indicadores del Mercado Laboral Municipal (ILMM)",
    "pipeline": "ilmm",
    "origen": "vw_tasa_desocupacion",
    "nivel": "municipal",
    "periodicidad": "anual",
    "cobertura": {"geografica": "Nacional", "temporal": "2017-2024"},
    "notas": "No comparable con la tasa estatal de la ENOE: distinto diseño muestral.",
    "parametros": [
      {"nombre": "cve_geo", "tipo": "str", "requerido": false,
       "descripcion": "Clave INEGI de 5 dígitos del municipio (ej. 14039). Omitir para todos."},
      {"nombre": "anio_min", "tipo": "int", "requerido": false,
       "descripcion": "Año inicial de la serie. Omitir para la serie completa."}
    ]
  }
]
```

> Con el catálogo ya grande, listar todo puede ser costoso en tokens. Opción admisible:
> devolver solo `id`, `nombre`, `tema`, `nivel`, `unidad` y `periodicidad`, y dejar el resto
> para `describir_indicador`. Lo que **no** es admisible es incluir `sql`.

### 9.2 `describir_indicador`

Metadata completa de uno. El agente la usa para saber qué parámetros existen antes de consultar.

```json
{
  "type": "object",
  "properties": {"id": {"type": "string"}},
  "required": ["id"],
  "additionalProperties": false
}
```

Respuesta: un objeto metadata, idéntico al de arriba.

### 9.3 `consultar_indicador`

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "parametros": {
      "type": "object",
      "description": "Parámetros declarados por el indicador. Ver describir_indicador.",
      "additionalProperties": {"type": ["string", "integer", "null"]}
    }
  },
  "required": ["id"],
  "additionalProperties": false
}
```

Respuesta — **la metadata acompaña a los datos**, para que el agente pueda citar unidad y
fuente sin una segunda llamada, y sin repetirlas en cada fila:

```json
{
  "indicador": "pobreza_municipal",
  "nombre": "Población en situación de pobreza, municipal",
  "unidad": "porcentaje",
  "fuente": "CONEVAL — Medición multidimensional de la pobreza",
  "notas": "Los años disponibles son 2010, 2015 y 2020; no es una serie anual continua.",
  "parametros_aplicados": {"cve_geo": "14039", "anio_min": null},
  "filas": [
    {"cve_geo": "14039", "nombre_geo": "Guadalajara", "periodo": "2010", "valor": 26.4, "categoria": null},
    {"cve_geo": "14039", "nombre_geo": "Guadalajara", "periodo": "2015", "valor": 23.1, "categoria": null},
    {"cve_geo": "14039", "nombre_geo": "Guadalajara", "periodo": "2020", "valor": 25.7, "categoria": null}
  ]
}
```

Reglas del sobre:

- `filas` respeta el orden y los nombres exactos de §2.
- `parametros_aplicados` incluye los opcionales resueltos a `null` — hace explícito que la
  serie no fue filtrada por ahí.
- `notas` se entrega **siempre** que exista. Es donde vive la letra chica que evita que el
  agente afirme de más.

### 9.4 Nota operativa

El servidor MCP es un proceso de larga vida frente a un CLI de una sola ejecución. Revisar §6
sobre pools cacheados y no cerrados antes de ponerlo bajo carga.

---

## 10. Errores

Todos los errores del banco son de un solo tipo en la implementación de referencia
(`ValueError`) y su mensaje está redactado para que **el agente pueda corregirse solo**. La api
los traduce a su transporte:

| Situación | Mensaje | HTTP | Recuperable por el agente |
|---|---|:-:|:-:|
| `id` inexistente | `Indicador '<id>' no existe en el catálogo` | 404 | ✅ vuelve a `listar_indicadores` |
| Parámetro no declarado | `<id>: parámetros desconocidos ['<x>']` | 400 | ✅ vuelve a `describir_indicador` |
| Falta un parámetro requerido | `<id>: falta el parámetro requerido '<x>'` | 400 | ✅ |
| Valor no coaccionable al tipo | error de conversión del tipo | 400 | ✅ |
| Resultado excede el límite | `<id>: la consulta excede 5000 filas; acota con [...]` | 413 | ✅ reintenta con filtro |
| Sin `.env` para el pipeline | indicador no disponible en este despliegue | 503 | ❌ es configuración |
| Base caída / query fallida | error del driver | 502 | ❌ |
| Catálogo inválido | ver §8 | — | ❌ impide el arranque |

Los errores recuperables deben llegarle al agente **con su texto íntegro**: la lista de
parámetros que trae el mensaje es justamente lo que le permite reintentar bien.

---

## 11. Cómo consumir el catálogo desde otro repo

Los **YAML son la parte portable**. `registro.py` no lo es: depende de `core.config` y
`core.db` de este repositorio.

Dos caminos:

### A. Reimplementar el motor (recomendado para el MCP)

El proyecto externo lee los YAML y reimplementa §3–§8. Son ~150 líneas: cargar y validar el
catálogo, resolver la conexión por pipeline, armar binds, ejecutar acotado y de solo lectura.
Las dependencias son las obvias: un parser YAML, un validador de esquemas y un driver de
PostgreSQL.

Para traer los YAML, en orden de preferencia:

1. **Submódulo de git o `git subtree`** apuntando a `core/indicadores/catalogo/` — el catálogo
   sigue teniendo un solo dueño y se actualiza con un `git pull`.
2. **Copia versionada** sincronizada en CI. Más simple, con riesgo de deriva.
3. **Paquete publicado** desde este repo. Solo vale la pena si aparece un tercer consumidor.

En cualquier caso el proyecto externo necesita, además de los YAML, **acceso de red y
credenciales de lectura a las bases de los pipelines** que cataloga.

### B. Consumir una api HTTP de este repo

Si se prefiere no duplicar el motor ni repartir credenciales de base, este repo expone una api
que envuelve `registro.py` y el MCP externo solo hace peticiones HTTP. Cambia el problema de
duplicación por un problema de despliegue y disponibilidad.

### Regla que no cambia en ningún camino

**El catálogo tiene un solo dueño: este repositorio.** Agregar o corregir un indicador es un PR
aquí, revisable como cualquier otro cambio. El proyecto externo consume; no edita YAML por su
cuenta. Es lo que impide que las definiciones de los indicadores institucionales se bifurquen.

---

## Referencias

| Documento | Qué aporta |
|---|---|
| [`banco_indicadores.md`](banco_indicadores.md) | Diseño interno, decisiones y el mapeo de los 12 indicadores piloto a sus vistas reales |
| [`core/indicadores/README.md`](../core/indicadores/README.md) | Cómo agregar un indicador; plantilla del YAML |
| [`estandares_datos.md`](estandares_datos.md) | Nomenclatura de tablas y los tres patrones de `municipio_id` |
| [`architecture.md`](architecture.md) | Reglas del ETL. §5: **las migraciones son la fuente de verdad**, no los README |
