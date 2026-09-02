# Metodología del pipeline `pendientes`

Este documento conserva el sustento de las decisiones científicas. Los estados, métricas y parámetros proceden del
código y de los manifests de evaluación generados durante las fases 4–8; no sustituyen una validación con verdad
terreno independiente.

## 1. Objetivo

Construir para Jalisco un modelo de elevación acondicionado y una familia de pendientes reproducible, conservadora y
trazable. Las decisiones finales son:

```text
FP2 = acondicionamiento seleccionado
Wood–Evans 5 x 5 = pendiente productiva
Horn 3 x 3 = referencia metodológica histórica
WE7 = descartado por mayor generalización
```

## 2. CEM 4.0 y contrato de datos

La fuente es el Continuo de Elevaciones Mexicano 4.0 de INEGI: nacional, EPSG:6365, 0.5 segundos de arco, `Int16`,
NoData 32767 y elevación en metros. El XML de banda declara una magnitud de tipo longitud y el contrato incorporó la
confirmación documental complementaria de metros. El CEM original es inmutable y sus rutas internas de producción
no son dependencias del pipeline.

El linaje institucional documenta `Resample`, desde `MDT_125_16bits_sust.tif` hacia
`MDT_15m_16bits_bilinear.tif`, con método bilinear; también menciona mosaicos e intermedios previos. Por ello el
CEM publicado ya contiene interpolación anterior al procesamiento IIEG.

## 3. Diagnóstico de discretización vertical

El escalonamiento observado no se atribuyó exclusivamente a `Int16`. La hipótesis registrada combina cuantización
vertical, procesamiento previo, remuestreo bilinear institucional, nueva reproyección a rejilla métrica y
amplificación visual al calcular derivadas, pendiente o hillshade.

El diagnóstico fuente–reproyección comparó superficies en una rejilla común, no índices de píxel de rejillas
distintas. La reproyección bilinear redujo parcialmente la expresión de niveles enteros, pero no recuperó información
vertical inexistente. Tampoco permitió separar cuantización de interpolación institucional. El detector de banding y
los perfiles se conservan para reproducir ese diagnóstico, no como gates productivos aislados.

## 4. Reproyección y baseline

El baseline técnico transforma CEM EPSG:6365 / 0.5 arcsec / `Int16` a EPSG:6368 / 15 m / `Float32`, NoData -9999,
mediante bilinear. Incluye Jalisco y buffer analítico. Bilinear se mantuvo por tratarse de una variable continua y por
coincidir con el método documentado en el producto publicado; esto implica una segunda interpolación espacial.

La QA registra distribución, superficie válida, NoData y comportamiento en terreno plano y montañoso. El baseline
no se publica y no se recorta antes de calcular derivados.

## 5. Acondicionamiento del DEM

### FP1, FP2 y FP3

Las tres alternativas finales usan WhiteboxTools `FeaturePreservingSmoothing` con filtro 11 y una iteración:

- FP1: `norm_diff=5`, `max_diff=0.25 m`;
- FP2: `norm_diff=5`, `max_diff=0.5 m`;
- FP3: `norm_diff=7.5`, `max_diff=0.5 m`.

El experimento local incluyó el área manual de banding y controles plano, lomerío y montaña. La calibración conservó
perfiles, hillshade, diferencias, pendiente Horn exploratoria, normales y métricas dirigidas. FP2 reprodujo el
candidato C1 anterior dentro del contrato de tolerancia registrado.

### Validación local y estatal

La validación espacial utilizó 30 chips alineados de 1024 × 1024, estratificados espacial y morfológicamente. En la
comparación estatal leve, las medianas fueron:

| Candidato | MAE Z (m) | ratio p50 segunda diferencia | ratio p95 segunda diferencia | MAE pendiente (°) |
| --- | ---: | ---: | ---: | ---: |
| FP1 | 0.079 | 0.918 | 1.002 | 0.146 |
| FP2 | 0.162 | 0.753 | 0.999 | 0.273 |
| FP3 | 0.172 | 0.751 | 1.004 | 0.290 |

En terreno plano, FP2 obtuvo ratios p50/p95 de 0.597/0.868. En montaña conservó el gradiente fuerte con ratio
mediano 0.9997 y diferencia angular p95 de normales de 0.827°. Los perfiles retuvieron 100% de los pasos fuertes por
encima de la mitad del umbral mediano; la revisión de diez hillshades no mostró pérdida clara de crestas, barrancas o
forma montañosa a escala de chip.

### Selección FP2

FP1, FP2 y FP3 quedaron no dominados sin construir un score ponderado arbitrario. FP1 cambiaba menos Z pero reducía
poco la segunda diferencia. FP3 aportaba ganancias p50 marginales y aisladas, con mayor alteración de Z, pendiente y
normales, sin mejora p95 territorial consistente frente a FP2. Se seleccionó FP2 como compromiso conservador.

El contrato congelado de FP2 es `filter=11`, `norm_diff=5`, `num_iter=1`, `max_diff=0.5`, `zfactor=1`, WhiteboxTools
2.4.0. La ejecución tileada validó halo de 24 píxeles: 30 de 30 referencias con contexto y el cruce de frontera de
tile fueron bitwise exactos. El DEM territorial contiene 356,528,880 píxeles válidos, cero válidos fuera de Jalisco y
valores bitwise idénticos a su padre contextual en la máscara.

## 6. Pendiente local

### Horn y Zevenbergen–Thorne

La evaluación local comparó `gdaldem` Horn y Zevenbergen–Thorne con GDAL 3.8.4, factor Z efectivo 1, salida en
grados y sin `compute_edges`. Ambos cumplieron 27 planos sintéticos con error máximo menor que 0.001°.

Con ruido sembrado, Horn obtuvo MAE/RMSE de 0.1323°/0.1664°, frente a 0.2162°/0.2712° para
Zevenbergen–Thorne. En los 30 chips reales, la mediana del p95 de diferencias vecinas fue 4.0608° para Horn y
4.3166° para Zevenbergen–Thorne. Horn fue seleccionado entonces para la producción local 3 × 3. Esa decisión se
conserva como referencia histórica; fue posteriormente sustituida como producto final por la evaluación de escala
espacial Wood–Evans.

### Pruebas sintéticas

Los planos verificaron exactitud sobre gradientes conocidos. Las superficies geomorfológicas y el ruido con semilla
fija evaluaron sensibilidad, estabilidad local y conservación de crestas, valles y transiciones. No se interpretaron
extremos mayores como exactitud superior sin verdad terreno.

## 7. Escala espacial de pendiente

Wood–Evans se implementó con `r.param.scale` de GRASS GIS 8.3.2: ajuste cuadrático bivariado no ponderado por
distancia (`exponent=0`), `method=slope`, `zscale=1` y soporte completo de ventana impar. Se compararon WE3, WE5 y
WE7 contra Horn 3 × 3 (H3). Las huellas nominales son 45, 75 y 105 m, pero no equivalen por sí mismas a la escala
espacial efectiva.

### WE3, WE5 y WE7

En ocho chips reales, las medianas fueron:

| Método | MAE vs H3 (°) | p95 diferencia vecina (°) | componentes conectados | cambio de clase vs H3 |
| --- | ---: | ---: | ---: | ---: |
| H3 | 0.000 | 3.762 | 18,532 | 0.0% |
| WE3 | 0.061 | 3.714 | no evaluado | no evaluado |
| WE5 | 0.618 | 3.107 | 11,348 | 13.31% |
| WE7 | 1.153 | 2.645 | 7,061 | 24.90% |

### Ruido sintético

El RMSE medio frente a ruido sembrado fue 0.712° para H3, 0.670° para WE3, 0.233° para WE5 y 0.119° para WE7.
Los errores máximos en planos fueron, respectivamente, 0.000182°, 0.000182°, 0.000070° y 0.000044°. Una ventana
mayor reduce microvariación, pero no establece exactitud universal.

### AMG, planicie, montaña y barranca

WE3 fue casi indistinguible de H3. WE5 redujo textura sal y pimienta en AMG y áreas planas, y conservó la continuidad
visible de crestas, cauces, pendientes y rupturas fuertes en montaña, barranca y transiciones. WE7 consolidó más las
clases, pero ensanchó y atenuó más estructuras del relieve. La revisión visual usó extensión, simbología, rango y
zoom comunes y se interpretó sólo como evidencia de legibilidad cartográfica.

### Selección WE5

WE5 fue el punto intermedio con reducción material de ruido y fragmentación, menor atenuación y menor cambio que
WE7. WE7 se descartó por mayor generalización: su reducción adicional de ruido no compensó el mayor cambio de clase,
MAE y atenuación visible. La selección `WoodEvans5x5_recomendado_para_produccion` aplica a este CEM, resolución,
acondicionamiento y objetivo, no como superioridad universal.

## 8. Metodología productiva final

El flujo científico congelado es CEM → reproyección bilinear → FP2 contextual → pendiente WE5 contextual → ventana
y máscara de Jalisco → grados → porcentaje. Grados y porcentaje proceden del mismo campo de pendiente; porcentaje se
calcula con `tan(radians(grados)) * 100` y no se trunca a 100. DEM y pendientes comparten EPSG:6368, 15 m, transform,
bounds, dimensiones, máscara y NoData.

## 9. Clasificación grados

El precedente cartográfico INEGI-DGG usa siete clases: 0–2, 2–5, 5–10, 10–15, 15–25, 25–50 y 50° o más. La
clasificación es una representación temática; no altera la pendiente continua.

## 10. Clasificación porcentaje

La clasificación FAO/IIASA GAEZ usa ocho clases: 0–0.5, 0.5–2, 2–5, 5–8, 8–16, 16–30, 30–45 y 45% o más. En
ambas clasificaciones el código 0 queda reservado, los códigos válidos empiezan en 1 y NoData es 255.

## 11. COG y overviews

El empaquetado COG pertenece a Transform y usa GDAL COG, DEFLATE nivel 9, bloques de 512 y `BIGTIFF=IF_SAFER`.
Los continuos `Float32` usan predictor flotante y overviews `AVERAGE`; los clasificados `UInt8`, overviews `MODE`.
Para los cinco productos la QA registró cero diferencias de máscara, cero píxeles base diferentes y diferencia
absoluta máxima cero. Los overviews son representaciones multirresolución y no se comparan bitwise con la base.

## 12. Estadísticas municipales

Extract congela las geometrías `geom_iieg` y `geom_inegi` de `cvegeo`. Transform selecciona por centro de píxel,
`all_touched=false`, y calcula estadísticas exactas sobre todos los píxeles seleccionados del DEM FP2 y pendiente WE5
contextuales. Cada fila se identifica por municipio y fuente de límite. Load inserta o actualiza de forma
transaccional el catálogo de dos fuentes y las estadísticas, sin cargar los rasters a PostgreSQL.

## 13. Limitaciones

- No existe verdad terreno independiente de mayor resolución para declarar exactitud absoluta en los chips reales.
- La doble interpolación y la cuantización del producto publicado no pueden aislarse causalmente con el CEM final.
- Banding visible en derivados no demuestra por sí solo invalidez del DEM.
- FP2 y WE5 son decisiones condicionadas por CEM 4.0, rejilla de 15 m, software y parámetros congelados.
- Las clasificaciones son convenciones temáticas; no sustituyen los productos continuos.
- Los límites municipales pueden cambiar estadísticas marginales; por eso se publican separadas por fuente.

## 14. Referencias

- Horn, B. K. P. (1981). *Hill Shading and the Reflectance Map*. DOI `10.1109/PROC.1981.11918`.
- Zevenbergen, L. W. y Thorne, C. R. (1987). *Quantitative analysis of land surface topography*. DOI
  `10.1002/esp.3290120107`.
- Jones, K. H. (1998). *A comparison of algorithms used to compute hill slope as a property of the DEM*. DOI
  `10.1016/S0098-3004(98)00032-6`.
- Florinsky, I. V. (1998). *Accuracy of local topographic variables derived from digital elevation models*. DOI
  `10.1080/136588198242003`.
- Wood, J. (1996). *The geomorphological characterisation of digital elevation models*. University of Leicester,
  handle `2381/34503`.
- Gao, J., Burt, J. E. y Zhu, A.-X. (2012). *Scale effects of slope based on resolution and neighbourhood size*. DOI
  `10.1080/13658816.2012.657201`.
- GRASS GIS, manual de `r.param.scale`.
- INEGI, Continuo de Elevaciones Mexicano 4.0 y metadata XML distribuida con el producto.
