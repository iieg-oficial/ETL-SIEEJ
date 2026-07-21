-- ========================================================================
-- V7: Comentarios en vistas materializadas ASG IMSS
-- ========================================================================
-- Descripcion de cada vista y columnas para consumidores GIS (QGIS, Geoserver,
-- dashboards, etc.).
-- ========================================================================

-- --- trabajadores_asegurados ----------------------------------------------
COMMENT ON MATERIALIZED VIEW trabajadores_asegurados IS
'Puestos de trabajo afiliados al IMSS por municipio de Jalisco. Fuente: ASG IMSS.';

COMMENT ON COLUMN trabajadores_asegurados.fid IS
'Identificador unico de fila para herramientas GIS.';
COMMENT ON COLUMN trabajadores_asegurados.geom_iieg IS
'Geometria municipal (EPSG:6368) alineada por el IIEG.';
COMMENT ON COLUMN trabajadores_asegurados.geom_inegi IS
'Geometria municipal (EPSG:6368) original INEGI.';
COMMENT ON COLUMN trabajadores_asegurados.nombre IS
'Nombre oficial del municipio.';
COMMENT ON COLUMN trabajadores_asegurados.fecha IS
'Fecha de corte (primer dia del mes de la fuente IMSS).';
COMMENT ON COLUMN trabajadores_asegurados.clave_entidad IS
'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN trabajadores_asegurados.clave_municipio IS
'Clave INEGI del municipio (5 digitos, con entidad).';
COMMENT ON COLUMN trabajadores_asegurados.total IS
'Total de puestos de trabajo asegurados (ta).';
COMMENT ON COLUMN trabajadores_asegurados.total_mujeres IS
'Total de puestos de trabajo asegurados para mujeres (sexo=2).';
COMMENT ON COLUMN trabajadores_asegurados.total_hombres IS
'Total de puestos de trabajo asegurados para hombres (sexo=1).';
COMMENT ON COLUMN trabajadores_asegurados.total_no_binario IS
'Total de puestos de trabajo asegurados para personas no binarias (sexo=3).';
COMMENT ON COLUMN trabajadores_asegurados.porcentaje_mujeres IS
'Porcentaje de puestos de trabajo asegurados ocupados por mujeres.';
COMMENT ON COLUMN trabajadores_asegurados.porcentaje_hombres IS
'Porcentaje de puestos de trabajo asegurados ocupados por hombres.';

-- --- trabajadores_asegurados_hombres --------------------------------------
COMMENT ON MATERIALIZED VIEW trabajadores_asegurados_hombres IS
'Puestos de trabajo afiliados al IMSS ocupados por hombres por municipio de Jalisco.';

COMMENT ON COLUMN trabajadores_asegurados_hombres.fid IS
'Identificador unico de fila para herramientas GIS.';
COMMENT ON COLUMN trabajadores_asegurados_hombres.geom_iieg IS
'Geometria municipal (EPSG:6368) alineada por el IIEG.';
COMMENT ON COLUMN trabajadores_asegurados_hombres.geom_inegi IS
'Geometria municipal (EPSG:6368) original INEGI.';
COMMENT ON COLUMN trabajadores_asegurados_hombres.nombre IS
'Nombre oficial del municipio.';
COMMENT ON COLUMN trabajadores_asegurados_hombres.fecha IS
'Fecha de corte (primer dia del mes de la fuente IMSS).';
COMMENT ON COLUMN trabajadores_asegurados_hombres.clave_entidad IS
'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN trabajadores_asegurados_hombres.clave_municipio IS
'Clave INEGI del municipio (5 digitos, con entidad).';
COMMENT ON COLUMN trabajadores_asegurados_hombres.total_hombres IS
'Total de puestos de trabajo asegurados para hombres (sexo=1).';
COMMENT ON COLUMN trabajadores_asegurados_hombres.porcentaje_hombres IS
'Porcentaje de puestos de trabajo asegurados ocupados por hombres (siempre 100 en esta vista).';

-- --- trabajadores_asegurados_mujeres --------------------------------------
COMMENT ON MATERIALIZED VIEW trabajadores_asegurados_mujeres IS
'Puestos de trabajo afiliados al IMSS ocupados por mujeres por municipio de Jalisco.';

COMMENT ON COLUMN trabajadores_asegurados_mujeres.fid IS
'Identificador unico de fila para herramientas GIS.';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.geom_iieg IS
'Geometria municipal (EPSG:6368) alineada por el IIEG.';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.geom_inegi IS
'Geometria municipal (EPSG:6368) original INEGI.';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.nombre IS
'Nombre oficial del municipio.';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.fecha IS
'Fecha de corte (primer dia del mes de la fuente IMSS).';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.clave_entidad IS
'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.clave_municipio IS
'Clave INEGI del municipio (5 digitos, con entidad).';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.total_mujeres IS
'Total de puestos de trabajo asegurados para mujeres (sexo=2).';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.porcentaje_mujeres IS
'Porcentaje de puestos de trabajo asegurados ocupados por mujeres (siempre 100 en esta vista).';

-- --- brecha_salarial ------------------------------------------------------
COMMENT ON MATERIALIZED VIEW brecha_salarial IS
'Brecha salarial estimada entre hombres y mujeres en Jalisco a partir de la masa salarial (masa_sal_ta) y puestos con salario (ta_sal) del IMSS.';

COMMENT ON COLUMN brecha_salarial.fid IS
'Identificador unico de fila para herramientas GIS.';
COMMENT ON COLUMN brecha_salarial.geom_iieg IS
'Geometria municipal (EPSG:6368) alineada por el IIEG.';
COMMENT ON COLUMN brecha_salarial.geom_inegi IS
'Geometria municipal (EPSG:6368) original INEGI.';
COMMENT ON COLUMN brecha_salarial.nombre IS
'Nombre oficial del municipio.';
COMMENT ON COLUMN brecha_salarial.fecha IS
'Fecha de corte (primer dia del mes de la fuente IMSS).';
COMMENT ON COLUMN brecha_salarial.clave_entidad IS
'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN brecha_salarial.clave_municipio IS
'Clave INEGI del municipio (5 digitos, con entidad).';
COMMENT ON COLUMN brecha_salarial.brecha_salarial IS
'Porcentaje de diferencia del salario promedio diario de mujeres respecto al de hombres.';
COMMENT ON COLUMN brecha_salarial.salario_promedio_diario_mujeres IS
'Salario promedio diario estimado para mujeres (masa_sal_ta / (ta_sal * dias del mes de corte)).';
COMMENT ON COLUMN brecha_salarial.salario_promedio_diario_hombres IS
'Salario promedio diario estimado para hombres (masa_sal_ta / (ta_sal * dias del mes de corte)).';
