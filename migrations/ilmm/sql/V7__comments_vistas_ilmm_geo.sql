-- ---------------------------------------------------------------------------
-- Comentarios de columna para vw_ocupacion_informal y vw_tasa_desocupacion
-- tras homologar su estructura con economia.* (proxmox) en V6.
-- ---------------------------------------------------------------------------
COMMENT ON COLUMN vw_ocupacion_informal.fid IS 'Identificador secuencial de fila (surrogate key), homólogo al fid de la capa GIS en proxmox. No es estable entre refrescos de la vista.';
COMMENT ON COLUMN vw_ocupacion_informal.geom_iieg IS 'Geometría del municipio (polígono IIEG), tomada de cvegeo_municipalities.';
COMMENT ON COLUMN vw_ocupacion_informal.geom_inegi IS 'Geometría del municipio (polígono INEGI), tomada de cvegeo_municipalities.';
COMMENT ON COLUMN vw_ocupacion_informal.nombre IS 'Nombre oficial del municipio (cvegeo_municipalities.nomgeo).';
COMMENT ON COLUMN vw_ocupacion_informal.fecha IS 'Fecha de referencia del trimestre (primer día del trimestre).';
COMMENT ON COLUMN vw_ocupacion_informal.clave_entidad IS 'Clave INEGI de 2 dígitos de la entidad federativa (cvegeo_municipalities.cve_ent).';
COMMENT ON COLUMN vw_ocupacion_informal.clave_municipio IS 'Clave INEGI de 5 dígitos del municipio.';
COMMENT ON COLUMN vw_ocupacion_informal.valor IS 'Porcentaje de ocupación en el sector informal (dato puntual, estimador_id=1).';
COMMENT ON COLUMN vw_ocupacion_informal.error_estandar IS 'Error estándar del porcentaje de ocupación informal (estimador_id=2). Usar para construir intervalos de confianza.';

COMMENT ON COLUMN vw_tasa_desocupacion.fid IS 'Identificador secuencial de fila (surrogate key), homólogo al fid de la capa GIS en proxmox. No es estable entre refrescos de la vista.';
COMMENT ON COLUMN vw_tasa_desocupacion.geom_iieg IS 'Geometría del municipio (polígono IIEG), tomada de cvegeo_municipalities.';
COMMENT ON COLUMN vw_tasa_desocupacion.geom_inegi IS 'Geometría del municipio (polígono INEGI), tomada de cvegeo_municipalities.';
COMMENT ON COLUMN vw_tasa_desocupacion.nombre IS 'Nombre oficial del municipio (cvegeo_municipalities.nomgeo).';
COMMENT ON COLUMN vw_tasa_desocupacion.fecha IS 'Fecha de referencia del trimestre (primer día del trimestre).';
COMMENT ON COLUMN vw_tasa_desocupacion.clave_entidad IS 'Clave INEGI de 2 dígitos de la entidad federativa (cvegeo_municipalities.cve_ent).';
COMMENT ON COLUMN vw_tasa_desocupacion.clave_municipio IS 'Clave INEGI de 5 dígitos del municipio.';
COMMENT ON COLUMN vw_tasa_desocupacion.valor IS 'Tasa de desocupación en porcentaje (dato puntual, estimador_id=1).';
COMMENT ON COLUMN vw_tasa_desocupacion.error_estandar IS 'Error estándar de la tasa de desocupación (estimador_id=2). Usar para construir intervalos de confianza.';
