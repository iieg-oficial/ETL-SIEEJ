# delitos_fuero_comun

> Pipeline ETL para el Registro Nacional de Incidencia Delictiva (RNID) del fuero común a nivel municipal, publicado mensualmente por la SSPC (Secretaría de Seguridad y Protección Ciudadana), con cobertura histórica 2015-2025 y actualización mensual para 2026.

---

## Fuentes

| Campo       | Fuente 1 — Histórico                                | Fuente 2 — 2026                                     |
|-------------|-----------------------------------------------------|-----------------------------------------------------|
| Proveedor   | SSPC / CNI                                          | SSPC / CNI                                          |
| Archivo     | `Municipal-Delitos-2015-2025_mar2026.csv`            | `RNID-Delitos_Municipal-2026-mar2026.csv`            |
| Formato     | ZIP → CSV (latin1, `,`)                             | ZIP → CSV (latin1, `,`)                             |
| Cobertura   | 2015–2025, 2 486 municipios, 2 562 994 filas         | 2026 (parcial: ene–mar), 2 510 municipios, 286 140 filas |
| Frecuencia  | Bootstrap único (se publica anualmente)             | Bootstrap + actualización mensual                   |
| Columnas    | 21                                                  | 21                                                  |
| Nivel       | Municipal                                           | Municipal                                           |

> **Nota de las URLs originales:** En el brief de la fuente, la etiqueta "Fuente 1 Histórico" apunta al ZIP del 2026, y la etiqueta "Fuente 2 2026" apunta al ZIP histórico. Los nombres de variable en `.env.example` respetan la semántica real (no la etiqueta del brief).

---

## Esquema de Base de Datos

> Diagrama ER no disponible — el archivo `assets/er_delitos_fuero_comun.png` no existe en este pipeline.

### Tablas catálogo (migración V1)

| Tabla                          | Clave natural          | Descripción                                                     |
|--------------------------------|------------------------|-----------------------------------------------------------------|
| `cat_municipio`                | `cve_municipio` (5 dígitos INEGI) | Municipios con clave de entidad y nombre.           |
| `cat_bien_juridico_afectado`   | `bien_juridico_afectado` | Categoría de bien jurídico afectado.                         |
| `cat_tipo_delito`              | `tipo_delito`          | Tipo de delito.                                                 |
| `cat_subtipo_delito`           | `subtipo_delito`       | Subtipo; FK a `cat_tipo_delito`.                                |
| `cat_modalidad`                | `modalidad`            | Modalidad; FK a `cat_subtipo_delito` (NULL cuando coincide texto). |

### Tablas de staging

| Tabla                                | Migración | Filas aprox. | Descripción                                                        |
|--------------------------------------|-----------|--------------|--------------------------------------------------------------------|
| `stg_delitos_fuero_comun_2015_2025`  | V2        | 2 562 994    | Carga histórica. Bootstrap único. FK a catálogos + 12 columnas mensuales. |
| `stg_delitos_fuero_comun_2026`       | V3        | 286 140+     | Año en curso. Bootstrap + upsert mensual. Añade `updated_at`.      |

NK compartida (restricción `UNIQUE`): `(anio, cve_municipio, bien_juridico_afectado_id, tipo_delito_id, subtipo_delito_id, modalidad_id)`.

### Vistas analíticas (migración V4)

| Vista                            | Fuentes                | Descripción                                                                                |
|----------------------------------|------------------------|--------------------------------------------------------------------------------------------|
| `v_delitos_serie_historica`      | 2015-2025 ∪ 2026       | Serie completa desagregada en filas `(mes, conteo)`. Excluye NULL y ceros.                 |
| `v_homicidio_doloso`             | ambas                  | `subtipo_delito = 'Homicidio doloso'`.                                                      |
| `v_tentativa_homicidio_doloso`   | solo 2026              | Categoría nueva 2026. `subtipo_delito = 'Tentativa de homicidio doloso'`.                  |
| `v_feminicidio`                  | ambas                  | `tipo_delito = 'Feminicidio'` excluyendo tentativa.                                        |
| `v_tentativa_feminicidio`        | solo 2026              | Categoría nueva 2026. `subtipo_delito = 'Tentativa de feminicidio'`.                       |
| `v_otros_vida_integridad`        | ambas                  | Tipo "otros vida/integridad" + tentativas de homicidio/feminicidio en 2026.                |
| `v_narcomenudeo`                 | ambas                  | Subtipos de narcomenudeo (venta y posesión simple comparables entre series).               |
| `v_extorsion`                    | ambas                  | `tipo_delito = 'Extorsión'` excluyendo tentativas (solo 2026).                             |
| `v_tentativa_extorsion`          | solo 2026              | Categorías nuevas 2026: tentativa de extorsión presencial y por otros medios.              |
| `v_otros_patrimonio`             | ambas                  | Tipo "otros patrimonio" + tentativas de extorsión en 2026.                                 |
| `v_trata_personas`               | ambas                  | Tipos "Trata de personas" y "Pornografía infantil".                                        |
| `v_otros_libertad_personal`      | ambas                  | Tipos de privación ilegal de libertad, retención de menores, y otros.                      |
| `v_otros_libertad_sexual`        | ambas                  | Delitos contra la libertad y seguridad sexual y violencia de género.                       |
| `v_otros_sociedad`               | ambas                  | Tipos "otros contra la sociedad" y "Discriminación".                                       |
| `v_otros_fuero_comun`            | ambas                  | Tipos residuales del fuero común y suplantación de identidad.                              |
| `v_servidores_publicos`          | ambas                  | Delitos cometidos por servidores públicos, administración de justicia y tortura.            |

---

## Implementación ETL

| Modo      | Implementado | Tipo                    | DAG                                   | Schedule         |
|-----------|:------------:|-------------------------|---------------------------------------|------------------|
| Bootstrap | ✅            | Carga histórica completa | `etl_delitos_fuero_comun_bootstrap`   | `None` (manual)  |
| Update    | ✅            | Upsert mensual (2026)   | `etl_delitos_fuero_comun_update`      | `0 12 1 * *`     |

---

## Diagrama de archivos

```
core/pipelines/delitos_fuero_comun/
├── config.py
├── attributes.py
├── schemas.py
├── .env.example
├── README.md  ← este archivo
├── eda/
│   ├── eda_delitos_fuero_comun.py
│   └── reporte_eda.json
└── stages/
    ├── extract.py
    ├── transform.py
    └── load.py

dags/
└── etl_delitos_fuero_comun.py

migrations/delitos_fuero_comun/sql/
├── V1__create_catalogos.sql
├── V2__create_stg_2015_2025.sql
├── V3__create_stg_2026.sql
└── V4__create_vistas.sql
```

---

## Metodología ETL

### Extract

Descarga dos ZIPs desde SharePoint de la SSPC via HTTP (`requests`, timeout 300 s). En modo **bootstrap** descarga ambos archivos (histórico + 2026); en modo **update** descarga solo el ZIP 2026. Los ZIPs se descomprimen al directorio de trabajo y se eliminan al finalizar la etapa. Si el nombre de CSV esperado no se encuentra dentro del ZIP, se usa el primer `.csv` disponible.

### Transform

Lee los CSVs con encoding `latin1` y renombra las columnas al esquema interno. Normaliza `clave_ent` a dos dígitos con cero a la izquierda (el histórico viene como `'1'`–`'32'`). Convierte `anio` a `Int16` y las 12 columnas de meses a `Int32` nullable (pandas nullable integers). Extrae cinco catálogos deduplicados a partir de la combinación de ambas fuentes (para evitar nuevas categorías de 2026 ausentes en el histórico). Limpia el directorio `data/extract/` al finalizar.

### Load

Conecta a la base de datos y garantiza que el esquema exista (`metadata.create_all`). Carga los cinco catálogos con `insert_records` (ON CONFLICT DO NOTHING) y sincroniza secuencias. Construye mapas `{texto → id}` para resolver FKs antes de cargar el staging.

- **Bootstrap**: `bulk_insert` en lotes de `LOAD_BATCH_SIZE` (default 5 000) para ambas tablas de staging.
- **Update**: `upsert_records` en `stg_delitos_fuero_comun_2026` usando la NK como clave de conflicto; actualiza columnas mensuales y `updated_at`.

---

## Variables de entorno

Definidas en `.env.example`. Copiar a `.env` local con los valores reales (no commitear).

| Variable          | Descripción                                                              |
|-------------------|--------------------------------------------------------------------------|
| `LOG_LEVEL`       | Nivel de logging (`INFO`, `DEBUG`, etc.). Por defecto `INFO`.            |
| `DB_USER`         | Usuario de la base de datos PostgreSQL.                                  |
| `DB_PASSWORD`     | Contraseña del usuario de la base de datos.                              |
| `DB_HOST`         | Host del servidor PostgreSQL.                                            |
| `DB_PORT`         | Puerto PostgreSQL (por defecto `5432`).                                  |
| `DB_NAME`         | Nombre de la base de datos. Por defecto `delitos_fuero_comun`.           |
| `URL_HISTORICO`   | URL de descarga directa del ZIP con el histórico 2015-2025 (SharePoint). |
| `URL_2026`        | URL de descarga directa del ZIP con los datos 2026 (SharePoint).         |
| `CSV_HISTORICO`   | Nombre esperado del CSV dentro del ZIP histórico (opcional; tiene default). |
| `CSV_2026`        | Nombre esperado del CSV dentro del ZIP 2026 (opcional; tiene default).   |
| `LOAD_BATCH_SIZE` | Tamaño de lote para `bulk_insert`. Por defecto `5000`.                   |

---

## Reglas de negocio

1. **Normalización de `clave_ent`**: El histórico 2015-2025 almacena la clave de entidad sin cero inicial (`'1'`–`'32'`). La etapa de transform aplica `.str.zfill(2)` para homologar con el formato de 2026 (`'01'`–`'32'`).

2. **Catálogos unificados**: Los catálogos se construyen combinando ambas fuentes antes de la carga. Esto garantiza que las categorías nuevas de 2026 (tentativas de homicidio, feminicidio, extorsión; pornografía infantil) queden registradas aunque no existan en el histórico.

3. **Meses no publicados son NULL, no cero**: Las columnas mensuales admiten `NULL`. Un valor `NULL` indica que el mes no ha sido publicado; un `0` indica que no hubo delitos registrados ese mes en ese municipio/categoría.

4. **NK del staging**: La restricción de unicidad `(anio, cve_municipio, bien_juridico_afectado_id, tipo_delito_id, subtipo_delito_id, modalidad_id)` previene duplicados. En modo update, actúa como clave de upsert.

5. **Histórico es bootstrap-only**: `stg_delitos_fuero_comun_2015_2025` no admite actualizaciones parciales. Si el proveedor publica una revisión histórica, se requiere borrar y re-cargar la tabla.

6. **Upsert mensual de 2026**: Cada ejecución de update descarga el CSV completo de 2026 (el proveedor acumula meses en el mismo archivo). El upsert actualiza las columnas mensuales y `updated_at` en registros existentes e inserta los nuevos.

---

## Notas metodológicas (SSPC)

La SSPC introdujo cambios en la taxonomía de delitos a partir de 2026:

| Categoría nueva (2026)              | Equivalencia histórica (2015-2025)                                              |
|-------------------------------------|---------------------------------------------------------------------------------|
| `Tentativa de homicidio doloso`      | Incluida en "Otros delitos que atentan contra la vida y la Integridad corporal" |
| `Tentativa de feminicidio`           | Incluida en "Otros delitos que atentan contra la vida y la Integridad corporal" |
| `Tentativa de extorsión presencial`  | Incluida en "Otros delitos que atentan contra el patrimonio"                    |
| `Tentativa de extorsión por otros medios` | Incluida en "Otros delitos que atentan contra el patrimonio"               |
| `Pornografía infantil`               | Incluida en "Trata de personas"                                                 |
| Subtipos de narcomenudeo             | Desagregados en "con fines de venta" y "posesión simple" (antes un solo subtipo) |

Las vistas analíticas (`v_otros_vida_integridad`, `v_otros_patrimonio`, `v_trata_personas`, `v_narcomenudeo`) implementan las reglas de comparabilidad indicadas en las notas metodológicas de la SSPC. Las vistas de tentativas están restringidas a `anio = 2026` porque no existen registros equivalentes en el histórico.

---

## Pasos para ejecutar

```bash
# 1. Configurar credenciales
cp core/pipelines/delitos_fuero_comun/.env.example \
   core/pipelines/delitos_fuero_comun/.env
# Editar .env con usuario, contraseña, host y URLs reales

# 2. Crear base de datos y aplicar migraciones
just pipeline-deploy delitos_fuero_comun

# 3. Bootstrap completo (histórico 2015-2025 + 2026)
conda run -n etl python dags/etl_delitos_fuero_comun.py

# 4. Actualización mensual (solo 2026, ejecutar tras publicación SSPC)
# Desde Airflow (DAG etl_delitos_fuero_comun_update) o:
conda run -n etl python -c "
from core.pipelines.delitos_fuero_comun.stages.extract import DelitosExtract
from core.pipelines.delitos_fuero_comun.stages.transform import DelitosTransform
from core.pipelines.delitos_fuero_comun.stages.load import DelitosLoad
from core.pipeline import Pipeline
Pipeline('delitos_fuero_comun', [
    DelitosExtract(mode='update'),
    DelitosTransform(mode='update'),
    DelitosLoad(mode='update'),
]).run(mode='update')
"
```
