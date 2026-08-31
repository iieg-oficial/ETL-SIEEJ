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

`helpers/conditioning.py` mantiene la línea base productiva `raw`; los candidatos de la fase 4 viven en módulos
experimentales separados y no están conectados al Transform estatal. No se ha seleccionado ni promovido mediana,
Gaussian, bilateral, spline ni otro filtro. `helpers/qa.py` implementa las métricas
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
final de ventanas permanece pendiente en la fase 3, que no genera hillshade ni pendientes exploratorias por defecto.

## Fase 4 experimental

La selección automática recorre ventanas alineadas de 1024 × 1024 completamente cubiertas por la geometría
canónica de Jalisco y con al menos 99.5 % de datos válidos. Una muestra sistemática a 1/8 de resolución caracteriza
cada ventana mediante la mediana de pendiente Horn y la mediana del Laplaciano absoluto de cuatro vecinos. Los
chips `plano`, `lomerio` y `montana` son los más próximos conjuntamente a los percentiles p10, p50 y p90 dentro de
restricciones p25/p40–p60/p75. El manifiesto conserva todos los percentiles y declara cualquier relajación. Una
coordenada opcional EPSG:6368 permite añadir `problema_manual` y se ajusta a la rejilla, sin coordenadas embebidas.

El experimento compara `RAW`, Gaussian A1–A3 y bilateral B1–B3 mediante implementaciones NumPy con NoData explícito
y halo de seis píxeles. C1–C3 ejecutan `FeaturePreservingSmoothing` de WhiteboxTools cuando ruta, versión exacta y
SHA-256 del motor coinciden con la configuración. Se evalúa porque fue diseñado para reducir variación de corta
escala en DEM usando normales de superficie y preservando rupturas; no se presupone que sea superior para el CEM
4.0 de 15 m y sus parámetros requieren calibración específica.

El frontend queda fijado como `whitebox==2.3.6` (MIT). Como descarga un motor desde una URL no versionada, no basta
con fijar el paquete Python: cada corrida valida y registra la versión, licencia y checksum del ejecutable. El
contrato probado para este piloto fue WhiteboxTools v2.4.0, pero el valor operativo siempre debe suministrarse en
`WHITEBOX_TOOLS_EXPECTED_VERSION` junto con `WHITEBOX_TOOLS_EXPECTED_SHA256`.

Para cada candidato se calculan cambios de elevación, pendiente Horn común, diferencias vecinas, Laplaciano,
conservación del gradiente fuerte p90 y diferencia angular de normales. No se definen pesos, score, umbrales de
promoción ni clasificaciones definitivas de crestas/barrancas. Los GeoTIFF QA conservan el grid; las composiciones
PNG usan un rango común por variable y documentan el orden de paneles. Hillshade usa azimuth 315°, altitude 45° y
z-factor 1. Todos los resultados viven bajo `data/transform/pendientes/fase_04_acondicionamiento/`.

```bash
export WHITEBOX_TOOLS_EXECUTABLE=/ruta/versionada/whitebox_tools
export WHITEBOX_TOOLS_EXPECTED_VERSION='WhiteboxTools vX.Y.Z (...)'
export WHITEBOX_TOOLS_EXPECTED_SHA256=<sha256-del-ejecutable>
python -c "from core.pipelines.pendientes.stages.experiment import PendientesExperiment; PendientesExperiment().execute()"
```

Esta ejecución no modifica el baseline, no procesa todo Jalisco, no genera productos finales y no ejecuta Load.

## Fase 4B: calibración dirigida

La calibración 4B reduce el diseño a `RAW`, B2 y cuatro variantes conservadoras Feature-Preserving FP1–FP4. A1
queda sólo como referencia visual opcional y no se ejecuta por defecto; A2, A3, B1, B3, C2 y C3 están descartados
de nuevas pruebas. Ningún `max_diff` supera 0.5 m y cada salida FP se rechaza si excede su límite más una tolerancia
numérica de `1e-5 m`. FP2 replica los parámetros de C1 y, para los controles, se compara píxel a píxel con aquella
salida para verificar reproducibilidad.

La precondición obligatoria es una coordenada `problema_manual` observada visualmente y configurada mediante
`EXPERIMENT_MANUAL_X/Y`. Si falta, `PendientesCalibration` escribe un manifiesto con estado
`pending_manual_problem_coordinate` y termina antes de ejecutar filtros, perfiles o clasificaciones. Nunca selecciona
automáticamente una coordenada problemática.

La firma dirigida de banding no usa `dz=0` ni un score compuesto. Sobre la magnitud
`hypot(d²z/dx², d²z/dy²)` identifica celdas por encima del p90 RAW del chip y conserva ese umbral para todos los
candidatos. Reporta separadamente: densidad de celdas, coherencia axial de sus normales, continuidad mediante
vecinos inmediatos en la tangente y máxima autocorrelación positiva/lag entre 4 y 64 píxeles de las proyecciones X/Y
de magnitud. No hay umbral de aprobación.

En `problema_manual`, tres transectos paralelos se orientan según la normal axial dominante RAW y se desplazan
−256, 0 y +256 píxeles en la tangente. Los CSV registran distancia, coordenadas, elevación RAW/candidato y delta Z;
los PNG usan las mismas líneas y rango vertical común. Las composiciones comparan exclusivamente
`RAW, B2, FP1, FP2, FP3, FP4` para hillshade, pendiente Horn, diferencia de elevación y magnitud dirigida de banding.

```bash
export EXPERIMENT_MANUAL_X=<x-epsg-6368-observada>
export EXPERIMENT_MANUAL_Y=<y-epsg-6368-observada>
python -c "from core.pipelines.pendientes.stages.calibration import PendientesCalibration; PendientesCalibration().execute()"
```

Las únicas clasificaciones permitidas son `descartar`, `mantener` y `recomendado_para_validacion_estatal`. Se dejan
vacías hasta disponer de evidencia cuantitativa y visual tanto en `problema_manual` como en los tres controles; esto
no equivale a promoción productiva.

Una vez revisada toda esa evidencia, `record_review()` exige una clasificación para B2 y FP1–FP4, la propaga a los
cuatro chips y conserva explícitamente `winner_selected=false` y `recommendation_is_not_promotion=true`. Por tanto,
`recomendado_para_validacion_estatal` autoriza sólo una validación posterior sobre Jalisco; no selecciona, promueve
ni conecta un método al Transform productivo.

## Fase 5A: validación espacial estatal FP3

La Fase 5A valida FP3 sin construir el DEM estatal. Selecciona reproduciblemente 30 chips de 1024×1024: un chip por
cada sector ocupado de una malla 6×6 y la coordenada problemática conocida. El inventario registra sector,
morfología descriptiva, elevación, pendiente Horn exploratoria, rugosidad, relieve local, cobertura y la firma RAW
de banding. La muestra incluye plano, lomerío, montaña, valle y transición valle–sierra.

Antes del lote de validación se compara Whitebox completo contra una reconstrucción de tiles internos de 512 px.
Los halos 5, 6, 8, 12 y 16 no fueron exactos; 24 px fue el mínimo que reprodujo bit a bit los cuatro chips de prueba,
sin diferencias en interior, bordes verticales/horizontales ni esquinas. El halo es un resultado empírico específico
de FP3 y WhiteboxTools 2.4.0, no una inferencia a partir del radio nominal del filtro.

La clasificación `banding_bajo/medio/alto` usa terciles de autocorrelación dominante RAW y es sólo descriptiva. La
densidad RAW cercana a 10% se debe a que el umbral de cada chip es su propio p90; no representa una tasa independiente
de artefactos. La coordenada problemática conocida quedó en `banding_bajo` bajo los terciles de autocorrelación, una
señal de que esa clasificación univariada necesita ajuste antes de una decisión productiva.

El resultado vigente es `requiere_ajuste`: FP3 respeta 0.5 m, conserva gradientes fuertes, reproduce la mejora del
caso manual y no crea costuras con halo 24, pero no reduce consistentemente densidad y autocorrelación en el estrato
alto ni preserva prácticamente intactos todos los casos sin banding. Esto no es rechazo definitivo ni promoción;
no se generó el DEM acondicionado estatal, pendientes finales o Load.

## Fase 5B: calibración del detector de banding

La Fase 5B reutiliza los 30 RAW de 5A, valida su rejilla y registra sus checksums sin volver a ejecutar FP3. Produce
`banding_review.csv` y un atlas RAW de 30 composiciones con escalas estatales comunes. Sólo `problema_manual` nace
etiquetado como `banding_presente`, con fuente `manual_known_problem`; las otras 29 etiquetas quedan vacías y se
preservan en ejecuciones posteriores para que una revisión humana no sea sobrescrita.

El detector v2 mantiene densidad, coherencia, continuidad, autocorrelación, eje y lag, y añade sin combinarlos en un
score: prominencia relativa del pico, estabilidad del lag en 16 subventanas, anisotropía Hessiana, persistencia de
corridas tangenciales y repetición de pasos en siete perfiles. Las pruebas sintéticas cubren plano, bandas periódicas,
cresta única, ruido isotrópico, periodicidad orientada y cambio de orientación.

La autocorrelación absoluta de `problema_manual` es la menor de los 30 chips porque el relieve natural produce picos
más altos en otros lugares. En cambio, el caso manual presenta lag 4 estable en todas las subventanas, coherencia y
conteo de pasos en perfiles cerca del extremo alto, y prominencia relativa por encima de la mediana. Esto demuestra
que la detección no debe depender de un único tercil de autocorrelación. No se entrenó clasificador ni se fijaron
negativos; la evaluación de precision/recall/F1 permanece bloqueada hasta disponer de ambas clases humanas.

La revisión visual posterior cambia su estado metodológico a `superseded_for_binary_localization`: el patrón aparece
de manera extendida y ya no se considera adecuada la hipótesis de una máscara local binaria presencia/ausencia. No
se borran código, atlas ni métricas; siguen siendo evidencia útil para caracterizar intensidad, orientación y
periodicidad, y forman parte del linaje experimental.

## Fase 5C: diagnóstico del origen fuente–reproyección–derivados

La Fase 5C compara `problema_manual` y los controles reproducibles `plano` y `montana` entre el CEM publicado nativo
EPSG:6365 y el baseline EPSG:6368/15 m. La elevación Int16, cuantización y diferencias vecinas se miden directamente
en la rejilla nativa, sin interpolación. Para una comparación espacial válida, el CEM nativo se muestrea por vecino
más cercano en los centros de la rejilla baseline y se compara allí con el baseline bilinear; nunca se emparejan
índices de rejillas distintas.

Los derivados nativos se calculan sobre una copia temporal métrica EPSG:6368/15 m obtenida por `nearest`, conservando
los niveles verticales enteros. Pendiente Horn, hillshade 315°/45° y segunda diferencia utilizan así XY y Z en metros.
La ventana Int16 original no se sobrescribe. Un warp bilinear local auxiliar se registra sólo como QA y no como una
reproducción necesariamente exacta del warp de raster completo, cuyo contexto de transformación GDAL puede variar.

La evidencia real clasifica el patrón como `principalmente_presente_en_fuente`: en `problema_manual`, 100% de las
elevaciones nativas son enteras, aproximadamente 41–44% de los vecinos forman mesetas y 42–43% cambian exactamente
1 m; tres perfiles geográficos contienen secuencias repetidas meseta–salto. El baseline bilinear reduce el p95 de
segunda diferencia frente a la referencia nearest, por lo que esta prueba no sustenta que nuestra reproyección sea
la causa principal. La cuantización y el remuestreo institucional previo no pueden separarse entre sí usando sólo el
CEM publicado.

Un hillshade o una pendiente pueden hacer visible una estructura débil del DEM; esa visibilidad no demuestra por sí
sola que el producto sea inválido. Eliminar toda textura exigiría potencialmente sobre-suavizado. El objetivo futuro
es el acondicionamiento y la reducción de señal sistemática sin borrar señal geomorfológica real, no atribuir errores
al productor sin evidencia. RAW permanece como referencia y no se promueve aún FP1, FP2 ni FP3.

## Fase 5D: validación estatal comparativa del acondicionamiento global leve

La Fase 5D reutiliza y verifica los 30 RAW de Fase 5A, incluida `problema_manual`, y ejecuta directamente cada chip
completo con FP1, FP2 y FP3. No usa las antiguas clases de banding, no prueba otros filtros y no generaliza el halo
24 de FP3 a las demás configuraciones. La comparación estratifica plano, valle, lomerío, transición valle–sierra y
montaña mediante alteración Z, pendiente Horn exploratoria, gradiente fuerte, normales, distribución de segunda
diferencia y perfiles idénticos.

FP1 es el extremo conservador: su MAE Z mediana es 0.079 m, pero su ratio p95 de segunda diferencia permanece cerca
de uno. FP2 reduce la mediana de segunda diferencia a 0.753 del RAW y, en terreno plano, reduce p50/p95 a 0.597/0.868,
con MAE Z mediana 0.162 m, MAE de pendiente 0.273° y normal p95 mediana 0.825°. FP3 alcanza una reducción p50 apenas
mayor, pero modifica más Z, pendiente y normales y no mejora consistentemente el p95 territorial. Los perfiles
conservan los pasos fuertes y la inspección de diez hillshades no muestra pérdida clara de crestas, barrancas o forma
montañosa a escala de chip.

Sin score ponderado, FP1, FP2 y FP3 son estrictamente no dominados porque cada uno conserva alguna ventaja aislada.
No obstante, FP3 no aporta una ventaja territorial material y consistente frente a FP2. La decisión permitida es
`FP2_recomendado_para_procesamiento_estatal`: significa únicamente que FP2 merece la siguiente QA sobre el baseline
completo. Antes de ello debe demostrarse su equivalencia tileada y determinarse empíricamente el halo; no se asumen
los 24 px de FP3.

La reproyección permanece congelada como CEM EPSG:6365/0.5 arcsec/Int16 → bilinear → EPSG:6368/15 m/Float32. El
bilinear reduce parcialmente la expresión de la discretización, pero no recupera información vertical inexistente.

## Fase 6A: candidato estatal FP2 con contexto

La Fase 6A conserva separados `execute()`, que produce el raster por tiles, y `finalize_existing()`, que sólo
valida un artefacto existente y escribe su manifiesto. El candidato de staging con buffer usa FP2, tiles de 2048 px,
orden row-major y halo 24. Este halo fue el mínimo bitwise exacto en seis controles y quedó confirmado con 32 px.

La prueba causal del ensamblado usa 30 referencias con 24 px de contexto real del baseline: las 30 son exactas y
el caso que cruza una frontera de producción también es exacto. Las referencias FP2 aisladas de Fase 5D difieren en
sus bordes porque no disponían de contexto exterior; su interior excluyendo 24 px permanece exacto, pero la igualdad
del chip aislado completo no es un hard gate. Las métricas de las 28 fronteras reales son descriptivas respecto al
baseline y no introducen umbrales arbitrarios.

El artefacto `modelo_elevacion_acondicionado_contexto_jalisco_15m.tif` conserva la rejilla y máscara del baseline,
incluido el buffer analítico. Su estado es `statewide_candidate_generated_not_promoted`: no es producto final, no se
ha recortado a Jalisco y no autoriza pendientes productivas ni Load.

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
