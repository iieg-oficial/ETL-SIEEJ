-- ========================================================================
-- V8: Indices espaciales (GiST) sobre las vistas materializadas GIS
-- ========================================================================
-- Mejora el rendimiento de filtros y renderizado en QGIS, GeoServer y otros
-- consumidores GIS. Las vistas de este pipeline son de tamano pequeno
-- (municipios de Jalisco), pero los indices siguen la convencion del repo.
-- ========================================================================

CREATE INDEX IF NOT EXISTS idx_trabajadores_asegurados_geom_iieg
    ON trabajadores_asegurados USING GIST (geom_iieg);

CREATE INDEX IF NOT EXISTS idx_trabajadores_asegurados_hombres_geom_iieg
    ON trabajadores_asegurados_hombres USING GIST (geom_iieg);

CREATE INDEX IF NOT EXISTS idx_trabajadores_asegurados_mujeres_geom_iieg
    ON trabajadores_asegurados_mujeres USING GIST (geom_iieg);

CREATE INDEX IF NOT EXISTS idx_brecha_salarial_geom_iieg
    ON brecha_salarial USING GIST (geom_iieg);

CREATE INDEX IF NOT EXISTS idx_trabajadores_asegurados_fecha
    ON trabajadores_asegurados (fecha);

CREATE INDEX IF NOT EXISTS idx_trabajadores_asegurados_hombres_fecha
    ON trabajadores_asegurados_hombres (fecha);

CREATE INDEX IF NOT EXISTS idx_trabajadores_asegurados_mujeres_fecha
    ON trabajadores_asegurados_mujeres (fecha);

CREATE INDEX IF NOT EXISTS idx_brecha_salarial_fecha
    ON brecha_salarial (fecha);
