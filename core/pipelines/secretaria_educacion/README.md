# secretaria_educacion

> Pipeline ETL para los conjuntos de datos que la Secretaría de Educación Jalisco entrega por el formulario de datasets del SIEEJ.

---

## Descripción general

A diferencia de los pipelines que consumen una fuente fija, este se organiza por **dependencia**: la Secretaría de Educación sube archivos a Acervo mediante el formulario del SIEEJ, y el pipeline descubre qué hay, lo rutea al conjunto que corresponde y lo carga.

Hoy llegan tres conjuntos sin relación estructural entre sí, salvo la clave de centro de trabajo (CCT) que comparten: el directorio de centros de trabajo con su estadística educativa, las escuelas beneficiadas por programas estratégicos estatales, y el equipamiento de aulas Google.

El prefijo del formulario concentra las cargas de **todas** las dependencias, así que cada una es un pipeline distinto y este filtra por el nombre de la suya.

## Fuente general

Acervo, el almacenamiento de objetos del IIEG, con API compatible con S3.

## Fuente específica

```shell
ACERVO_FORM_PREFIX=<prefijo del formulario dentro del bucket>
ACERVO_BUCKET=sieej
```

Ambos se configuran en `core/acervo/.env`, no en el `.env` de este pipeline. Ver [`core/acervo/README.md`](../../acervo/README.md) para el detalle del acceso.

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | Directorio `2025-09-30`, programas `2026-06-30`, aulas `2026-09-10` |
| Frecuencia de actualización | Quincenal |
| Desagregación | Centro de trabajo |
| Cobertura | Estatal, los 125 municipios de Jalisco |
| ¿Tiene update? | Sí |
| Update | Automático (`0 19 1,16 * *`) |
| Estrategia de carga | Recarga por corte: `delete` del `fecha_corte` + `bulk_insert` |

Cada conjunto declara su propia frecuencia en el formulario: Aulas Google es **quincenal** y los otros dos **anuales**. El DAG corre quincenal, que cubre al más exigente sin costo para los demás, porque el incremental arranca desde el watermark y salta los envíos cuyo `etag` no cambió.

La recarga es por corte y no un upsert fila a fila porque la dependencia entrega el conjunto completo en cada envío, no incrementos.

## Diagrama de entidad relación

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_directorio_centros_trabajo

| variable | descripción |
|---|---|
| `entidad_id` | Clave de la entidad. Siempre 14 (Jalisco). Referencia lógica a `cvegeo_states.cve_ent` |
| `municipio_id` | Clave del municipio. Referencia lógica a `cvegeo_municipalities.cve_mun` |
| `localidad_id` | Localidad en `cat_localidades`. cvegeo no cubre este nivel |
| `colonia_id` | Colonia en `cat_colonias`. Nula cuando el origen no la reporta |
| `clave_ct` | Clave del centro de trabajo (CCT), llave de relación con los demás conjuntos |
| `turno_id` | Turno en que opera |
| `nombre_ct` | Nombre del centro de trabajo |
| `domicilio` | Domicilio tal como lo reporta el origen |
| `medio_id` | Medio en que se ubica: rural o urbano |
| `director` | Nombre del director. Conserva el title case sin acentos: el origen los omite |
| `codigo_postal` | Nulo cuando el origen lo reporta en cero |
| `telefono` | Nulo cuando el origen lo reporta en cero |
| `zona_escolar` | Nula cuando el origen la reporta en 0 (sin asignar) o en 999 (no especificado) |
| `sector` | Nulo cuando el origen lo reporta en 0, que corresponde a los niveles donde no aplica |
| `sostenimiento_id` | Origen del financiamiento |
| `nivel_id` | Nivel educativo que imparte |
| `programa_id` | Modalidad educativa |
| `region_id` | Región del estado |
| `longitud`, `latitud` | Ubicación en grados decimales |
| `escuelas` | Indicador 0/1 que marca si la fila cuenta para el total oficial. Las filas en 0 son planteles en liquidación |
| `hombres_matriculados`, `mujeres_matriculadas`, `total_matriculados` | Matrícula inscrita |
| `total_docentes_directivo` | Docentes y directivos frente a grupo |
| `fecha_corte` | Fecha a la que corresponden los datos, capturada por la dependencia |
| `fecha_actualizacion_fuente` | Fecha en que la dependencia actualizó el conjunto |

### stg_escuelas_programas_estrategicos

| variable | descripción |
|---|---|
| `clave_ct` | Clave del centro de trabajo. Sin llave foránea al directorio: los cortes de ambos conjuntos son independientes |
| `programa_estrategico_id` | Programa estatal que beneficia a la escuela. Concepto distinto de `programa_id` del directorio, que es la modalidad educativa |
| `fecha_corte` | Fecha a la que corresponden los datos |
| `fecha_actualizacion_fuente` | Fecha en que la dependencia actualizó el conjunto |

### stg_aulas_google

| variable | descripción |
|---|---|
| `entidad_id` | Clave de la entidad. Siempre 14 (Jalisco) |
| `municipio_id` | Resuelto contra cvegeo desde el nombre: el origen no manda la clave. Nulo si el nombre no coincide con el oficial |
| `clave_ct` | Clave del centro de trabajo. Sin llave foránea al directorio |
| `nombre_ct` | Nombre del centro de trabajo |
| `inmueble` | Clave del inmueble que ocupa |
| `region_operativa_id` | Región operativa de la dependencia |
| `aulas_asignadas` | Número de aulas Google asignadas |
| `fecha_corte` | Fecha a la que corresponden los datos |
| `fecha_actualizacion_fuente` | Fecha en que la dependencia actualizó el conjunto |

### cargas_acervo

Control de envíos procesados: da el watermark del incremental.

| variable | descripción |
|---|---|
| `envio_id` | Identificador del envío en el formulario |
| `conjunto` | Nombre del conjunto tal como lo capturó la dependencia |
| `object_key` | Ruta del archivo dentro del bucket |
| `etag` | MD5 del contenido. Si coincide con la carga anterior, el archivo no cambió. No es MD5 en subidas multiparte |
| `actualizado_en` | Última modificación del envío. Es el watermark del incremental |
| `procesado_en` | Momento en que el ETL procesó el envío |

### Catálogos

| tabla | contenido |
|---|---|
| `cat_turnos` | Turnos escolares. El id es el código del origen y no es secuencial |
| `cat_medios` | Rural o Urbana |
| `cat_sostenimientos` | Federal, Federalizado, Estatal, Particular, Autónomo |
| `cat_niveles` | De Inicial a Superior |
| `cat_programas` | Modalidad educativa del plantel: Escolarizado, CENDI, CONAFE, Indígena, CAM |
| `cat_regiones` | Las 13 regiones del estado. El id es el código regional del origen |
| `cat_localidades` | Localidades, con `cve_geo_id` compuesto. cvegeo solo cubre entidad y municipio |
| `cat_colonias` | Colonias, dependientes de su localidad |
| `cat_programas_estrategicos` | Programas estatales que benefician escuelas |
| `cat_regiones_operativas` | Regionalización propia de la dependencia, distinta de la estatal |

## Migraciones

| migración | descripción |
|---|---|
| `V1__foreign_tables.sql` | Servidor FDW y foreign tables `cvegeo_states` y `cvegeo_municipalities` |
| `V2__catalogs_secretaria_educacion.sql` | Los 10 catálogos |
| `V3__tables_secretaria_educacion.sql` | Las 3 tablas de hechos y la de control |
| `V4__views_secretaria_educacion.sql` | Las 3 vistas |
| `V5__comments_secretaria_educacion.sql` | `COMMENT ON` de todas las tablas, vistas y columnas |

## Vistas

| vista | alcance |
|---|---|
| `vw_directorio_centros_trabajo` | Directorio con catálogos resueltos; entidad y municipio desde cvegeo, localidad y colonia desde los catálogos propios |
| `vw_escuelas_programas_estrategicos` | Relación escuela-programa con el nombre del programa resuelto |
| `vw_aulas_google` | Equipamiento con región operativa y municipio resueltos |

## Variables de entorno

| variable | descripción |
|---|---|
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | Conexión a la base del pipeline |
| `DEPENDENCIA` | Nombre de la dependencia a filtrar en el formulario |

Las credenciales de Acervo viven en `core/acervo/.env`. Los placeholders FDW del `flyway.conf` no se declaran aquí: la receta `just flyway-config` los resuelve desde `migrations/cvegeo/.env`.

## Notas metodológicas

### Extract

Recorre los envíos del formulario, descarta los que no estén en estado enviado y filtra por el nombre de la dependencia, normalizado para tolerar acentos y mayúsculas.

El descubrimiento va por los metadatos de cada envío y **no por las rutas de los objetos**: el nombre del archivo cambia en cada carga y cada persona sube a su propia carpeta, así que la ruta no es predecible. Los metadatos, en cambio, traen la clave exacta del objeto.

> **Un envío conserva todas las versiones de un campo.** Si quien captura reemplaza el archivo antes de enviar, quedan varios objetos para el mismo `field_path`. Se toma el más reciente por `subido_en`; sin ese paso, un bootstrap carga el mismo conjunto varias veces. En los datos actuales 5 objetos colapsan a 3 conjuntos.

El conjunto se rutea a su dataset por **prefijo** del nombre, no por igualdad, porque es texto libre y suele arrastrar el ciclo escolar. Un conjunto que no corresponde a ningún dataset conocido se omite con warning en lugar de romper la corrida: la dependencia sube datasets nuevos sin avisar.

En modo `update` se descarta lo anterior al watermark (`actualizado_en` del último envío procesado) y se saltan los envíos cuyo `etag` ya fue cargado, que es el caso de un reenvío que solo corrigió metadatos. El watermark va sobre la fecha del envío y no sobre la del archivo, porque un envío puede mandarse días después de subir el archivo.

Cada dataset llega en un formato distinto: el directorio en un ZIP con una hoja de cálculo cuyo encabezado real está en la fila 13, después del título y cuatro notas metodológicas; los otros dos en CSV.

### Transform

Normaliza el texto, que llega íntegramente en mayúsculas y sin acentos. Los nombres propios reciben title case con las preposiciones en minúscula y los acentos restituidos contra el mapa global más uno propio del pipeline.

> **En los nombres de persona no se inventan acentos.** Son miles de valores distintos y adivinarlos escribiría mal a personas reales. Las partículas sí van en minúscula, según la RAE: en `Gloria del Pilar` la preposición sigue al nombre de pila.

Construye los catálogos, convierte a nulo los ceros en las columnas donde el origen usa 0 como "sin dato", y aplica los centinelas declarados. Persiste los catálogos en disco para que el load pueda correr como tarea independiente.

### Load

Carga los catálogos, resuelve las llaves foráneas y recarga cada conjunto por su `fecha_corte`: borra las filas de ese corte y las reinserta, así correr dos veces no duplica.

Los catálogos con id del origen se cargan con `upsert_records` y no con `insert_records`, porque el segundo usa `ON CONFLICT DO NOTHING` y dejaría congelada para siempre una etiqueta que la dependencia corrigiera.

El municipio de Aulas Google se resuelve contra cvegeo desde el nombre, porque el origen no manda la clave. Al final registra el envío en `cargas_acervo`, que alimenta el watermark de la siguiente corrida.

## Ejecución

**Bootstrap** (carga inicial):

```shell
just env-init secretaria_educacion
just create-db secretaria_educacion
just flyway-config secretaria_educacion
just flyway-migrate secretaria_educacion
python dags/etl_secretaria_educacion.py
```

**Update** (quincenal, DAG `etl_secretaria_educacion_update`, schedule `0 19 1,16 * *`):

Arranca desde el watermark de `cargas_acervo`, así que una corrida sin cargas nuevas termina sin tocar la base. Para dispararlo a mano, descomentar `run_update()` en el bloque final del DAG.

## Notas adicionales

- **El DAG declara una tarea por stage** (`extract >> transform >> load`), de modo que se puede reintentar una sola sin repetir las anteriores. La excepción es reintentar `load` **después** de un run exitoso: su limpieza borra los archivos intermedios, así que hay que reintentar desde `transform`.
- **Correr `load` sin extract previo termina en verde** sin cargar nada, en lugar de avisar que falta el paso anterior. Limitación conocida.
- **Los nombres de entidad y municipio no se guardan**: se resuelven en las vistas contra cvegeo, que tiene la ortografía oficial. El origen dice `TLAQUEPAQUE` y el nombre oficial es `San Pedro Tlaquepaque`.
- **Sin llaves foráneas entre tablas de hechos.** 12 CCT de programas y 2 de aulas no existen en el directorio, y los cortes de los tres conjuntos son independientes.
- **El directorio se solapa con el pipeline `escuelas`**, que carga la misma fuente desde Google Drive. Se cargan por separado a propósito; unificarlos es otro issue.
- **`conunto_datos`** aparece así, con el error de escritura, en las rutas del origen. No se corrige para no romper la correspondencia con el formulario.
- **El acceso a Acervo requiere red interna.** Para desarrollo local hace falta un túnel; ver [`core/acervo/README.md`](../../acervo/README.md).
