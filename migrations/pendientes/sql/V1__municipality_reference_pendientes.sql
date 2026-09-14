CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS cvegeo_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (dbname '${fdw_dbname}', host '${fdw_host}', port '${fdw_port}');

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
SERVER cvegeo_server
OPTIONS (user '${fdw_user}', password '${fdw_password}');

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id INTEGER,
    cvegeo INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo VARCHAR,
    nom_ent VARCHAR,
    geom_iieg geometry(MultiPolygon, 6368),
    geom_inegi geometry(MultiPolygon, 6368)
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

DO $$
DECLARE
    jalisco_count INTEGER;
    distinct_municipalities INTEGER;
BEGIN
    SELECT count(*), count(DISTINCT cve_mun)
    INTO jalisco_count, distinct_municipalities
    FROM cvegeo_municipalities
    WHERE cve_ent = 14;

    IF jalisco_count <> 125 OR distinct_municipalities <> 125 THEN
        RAISE EXCEPTION 'Invalid cvegeo Jalisco catalog: rows=%, distinct=%',
            jalisco_count, distinct_municipalities;
    END IF;
    IF EXISTS (
        SELECT 1 FROM cvegeo_municipalities
        WHERE cve_ent = 14 AND (cvegeo IS NULL OR cvegeo <> 14000 + cve_mun)
    ) THEN
        RAISE EXCEPTION 'Invalid cvegeo/cve_mun identity for Jalisco';
    END IF;
END
$$;
