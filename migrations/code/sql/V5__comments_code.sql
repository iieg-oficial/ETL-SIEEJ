COMMENT ON TABLE cat_actividades IS 'Catálogo de actividades físicas y deportivas del programa Reto. El id es el código del origen y no cambia entre cortes.';
COMMENT ON COLUMN cat_actividades.id IS 'Código de actividad asignado por CODE.';
COMMENT ON COLUMN cat_actividades.actividad IS 'Nombre de la actividad (ej: Baile, Acondicionamiento físico y aerobics).';

COMMENT ON TABLE cat_regiones IS 'Catálogo de las 13 regiones del estado de Jalisco con las que CODE reporta el programa, ya normalizadas (sin espacios sobrantes y con acentos).';
COMMENT ON COLUMN cat_regiones.id IS 'Identificador único de la región en este pipeline.';
COMMENT ON COLUMN cat_regiones.region IS 'Nombre de la región (ej: Altos Norte, Ciénega, Costa-Sierra Occidental).';

COMMENT ON TABLE stg_puntos_activacion_reto IS 'Puntos de activación del programa Reto, Reactivación para Todas y Todos del Consejo Estatal para el Fomento Deportivo (CODE). Una fila por espacio y corte. cantidad_usuarios parece ser una cifra por municipio repetida en cada espacio (pendiente de confirmar con CODE), por lo que no debe sumarse entre espacios.';
COMMENT ON COLUMN stg_puntos_activacion_reto.id IS 'Identificador único del registro.';
COMMENT ON COLUMN stg_puntos_activacion_reto.clave_punto IS 'Identificador del punto de activación en el archivo de origen. Tiene huecos y no es estable entre cortes.';
COMMENT ON COLUMN stg_puntos_activacion_reto.entidad_id IS 'Clave de la entidad federativa. Siempre 14 (Jalisco). Referencia lógica a cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_puntos_activacion_reto.municipio_id IS 'Clave del municipio (clave_agem del origen). Referencia lógica a cvegeo_municipalities.cve_mun.';
COMMENT ON COLUMN stg_puntos_activacion_reto.region_id IS 'Región del estado en que se ubica el punto.';
COMMENT ON COLUMN stg_puntos_activacion_reto.nombre_espacio IS 'Nombre del espacio donde se realiza la actividad (ej: Auditorio municipal).';
COMMENT ON COLUMN stg_puntos_activacion_reto.dias_horarios IS 'Días y horarios de la actividad en texto libre, tal como los captura CODE. No se interpreta.';
COMMENT ON COLUMN stg_puntos_activacion_reto.actividad_id IS 'Actividad que se realiza en el punto. Nula cuando el origen no la reporta.';
COMMENT ON COLUMN stg_puntos_activacion_reto.cantidad_usuarios IS 'Cantidad de usuarios reportada. Parece ser una cifra por municipio repetida en cada espacio (pendiente de confirmar con CODE): no sumar entre espacios.';
COMMENT ON COLUMN stg_puntos_activacion_reto.longitud IS 'Longitud en grados decimales (EPSG:4326), columna x del origen.';
COMMENT ON COLUMN stg_puntos_activacion_reto.latitud IS 'Latitud en grados decimales (EPSG:4326), columna y del origen.';
COMMENT ON COLUMN stg_puntos_activacion_reto.fecha_corte IS 'Fecha a la que corresponden los datos, tomada de la columna fecha del archivo.';
COMMENT ON COLUMN stg_puntos_activacion_reto.fecha_actualizacion_fuente IS 'Fecha en que CODE envió el conjunto por el formulario. CODE no captura fecha de actualización, así que se toma la fecha del envío.';
COMMENT ON COLUMN stg_puntos_activacion_reto.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';

COMMENT ON TABLE cargas_acervo IS 'Control de los envíos ya procesados desde Acervo. Da el watermark de la carga incremental y evita reprocesar un envío cuyo archivo no cambió.';
COMMENT ON COLUMN cargas_acervo.id IS 'Identificador único del registro de carga.';
COMMENT ON COLUMN cargas_acervo.envio_id IS 'Identificador del envío en el formulario de datasets del SIEEJ.';
COMMENT ON COLUMN cargas_acervo.conjunto IS 'Nombre del conjunto de datos tal como lo capturó la dependencia.';
COMMENT ON COLUMN cargas_acervo.object_key IS 'Ruta del archivo dentro del bucket de Acervo.';
COMMENT ON COLUMN cargas_acervo.etag IS 'Hash MD5 del contenido. Si coincide con el de la carga anterior, el archivo no cambió. No es MD5 en subidas multiparte.';
COMMENT ON COLUMN cargas_acervo.fecha_corte IS 'Fecha a la que corresponden los datos del envío.';
COMMENT ON COLUMN cargas_acervo.fecha_actualizacion_fuente IS 'Fecha en que la dependencia envió el conjunto de datos.';
COMMENT ON COLUMN cargas_acervo.actualizado_en IS 'Última modificación del envío. Es el watermark de la carga incremental.';
COMMENT ON COLUMN cargas_acervo.procesado_en IS 'Momento en que el ETL procesó el envío.';

COMMENT ON VIEW vw_puntos_activacion_reto IS 'Puntos de activación del programa Reto con región y actividad resueltas. Entidad y municipio provienen de cvegeo. Expone longitud y latitud. cantidad_usuarios no debe sumarse entre espacios.';
