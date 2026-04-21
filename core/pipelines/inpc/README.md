# Pipeline: INPC

Pipeline ETL para el Índice Nacional de Precios al Consumidor (INPC) publicado por el INEGI. Procesa series históricas de precios a nivel nacional, estatal y por ciudad.

## Fuentes de datos

El pipeline consume la API de series del INEGI, consultada por tipo de ubicación (nacional, entidad, ciudad):

- **URL**: `INPC_BASE_URL` e `INPC_URL_NODOS` configuradas en `.env`
- **Cobertura histórica**: A partir de enero de 1979 (`BOOTSTRAP_START_YEAR`)
- **Frecuencia de publicación**: Mensual. Cada observación representa el índice de precios de un mes dado
- **Ubicaciones**: 55 ciudades, 32 entidades federativas y nivel nacional
- **Categorías**: 9 objetos de gasto (índice general + 8 subcategorías)

## Esquema de base de datos

### Catálogos

```
┌──────────────────────────┐     ┌──────────────────────────┐
│         ciudades         │     │      objetos_gasto        │
│──────────────────────────│     │──────────────────────────│
│  id SERIAL PK            │     │  id INTEGER PK           │
│  ciudad VARCHAR(100)     │     │  objeto_gasto VARCHAR(100)│
│    UNIQUE NOT NULL       │     │    UNIQUE NOT NULL       │
│  entidad VARCHAR(100)    │     └──────────────────────────┘
└──────────────────────────┘
```

`ciudades` es un catálogo dinámico (extraído de los datos). `objetos_gasto` es estático con IDs predefinidos en `mappings.py`.

### Tablas principales

```
┌──────────────────────────────────────┐
│            inpc_ciudades             │
│──────────────────────────────────────│
│  id SERIAL PK                        │
│  ciudad_id → ciudades(id)            │
│  fecha DATE NOT NULL                 │
│  objeto_gasto_id → objetos_gasto(id) │
│  indice_de_precios FLOAT             │
│  fecha_actualizacion DATE NOT NULL   │
│  UNIQUE(ciudad_id, fecha,            │
│    objeto_gasto_id)                  │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│           inpc_entidades             │
│──────────────────────────────────────│
│  id SERIAL PK                        │
│  entidad_id INTEGER NOT NULL         │
│    (ref. cvegeo_states.cve_ent)      │
│  fecha DATE NOT NULL                 │
│  objeto_gasto_id → objetos_gasto(id) │
│  indice_de_precios FLOAT             │
│  fecha_actualizacion DATE NOT NULL   │
│  UNIQUE(entidad_id, fecha,           │
│    objeto_gasto_id)                  │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│            inpc_nacional             │
│──────────────────────────────────────│
│  id SERIAL PK                        │
│  fecha DATE NOT NULL                 │
│  objeto_gasto_id → objetos_gasto(id) │
│  indice_de_precios FLOAT             │
│  fecha_actualizacion DATE NOT NULL   │
│  UNIQUE(fecha, objeto_gasto_id)      │
└──────────────────────────────────────┘
```

**Catálogo estático**: `objetos_gasto` tiene IDs predefinidos definidos en `mappings.py` (9 categorías).

**Catálogo dinámico**: `ciudades` se extrae de los datos y se inserta con `ON CONFLICT DO NOTHING`.

**Llave única**: `(entidad_id, fecha, objeto_gasto_id)`, `(ciudad_id, fecha, objeto_gasto_id)` y `(fecha, objeto_gasto_id)` — cada registro representa el índice de precios de una ubicación/categoría en un mes dado.

## Flujo del pipeline

### Extract

1. Itera sobre tres tipos de ubicación: nacional, 55 ciudades (`INPC_CITIES`) y 32 entidades (`INPC_ENTITIES`)
2. Para cada ubicación, descubre los IDs de series disponibles en la API del INEGI mediante traversal recursivo del árbol de nodos (`discover_series_ids`)
3. Descarga los datos en formato CSV con hasta 6 reintentos; aplica 1 segundo de espera entre solicitudes
4. Parsea cada CSV (codificación latin-1, omite filas de encabezado):
   - Renombra columnas según `RENAME_HEADER`
   - Reemplaza abreviaturas de mes en español (Ene → 01, Feb → 02, …) y convierte a `date`
   - Agrega `fecha_actualizacion` con la fecha de ejecución
   - Para ciudades: agrega `ciudad_id`, `ciudad` y `entidad`
   - Para entidades: agrega `entidad_id` y nombre de entidad
5. Persiste tres pickles en `data/extract/inpc/` (ciudades, entidades, nacional)

### Transform

1. Carga los pickles generados en la etapa de extracción
2. Reemplaza valores nulos conocidos (`N/E` → `None`)
3. Aplica formato wide→long (`melt`) sobre las 9 columnas numéricas de objetos de gasto por cada tipo de ubicación:
   - Ciudades: pivota sobre `[ciudad_id, fecha, fecha_actualizacion]`
   - Entidades: pivota sobre `[entidad_id, entity, fecha, fecha_actualizacion]`
   - Nacional: pivota sobre `[fecha, fecha_actualizacion]`
4. Convierte valores de `indice_de_precios` a float con 3 decimales
5. Mapea nombres de objeto de gasto a su `objeto_gasto_id` y elimina la columna de texto
6. Construye catálogos:
   - `ciudades`: registros únicos de `(ciudad_id, ciudad, entidad)`
   - `objetos_gasto`: extraído del enum `ObjetoGasto` en `mappings.py`
7. Filtra filas anteriores a `date_from` en modo update
8. Persiste tres pickles en `data/transform/inpc/`

### Load

1. Inserta `objetos_gasto` con IDs predefinidos (`ON CONFLICT DO NOTHING`)
2. Sincroniza secuencia de `ciudades` e inserta registros dinámicos (`ON CONFLICT DO NOTHING`)
3. Mapea `entidad_id`:
   - Obtiene tabla `cvegeo_states` (nom_ent → cve_ent) vía postgres_fdw
   - Aplica aliases de nombres (`ENTITY_NAME_ALIASES`) y normaliza con `normalize_col()`
   - Mapea al `cve_ent` correspondiente y elimina columna de texto
4. Inserta en `inpc_ciudades`, `inpc_entidades` e `inpc_nacional` en chunks de 10,000 registros con `ON CONFLICT DO NOTHING`

## Periodicidad

- **Bootstrap**: Bajo demanda. Carga la serie histórica completa desde 1979 hasta el año en curso (`etl_inpc_bootstrap`)
- **Update**: Mensual (`@monthly`). Consulta el último `fecha_actualizacion` en la base de datos y descarga desde ese año en adelante (`etl_inpc_update`)
