COMMENT ON TABLE cat_deportes IS 'Catálogo de deportes de CODE, compartido por Academias deportivas y Polideportivos. El id es el código del origen.';
COMMENT ON COLUMN cat_deportes.id IS 'Código de deporte asignado por CODE.';
COMMENT ON COLUMN cat_deportes.deporte IS 'Nombre del deporte (ej: Natación, Charrería).';

COMMENT ON TABLE cat_tipos_academia IS 'Catálogo de tipos de academia deportiva (ej: Regular, Centro Regional). Incluye tipos presentes en los datos que el catálogo de CODE no lista.';
COMMENT ON COLUMN cat_tipos_academia.id IS 'Identificador único del tipo en este pipeline. No es el código del origen: en el origen Semillero Rojiblanco comparte código con Regular.';
COMMENT ON COLUMN cat_tipos_academia.tipo IS 'Nombre del tipo de academia.';

COMMENT ON TABLE stg_academias_deportivas IS 'Academias deportivas, Espacios para la Paz, del Consejo Estatal para el Fomento Deportivo (CODE). Una fila por academia, deporte y corte. El origen repite domicilio para varios deportes, por lo que no hay llave única natural.';
COMMENT ON COLUMN stg_academias_deportivas.id IS 'Identificador único del registro.';
COMMENT ON COLUMN stg_academias_deportivas.entidad_id IS 'Clave de la entidad federativa. Siempre 14 (Jalisco). Referencia lógica a cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_academias_deportivas.municipio_id IS 'Clave del municipio (cve_mun del origen, sin ceros a la izquierda). Referencia lógica a cvegeo_municipalities.cve_mun.';
COMMENT ON COLUMN stg_academias_deportivas.deporte_id IS 'Deporte de la academia. Se resuelve por nombre contra el catálogo porque cat_deporte del origen no coincide con él.';
COMMENT ON COLUMN stg_academias_deportivas.tipo_id IS 'Tipo de academia, resuelto por nombre.';
COMMENT ON COLUMN stg_academias_deportivas.deporte_nombre_largo IS 'Nombre largo con que CODE captura la academia o disciplina (ej: FUTBOL COLMENA SAN JUAN DE DIOS), tal como viene.';
COMMENT ON COLUMN stg_academias_deportivas.beneficiarios_total IS 'Total de beneficiarios reportado. Nulo si el origen no lo trae; puede no igualar hombres más mujeres.';
COMMENT ON COLUMN stg_academias_deportivas.beneficiarios_hombres IS 'Beneficiarios hombres. Nulo si el origen no lo trae.';
COMMENT ON COLUMN stg_academias_deportivas.beneficiarios_mujeres IS 'Beneficiarias mujeres. Nulo si el origen no lo trae.';
COMMENT ON COLUMN stg_academias_deportivas.domicilio IS 'Domicilio de la academia en texto libre.';
COMMENT ON COLUMN stg_academias_deportivas.horarios IS 'Días y horarios en texto libre. No se interpreta.';
COMMENT ON COLUMN stg_academias_deportivas.longitud IS 'Longitud en grados decimales (EPSG:4326), obtenida de la geometría del origen.';
COMMENT ON COLUMN stg_academias_deportivas.latitud IS 'Latitud en grados decimales (EPSG:4326), obtenida de la geometría del origen.';
COMMENT ON COLUMN stg_academias_deportivas.fecha_corte IS 'Fecha a la que corresponden los datos, tomada de la columna fecha del archivo.';
COMMENT ON COLUMN stg_academias_deportivas.fecha_actualizacion_fuente IS 'Fecha en que CODE envió el conjunto por el formulario.';
COMMENT ON COLUMN stg_academias_deportivas.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';

COMMENT ON TABLE stg_polideportivos IS 'Polideportivos de CODE. Una fila por centro y corte. Los deportes viven en polideportivo_deportes.';
COMMENT ON COLUMN stg_polideportivos.id IS 'Identificador único del registro.';
COMMENT ON COLUMN stg_polideportivos.entidad_id IS 'Clave de la entidad federativa (clave_entidad del origen). Referencia lógica a cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_polideportivos.municipio_id IS 'Clave del municipio (cve_mun del origen, sin ceros a la izquierda). Referencia lógica a cvegeo_municipalities.cve_mun.';
COMMENT ON COLUMN stg_polideportivos.nombre_centro IS 'Nombre del polideportivo.';
COMMENT ON COLUMN stg_polideportivos.domicilio IS 'Domicilio en texto libre.';
COMMENT ON COLUMN stg_polideportivos.horarios IS 'Días y horarios en texto libre. No se interpreta.';
COMMENT ON COLUMN stg_polideportivos.servicios IS 'Descripción de servicios y disciplinas en texto libre, tal como la captura CODE. No se normaliza.';
COMMENT ON COLUMN stg_polideportivos.longitud IS 'Longitud en grados decimales (EPSG:4326), obtenida de la geometría del origen.';
COMMENT ON COLUMN stg_polideportivos.latitud IS 'Latitud en grados decimales (EPSG:4326), obtenida de la geometría del origen.';
COMMENT ON COLUMN stg_polideportivos.fecha_corte IS 'Fecha a la que corresponden los datos, tomada de la columna fecha del archivo.';
COMMENT ON COLUMN stg_polideportivos.fecha_actualizacion_fuente IS 'Fecha en que CODE envió el conjunto por el formulario.';
COMMENT ON COLUMN stg_polideportivos.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';

COMMENT ON TABLE polideportivo_deportes IS 'Tabla puente entre polideportivos y los deportes que ofrecen. Se borra en cascada con el polideportivo al recargar un corte.';
COMMENT ON COLUMN polideportivo_deportes.polideportivo_id IS 'Polideportivo (stg_polideportivos.id).';
COMMENT ON COLUMN polideportivo_deportes.deporte_id IS 'Deporte que se ofrece en el polideportivo (cat_deportes.id).';

COMMENT ON VIEW vw_academias_deportivas IS 'Academias deportivas con deporte y tipo resueltos. Entidad y municipio provienen de cvegeo. Expone longitud y latitud.';
COMMENT ON VIEW vw_polideportivos IS 'Polideportivos con la lista de deportes agregada en texto. Entidad y municipio provienen de cvegeo. Expone longitud y latitud.';
COMMENT ON VIEW vw_polideportivo_deportes IS 'Una fila por polideportivo y deporte que ofrece, con nombres resueltos.';
