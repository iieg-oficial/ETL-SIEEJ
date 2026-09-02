# Pipeline `pendientes`

Pipeline ETL para producir y distribuir localmente el modelo de elevación acondicionado y la pendiente de Jalisco.
La justificación de FP2, Wood–Evans 5 × 5 y las alternativas evaluadas se conserva en
[METODOLOGIA.md](METODOLOGIA.md).

## Objetivo

El pipeline entrega una familia raster coherente sobre una única rejilla territorial. El CEM 4.0 de INEGI se
mantiene como fuente inmutable; no se renombra ni se presenta como producto IIEG. El buffer exterior sólo participa
en el cálculo y nunca aparece como superficie válida en los productos territoriales.

## Fuente y linaje

La fuente es el Continuo de Elevaciones Mexicano 4.0 de INEGI: cobertura nacional, EPSG:6365, píxel de 0.5 segundos
de arco, `Int16`, NoData 32767 y Z en metros. Su XML tipifica Z como longitud y el contrato registra la confirmación
documental complementaria de metros. Extract conserva el checksum y el remuestreo bilinear institucional documentado
sin convertir rutas internas de producción en dependencias funcionales.

```text
CEM 4.0 INEGI
  -> baseline reproyectado EPSG:6368 / 15 m / Float32 / buffer analítico
  -> acondicionamiento FP2
  -> modelo de elevación acondicionado territorial
  -> pendiente Wood–Evans 5 x 5 en grados
  -> pendiente derivada en porcentaje y clasificaciones
  -> empaquetado COG lossless
  -> release local y estadísticas municipales
```

El baseline con buffer es un artefacto técnico, no publicable.

## Productos

Los tres productos continuos son `Float32`, NoData -9999, EPSG:6368, resolución 15 × 15 m y comparten dimensiones,
transform, bounds y máscara de Jalisco:

- `modelo_elevacion_acondicionado_jalisco_15m.tif`, Z en metros;
- `pendiente_grados_jalisco_15m.tif`, pendiente Wood–Evans 5 × 5 en grados;
- `pendiente_porcentaje_jalisco_15m.tif`, calculada como `tan(radians(grados)) * 100`, sin limitar valores a 100.

Los productos cartográficos son `UInt8`, reservan 0 y usan NoData 255:

- `pendiente_grados_clasificada_jalisco_15m.tif`;
- `pendiente_porcentaje_clasificada_jalisco_15m.tif`.

Los manifests enlazan cada derivado con el checksum de su raster científico padre. Load exige el conjunto completo y
rechaza diferencias de rejilla, máscara, contrato COG o checksum.

## Metodología productiva resumida

FP2 es `FeaturePreservingSmoothing` de WhiteboxTools con `filter=11`, `norm_diff=5`, `num_iter=1`,
`max_diff=0.5` y `zfactor=1`. La ejecución estatal usa tiles de 2048 píxeles y halo validado de 24 píxeles. El DEM
territorial se obtiene por ventana entera y máscara de centro de píxel (`all_touched=false`), sin reproyección,
interpolación ni cambio adicional de Z.

La pendiente productiva es Wood–Evans 5 × 5 mediante `r.param.scale` de GRASS GIS: ajuste cuadrático bivariado por
mínimos cuadrados, `method=slope`, `size=5`, `exponent=0` y `zscale=1`. Se calcula desde el DEM acondicionado con
contexto y se aplica después la ventana y máscara territorial. Horn 3 × 3 se conserva únicamente como referencia
metodológica histórica.

## Clasificaciones

La clasificación en grados sigue el precedente cartográfico INEGI-DGG: 0–2, 2–5, 5–10, 10–15, 15–25, 25–50 y
50° o más. La clasificación porcentual sigue FAO/IIASA GAEZ: 0–0.5, 0.5–2, 2–5, 5–8, 8–16, 16–30, 30–45 y
45% o más. Los límites inferiores son inclusivos y los superiores exclusivos, salvo el último intervalo abierto.

## COG

Transform empaqueta los cinco rasters con el driver COG de GDAL, compresión lossless DEFLATE, nivel 9, bloques de
512 y `BIGTIFF=IF_SAFER`. Los continuos usan predictor de punto flotante y overviews `AVERAGE`; los clasificados usan
overviews `MODE`. La QA exige layout COG, overviews, metadata y rejilla correctos, además de:

```text
mask_mismatch_pixels = 0
different_base_pixels = 0
max_abs_difference = 0
```

Load no crea ni modifica COG: sólo valida, materializa por hardlink o copia atómica y vuelve a comprobar SHA-256.

## Stages

La ruta productiva contiene exactamente tres stages.

### Extract

Adquiere o reutiliza el CEM, valida su contrato real y checksum, y congela desde `cvegeo` las dos fuentes de límites
municipales (`geom_iieg` y `geom_inegi`). Puede reutilizar un GeoPackage institucional previamente validado cuando
no existe conexión directa.

### Transform

Valida y reutiliza los cinco COG científicos congelados; no recalcula FP2 ni Wood–Evans. Calcula las estadísticas
municipales desde el DEM FP2 y la pendiente WE5 contextuales, escribe Parquet con procedencia y genera el manifest
final de Transform.

### Load

Valida y materializa los COG en `data/load/pendientes/`, verifica SHA-256 y hace upsert transaccional del catálogo de
fuentes y las estadísticas municipales. No carga píxeles raster en PostgreSQL.

## Estadísticas municipales e indicadores

Las zonales usan centro de píxel y `all_touched=false` sobre ambas geometrías institucionales. Los percentiles son
exactos sobre todos los píxeles seleccionados. La tabla conserva procedencia del snapshot, DEM FP2, pendiente WE5 y
regla de inclusión. Los indicadores configurados son:

- elevación media municipal (m);
- pendiente media municipal (grados);
- pendiente mediana municipal (grados);
- percentil 95 municipal de pendiente (grados);
- pendiente media municipal (porcentaje).

## Configuración

Copiar `.env.example` al archivo de entorno del pipeline y configurar la base. Para la fuente se usa una de estas
opciones:

- `SOURCE_TIFF_PATH`: CEM nacional ya descargado y con el nombre contractual;
- `SOURCE_URL`: descarga institucional con reintentos.

`CVEGEO_MUNICIPAL_BOUNDARY_SNAPSHOT_PATH` admite sólo un snapshot previamente congelado desde `cvegeo` con las dos
capas municipales. Las variables `EXPERIMENT_MANUAL_*` y `WHITEBOX_TOOLS_*` pertenecen a reproducción metodológica,
no a la ruta ETL ordinaria.

## Ejecución

```bash
cp core/pipelines/pendientes/.env.example core/pipelines/pendientes/.env

.venv/bin/python -c "from core.pipelines.pendientes.stages.extract import PendientesExtract; PendientesExtract().execute()"
.venv/bin/python -c "from core.pipelines.pendientes.stages.transform import PendientesTransform; PendientesTransform().execute()"
.venv/bin/python -c "from core.pipelines.pendientes.stages.load import PendientesLoad; PendientesLoad().execute()"
```

El DAG `dags/etl_pendientes.py` ejecuta la misma secuencia Extract → Transform → Load.

## Idempotencia y archivos de ejecución

Extract reutiliza descargas y snapshots válidos. Transform reutiliza artefactos congelados únicamente después de
verificar manifests y checksums. Load vuelve a validar los COG, materializa atómicamente y usa upsert sin duplicar
claves municipales.

Todo raster, GeoPackage, Parquet, PNG experimental y manifest de ejecución vive bajo `data/`, que está ignorado por
Git. El repositorio sólo versiona código, configuración, migraciones, indicadores, documentación y tests.
