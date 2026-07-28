-- =============================================================================
-- V2__catalogs_rastros.sql  |  Pipeline: rastros
-- Catálogos de la Estadística de Sacrificio de Ganado en Rastros Municipales
-- (ESGRM, INEGI). Los ids los asigna PostgreSQL; el texto es la clave natural.
-- =============================================================================

CREATE TABLE IF NOT EXISTS cat_estatus (
    id      SERIAL PRIMARY KEY,
    estatus TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE cat_estatus IS
    'Catálogo del estatus de disponibilidad de una cifra en la ESGRM. Valores posibles según el diccionario de datos del INEGI: Disponible (cumple el principio de confidencialidad de la LSNIEG), No disponible (la información no se genera o está en proceso), No aplicable (cruces conceptuales incompatibles o cálculos no procedentes), No significativo (número distinto de cero que por redondeo se expresaría como tal) y Confidencial (no publicable por el principio de confidencialidad de la LSNIEG).';
COMMENT ON COLUMN cat_estatus.id IS
    'Identificador único del estatus. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_estatus.estatus IS
    'Descripción del estatus de la cifra (ej. Disponible, No significativo).';


CREATE TABLE IF NOT EXISTS cat_especies_ganaderas (
    id               SERIAL PRIMARY KEY,
    especie_ganadera TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE cat_especies_ganaderas IS
    'Catálogo de especies ganaderas sacrificadas en rastros municipales. Clasificación de los animales que agrupa a los individuos con rasgos comunes entre sí dentro de una misma categoría.';
COMMENT ON COLUMN cat_especies_ganaderas.id IS
    'Identificador único de la especie ganadera. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_especies_ganaderas.especie_ganadera IS
    'Nombre de la especie ganadera (ej. Ganado bovino, Ganado porcino, Ganado ovino, Ganado caprino).';


CREATE TABLE IF NOT EXISTS cat_tipo_cifra (
    id          SERIAL PRIMARY KEY,
    tipo_cifra  TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE cat_tipo_cifra IS
    'Catálogo del estatus de las cifras conforme a los Lineamientos de Cambios a la información divulgada en las publicaciones estadísticas y geográficas del INEGI.';
COMMENT ON COLUMN cat_tipo_cifra.id IS
    'Identificador único del tipo de cifra. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN cat_tipo_cifra.tipo_cifra IS
    'Tipo de cifra publicada: Cifras Definitivas o Cifras Preliminares.';
