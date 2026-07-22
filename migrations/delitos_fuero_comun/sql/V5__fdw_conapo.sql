-- =============================================================================
-- V5__fdw_conapo.sql  |  Pipeline: delitos_fuero_comun
-- FDW hacia la BD conapo para obtener pob_mit_mun (población a mitad de año).
-- Solo expone las columnas necesarias para calcular la tasa por 100k hab.
-- conapo comparte host/user/password con cvegeo pero usa puerto distinto
-- (fdw_conapo_port, tipicamente 5434 en el mismo cluster).
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS conapo_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (
        dbname 'conapo',
        host   '${fdw_host}',
        port   '${fdw_conapo_port}'
    );

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
    SERVER conapo_server
    OPTIONS (
        user     '${fdw_user}',
        password '${fdw_password}'
    );

CREATE FOREIGN TABLE IF NOT EXISTS conapo_indicadores_demograficos (
    municipio_id INTEGER,
    entidad_id   INTEGER,
    anio         INTEGER,
    pob_mit_mun  INTEGER
)
SERVER conapo_server
OPTIONS (schema_name 'public', table_name 'stg_indicadores_demograficos');
