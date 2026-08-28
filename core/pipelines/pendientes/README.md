# Pipeline `pendientes`

Pipeline raster del issue #257 para derivar, desde el Continuo de Elevaciones Mexicano 4.0, una familia de tres
productos canónicos: `modelo_elevacion_acondicionado`, `pendiente_grados` y `pendiente_porcentaje`.

## Contrato congelado en la fase 2

La inspección del CEM 4.0 congeló el siguiente contrato, validado contra la metadata leída del TIFF y no impuesto
como CRS de entrada durante la apertura:

- miembro ZIP: `conjunto_de_datos/continuonacional_15m.tif`;
- EPSG:6365, una banda, `Int16`, NoData 32767;
- píxel angular X/Y compatible con `1/7200°` (0.5 arcsec), con tolerancia absoluta `1e-10`;
- estadísticas observadas (mínimo, máximo, media y desviación) como QA, nunca como requisitos binarios.

El XML tipifica la magnitud vertical como `length` sin poblar el nombre de unidad del GeoTIFF. La confirmación
documental complementaria indica metros, por lo que el manifiesto separa `source_vertical_quantity=length`,
`source_vertical_unit=metre` y el `unit` nulo observado en el TIFF. No se inventa ni configura un `z_factor`.

El límite territorial se consulta desde `cvegeo.public.cvegeo_state_boundary`; no se mantiene una copia estática
en Git. En EPSG:6368 se construye un buffer configurable de 10 km, se obtiene su bbox y se redondea hacia afuera
a múltiplos de 15 m. GDAL reproyecta el CEM con remuestreo bilinear a esa extensión, EPSG:6368 y píxel exacto de
15 × 15 m (equivalente a `targetAlignedPixels`). El resultado `cem_reproyectado_baseline.tif` es un artefacto previo al
acondicionamiento y no un producto publicable.

Transform no crea un arreglo del CEM nacional. Calcula la ventana fuente que cubre el bbox analítico —incluyendo
un margen de kernel bilinear— y consume un `WarpedVRT` por bloques de salida. El GeoTIFF resultante es tiled,
DEFLATE, `Float32`, NoData -9999 y `BIGTIFF=IF_SAFER`. El manifiesto registra la ventana fuente, su fracción del
CEM, bloques escritos, máximo bloque materializado y límite de memoria del warp.

## Contrato de Extract

- ZIP válido, tamaño y SHA-256, sin carga completa en memoria.
- exactamente un TIFF no ambiguo, con nombre, tamaño y CRC del inventario ZIP;
- TIFF extraído por streaming y tratado como inmutable;
- driver, WKT/EPSG detectado, tamaño de píxel, extensión, dimensiones, bandas, datatype, NoData y unidades Z;
- estadísticas básicas por bloques, muestreadas de forma explícita cuando el raster excede `STATS_MAX_CELLS`;
- coincidencia con EPSG:6365, una banda, `Int16`, NoData 32767 y resolución aproximada de 0.5 arcsec;
- CRS presente, dimensiones/píxel válidos y muestra con datos.

## Linaje y doble interpolación

El XML documenta la operación institucional `Resample`:

```text
MDT_125_16bits_sust.tif
→ MDT_15m_16bits_bilinear.tif
método: BILINEAR
```

También referencia `MDT_125_16bits_filtro2.tif`, `MDT_125_sust.tif` y un mosaico previo. Sólo se conservan esos
nombres de linaje; rutas internas de estaciones de trabajo no son rutas funcionales ni dependencias.

Por tanto, la normalización EPSG:6365 / 0.5 arcsec → EPSG:6368 / 15 m con baseline bilinear constituye una segunda
interpolación espacial. QA distingue explícitamente: artefactos del CEM publicado, efecto de nuestra reproyección,
efecto del acondicionamiento y efecto del algoritmo de pendiente. Bilinear se mantiene por tratarse de una variable
continua y coincidir con el método institucional documentado; no se ha elegido alternativa.

## Fuente, staging y productos

Los roles no son intercambiables:

1. **Fuente:** CEM 4.0 original de INEGI, nacional, EPSG:6365, 0.5 arcsec, `Int16`, NoData 32767 e inmutable. No es
   un producto IIEG y conserva su identidad institucional.
2. **Staging:** `cem_reproyectado_baseline.tif`, EPSG:6368, 15 m, `Float32`, NoData -9999 y Jalisco + buffer. Es el baseline
   técnico RAW y nunca se publica.
3. **Producto padre:** `modelo_elevacion_acondicionado`, recortado a Jalisco y producido únicamente por el candidato
   promovido del experimento.
4. **Productos hijos:** ambas pendientes, calculadas exclusivamente desde el producto padre de la misma corrida.

```text
CEM 4.0 INEGI
    ↓
CEM reproyectado baseline (staging con buffer)
    ↓
método y parámetros de acondicionamiento promovidos
    ↓
modelo_elevacion_acondicionado
          │
          ├── pendiente_grados
          └── pendiente_porcentaje
```

Los nombres de archivo previstos, sujetos al futuro patrón raster institucional, son:

- `modelo_elevacion_acondicionado_jalisco_15m.tif`;
- `pendiente_grados_jalisco_15m.tif`;
- `pendiente_porcentaje_jalisco_15m.tif`.

## Acondicionamiento y pendiente

`helpers/conditioning.py` registra solamente la línea base `raw` y permite incorporar candidatos explícitos más
adelante. No selecciona mediana, Gaussian, cubic, spline ni otro filtro. `helpers/qa.py` implementa las métricas
cuantitativas ya definibles: diferencias, MAE, RMSE, bias, percentiles absolutos, máximo, porcentaje modificado y
distribuciones reproducibles de pendiente. Deja pendientes las definiciones operativas de conservación de crestas,
barrancas, reducción de banding y comportamiento en terreno plano/montañoso.

Convertir el DEM acondicionado en producto hace obligatorio registrar, antes de promover un candidato: CRS,
resolución, alineación, extensión, `Float32`, NoData -9999, unidad Z `metre`, checksum, máscara territorial y
cobertura, además de MAE, RMSE, bias, p50/p90/p95/p99 y máximo del cambio absoluto, porcentaje modificado y las
métricas futuras de terreno. Los campos aún no estudiados son obligatorios en el manifiesto, pero pueden permanecer
sin valor y no tienen umbrales inventados.

La hipótesis de banding no atribuye causalidad a un único factor. Puede combinar cuantización vertical `Int16`,
procesamiento e interpolación institucional previos, el bilinear documentado por INEGI, nuestra nueva reproyección
y la amplificación producida por derivadas de primer orden. No hay causalidad demostrada ni filtro seleccionado.

Para QA de reproyección, las ventanas fuente y destino se resumen sobre la misma huella geográfica pero en sus
rejillas nativas: rango, media, desviación, percentiles, histograma, superficie válida y NoData. No se emparejan por
índice píxeles pertenecientes a rejillas distintas. La revisión visual reproducible reserva estratos planos y de
montaña; una comparación posterior con otro remuestreo continuo queda abierta y controlada.

La fase 3 añade un barrido exacto por bloques del baseline para contar píxeles válidos/NoData y calcular mínimo,
máximo, media, desviación y superficie válida. Los percentiles se obtienen mediante una muestra sistemática,
determinista y acotada, que el manifiesto identifica como tal. El mismo barrido caracteriza `|dz_x|` y `|dz_y|`:
porcentajes iguales a cero y menores o iguales a 0.25, 0.5, 1 y 2 m, además de p50/p90/p95/p99 muestreados. La
fracción casi plana usa una tolerancia documentada de `1e-6 m`; es descriptiva y no constituye un umbral de banding.

`helpers/diagnostics.py` también permite extraer chips QA reproducibles de 1024 × 1024 celdas mediante coordenadas
de fila/columna y una etiqueta de terreno (`flat`, `rolling_hills`, `mountain` o `manual_problem_area`). Los chips
conservan EPSG:6368, resolución y alineación del baseline, y deben escribirse bajo `data/`, fuera de Git. La selección
final de ventanas permanece pendiente; la fase 3 no genera hillshade ni pendientes exploratorias por defecto.

`helpers/slope.py` contiene una evaluación en memoria del candidato inicial Horn para pruebas sintéticas. No está
conectada al Transform productivo. Ambos productos se derivan del mismo módulo de gradiente: grados mediante
`atan(rise/run)` y porcentaje mediante `rise/run × 100`, en `Float32`.

La revisión de la [documentación oficial de `gdaldem`](https://gdal.org/en/stable/programs/gdaldem.html) confirma
dos algoritmos admitidos para pendiente, Horn y Zevenbergen–Thorne, y salidas en grados o porcentaje. Horn queda
como candidato inicial, no como ganador. Antes de conectarlo a producción quedan por definir la política de
bordes/NoData y la comparación con Zevenbergen–Thorne sobre muestras reales.

Las pendientes deben compartir extensión, transform, resolución, CRS, NoData y máscara con el DEM acondicionado.
Cada entrada hija del manifiesto declara `parent_product=modelo_elevacion_acondicionado` y el SHA-256 calculado del
padre. Load rechaza cualquier pendiente generada desde otro DEM, incluso si su rejilla coincide.

El manifiesto de productos debe contener, como mínimo:

```text
source: productor INEGI, nombre CEM 4.0, role=source_original, scope=national, checksum, immutable=true
reprojection: method=bilinear, role=staging_baseline, publishable=false, includes_analytic_buffer=true, checksum
conditioning: candidate_id, method, parameters, promoted=true, baseline_sha256, QA
products:
  modelo_elevacion_acondicionado: path, sha256
  pendiente_grados: path, sha256, parent_product, parent_sha256
  pendiente_porcentaje: path, sha256, parent_product, parent_sha256
```

## Publicación

`PendientesLoad` es por ahora una puerta de prepublicación, no una implementación de publicación institucional.
Exige exactamente los tres productos en EPSG:6368, 15 m, `Float32` y NoData -9999, con la misma rejilla y máscara.
Recorre bloques para rechazar valores fuera de Jalisco y reporta cobertura interior. También valida unidades de
banda (`metre`, `degree`, `percent`), checksums, promoción reproducible, linaje padre-hijo y consistencia matemática
entre pendientes. Si todo pasa, escribe un manifiesto con estado
`validated_pending_institutional_raster_publication_pattern`; no copia ni publica los TIFF.

## Ejecución de Extract y Transform

```bash
cp core/pipelines/pendientes/.env.example core/pipelines/pendientes/.env
export SOURCE_TIFF_PATH=/ruta/al/conjunto_de_datos/continuonacional_15m.tif
python -c "from core.pipelines.pendientes.stages.extract import PendientesExtract; PendientesExtract().execute()"
python -c "from core.pipelines.pendientes.stages.transform import PendientesTransform; PendientesTransform().execute()"
```

`SOURCE_TIFF_PATH` reutiliza el GeoTIFF nacional ya descargado: Extract valida nombre, contrato y checksum sin
copiarlo ni descargarlo de nuevo. En entornos donde la conexión directa configurada a `cvegeo` no está disponible,
`CVEGEO_BOUNDARY_SNAPSHOT_PATH` puede apuntar a una captura EWKB generada por una consulta real; se validan base,
tabla, columna, SRID y cardinalidad antes de usarla. La captura y todos los resultados reales permanecen en `data/`.

Los raster grandes viven bajo `data/`, que está fuera del control de versiones.
