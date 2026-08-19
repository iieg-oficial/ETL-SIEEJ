-- =============================================================================
-- V2__catalogs_emim.sql  |  Pipeline: emim
-- Catálogos de la Encuesta Mensual de la Industria Manufacturera (EMIM, INEGI),
-- Serie 2018. Los ids los asigna PostgreSQL.
-- =============================================================================

CREATE TABLE IF NOT EXISTS cat_estatus (
    id      SERIAL PRIMARY KEY,
    estatus TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE cat_estatus IS
    'Catálogo del estatus de los datos publicados en la EMIM. Según el diccionario de datos del INEGI el estatus puede ser: Cifras preliminares, Cifras revisadas, Cifras definitivas, y cifras ajustadas y/o corregidas. Un periodo se publica primero como preliminar y el INEGI lo reemplaza en ediciones posteriores.';
COMMENT ON COLUMN cat_estatus.id IS
    'Identificador único del estatus. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_estatus.estatus IS
    'Descripción del estatus de los datos (Cifras definitivas, Cifras revisadas o Cifras preliminares).';


CREATE TABLE IF NOT EXISTS cat_actividad (
    id               SERIAL PRIMARY KEY,
    codigo_actividad TEXT   NOT NULL UNIQUE,
    descripcion      TEXT   NOT NULL
);

COMMENT ON TABLE cat_actividad IS
    'Catálogo de las actividades manufactureras del clasificador SCIAN 2018 que publica el INEGI en catalogos/tc_actividad.csv. Contiene los 314 niveles del clasificador (sector, subsector, rama y clase); el conjunto por entidad federativa solo desglosa el sector 31-33 y sus 21 subsectores.';
COMMENT ON COLUMN cat_actividad.id IS
    'Identificador único de la actividad. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_actividad.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio (sector, subsector, rama o clase). El valor que se presenta es un código dentro del clasificador SCIAN 2018. Es TEXTO y no un número: el sector manufacturero se publica como el rango "31-33". Clave natural referenciada por stg_emim.';
COMMENT ON COLUMN cat_actividad.descripcion IS
    'Nombre de la actividad manufacturera según el clasificador SCIAN 2018 (ej. Industria alimentaria).';
