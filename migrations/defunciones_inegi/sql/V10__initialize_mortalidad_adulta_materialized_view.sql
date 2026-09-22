CREATE EXTENSION IF NOT EXISTS postgis;

ALTER FOREIGN TABLE cvegeo_municipalities
    ADD COLUMN IF NOT EXISTS geom_iieg geometry(MultiPolygon, 6368),
    ADD COLUMN IF NOT EXISTS geom_inegi geometry(MultiPolygon, 6368);

CREATE SERVER IF NOT EXISTS conapo_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    dbname 'conapo',
    host '${fdw_host}',
    port '${fdw_port}'
);

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
SERVER conapo_server
OPTIONS (
    user '${fdw_user}',
    password '${fdw_password}'
);

CREATE FOREIGN TABLE IF NOT EXISTS conapo_poblacion_mitad_anio (
    municipio_id INTEGER,
    entidad_id INTEGER,
    sexo_id INTEGER,
    anio INTEGER,
    pob_15_19 INTEGER,
    pob_20_24 INTEGER,
    pob_25_29 INTEGER,
    pob_30_34 INTEGER,
    pob_35_39 INTEGER,
    pob_40_44 INTEGER,
    pob_45_49 INTEGER,
    pob_50_54 INTEGER,
    pob_55_59 INTEGER
)
SERVER conapo_server
OPTIONS (schema_name 'public', table_name 'stg_poblacion_mitad_anio');
