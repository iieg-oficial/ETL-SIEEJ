-- =============================================================================
-- V2__catalogs_enec.sql  |  Pipeline: enec
-- Catálogos de la Encuesta Nacional de Empresas Constructoras (ENEC, INEGI),
-- Serie 2018. Los ids los asigna PostgreSQL.
-- =============================================================================

CREATE TABLE IF NOT EXISTS cat_estatus (
    id      SERIAL PRIMARY KEY,
    estatus TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE cat_estatus IS
    'Catálogo del estatus de los datos publicados en la ENEC. Según el diccionario de datos del INEGI el estatus puede ser: Cifras Definitivas, Cifras Revisadas o Cifras Preliminares. Un periodo se publica primero como preliminar y el INEGI lo reemplaza en ediciones posteriores.';
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
    'Catálogo de las actividades de la construcción bajo estudio en la ENEC. A diferencia de EMEC, EMS y EMIM, el ZIP de la ENEC NO incluye carpeta de catálogos: este se deriva del campo DESCRIPCION_ACTIVIDAD que la fuente trae en línea con los datos del conjunto nacional. Cuatro entradas: 23 construcción, 236 edificación, 237 construcción de obras de ingeniería civil y 238 trabajos especializados para la construcción.';
COMMENT ON COLUMN cat_actividad.id IS
    'Identificador único de la actividad. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_actividad.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio (sector, subsector, rama o clase) dentro del clasificador SCIAN. Clave natural referenciada por stg_enec_nacional.';
COMMENT ON COLUMN cat_actividad.descripcion IS
    'Nombre de la actividad de la construcción (ej. Construcción, Edificación).';
