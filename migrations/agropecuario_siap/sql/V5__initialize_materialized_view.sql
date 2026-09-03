CREATE EXTENSION IF NOT EXISTS postgis;

ALTER FOREIGN TABLE cvegeo_municipalities
    ADD COLUMN IF NOT EXISTS geom_iieg geometry(MultiPolygon, 6368),
    ADD COLUMN IF NOT EXISTS geom_inegi geometry(MultiPolygon, 6368);
