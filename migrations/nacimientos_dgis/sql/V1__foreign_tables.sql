CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SERVER IF NOT EXISTS cvegeo_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    dbname '${fdw_dbname}',
    host '${fdw_host}',
    port '${fdw_port}'
);

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
SERVER cvegeo_server
OPTIONS (
    user '${fdw_user}',
    password '${fdw_password}'
);

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_states (
    id      INTEGER,
    cve_ent INTEGER,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_states');

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id         INTEGER,
    cvegeo     INTEGER,
    cve_ent    INTEGER,
    cve_mun    INTEGER,
    nomgeo     VARCHAR,
    nom_ent    VARCHAR,
    geom_iieg  geometry(MultiPolygon, 6368),
    geom_inegi geometry(MultiPolygon, 6368)
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

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

CREATE FOREIGN TABLE IF NOT EXISTS conapo_poblacion (
    municipio_id  INTEGER,
    sexo_id       INTEGER,
    anio          INTEGER,
    pob_10_14     INTEGER,
    pob_15_19     INTEGER,
    pob_20_24     INTEGER,
    pob_25_29     INTEGER,
    pob_30_34     INTEGER,
    pob_35_39     INTEGER,
    pob_40_44     INTEGER,
    pob_45_49     INTEGER
)
SERVER conapo_server
OPTIONS (schema_name 'public', table_name 'stg_poblacion_mitad_anio');
