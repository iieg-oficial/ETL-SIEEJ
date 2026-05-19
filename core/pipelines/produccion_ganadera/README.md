# produccion_ganadera

## Descripción

Los datos de producción ganadera son publicados anualmente por el Servicio de Información Agroalimentaria y Pesquera ([SIAP](https://nube.agricultura.gob.mx/datosAbiertos/Pecuario.php)) y reportan volumen, valor y precio de los productos ganaderos por especie, municipio y distrito de desarrollo rural a nivel nacional.

## ERD

![ERD](assets/erd.svg)

## Diccionario de variables

### `stg_ganadera`

| Variable | Descripción |
|---|---|
| `entidad_id` | Clave INEGI de la entidad federativa (ref. `cvegeo_states`) |
| `municipio_id` | Clave INEGI del municipio (ref. `cvegeo_municipalities`) |
| `distrito_des_rural_id` | FK a `cat_distritos_des_rural` |
| `especie_id` | FK a `cat_especies` |
| `producto_id` | FK a `cat_productos` |
| `volumen_produccion` | Volumen de producción (toneladas) |
| `peso_sacrificio` | Peso en canal de animales sacrificados (toneladas) |
| `precio_med_rural` | Precio medio rural (pesos por tonelada) |
| `valor_produccion` | Valor de la producción (miles de pesos) |
| `animales_sacrificados` | Número de cabezas sacrificadas |

## Fuentes

| Nivel | Fuente |
|---|---|
| Nacional | [Producción Ganadera SIAP](https://nube.agricultura.gob.mx/datosAbiertos/Pecuario.php) |



## Actualización

Anual, automática. El DAG `etl_produccion_ganadera_update` corre con `@yearly` y detecta el último año cargado para descargar solo los años faltantes. Los datos SIAP se publican con cierto rezago, por lo que el pipeline verifica que el año tenga registros antes de continuar.

## Comentarion

El primer año con datos disponibles en la API es 2006.
