-- =============================================================================
-- V2__catalogs_emec.sql  |  Pipeline: emec
-- Catálogos de la Encuesta Mensual sobre Empresas Comerciales (EMEC, INEGI),
-- Serie 2018. Los ids los asigna PostgreSQL.
-- =============================================================================

CREATE TABLE IF NOT EXISTS cat_estatus (
    id      SERIAL PRIMARY KEY,
    estatus TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE cat_estatus IS
    'Catálogo del estatus de los datos publicados en la EMEC. Según el diccionario de datos del INEGI el estatus puede ser: Cifras Definitivas, Cifras Revisadas o Cifras Preliminares. Un periodo se publica primero como preliminar y el INEGI lo reemplaza por cifras revisadas o definitivas en ediciones posteriores.';
COMMENT ON COLUMN cat_estatus.id IS
    'Identificador único del estatus. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_estatus.estatus IS
    'Descripción del estatus de los datos (Cifras definitivas, Cifras revisadas o Cifras preliminares).';


CREATE TABLE IF NOT EXISTS cat_actividad (
    id               SERIAL  PRIMARY KEY,
    codigo_actividad INTEGER NOT NULL UNIQUE,
    descripcion      TEXT    NOT NULL
);

COMMENT ON TABLE cat_actividad IS
    'Catálogo de las actividades económicas bajo estudio en la EMEC (sector, subsector, rama o clase del comercio al por mayor y al por menor), publicado por el INEGI en catalogos/tc_actividad.csv. Contiene todas las actividades del programa; el conjunto por entidad federativa solo desglosa los sectores 43 y 46.';
COMMENT ON COLUMN cat_actividad.id IS
    'Identificador único de la actividad. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_actividad.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio (sector, subsector, rama o clase). El valor que se presenta es un código dentro del clasificador SCIAN 2013. Clave natural referenciada por stg_emec.';
COMMENT ON COLUMN cat_actividad.descripcion IS
    'Nombre de la actividad económica según el clasificador SCIAN 2013 (ej. Comercio al por mayor, Comercio al por menor).';
