# defunciones

## Descripción general

Registro de defunciones generales de México publicado por la Dirección General de Información en Salud (DGIS) de la Secretaría de Salud, filtrado a residentes de Jalisco (`ent_resid = 14`). Cada fila es una defunción registrada, con su causa (CIE-10 y clasificaciones agregadas), características demográficas y socioeconómicas del fallecido, circunstancias de la muerte y su geografía (registro, residencia y ocurrencia). Se carga desde la edición 2019 en adelante, que es el inicio del esquema de codificación vigente de DGIS.

## Fuente general

http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_defunciones_gobmx.html

## Fuente específica

Las URLs se descubren automáticamente de la página (no se hardcodean por año). Opcionalmente se puede fijar una edición:

```shell
REGISTRO_URL=http://www.dgis.salud.gob.mx/descargas/datosabiertos/defunciones/registro/DEFUN_2024.zip
CATALOG_URL=http://www.dgis.salud.gob.mx/descargas/datosabiertos/defunciones/catalogos/CATALOGOS_DEFUN_2024.zip
```

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `2024` |
| Frecuencia de actualización | Anual |
| Desagregación | Municipal |
| ¿Tiene update? | Sí |
| Update | Automático |

## Diagrama de entidad relación

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_defunciones

| variable | descripción |
|---|---|
| `id` | Identificador único de la fila (surrogate) |
| `entidad_registro` | Entidad de registro |
| `municipio_regis` | Municipio de registro |
| `entidad_registro_id` / `municipio_regis_id` | Entidad y municipio de registro (nombres, contra `cat_localidades`) |
| `tamanio_loc_regis_id` | Tamaño de localidad de registro |
| `localidad_regis_id` | Localidad de registro (resuelta contra `cat_localidades`) |
| `entidad_resid` | Entidad de residencia habitual (código crudo) |
| `municipio_resid` | Municipio de residencia habitual (código crudo) |
| `entidad_resid_id` / `municipio_resid_id` | Entidad y municipio de residencia (nombres, contra `cat_localidades`) |
| `tamanio_loc_resid_id` | Tamaño de localidad de residencia |
| `localidad_resid_id` | Localidad de residencia habitual (resuelta contra `cat_localidades`) |
| `entidad_ocurr` | Entidad de ocurrencia (código crudo) |
| `municipio_ocurr` | Municipio de ocurrencia (código crudo) |
| `entidad_ocurr_id` / `municipio_ocurr_id` | Entidad y municipio de ocurrencia (nombres, contra `cat_localidades`) |
| `tamanio_loc_ocurr_id` | Tamaño de localidad de ocurrencia |
| `localidad_ocurr_id` | Localidad de ocurrencia (resuelta contra `cat_localidades`) |
| `causa_defuncion_id` | Causa de la defunción (CIE-10, lista detallada) |
| `cod_adicional_id` | Código adicional CIE |
| `lista_mex_id` | Causa de la defunción (lista mexicana) |
| `sexo_id` | Sexo del fallecido |
| `entidad_pais_nac_id` | Lugar de nacimiento, entidad federativa o país (resuelto contra `cat_entidad_pais`) |
| `afromex_id` | Autoadscripción afromexicana |
| `cond_indigena_id` | Autoadscripción indígena |
| `lengua_indigena_id` | Condición de habla lengua indígena |
| `lenguas_id` | Clave de la lengua indígena |
| `nacionalid_id` | Nacionalidad (mexicana / extranjera) |
| `origen_id` | Origen específico (estado si mexicano, país si extranjero) |
| `edad_id` | Edad del fallecido (código DGIS unidad+cantidad) |
| `edad_gestacional_id` | Semanas de gestación |
| `gramos_id` | Peso en gramos (fallecidos con menos de 28 días) |
| `dia_ocurr_id` / `mes_ocurr_id` / `anio_ocurr_id` | Fecha de ocurrencia |
| `dia_registro_id` / `mes_registro_id` / `anio_registro_id` | Fecha de registro |
| `dia_nacimiento_id` / `mes_nacimiento_id` / `anio_nacimiento_id` | Fecha de nacimiento |
| `condicion_act_id` | Condición de actividad económica |
| `ocupacion_id` | Ocupación (catálogo versionado) |
| `escolaridad_id` | Nivel de escolaridad |
| `edo_civil_id` | Estado conyugal |
| `tipo_defuncion_id` | Tipo de defunción / presunta violencia (catálogo versionado) |
| `ocurr_trab_id` | Ocurrió en el desempeño del trabajo |
| `lugar_ocurr_id` | Lugar de ocurrencia de la lesión |
| `parentesco_agre_id` | Parentesco del presunto agresor |
| `violencia_familiar_id` | Violencia familiar |
| `asist_medica_id` | Condición de atención médica |
| `cirugia_id` | Condición de cirugía |
| `accidental_vio_id` | Muerte accidental o violenta |
| `necropsia_id` | Condición de necropsia |
| `uso_necropsia_id` | Uso de la necropsia |
| `encefalica_id` | Condición de muerte encefálica |
| `donador_id` | Condición de donador de órganos |
| `sitio_ocur_id` | Sitio de ocurrencia de la defunción |
| `certificante_id` | Persona que certificó la defunción |
| `derecho_hab_id` | Derechohabiencia (catálogo versionado) |
| `embarazo_id` | Condición de embarazo |
| `rel_emba_id` | Causas relacionadas con el embarazo |
| `horas_id` / `minutos_id` | Hora de la defunción |
| `capitulo` / `grupo` | Capítulo y grupo CIE-10 (crudos) |
| `capitulo_grupo_id` | Clasificación CIE-10 capítulo/grupo (surrogate) |
| `lista_cie_id` | Lista de tabulación 1 para mortalidad de la CIE |
| `gr_lismex_id` | Lista mexicana de enfermedades (grupo) |
| `area_urbana_id` | Área urbana-rural de residencia |
| `edad_agrupada_id` | Edad agrupada |
| `complicaron_id` | Complicaron el embarazo |
| `dia_certificacion_id` / `mes_certificacion_id` / `anio_certificacion_id` | Fecha de certificación |
| `maternas_id` | Defunciones maternas totales |
| `entidad_ocules` / `municipio_ocules` | Entidad y municipio de ocurrencia de la lesión (códigos crudos) |
| `entidad_ocules_id` / `municipio_ocules_id` | Entidad y municipio de ocurrencia de la lesión (nombres, contra `cat_localidades`) |
| `localidad_ocules_id` | Localidad de ocurrencia de la lesión (resuelta contra `cat_localidades`) |
| `razon_m_id` | Razón de mortalidad materna |
| `dis_re_oax` | Distritos de registro de Oaxaca |
| `cvegeo_resid_id` | Municipio de residencia en `cvegeo` (solo clave geográfica y geometría, para mapas) |
| `cvegeo_ocurr_id` | Municipio de ocurrencia en `cvegeo` (solo clave geográfica y geometría, para mapas) |
| `edicion_id` | Edición DGIS de la que proviene la fila (procedencia) |
| `fecha_actualizacion` | Fecha de carga ETL |

Cada columna `*_id` es FK a su catálogo (`cat_*`). Las columnas `entidad_*` / `municipio_*` sin sufijo `_id` son los códigos crudos DGIS y se conservan porque de ellos se derivan las FK. Para cada uno de los cuatro roles geográficos (registro, residencia, ocurrencia, ocurrencia de la lesión) hay tres FK a `cat_localidades`, una por nivel: entidad, municipio y localidad. Los `cvegeo_*_id` apuntan a `cvegeo_municipalities` y sirven **solo** como clave geográfica y geometría para mapas, nunca como etiqueta.

### cat_entidad_pais

Catálogo combinado de entidades federativas mexicanas (`001`-`032`) y países (`100`+), fuente `paises.csv` de DGIS. Incluye sentinelas: `888` No aplica, `998` Mexicana sin entidad especificada, `999` No especificado. No está disponible en todas las ediciones (ver nota abajo).

### cat_localidades

Catálogo versionado y jerárquico (`entidad_municipio_localidad_<edicion>.csv`). Su `codigo` de 9 dígitos combina `cve_ent` (2) + `cve_mun` (3) + `cve_loc` (4). El archivo trae una fila por cada nivel, no solo por localidad:

| codigo | descripción |
|---|---|
| `14 000 0000` | Jalisco |
| `14 039 0000` | Guadalajara |
| `88 000 0000` | Entidad no aplica para A00 - R99 Y V90 - Y89 |
| `88 888 0000` | Municipio no aplica para A00 - R99 Y V90 - Y89 |
| `99 000 0000` | Entidad no especificada |
| `99 999 0000` | Municipio no especificado |
| `99 999 9999` | Localidad no especificada |

Por eso los tres niveles de cada rol se resuelven contra la misma tabla, y los sentinelas rinden su nombre en vez de NULL.

## Migraciones

| migración | descripción |
|---|---|
| `V1__foreign_tables.sql` | Extensión `postgres_fdw` y foreign tables `cvegeo_states` / `cvegeo_municipalities` (conexión a la BD `cvegeo`) |
| `V2__catalogs_defunciones.sql` | Crea los ~48 catálogos (simples, codificados, versionados, override, compuesto, edición) |
| `V3__tables_defunciones.sql` | Crea la tabla de hechos `stg_defunciones` con sus FK a los catálogos locales |
| `V4__comments_defunciones.sql` | `COMMENT ON TABLE`/`COLUMN` de todas las tablas (documentación en BD desde el diccionario DGIS) |
| `V5__views_defunciones.sql` | Vistas analíticas: `vw_defunciones` (base denormalizada) y agregadas (principales causas, por municipio, mortalidad materna e infantil) |
| `V6__normalize_anio_descripcion.sql` | Normaliza `cat_anio.descripcion` ("Año 2019" → "2019") |
| `V7__geo_catalogs_defunciones.sql` | Crea `cat_entidad_pais` y `cat_localidades`; reemplaza los códigos crudos por FKs resueltas en los tres niveles (entidad, municipio, localidad) de los cuatro roles geográficos; separa la clave `cvegeo_*_id` de la etiqueta; recrea las vistas de V5 |

## Variables de entorno

| variable | descripción |
|---|---|
| `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` / `DB_NAME` | Conexión a la base del pipeline |
| `CHUNK_SIZE` | Tamaño de lote al insertar la tabla de hechos (default 10000) |
| `BACKFILL_MIN_YEAR` | Año mínimo del backfill en bootstrap (default 2019) |
| `CATALOG_URL` / `REGISTRO_URL` | Opcional: fija una edición específica en vez de descubrir la última |
| `CATALOGO_2021_FILE_ID` | **Requerido.** Id del espejo en Drive del catálogo 2021 (ver nota abajo) |

### Nota: catálogo 2021 servido desde Drive

El catálogo `CATALOGOS_DEFUN_2021.zip` **no es alcanzable desde la red del IIEG**: el proxy de salida
(Cisco WSA) intercepta la petición y devuelve un HTTP 500 sintético. La misma URL responde 200 desde
fuera de la red, y otras ediciones del mismo host (2022, 2024) sí descargan, así que no es un bloqueo
de dominio ni un límite de tasa. El caso está escalado a redes.

La edición 2021 no es prescindible: aporta 2 catálogos que no existen en 2022
(`entidad_municipio_localidad_2021`, `violencia_familiar`) y 28 de los 34 catálogos compartidos tienen
contenido distinto. Como los catálogos son versionados, cada defunción se resuelve contra el catálogo
de su propia edición, así que omitirla no falla: etiqueta mal los registros de 2021.

Por eso se mantiene un espejo del ZIP original en Drive, byte a byte idéntico a la fuente (incluyendo
su ZIP anidado). El extract lo descarga por id cuando la edición es 2021; el resto se baja de DGIS
como siempre.

Cuando redes libere el acceso directo, basta con eliminar `MIRRORED_EDITION` de `constants/source.py`
y esta variable.

## Notas metodológicas

### Extract

Descubre las ediciones publicadas scrapeando la página de DGIS (patrón `CATALOGOS_DEFUN_*` / `registro/DEFUN_*`). En **bootstrap** descarga cada edición desde `BACKFILL_MIN_YEAR`; en **update** solo la última. Por cada edición baja el ZIP del registro (~240 MB), lo lee como texto (preservando ceros a la izquierda), lo filtra a residentes de Jalisco y concatena las ediciones. Absorbe las rarezas de la fuente: ZIP anidado (2021), BOM UTF-8 vs us-ascii, filas basura antes del header, tabs/espacios en los valores, y el rename de columna `presunto → tipo_defun` (aplicado por edición antes de concatenar). Los catálogos versionados se leen de **cada** edición; los demás, de la última.

### Transform

Construye los registros de cada familia de catálogo y de la tabla de hechos. Normaliza descripciones (capitalize + acentos vía `apply_accents`, siglas y epónimos en su casing canónico). Renombra las columnas del registro a nombres descriptivos (`causa_defuncion_id`, `entidad_registro`, …). Un guardia de reconciliación avisa columnas de la fuente no modeladas (se ignoran) y columnas modeladas ausentes en la edición (quedan NULL), sin pérdida silenciosa.

### Load

Hace upsert de los catálogos (por `id`, `codigo`, `(codigo, edicion)` o `(cap, gpo)` según la familia). Resuelve en la tabla de hechos: códigos alfanuméricos → id surrogate, códigos versionados → surrogate por `(codigo, edición)`, `capitulo`+`grupo` → surrogate, entidad / municipio / localidad de cada rol → surrogate de `cat_localidades` por `(codigo, edición)` (cada nivel desde su propio código crudo), y entidad+municipio → id de `cvegeo` para la clave de mapas. Recarga idempotente por año (`DELETE` del año + `bulk_insert` en lotes de `CHUNK_SIZE`).

## Ejecución

Primero aplicar las migraciones:

```shell
just flyway-migrate defunciones
```

**Bootstrap** (carga inicial, todas las ediciones ≥ `BACKFILL_MIN_YEAR`) — DAG `etl_defunciones_bootstrap`, on demand. Se dispara desde Airflow o localmente:

```shell
python dags/etl_defunciones.py
```

**Update** (anual, DAG `etl_defunciones_update`, schedule `0 4 1 7 *`): baja la última edición publicada y la carga de forma idempotente por año (`DELETE` del año + reinserción). Se ejecuta automáticamente en Airflow.

## Notas adicionales

- **Familias de catálogos.** Ningún catálogo tiene id de texto. (1) *Simples*: `id` entero = código fuente. (2) *Codificados* (causa CIE, códigos, listas, peso): el código alfanumérico va en `codigo` con un `id` surrogate. (3) *Versionados* (ocupación, tipo de defunción, derechohabiencia): sus códigos cambian de significado entre ediciones, así que llevan `(codigo, edicion_id)` con id surrogate. (4) *Override* (`razon_materna`): definido a mano porque el archivo de DGIS está inconsistente. (5) *Compuesto* (`capitulo_grupo`): surrogate sobre `(cap, gpo)`, con `gpo = 0` para el capítulo completo.

- **Versionado por edición.** DGIS reutiliza códigos con distinto significado entre años (ej. ocupación `11` = "No trabaja" en 2019, "Funcionarios" en 2024). Cargar histórico contra un solo catálogo produciría etiquetas incorrectas en silencio (misresolución). Por eso esos catálogos se versionan por edición y cada fila se resuelve contra el catálogo de **su** año. El backfill arranca en 2019 porque antes cambió el esquema de codificación.

- **Geografía sin FK.** `cvegeo_municipalities` es una foreign table (FDW), y PostgreSQL no permite FK a foreign tables. Por eso `cvegeo_resid_id` / `cvegeo_ocurr_id` no son constraints: se resuelven en el load (`entidad + municipio → cvegeo → id`) usando `core.utils.geo`.

- **Nombres contra `cat_localidades`, claves contra `cvegeo`.** Antes, `municipio_resid_id` / `municipio_ocurr_id` apuntaban a `cvegeo` y se usaban también como etiqueta. `cvegeo` no conoce los códigos sentinela, así que convertía en NULL en silencio los municipios `999` (308 filas en residencia, 1,071 en ocurrencia) y habría hecho lo mismo con el 90% de `entidad_ocules` (`88` = "No aplica", 320,242 filas). Ahora cada FK apunta a donde dice su nombre: la etiqueta sale de `cat_localidades` (que sí trae los sentinelas) y `cvegeo` queda reservado para la clave geográfica y la geometría de los mapas.

- **Cada nivel se resuelve por su propio código.** La entidad usa `(ent, 0, 0)` y el municipio `(ent, mun, 0)`; no se derivan de la fila de la localidad. El catálogo no es denso: `(14, 039, 9999)` no existe aunque `(14, 120, 9999)` sí (solo 854 de las combinaciones `(ent, mun)` tienen fila `9999`). Derivarlos de la jerarquía de la localidad haría que una localidad no resuelta arrastrara consigo a la entidad y al municipio.

- **Alcance Jalisco.** Se cargan solo defunciones de residentes de Jalisco (`ent_resid = 14`). Cambiar `JALISCO_FILTER_COLUMN` a `ent_ocurr` cargaría por ocurrencia en vez de residencia.

- **`paises.csv` no está en todas las ediciones.** La edición 2021 no trae `paises.csv` (confirmado contra el ZIP real), por lo que `cat_entidad_pais` no tiene filas de esa edición y las defunciones de 2021 quedan con `entidad_pais_nac_id` en NULL aunque el código crudo `ent_nac` exista en el registro. No se trata de una pérdida introducida por este cambio: es una ausencia de la fuente, igual que otros catálogos faltantes en 2021 (ver nota de Drive arriba). `cat_localidades` no tiene este problema: `entidad_municipio_localidad_2021.csv` sí existe en esa edición.

- **Múltiples clasificaciones de causa.** El registro trae la causa a varios niveles (`causa_defuncion` CIE completa, `lista_cie`/`lista_mexicana` listas cortas, `capitulo_grupo`), útiles para tablas de "principales causas" sin manejar los ~10 mil códigos CIE.

- **FDW.** El bootstrap requiere que la BD `cvegeo` exista con las tablas `cvegeo_*` y que `flyway.conf` defina los placeholders `fdw_*`. Sin el FDW, las columnas `municipio_*_id` quedan NULL (degradación elegante) pero el resto carga.
