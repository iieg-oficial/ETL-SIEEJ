# Indicadores del Mercado de Trabajo Municipal (ILMM)

> Pipeline que ingesta los Indicadores del Mercado Laboral a Nivel Municipal (ILMM) publicados por el INEGI, cargando la tasa de desocupación y el porcentaje de ocupación informal para cada municipio del país a partir de 2017.

---

## Fuente

| Campo       | Valor                                                                                                                |
|-------------|----------------------------------------------------------------------------------------------------------------------|
| Proveedor   | INEGI — Programa de Indicadores del Mercado Laboral Municipal                                                        |
| URL         | `https://www.inegi.org.mx/contenidos/programas/ilmm/datosabiertos/conjunto_de_datos_ilmm_{year}_1t_csv.zip`         |
| Formato     | ZIP/CSV (`encoding: utf-8-sig`, separador `,`)                                                                       |
| Frecuencia  | Anual (publicación en junio de cada año)                                                                             |
| Último dato | 2024-01-01                                                                                                           |

---

## Esquema de Base de Datos

> **Nota:** el diagrama ER no está disponible (`assets/er_ilmm.png` no existe).

### Tablas catálogo

| Tabla              | Descripción                                                                     |
|--------------------|---------------------------------------------------------------------------------|
| `ilmm_estimador`   | Tipo de estimación: Valor, Error estándar, Límites de confianza, CV             |
| `ilmm_indicador`   | Indicadores disponibles: `tasa_desocupacion`, `porcentaje_ocupacion_informal`   |

### Tabla principal

| Tabla  | Descripción                                                                                      |
|--------|--------------------------------------------------------------------------------------------------|
| `ilmm` | Registro de hechos por municipio, año e indicador. Incluye valor estimado y error estándar.      |

**Columnas de `ilmm`:**

| Columna           | Tipo           | Descripción                                                    |
|-------------------|----------------|----------------------------------------------------------------|
| `id`              | BIGSERIAL PK   | Clave surrogate autoincremental                                |
| `clave_municipio` | VARCHAR(5)     | Clave INEGI 5 dígitos (ej. `"01001"`)                          |
| `fecha`           | DATE           | Primer día del año de referencia (ej. `2024-01-01`)            |
| `indicador_id`    | SMALLINT FK    | Referencia a `ilmm_indicador.id`                               |
| `valor`           | NUMERIC(12,4)  | Estimación puntual del indicador (puede ser NULL)              |
| `error_estandar`  | NUMERIC(12,4)  | Error estándar de la estimación (puede ser NULL)               |

**Restricción de unicidad:** `(clave_municipio, fecha, indicador_id)`

**Índices:** `idx_ilmm_municipio`, `idx_ilmm_fecha`, `idx_ilmm_indicador`

### Vista de integración

No implementada.

---

## Implementación ETL

| Modo      | Implementado | Tipo                                  |
|-----------|:------------:|---------------------------------------|
| Bootstrap | ✅            | Carga histórica completa 2017–2024    |
| Update    | ✅            | Solo-inserciones (`append-only`)      |

### DAGs

| DAG                    | Schedule            | Descripción                              |
|------------------------|---------------------|------------------------------------------|
| `etl_ilmm_bootstrap`   | On demand           | Carga histórica completa 2017–2024       |
| `etl_ilmm_update`      | `0 0 1 6 *`         | Actualización anual el 1 de junio        |

---

## Diagrama de archivos

```
core/pipelines/ilmm/
├── config.py
├── attributes.py
├── schemas.py
├── .env.example
├── README.md          ← este archivo
├── eda/
│   └── reporte_eda.json
└── stages/
    ├── extract.py
    ├── transform.py
    └── load.py

dags/
└── etl_ilmm.py

migrations/ilmm/sql/
└── V001__create_ilmm_tables.sql
```

---

## Metodología ETL

### Extract

Descarga ZIPs públicos del INEGI sin credenciales, uno por año. Cada ZIP contiene un CSV en `conjunto_de_datos/conjunto_de_datos_ilmm_{year}_1t.csv`. Todos los años se descargan en secuencia, se concatenan en un único DataFrame y se persisten en `data/extract/ilmm/ilmm_raw.pkl`.

En modo **bootstrap** se descargan los años definidos en `BOOTSTRAP_YEARS` (por defecto 2017–2024). En modo **update** se descarga únicamente el año en curso.

### Transform

A partir del DataFrame crudo se aplican las siguientes transformaciones:

1. **Filtrado de agregados**: se eliminan filas con `ent=0` o `mun=0` (totales nacionales y estatales).
2. **Filtrado por estimador**: se retienen solo `est=1` (Valor) y `est=2` (Error estándar).
3. **Construcción de `clave_municipio`**: `LPAD(ent, 2) || LPAD(mun, 3)` → 5 dígitos.
4. **Pivote por indicador**:
   - `indicador_id=1` (`tasa_desocupacion`): `valor = 100 − ocupados(est=1)`, `error_estandar = ocupados(est=2)`.
   - `indicador_id=2` (`porcentaje_ocupacion_informal`): `valor = informales(est=1)`, `error_estandar = informales(est=2)`.
5. **Fecha**: se asigna `fecha = date(year, 1, 1)` por cada año.

El resultado se persiste en `data/transform/ilmm/ilmm_transformed.pkl`.

### Load

Inserta los registros en la tabla `ilmm` en chunks de 5,000 filas usando `INSERT … ON CONFLICT DO NOTHING` sobre la llave única `(clave_municipio, fecha, indicador_id)`. Al finalizar, limpia los archivos temporales de `data/extract/` y `data/transform/`.

**Bootstrap validado:** 39,404 registros cargados (8 años × ~2,469 municipios × 2 indicadores). Cobertura: `2017-01-01` → `2024-01-01`.

---

## Variables de entorno

Definidas en `.env.example`. Crear `.env` local con los valores reales (no commitear).

| Variable          | Descripción                                             |
|-------------------|---------------------------------------------------------|
| `LOG_LEVEL`       | Nivel de log (`INFO` por defecto)                       |
| `DB_USER`         | Usuario de la base de datos                             |
| `DB_PASSWORD`     | Contraseña de la base de datos                          |
| `DB_HOST`         | Host de la base de datos                                |
| `DB_PORT`         | Puerto de la base de datos                              |
| `DB_NAME`         | Nombre de la base de datos (`ilmm`)                     |
| `ILMM_BASE_URL`   | URL plantilla de descarga (contiene `{year}`)           |
| `BOOTSTRAP_YEARS` | Lista de años a cargar en bootstrap (ej. `[2017,...,2024]`) |

---

## Pasos manuales requeridos

1. Copiar `.env.example` a `.env` y completar las credenciales de base de datos.
2. Ejecutar las migraciones: `just migrate ilmm`.
3. Ejecutar el bootstrap desde Airflow (`etl_ilmm_bootstrap`) o localmente:
   ```bash
   conda run -n etl python dags/etl_ilmm.py
   ```
