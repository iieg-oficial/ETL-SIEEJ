# Testing Checklist — ETL-SIEEJ Production Pipelines

> **Fecha de generación**: 2026-05-21
> **Versión del sistema**: v1.1.0
> **Pipelines en producción**: 18

---

## Instrucciones de uso

1. Antes de cada despliegue o revisión, ejecuta los checks de la **Sección A** (comunes a todos los pipelines).
2. Luego ejecuta los checks de la sección específica del pipeline en cuestión.
3. Marca cada ítem con `[x]` cuando pase, `[~]` si aplica parcialmente, o `[-]` si no aplica al pipeline.

---

## Sección A — Checks comunes a todos los pipelines

### A1. Migraciones (Flyway)

- [ ] `flyway.conf` configurado (no commiteado; solo el `.example`)
- [ ] `just flyway-reset {pipeline}` termina con exit code 0
- [ ] `just flyway-info {pipeline}` muestra todos los scripts como `Success`
- [ ] Todos los scripts `V*.sql` son idempotentes (`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`)
- [ ] `V1__foreign_tables.sql` referencia tablas de `cvegeo` correctamente
- [ ] `V2__catalogs.sql` existe y crea tablas con prefijo `cat_`
- [ ] `V3__tables_{pipeline}.sql` crea tablas principales con prefijo `stg_`
- [ ] `UniqueConstraint` definidos en la migración y en el schema ORM
- [ ] Columna `id SERIAL PRIMARY KEY` en todas las tablas

### A2. DAG (Airflow)

- [ ] `python dags/etl_{pipeline}.py` no lanza excepciones
- [ ] El DAG aparece en la UI de Airflow sin errores de importación
- [ ] El DAG bootstrap tiene `schedule=None` (disparo manual)
- [ ] El DAG update tiene el cron correcto (ver tabla por pipeline)
- [ ] `catchup=False` configurado en el DAG update
- [ ] Los tasks tienen dependencias declaradas (`>>`)
- [ ] Nombre del dag sigue el patrón `etl_{pipeline}_bootstrap` / `etl_{pipeline}_update`

### A3. Estructura de archivos

- [ ] `core/pipelines/{pipeline}/constants.py` existe (solo MAYÚSCULAS)
- [ ] `core/pipelines/{pipeline}/schemas.py` existe con modelos SQLAlchemy 2.x
- [ ] `core/pipelines/{pipeline}/attributes.py` (o carpeta `attributes/`) existe
- [ ] `core/pipelines/{pipeline}/stages/extract.py` existe
- [ ] `core/pipelines/{pipeline}/stages/transform.py` existe
- [ ] `core/pipelines/{pipeline}/stages/load.py` existe
- [ ] `core/pipelines/{pipeline}/.env.example` existe y commiteado
- [ ] `migrations/{pipeline}/flyway.conf.example` existe y commiteado
- [ ] Helpers de pipeline-específicos en `core/pipelines/{pipeline}/helpers/`

### A4. Calidad de código

- [ ] Imports ordenados: stdlib → third-party → `core.*` (línea en blanco entre grupos)
- [ ] Sin URLs hardcodeadas en stages (deben estar en `constants.py` o `config.py`)
- [ ] Sin credenciales en el código (todo via `.env`)
- [ ] Logging usando `get_logger()` de `core.utils.logger`
- [ ] Sin lógica duplicada de `core/utils/` (usar `normalize_col`, `list_values_to_null`, etc.)
- [ ] Schemas SQLAlchemy 2.0 (`Mapped`, `mapped_column`) — sin sintaxis 1.x
- [ ] FK columns: patrón `{tabla_singular}_id` (ej. `municipio_id`, `cultivo_id`)

### A5. Extract stage

- [ ] La fuente de datos es accesible (no devuelve 403 / 500)
- [ ] El archivo de inventario se genera en `data/extract/{pipeline}/`
- [ ] Modo bootstrap descarga el dataset completo
- [ ] Modo update descarga solo datos incrementales/recientes
- [ ] Registros extraídos > 0 (o log explícito si la fuente está vacía)
- [ ] Descompresión de ZIP/CSV funciona correctamente (si aplica)
- [ ] Los nombres de columnas en la fuente coinciden con `RENAME_HEADER` en `constants.py`

### A6. Transform stage

- [ ] Lee correctamente el inventario de `data/extract/{pipeline}/`
- [ ] `NULL_VALUES` convertidos a `None` (incluyendo `"N/A"`, `"n/a"`, `"NA"`, `"-"`, `""`)
- [ ] Renombrado de columnas completo y correcto
- [ ] Columnas de texto en `TITLE_COLS` aplicadas con `.title()` y `apply_accents()`
- [ ] Columnas de fecha parseadas a `date`/`datetime` (no strings)
- [ ] Columnas numéricas casteadas a `int`/`float` (sin dtype `object`)
- [ ] Sin `NaN` en columnas FK tras `.map()` (verificar con `df[col].isna().sum()`)
- [ ] Duplicados removidos donde aplique
- [ ] Output guardado en `data/transform/{pipeline}/` como parquet o pickle
- [ ] Shape del DataFrame razonable (columnas y filas en rango esperado)

### A7. Load stage

- [ ] Catálogos (`cat_*`) se insertan ANTES de las tablas principales
- [ ] `sync_id_sequence()` llamado tras cargar catálogos con IDs fijos
- [ ] `df.astype(object).where(df.notna(), None)` aplicado antes de insertar
- [ ] La columna `id` SERIAL excluida de la lista de columnas en INSERT
- [ ] `insert_records()` o `upsert_records()` de `core.utils.bulk_ops` (sin `session.add()`)
- [ ] FK constraints satisfechos (sin IDs huérfanos)
- [ ] `cleanup_pipeline_data()` llamado al finalizar
- [ ] Sesión de base de datos cerrada correctamente
- [ ] Logs muestran conteo de registros por tabla

### A8. Calidad de datos (post-load)

- [ ] Conteos de registros razonables (no 0, salvo fuente genuinamente vacía)
- [ ] Fechas en rango plausible (sin fechas futuras inesperadas)
- [ ] Métricas numéricas no negativas (salvo que el dominio lo permita)
- [ ] Códigos geográficos (`municipio_id`, `estado_id`) resueltos a valores conocidos de `cvegeo`
- [ ] Sin PKs duplicadas en la tabla principal
- [ ] Encoding correcto: acentos y ñ preservados en campos de texto
- [ ] Columnas de timestamp (`fecha_actualizacion`, `updated_at`) tienen valores recientes

---

## Sección B — Checks por pipeline

---

### B1. `agropecuario_siap` — Datos Agrícolas SIAP

**Fuente**: SIAP (Sistema de Información Agroalimentaria de Consulta)
**Cron update**: `@yearly`
**Tablas**: `cat_cultivos`, `cat_unidades_medida`, `cat_modalidades`, `cat_ciclos`, `cat_ctrs_apoyo_des_rural`, `cat_distritos_des_rural`, `stg_agricola`

#### Extract
- [ ] La URL de descarga SIAP es accesible para el año configurado
- [ ] El archivo descargado contiene todas las columnas esperadas (año, estado, municipio, cultivo, modalidad, ciclo)
- [ ] Registros cubren todos los municipios de Jalisco

#### Transform
- [ ] Columnas de área (sembrada, cosechada, siniestrada) casteadas a `float`
- [ ] Columna de producción casteada a `float`
- [ ] Nombres de cultivos y centros normalizados con `.title()` y `apply_accents()`
- [ ] `municipio_id` mapeado correctamente desde cvegeo (sin NaN residuales)

#### Load
- [ ] 6 catálogos cargados antes de `stg_agricola`
- [ ] `sync_id_sequence()` llamado para cada catálogo
- [ ] `UniqueConstraint(anio, municipio_id, cultivo_id, ...)` respetado (sin duplicados)
- [ ] Métricas float aceptan `None` (no todos los municipios tienen todos los cultivos)

#### Datos
- [ ] Al menos un registro por municipio de Jalisco para el año procesado
- [ ] Valores de producción (toneladas) en rango plausible (no negativos, no astronómicos)

---

### B2. `asg_imss` — Asegurados IMSS

**Fuente**: `http://datos.imss.gob.mx/` (archivos CSV mensuales)
**Cron update**: `0 6 1 * *` (1° de cada mes a las 6am)
**Tablas**: `stg_asg_imss_*` (múltiples tablas por concepto métrico)

#### Extract
- [ ] URL template `asg-{YYYY-MM-DD}.csv` genera la URL correcta para el período
- [ ] El archivo CSV del período actual existe en datos.imss.gob.mx (puede tardar hasta 5 días hábiles)
- [ ] Fallback documentado si el archivo del mes aún no está disponible
- [ ] Columnas de estado/municipio presentes y con codificación INEGI

#### Transform
- [ ] Columnas de asegurados (`ta`, `teu`, etc.) casteadas a `int`
- [ ] Columnas de masa salarial casteadas a `float`
- [ ] Claves de estado/municipio mapeadas a `municipio_id` de cvegeo
- [ ] Sin NaN en columnas de conteos (rellenar 0 si fuente lo omite)

#### Load
- [ ] Tablas separadas por concepto creadas en orden correcto
- [ ] Modo update inserta solo el período nuevo (sin duplicar períodos ya cargados)
- [ ] `UniqueConstraint(anio, mes, municipio_id, ...)` respetado

#### Datos
- [ ] Registros para los 125 municipios de Jalisco
- [ ] Conteos de asegurados no negativos
- [ ] Variación intermensual en rango plausible (no > 50% de un mes al otro)

---

### B3. `censo_poblacion` — Censo de Población 2020

**Fuente**: INEGI Censo 2020
**Cron update**: `None` (datos decenales, carga manual)
**Tablas**: `stg_censo_poblacion_datos`, catálogos de atributos

#### Extract
- [ ] Archivos fuente disponibles (descarga previa o path local configurado)
- [ ] Todos los archivos de entidades federativas incluidos
- [ ] Headers del CSV coinciden con `RENAME_HEADER` en constants

#### Transform
- [ ] Conteos de población casteados a `int`
- [ ] CVEGEO de localidad (6 dígitos) mapeado correctamente
- [ ] Columnas de sexo/edad normalizadas a valores de catálogo

#### Load
- [ ] Catálogos de atributos cargados primero
- [ ] `stg_censo_poblacion_datos` sin duplicados por clave (estado + municipio + localidad + variable)
- [ ] Total de registros consistente con la cobertura esperada (nacional o por estado)

#### Datos
- [ ] Suma de población por municipio coincide con totales INEGI publicados
- [ ] Sin localidades con población 0 a menos que sea inactiva

---

### B4. `censos_economicos` — Censos Económicos INEGI

**Fuente**: INEGI Censos Económicos (`https://www.inegi.org.mx/...`)
**Cron update**: `None` (por año de censo: 2019, 2024)
**Tablas**: `stg_ce_data`, `cat_actividad`, `cat_tamaño_estab`, catálogos adicionales

#### Extract
- [ ] URL por año y slug de estado accesible
- [ ] ZIP descargado y descomprimido correctamente
- [ ] Todos los archivos de estados incluidos (32 entidades)

#### Transform
- [ ] ~300 columnas renombradas correctamente via `RENAME_HEADER`
- [ ] Columnas de personal ocupado casteadas a `int`
- [ ] Columnas de producción/ventas casteadas a `float`
- [ ] Código SCIAN (actividad económica) mapeado a `cat_actividad`
- [ ] Columna de tamaño de establecimiento mapeada a `cat_tamaño_estab`

#### Load
- [ ] Catálogos cargados antes de `stg_ce_data`
- [ ] Manejo de múltiples años sin duplicar (clave: año + establecimiento + actividad)
- [ ] Sin error de memoria en datasets grandes (~300 cols × millones de filas)

#### Datos
- [ ] Registros para Jalisco presentes
- [ ] Totales de unidades económicas en rango plausible (comparar con DENUE)
- [ ] Sin valores negativos en métricas de empleo

---

### B5. `centros_educativos` — Escuelas (SEP/INEGI)

**Fuente**: INEGI / SEP directorio de escuelas
**Cron update**: `None` (carga manual o anual)
**Tablas**: `tipos_sostenimiento`, `niveles_educativos`, `escuelas`, `localidades`, `colonias`

#### Extract
- [ ] Fuente accesible y formato estable
- [ ] Columnas de geolocalización (latitud, longitud) presentes

#### Transform
- [ ] Nombre de escuela normalizado con `.title()` y `apply_accents()`
- [ ] Coordenadas casteadas a `float`
- [ ] Nivel educativo mapeado a `niveles_educativos`
- [ ] Tipo de sostenimiento mapeado a `tipos_sostenimiento`

#### Load
- [ ] `localidades` y `colonias` cargados antes de `escuelas`
- [ ] `tipos_sostenimiento` y `niveles_educativos` cargados antes de `escuelas`
- [ ] Coordenadas en rango de México (lat: 14–33, lon: -118 a –86)

#### Datos
- [ ] Escuelas de Jalisco presentes para todos los niveles
- [ ] Sin escuelas con coordenadas fuera de México

---

### B6. `datamexico` — Data México API

**Fuente**: API de Data México (`dataméxico.org`)
**Cron update**: `0 8 1 */3 *` (trimestral, 1° del mes a las 8am)
**Tablas**: `stg_datamexico_empleo`, indicadores económicos varios

#### Extract
- [ ] Autenticación/token de API vigente (si requiere)
- [ ] Paginación manejada correctamente (no cortar a primera página)
- [ ] Respuesta JSON parseada sin errores de estructura

#### Transform
- [ ] Columnas de empleo casteadas a `int`
- [ ] Columnas de salario/ingresos casteadas a `float`
- [ ] Municipio mapeado a `municipio_id` cvegeo

#### Load
- [ ] Sin duplicados por período + municipio + sector
- [ ] Modo update inserta solo el trimestre nuevo

#### Datos
- [ ] Datos de Jalisco presentes para el trimestre procesado
- [ ] Sector de actividad en valores de catálogo reconocidos

---

### B7. `delitos_fuero_comun` — Delitos INEGI

**Fuente**: INEGI estadísticas de crimen por estado/municipio
**Cron update**: `0 12 1 * *` (1° de mes al mediodía)
**Tablas**: `stg_delitos_fuero_comun_*`

#### Extract
- [ ] URL del archivo INEGI accesible para el período actual
- [ ] Encoding del CSV correcto (UTF-8 con BOM o Latin-1)

#### Transform
- [ ] Conteos de delitos casteados a `int`
- [ ] Tipo de delito normalizado y mapeado a catálogo
- [ ] CLAVE INEGI de municipio mapeada a `municipio_id` cvegeo

#### Load
- [ ] Sin duplicados por año + mes + municipio + tipo de delito
- [ ] Modo update no reemplaza períodos históricos

#### Datos
- [ ] Registros para todos los tipos de delito del período
- [ ] Conteos no negativos
- [ ] Jalisco presente y con valores plausibles (comparar con fiscalia si aplica)

---

### B8. `denue` — Directorio Nacional de Unidades Económicas

**Fuente**: INEGI DENUE
**Cron update**: `timedelta(days=10)` (cada 10 días)
**Tablas**: `stg_denue`, `cat_actividad_economica`

#### Extract
- [ ] Descarga del DENUE vigente (INEGI actualiza frecuentemente)
- [ ] Coordenadas geográficas incluidas en la descarga
- [ ] Archivos por entidad o nacional manejados correctamente

#### Transform
- [ ] Nombre de establecimiento normalizado
- [ ] Latitud/longitud casteadas a `float`
- [ ] Estrato de personal (`2–5`, `6–10`, etc.) mapeado a catálogo
- [ ] Código SCIAN mapeado a `cat_actividad_economica`

#### Load
- [ ] `cat_actividad_economica` cargado antes de `stg_denue`
- [ ] Upsert por ID de establecimiento (no duplicar en actualizaciones)
- [ ] Coordinadas validadas (dentro de bbox de México)

#### Datos
- [ ] Al menos N establecimientos en Jalisco (> 100,000 es plausible)
- [ ] Sin establecimientos con coordenadas en el océano o fuera de México
- [ ] Distribución de estratos plausible (muchas PyMEs, pocas grandes)

---

### B9. `efipem` — Empleo Formal Mujeres (INEGI)

**Fuente**: INEGI indicadores de participación económica femenina
**Cron update**: `0 2 15 2,5,8,11 *` (15 de feb, may, ago, nov a las 2am)
**Tablas**: `stg_efipem_*`

#### Extract
- [ ] Fuente disponible en fechas de publicación INEGI (trimestral)
- [ ] Todas las variables de indicador descargadas

#### Transform
- [ ] Indicadores de participación casteados a `float`
- [ ] Estado/municipio mapeado a cvegeo
- [ ] Período (trimestre + año) parseado correctamente

#### Load
- [ ] Sin duplicados por período + estado + indicador
- [ ] Tablas de indicadores separadas si el diseño lo requiere

#### Datos
- [ ] Valores de participación en rango [0, 100] si son porcentajes
- [ ] Jalisco presente para todos los trimestres del año

---

### B10. `establecimientos_de_salud` — Red de Salud

**Fuente**: INEGI / Secretaría de Salud directorio de unidades médicas
**Cron update**: `@monthly`
**Tablas**: `cat_tipos_establecimiento`, `cat_instituciones`, `stg_establecimientos_de_salud`

#### Extract
- [ ] Fuente accesible mensualmente
- [ ] Claves de institución (IMSS, ISSSTE, SS, privado) presentes

#### Transform
- [ ] Nombre del establecimiento normalizado (`.title()`, `apply_accents()`)
- [ ] Latitud/longitud casteadas a `float`
- [ ] Tipo de establecimiento mapeado a `cat_tipos_establecimiento`
- [ ] Institución mapeada a `cat_instituciones`

#### Load
- [ ] Catálogos cargados antes de `stg_establecimientos_de_salud`
- [ ] Modo update: upsert por ID de unidad médica
- [ ] Sin duplicados por clave de unidad + fecha de corte

#### Datos
- [ ] Al menos N unidades en Jalisco (> 2,000 plausible)
- [ ] Coordenadas dentro del polígono de Jalisco para registros jalisciences
- [ ] Distribución por institución plausible (IMSS + privado mayoritarios)

---

### B11. `etef` — Empleo en el Sector Formal (INEGI)

**Fuente**: INEGI índice de empleo formal
**Cron update**: `@quarterly`
**Tablas**: `stg_etef_mensual`

#### Extract
- [ ] Datos trimestrales accesibles en INEGI
- [ ] Serie histórica completa disponible en bootstrap

#### Transform
- [ ] Índice casteado a `float`
- [ ] Variación anual/mensual casteada a `float` (puede ser negativa)
- [ ] Período (mes + año) parseado correctamente
- [ ] Región/estado mapeado a cvegeo o catálogo propio

#### Load
- [ ] Sin duplicados por período + estado
- [ ] Modo update: solo el trimestre nuevo, sin sobreescribir histórico

#### Datos
- [ ] Índice en rango plausible (ej. 80–120 si base = 100)
- [ ] Variaciones no mayores al ±30% mensual (si ocurre, verificar con fuente)
- [ ] Jalisco presente en todos los períodos

---

### B12. `fiscalia` — Datos del Ministerio Público Jalisco

**Fuente**: Fiscalía General del Estado de Jalisco
**Cron update**: `@monthly` (1° de mes a las 12:01am)
**Tablas**: `stg_fiscalia_casos`, `cat_delitos`, `cat_violencia`, `cat_zonas_geograficas`, `cat_colonias`, `cat_calles`, `cat_cruces`, `cat_bien_afectado`

#### Extract
- [ ] Endpoint de la Fiscalía accesible y respondiendo
- [ ] Paginación/scroll manejado (puede ser dataset grande)
- [ ] Campos geográficos (zona, colonia, calle, cruce) incluidos

#### Transform
- [ ] Tipo de delito normalizado y mapeado a `cat_delitos`
- [ ] Clasificación de violencia mapeada a `cat_violencia`
- [ ] Zona geográfica mapeada a `cat_zonas_geograficas`
- [ ] Colonia, calle y cruce normalizados (`.title()`, `apply_accents()`)
- [ ] Coordenadas (si existen) casteadas a `float`
- [ ] Fecha del hecho parseada a `date`

#### Load
- [ ] 7 catálogos cargados antes de `stg_fiscalia_casos`
- [ ] `sync_id_sequence()` para catálogos con IDs fijos
- [ ] Modo update: upsert por folio/ID de caso (no duplicar)
- [ ] Sin NaN en `delito_id` ni `violencia_id` (campos clave)

#### Datos
- [ ] Registros del mes recién cerrado presentes tras el update
- [ ] Sin casos con fecha futura
- [ ] Distribución de tipos de delito plausible (robo mayoritario, homicidio menor)
- [ ] Colonias del catálogo reconocibles como colonias de Guadalajara/ZMG

---

### B13. `inpc` — Índice Nacional de Precios al Consumidor

**Fuente**: INEGI INPC
**Cron update**: `@monthly`
**Tablas**: `stg_inpc_mensual`, `cat_objeto_gasto`

#### Extract
- [ ] INEGI publica el INPC los primeros días del mes siguiente
- [ ] Todas las categorías de objeto del gasto presentes

#### Transform
- [ ] Índice base casteado a `float`
- [ ] Variación mensual/anual casteada a `float` (puede ser negativa)
- [ ] `ObjetoGasto` enum en `mappings.py` coincide con valores de la fuente
- [ ] Período (mes + año) parseado correctamente

#### Load
- [ ] `cat_objeto_gasto` cargado antes de `stg_inpc_mensual`
- [ ] Sin duplicados por período + categoría
- [ ] Modo update inserta solo el mes nuevo

#### Datos
- [ ] Índice en rango plausible para México (INPC base 2Q2018=100, actualmente ~130–160)
- [ ] Variación anual en rango [0%, 15%] bajo condiciones normales
- [ ] Todas las categorías del `ObjetoGasto` enum presentes en la carga

---

### B14. `intensidad_migratoria` — Índice CONAPO

**Fuente**: CONAPO (Consejo Nacional de Población)
**Cron update**: `None` (datos por quinquenio, carga manual)
**Tablas**: `stg_intensidad_migratoria`, catálogos de atributos

#### Extract
- [ ] Archivo CONAPO disponible en path o URL configurada
- [ ] Columnas de grado (alto, medio, bajo, muy alto, muy bajo) presentes

#### Transform
- [ ] Índice numérico casteado a `float`
- [ ] Grado de intensidad mapeado a catálogo
- [ ] Municipio mapeado a `municipio_id` cvegeo
- [ ] Año del índice parseado

#### Load
- [ ] Sin duplicados por año + municipio
- [ ] Grado de intensidad sin NaN

#### Datos
- [ ] 125 municipios de Jalisco presentes para el año configurado
- [ ] Distribución de grados plausible (no todos en "muy alto")
- [ ] Valores de índice en rango publicado por CONAPO

---

### B15. `marginacion` — Índice de Marginación CONAPO

**Fuente**: CONAPO índice de marginación por municipio
**Cron update**: `None` (datos por quinquenio o censo, carga manual)
**Tablas**: `stg_marginacion_datos`, `cat_grado_marginacion`

#### Extract
- [ ] Archivo CONAPO de marginación disponible
- [ ] Columnas de indicadores socioeconómicos incluidas

#### Transform
- [ ] Índice de marginación casteado a `float`
- [ ] Grado de marginación mapeado a `cat_grado_marginacion`
- [ ] Ranking municipal casteado a `int`
- [ ] Municipio mapeado a `municipio_id` cvegeo

#### Load
- [ ] `cat_grado_marginacion` (5 categorías: muy alto, alto, medio, bajo, muy bajo) cargado primero
- [ ] Sin duplicados por año + municipio
- [ ] `sync_id_sequence()` después de `cat_grado_marginacion`

#### Datos
- [ ] 125 municipios de Jalisco presentes
- [ ] Distribución de grados consistente con publicación CONAPO
- [ ] Ranking sin saltos ni duplicados (1 a N secuencial)

---

### B16. `pobreza_multidimensional` — CONEVAL

**Fuente**: CONEVAL (medición de pobreza 2020/2022)
**Cron update**: `None` (bi o trianual, carga manual)
**Tablas**: `stg_pobreza_multidimensional_*`, catálogos de clasificación de pobreza

#### Extract
- [ ] Archivo CONEVAL accesible para el año de medición
- [ ] Indicadores de privaciones (educación, salud, vivienda, servicios) incluidos

#### Transform
- [ ] Porcentajes de pobreza casteados a `float`
- [ ] Conteos absolutos casteados a `int`
- [ ] Indicadores de privación mapeados a catálogo
- [ ] Municipio mapeado a `municipio_id` cvegeo

#### Load
- [ ] Tablas por indicador (si el diseño las separa) cargadas en orden
- [ ] Sin duplicados por año + municipio + indicador
- [ ] Catálogos de clasificación cargados primero

#### Datos
- [ ] 125 municipios de Jalisco para el año de medición
- [ ] Porcentajes en rango [0, 100]
- [ ] Suma de categorías de pobreza consistente (pobreza extrema ⊂ pobreza total)

---

### B17. `produccion_ganadera` — Ganadería SIAP

**Fuente**: SIAP datos de producción pecuaria
**Cron update**: `@yearly`
**Tablas**: `stg_produccion_ganadera`, catálogos (especie, producto)

#### Extract
- [ ] URL SIAP para ganadería accesible para el año configurado
- [ ] Columnas de especie, producto y métricas presentes

#### Transform
- [ ] Métricas de producción casteadas a `float`
- [ ] Nombres de especie y producto normalizados (`.title()`, `apply_accents()`)
- [ ] Municipio mapeado a `municipio_id` cvegeo
- [ ] Año parseado correctamente

#### Load
- [ ] Catálogos de especie y producto cargados antes de `stg_produccion_ganadera`
- [ ] `sync_id_sequence()` después de catálogos
- [ ] Sin duplicados por año + municipio + especie + producto

#### Datos
- [ ] Registros para los 125 municipios de Jalisco (o los que tienen actividad ganadera)
- [ ] Valores de producción no negativos
- [ ] Jalisco en posición relevante para ganado bovino y porcino (verificar con publicaciones SIAP)

---

### B18. `repd` — Registro Estatal de Personas Desaparecidas

**Fuente**: API REPD Jalisco (`https://repd.jalisco.gob.mx/api/v1/...`)
**Cron update**: `0 3 1 * *` (1° de mes a las 3am)
**Tablas**: `stg_repd_case_current`, `stg_repd_case_history`, `stg_repd_cat_sexo`, `stg_repd_cat_nacionalidad`, `stg_repd_cat_rango_edad`, `stg_repd_cat_estatus`, `stg_repd_cat_condicion_localizacion`, `stg_repd_cat_clasificacion_localizacion`, `stg_repd_cat_tipo_cierre`

#### Extract
- [ ] Endpoint de la API REPD responde (sin timeout en dataset grande)
- [ ] Paginación manejada correctamente (todos los folios descargados)
- [ ] Campos de hash para detección de cambios presentes en respuesta

#### Transform
- [ ] ~81 campos incluidos en cálculo del `record_hash`
- [ ] Fechas (desaparición, localización, cierre) parseadas a `date`
- [ ] Sexo, nacionalidad, rango de edad mapeados a catálogos `cat_*`
- [ ] Estatus, condición y clasificación de localización mapeados
- [ ] Sin NaN en campos que van al hash

#### Load
- [ ] 7 catálogos cargados antes de las tablas principales
- [ ] `sync_id_sequence()` para todos los catálogos
- [ ] `stg_repd_case_current`: upsert por FEB (folio), actualiza si `record_hash` cambia
- [ ] `stg_repd_case_history`: inserta nueva versión con `valid_from = hoy`, cierra la anterior con `valid_to = hoy - 1 día`
- [ ] Sin registros en `current` sin correspondencia en `history`
- [ ] Sin solapamientos de `valid_from`/`valid_to` para el mismo FEB

#### Datos
- [ ] Total de registros en `current` = total de folios únicos de la API
- [ ] `valid_to IS NULL` para la versión activa de cada FEB (solo una por FEB)
- [ ] Fechas de desaparición no futuras
- [ ] Distribución de sexo y rango de edad plausible
- [ ] Casos de cierre (`tipo_cierre`) presentes solo en registros con fecha de cierre

---

## Sección C — Checks de infraestructura compartida

### C1. cvegeo (catálogos geográficos compartidos)

- [ ] `just flyway-reset cvegeo` sin errores
- [ ] Tablas: estados (32), municipios (2,475 nacional / 125 Jalisco), localidades presentes
- [ ] Todos los pipelines con `municipio_id` resuelven FKs correctamente
- [ ] Índices de búsqueda geográfica creados (`CREATE INDEX IF NOT EXISTS`)

### C2. Docker / Airflow

- [ ] `just up` levanta todos los contenedores sin errores
- [ ] Airflow Webserver accesible en `http://localhost:8080`
- [ ] Variables de entorno del `.env` propagadas a los workers de Airflow
- [ ] Volumen de datos (`data/`) montado correctamente en el contenedor
- [ ] Logs de Airflow en `logs/` accesibles

### C3. Dependencias Python

- [ ] `pip install -r requirements.txt` sin conflictos
- [ ] `pyproject.toml` y `requirements.txt` sincronizados
- [ ] Versiones de SQLAlchemy (2.x), pandas, Airflow, Flyway compatibles

---

## Apéndice — Comandos de referencia rápida

```bash
# Levantar entorno
just up

# Migrar un pipeline
just flyway-migrate {pipeline}

# Resetear migraciones de un pipeline (destructivo, solo dev)
just flyway-reset {pipeline}

# Validar DAG sin errores de importación
python dags/etl_{pipeline}.py

# Verificar estado de migraciones
just flyway-info {pipeline}

# Pipelines disponibles
agropecuario_siap  asg_imss  censo_poblacion  censos_economicos
centros_educativos  datamexico  delitos_fuero_comun  denue
efipem  establecimientos_de_salud  etef  fiscalia
inpc  intensidad_migratoria  marginacion  pobreza_multidimensional
produccion_ganadera  repd
```
