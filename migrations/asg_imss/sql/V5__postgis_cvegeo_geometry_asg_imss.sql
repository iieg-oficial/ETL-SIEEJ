-- ========================================================================
-- V5: PostGIS + geometrias en FDW cvegeo_municipalities
-- ========================================================================
-- Se agregan las columnas geom_iieg y geom_inegi (SRID 6368) a la
-- foreign table de cvegeo, necesarias para las vistas materializadas GIS.
-- ========================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

ALTER FOREIGN TABLE cvegeo_municipalities
    ADD COLUMN IF NOT EXISTS geom_iieg geometry(MultiPolygon, 6368),
    ADD COLUMN IF NOT EXISTS geom_inegi geometry(MultiPolygon, 6368);
