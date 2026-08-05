-- =============================================================================
-- V2__catalogs_ems.sql  |  Pipeline: ems
-- Catálogos de la Encuesta Mensual de Servicios (EMS, INEGI), Serie 2018.
-- Los ids los asigna PostgreSQL.
-- =============================================================================

CREATE TABLE IF NOT EXISTS cat_estatus (
    id      SERIAL PRIMARY KEY,
    estatus TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE cat_estatus IS
    'Catálogo del estatus de los datos publicados en la EMS. Según el diccionario de datos del INEGI el estatus puede ser: Cifras Definitivas, Cifras Revisadas o Cifras Preliminares. Un periodo se publica primero como preliminar y el INEGI lo reemplaza por cifras revisadas o definitivas en ediciones posteriores.';
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
    'Catálogo de los sectores de servicios privados no financieros que cubre la EMS, publicado por el INEGI en catalogos/tc_actividad.csv. Son los siete sectores del clasificador SCIAN 2018 bajo estudio: 51 información en medios masivos, 53 servicios inmobiliarios y de alquiler, 54 servicios profesionales, 61 servicios educativos, 62 servicios de salud y asistencia social, 71 esparcimiento y 72 alojamiento y preparación de alimentos.';
COMMENT ON COLUMN cat_actividad.id IS
    'Identificador único de la actividad. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_actividad.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio (sector, subsector, rama o clase). El valor que se presenta es un código dentro del clasificador SCIAN 2018. Clave natural referenciada por stg_ems.';
COMMENT ON COLUMN cat_actividad.descripcion IS
    'Nombre del sector de servicios según el clasificador SCIAN 2018 (ej. Servicios educativos).';
