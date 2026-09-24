# Acervo

Cliente de lectura para [Acervo](https://github.com/iieg-oficial/acervo), el almacenamiento
de objetos del IIEG (SeaweedFS con API S3). Descubre y descarga los conjuntos de datos que
las dependencias suben por el formulario del SIEEJ.

El módulo es genérico: recibe el nombre de la dependencia como parámetro, así que cada
pipeline que consuma este origen lo usa sin duplicar lógica.

## Uso

```python
from pathlib import Path

from core.acervo import list_uploads, download, download_all

# Inventario, sin descargar
for upload in list_uploads("Secretaría de Educación"):
    print(upload.conjunto, upload.fecha_corte, upload.object_key)

# Bootstrap: todo el histórico de la dependencia
download_all("Secretaría de Educación", Path("data/extract/secretaria_educacion"))

# Incremental: solo lo posterior al watermark
download_all(
    "Secretaría de Educación",
    Path("data/extract/secretaria_educacion"),
    since="2026-09-01 00:00:00+00:00",
)
```

El nombre de la dependencia se compara normalizado (sin acentos ni mayúsculas), porque en el
formulario es captura libre: `"SECRETARIA DE EDUCACION"` y `"Secretaría de Educación"`
resuelven igual.

## Funciones

Todo lo público se importa desde `core.acervo`. Lo demás es privado y puede cambiar.

### `list_uploads`

```python
list_uploads(
    dependencia: str,
    client=None,
    bucket: str | None = None,
    prefix: str | None = None,
    estado: str = "enviado",
) -> list[Upload]
```

Devuelve los archivos que envió una dependencia, del más viejo al más nuevo. Aplica las cinco
reglas de descubrimiento, así que ya vienen deduplicados: un envío con tres versiones del
mismo campo produce un solo `Upload`.

| parámetro | para qué |
|---|---|
| `dependencia` | Nombre como aparece en el formulario. Los acentos y mayúsculas dan igual |
| `client` | Cliente S3 a reutilizar. Si se omite, construye uno nuevo en cada llamada |
| `bucket` | Bucket alterno. Por defecto el configurado |
| `prefix` | Prefijo alterno. Por defecto el configurado |
| `estado` | Estado a aceptar. Con `None` acepta todos, incluidos los borradores |

No hace ninguna descarga, solo lee los metadatos de cada envío. Es la función barata para
inventariar antes de decidir qué bajar.

### `download`

```python
download(
    upload: Upload,
    output_folder: Path,
    client=None,
    bucket: str | None = None,
) -> Path
```

Descarga un `Upload` y devuelve la ruta del archivo. Crea la carpeta destino si no existe.

El archivo se guarda con el nombre del `object_key`, no con `filename`. Es deliberado: el
nombre original se repite entre cargas (la misma dependencia sube dos veces
`EQUIPAMIENTO.xlsx`) y se pisarían entre ellas. El del `object_key` trae timestamp y hash, así
que es único.

### `download_all`

```python
download_all(
    dependencia: str,
    output_folder: Path,
    client=None,
    bucket: str | None = None,
    since: str | None = None,
) -> list[Path]
```

Descarga las cargas de una dependencia y devuelve las rutas. Sin `since` hace el bootstrap;
con `since` se queda con los envíos cuyo `updated_at` sea posterior, que es el incremental.

Si no hay nada que bajar devuelve una lista vacía y lo avisa por log, no falla.

Llama a `list_uploads` internamente con los valores por defecto, así que no expone `prefix` ni
`estado`. Para afinarlos, combinar `list_uploads` con `download`.

### `get_client`

```python
get_client()
```

Construye el cliente S3 contra Acervo con la configuración del módulo. Útil para reutilizar
una sola conexión entre varias llamadas en vez de dejar que cada una abra la suya.

### `normalize`

```python
normalize(text: str) -> str
```

Quita acentos, baja a minúsculas y colapsa espacios. Es pública porque el pipeline la necesita
para comparar el `conjunto` de un `Upload` contra su registro de conjuntos conocidos, con el
mismo criterio que el módulo usa para la dependencia.

A diferencia de `normalize_text` de `core/utils/normalize.py`, conserva los espacios en vez de
convertirlos en guiones bajos.

### `settings`

Configuración ya instanciada. Se importa cuando hace falta leer un valor suelto, por ejemplo
`settings.ACERVO_BUCKET` para registrar de qué bucket vino una carga.

### `Upload`

Dataclass inmutable con los metadatos de un archivo. Campos en
[El objeto `Upload`](#el-objeto-upload).

Trae además la propiedad `etag_is_md5`, que indica si el `etag` sirve como hash de contenido.

## Variables de entorno

Viven en `core/acervo/.env`. Plantilla en `.env.example`.

| variable | requerida | descripción |
|---|---|---|
| `ACERVO_ENDPOINT` | | URL del servicio S3 |
| `ACERVO_ACCESS_KEY` | | Identidad S3 |
| `ACERVO_SECRET_KEY` | | Secreto de la identidad |
| `ACERVO_BUCKET` | | Bucket a leer (default `sieej`) |
| `ACERVO_REGION` | | Región nominal, la ignora SeaweedFS (default `us-east-1`) |
| `ACERVO_FORM_PREFIX` | sí | Prefijo del formulario dentro del bucket |
| `ACERVO_ENVIO_FILENAME` | sí | Nombre del archivo de metadatos de cada envío |

Las dos requeridas no tienen default a propósito: `Settings()` se instancia al importar el
módulo, así que si faltan, el import falla nombrando ambas en vez de leer un prefijo
equivocado en silencio.

## Cómo descubre los archivos

El nombre del archivo cambia en cada carga y cada persona sube a su propia carpeta, así que
el descubrimiento no pasa por las rutas sino por el archivo de metadatos que acompaña a cada
envío:

1. Recorre los envíos bajo el prefijo, con paginación.
2. Descarta los que no estén en estado `enviado`, es decir los borradores.
3. Filtra por el nombre de la dependencia, normalizado.
4. Agrupa los archivos por `field_path` y se queda con el más reciente.
5. Devuelve los `Upload` ordenados por fecha de subida.

El paso 4 es la deduplicación. Quien captura puede reemplazar un archivo antes de enviar, y
entonces el envío conserva **todos** los objetos de ese campo. Sin este paso, un bootstrap
carga el mismo conjunto varias veces.

## El objeto `Upload`

| campo | para qué sirve |
|---|---|
| `object_key` | Ruta exacta en el bucket. No construirla a mano |
| `filename` | Nombre original que subió la dependencia |
| `size` | Tamaño en bytes |
| `uploaded_at` | Cuándo se subió el archivo |
| `envio_id` | Identificador del envío |
| `conjunto` | Nombre del conjunto de datos, para rutear al transform |
| `updated_at` | Última modificación del envío, es el watermark |
| `fecha_corte` | A qué fecha corresponden los datos |
| `fecha_actualizacion` | Cuándo la dependencia actualizó el conjunto |
| `etag` | MD5 del contenido, para saltar recargas sin cambios |

## Bootstrap e incremental

| modo | filtro |
|---|---|
| Bootstrap | Todos los envíos en estado `enviado` |
| Incremental | `updated_at` posterior al watermark guardado |

El watermark va sobre `updated_at` del envío y no sobre la fecha del archivo. Un envío puede
mandarse días después de que se subió el archivo, así que usar la fecha del archivo deja
huecos.

Para evitar reprocesar un envío que se corrigió sin tocar los datos, compara el `etag` contra
el de la última carga: si coincide, el archivo es idéntico y no hace falta volver a cargarlo.

## Trampas

**El `etag` no siempre es el MD5.** En subidas multiparte trae un sufijo `-N` y deja de ser el
hash del contenido. `Upload.etag_is_md5` lo distingue y el módulo avisa por log; en ese caso
hay que caer al watermark.

**`fecha_corte` es captura libre.** Se ha visto que coincide con el día en que se subió el
archivo, lo que sugiere que no siempre refleja el corte real. El módulo avisa cuando la fecha
de corte es posterior a la de subida, que sería imposible, pero el resto no lo puede validar.

**Los metadatos del envío traen datos personales** del responsable y del enlace técnico. No
volcarlos en logs.

## Acceso

Airflow llega a Acervo por la red interna. Para desarrollo local hace falta un túnel SSH
contra el servidor que sí tiene alcance, y apuntar `ACERVO_ENDPOINT` al extremo local del
túnel. Pedir los valores a quien administra la infraestructura.

Conviene usar una identidad de **solo lectura** sobre el bucket. Las identidades
`<bucket>-user` que entrega Acervo traen permisos de escritura y administración, que un ETL
no necesita.
