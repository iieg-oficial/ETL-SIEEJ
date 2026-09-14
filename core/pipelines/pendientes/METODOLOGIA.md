# Metodología del pipeline `pendientes`

Este documento describe el método productivo final y sintetiza la evidencia usada para seleccionarlo. Las
comparaciones entre algoritmos no equivalen a una validación de exactitud frente a terreno.

## 1. Objetivo

Producir para Jalisco un modelo de elevación acondicionado y una familia coherente de pendientes analíticas y
representaciones cartográficas, con grid, máscara y linaje reproducibles.

## 2. CEM 4.0 y contrato de datos

La fuente es el Continuo de Elevaciones Mexicano 4.0 de INEGI: nacional, EPSG:6365, 0.5 segundos de arco, `Int16`,
NoData 32767 y Z en metros. El original es inmutable y no se renombra ni presenta como producto IIEG.

La metadata institucional registra un `Resample` bilinear desde `MDT_125_16bits_sust.tif` hacia
`MDT_15m_16bits_bilinear.tif`, además de intermedios y un mosaico previo. Las rutas internas de producción de INEGI
son trazabilidad documental, no dependencias funcionales.

## 3. Diagnóstico de discretización vertical

El banding observado puede combinar cuantización `Int16`, procesamiento e interpolación institucionales, el
remuestreo bilinear documentado, la reproyección a una nueva rejilla métrica y la amplificación de derivadas. No se
atribuyó causalidad exclusiva al tipo de dato. La comparación fuente–reproyección se hizo sobre una rejilla común y
con perfiles y métricas dirigidas, no mediante índices de píxel de rejillas distintas.

## 4. Reproyección y baseline

El baseline transforma el CEM a EPSG:6368, 15 × 15 m, `Float32`, NoData -9999, mediante bilinear. Cubre Jalisco más
10 km de buffer analítico. Es un artefacto técnico no publicable. Como el CEM publicado ya fue remuestreado con
bilinear, esta etapa implica una segunda interpolación espacial.

## 5. Acondicionamiento del DEM

Se compararon RAW, Gaussian `sigma=1.5`, `sigma=2.0` y `sigma=3.0`, reconstrucción polinómica/local, alternativas
residuales y el FP2 histórico basado en `FeaturePreservingSmoothing`. FP2 quedó descartado como método productivo y
WhiteboxTools ya no forma parte del runtime.

La evaluación combinó chips de terreno plano, lomerío, montaña y la localización manual del patrón; diferencias de
elevación, pendiente y normales; perfiles; hillshade; preservación de crestas y barrancas; y métricas dirigidas de
banding. Gaussian `sigma=1.5` fue el mejor compromiso observado entre reducción del patrón y conservación del detalle
topográfico.

El método final usa `sigma=1.5` píxeles, equivalente a 22.5 m sobre la rejilla de 15 m, y `truncate=4.0`. La
convolución se ejecuta por tiles con halo igual al radio completo del kernel. Se filtran por separado elevaciones
válidas y pesos de máscara; su cociente normaliza el resultado. Así NoData no contamina valores válidos y la máscara
original se conserva. La salida es `Float32`.

## 6. Pendiente local

Horn y Zevenbergen–Thorne se evaluaron previamente con planos sintéticos, superficies geomorfológicas y ruido de
semilla fija. Horn 3×3 fue la referencia local histórica por su estabilidad relativa, pero no es el estimador
productivo final. Estas pruebas verifican implementación y sensibilidad, no exactitud territorial.

## 7. Escala espacial de pendiente

Wood–Evans se implementó mediante GRASS `r.param.scale`, `method=slope`, `exponent=0`, `zscale=1`. Se compararon
WE3, WE5 y WE7, además de Horn 3×3, sobre ruido sintético y chips representativos de AMG/planicie, montaña, barranca
y transiciones. WE3 fue cercano a Horn; WE7 redujo más microvariación pero produjo mayor generalización. WE5 redujo
mejor el ruido visible en zonas planas y conservó suficientemente el detalle en pendientes pronunciadas.

La comparación estatal WE5–Horn sobre 817,364,253 píxeles comunes obtuvo bias -0.1906°, MAE 0.3116° y RMSE
0.4420°. Los percentiles p50, p90, p95 y p99 de `|delta|` fueron 0.2215°, 0.7085°, 0.9275° y 1.4415°; el máximo fue
13.5363°. Superaron 0.5°, 1°, 2° y 5° el 19.454%, 3.978%, 0.209% y 0.001%, respectivamente. Son diferencias entre
estimadores, no error frente al terreno.

La decisión final es **Wood–Evans 5×5 productivo**. Horn 3×3 queda sólo como referencia metodológica histórica y
WE7 se descarta por mayor generalización.

## 8. Metodología productiva final

```text
CEM 4.0 INEGI
  -> reproyección bilinear EPSG:6368 / 15 m con buffer
  -> Gaussian normalizado sigma=1.5
  -> DEM G15 territorial
       -> Wood-Evans 5x5 grados
            -> tan(radians(grados)) * 100
       -> Q10 RAW para geoportal
```

La pendiente porcentual se deriva exactamente del raster de grados, en precisión intermedia `Float64` y salida
`Float32`; no usa un estimador independiente. DEM, grados y porcentaje comparten grid y máscara territorial. Las
estadísticas municipales y los indicadores se calculan desde los continuos G15/WE5 no generalizados.

## 9. Clasificación grados

El precedente cartográfico INEGI-DGG emplea siete intervalos: `[0,2)`, `[2,5)`, `[5,10)`, `[10,15)`, `[15,25)`,
`[25,50)` y `>=50` grados. Los códigos válidos son 1..7, 0 está reservado y 255 es NoData.

## 10. Clasificación porcentaje

El esquema FAO/IIASA GAEZ usa ocho intervalos: `[0,0.5)`, `[0.5,2)`, `[2,5)`, `[5,8)`, `[8,16)`, `[16,30)`,
`[30,45)` y `>=45` por ciento. Los códigos válidos son 1..8. Esta clasificación no es espacialmente equivalente a
la de grados y se genera de forma independiente.

En ambos productos cartográficos, un sieve GDAL de 8 vecinos con `threshold=8` propone cambios para componentes de
1 a 7 píxeles. Sólo se acepta una propuesta si `abs(clase_nueva - clase_original) == 1`; saltos de dos o más clases y
NoData conservan el valor original. La operación generaliza la representación clasificada, no la pendiente continua.

## 11. COG y overviews

Transform empaqueta directamente con el driver COG de GDAL y DEFLATE lossless. Los continuos `Float32` usan
overviews `AVERAGE`; los clasificados `UInt8` y la elevación Q10 `Int16` usan `MODE`. La QA exige COG válido, bloques
512, overviews, grid y máscara idénticos y cero diferencias en valores base respecto del raster científico.

La elevación Q10 parte directamente del DEM G15 territorial y calcula `round(z / 10) * 10`. Almacena elevaciones
reales, usa NoData -32768 y no aplica mediana, sieve ni suavizado adicional. Se denomina producto con **intervalo
vertical de representación de 10 m**, no resolución ni exactitud vertical.

Se evaluó un sieve de elevación restringido a ±10 m. Para tamaños <=3, <=5 y <=7 píxeles propuso 2,003,256,
3,057,810 y 3,884,730 cambios, de los cuales aceptó 847,674 (0.1037% del raster), 1,296,237 (0.1585%) y 1,657,185
(0.2027%). Se descartó porque Q10 RAW ya resultaba adecuado y una componente pequeña no demuestra ruido topográfico.

## 12. Estadísticas municipales

Extract congela 125 municipios para cada fuente territorial IIEG e INEGI. Transform selecciona por centro de píxel
(`all_touched=false`) sobre los raster contextuales continuos G15 y WE5 para evitar pérdidas de borde, y genera 250
filas con estadísticas de elevación, grados, porcentaje y cobertura. Load realiza upsert por municipio y fuente.

## 13. QA y limitaciones

Los gates comprueban fuente, checksum, CRS, resolución, alineación, extensión, máscara, dtype, NoData, unidades,
rangos, relación padre–hijo, igualdad lossless del COG y conteos municipales. Los checkpoints sólo reutilizan
artefactos cuyos hashes corresponden a la corrida.

El acondicionamiento y WE5 fueron seleccionados para CEM 4.0, la malla de 15 m y el propósito institucional descrito;
no son métodos universalmente superiores. La evaluación no incorpora verdad terreno independiente ni estima exactitud
vertical. Una validación física con datos de control independientes sigue siendo trabajo posterior posible.

## 14. Referencias

- INEGI. Continuo de Elevaciones Mexicano 4.0 y metadata de linaje asociada.
- GRASS GIS. `r.param.scale`, método `slope`.
- Wood, J. (1996). *The Geomorphological Characterisation of Digital Elevation Models*.
- FAO/IIASA. Global Agro-Ecological Zones (GAEZ), clases de pendiente porcentual.
- GDAL. Drivers COG y utilitario `gdal_sieve.py`.
