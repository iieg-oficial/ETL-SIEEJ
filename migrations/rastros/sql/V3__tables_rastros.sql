-- =============================================================================
-- V3__tables_rastros.sql  |  Pipeline: rastros
-- Tabla staging de la Estadística de Sacrificio de Ganado en Rastros
-- Municipales (ESGRM), información mensual, cobertura estatal.
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_rastros (
    id                      SERIAL PRIMARY KEY,
    fecha                   DATE    NOT NULL,
    entidad_id              INTEGER NOT NULL,
    especie_ganadera_id     INTEGER NOT NULL REFERENCES cat_especies_ganaderas(id),
    numero_cabezas          INTEGER,
    estatus_cabeza_id       INTEGER REFERENCES cat_estatus(id),
    produccion_carne        INTEGER,
    estatus_produccion_id   INTEGER REFERENCES cat_estatus(id),
    vproduccion             INTEGER,
    estatus_vproduccion_id  INTEGER REFERENCES cat_estatus(id),
    tipo_cifra_id           INTEGER REFERENCES cat_tipo_cifra(id),
    fecha_actualizacion     DATE    NOT NULL,
    CONSTRAINT uq_stg_rastros UNIQUE (fecha, entidad_id, especie_ganadera_id)
);

COMMENT ON TABLE stg_rastros IS
    'Estadística de Sacrificio de Ganado en Rastros Municipales (ESGRM) del INEGI, información mensual desde 2008. Reporta la producción de carne en canal destinada al consumo humano que aportan los rastros administrados por los gobiernos municipales del país. La cobertura geográfica de la fuente es ESTATAL: el nombre "rastros municipales" describe al administrador del establecimiento, no al nivel de desglose publicado. Grano: un registro por periodo, entidad federativa y especie ganadera.';

COMMENT ON COLUMN stg_rastros.id IS
    'Identificador único del registro. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN stg_rastros.fecha IS
    'Primer día del mes de referencia de la información, derivado de los campos ANIO e ID_MES de la fuente.';
COMMENT ON COLUMN stg_rastros.entidad_id IS
    'Clave de la entidad federativa (CVEGEO de la fuente, 1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI. Ref. cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_rastros.especie_ganadera_id IS
    'FK a cat_especies_ganaderas; especie ganadera sacrificada.';
COMMENT ON COLUMN stg_rastros.numero_cabezas IS
    'Número de animales vivos que ingresan al rastro para su matanza, destinados a la producción de carne apta para consumo humano. No se hace distinción del origen del ganado ni del lugar donde inició o finalizó el proceso de engorda.';
COMMENT ON COLUMN stg_rastros.estatus_cabeza_id IS
    'FK a cat_estatus; disponibilidad de la cifra de numero_cabezas.';
COMMENT ON COLUMN stg_rastros.produccion_carne IS
    'Volumen de carne en canal obtenida a partir del sacrificio del ganado introducido al rastro, en TONELADAS. Considera el peso total de las canales sin importar el origen de los animales. Por redondeo, la suma de los parciales puede no coincidir con el total nacional.';
COMMENT ON COLUMN stg_rastros.estatus_produccion_id IS
    'FK a cat_estatus; disponibilidad de la cifra de produccion_carne.';
COMMENT ON COLUMN stg_rastros.vproduccion IS
    'Valor de la carne en canal producida en los rastros municipales, en MILES DE PESOS. Por redondeo, la suma de los parciales puede no coincidir con el total nacional.';
COMMENT ON COLUMN stg_rastros.estatus_vproduccion_id IS
    'FK a cat_estatus; disponibilidad de la cifra de vproduccion.';
COMMENT ON COLUMN stg_rastros.tipo_cifra_id IS
    'FK a cat_tipo_cifra; indica si el registro corresponde a cifras definitivas o preliminares.';
COMMENT ON COLUMN stg_rastros.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base. No proviene de la fuente.';
