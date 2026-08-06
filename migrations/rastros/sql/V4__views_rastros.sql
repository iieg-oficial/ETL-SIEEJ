-- =============================================================================
-- V4__views_rastros.sql  |  Pipeline: rastros
-- vw_rastros          -> las 32 entidades federativas
-- vw_rastros_jalisco  -> solo Jalisco (cve_ent = 14)
-- =============================================================================

CREATE OR REPLACE VIEW vw_rastros AS
SELECT
    sr.fecha,
    e.nom_ent                       AS entidad,
    ceg.especie_ganadera,
    sr.numero_cabezas,
    ecbz.estatus                    AS estatus_cabeza,
    sr.produccion_carne,
    eprod.estatus                   AS estatus_produccion,
    sr.vproduccion,
    evprod.estatus                  AS estatus_vproduccion,
    tc.tipo_cifra,
    sr.fecha_actualizacion
FROM stg_rastros sr
LEFT JOIN cvegeo_states e            ON e.cve_ent    = sr.entidad_id
LEFT JOIN cat_especies_ganaderas ceg ON ceg.id       = sr.especie_ganadera_id
LEFT JOIN cat_estatus ecbz           ON ecbz.id      = sr.estatus_cabeza_id
LEFT JOIN cat_estatus eprod          ON eprod.id     = sr.estatus_produccion_id
LEFT JOIN cat_estatus evprod         ON evprod.id    = sr.estatus_vproduccion_id
LEFT JOIN cat_tipo_cifra tc          ON tc.id        = sr.tipo_cifra_id;

COMMENT ON VIEW vw_rastros IS
    'Vista desnormalizada de la Estadística de Sacrificio de Ganado en Rastros Municipales (ESGRM) del INEGI para las 32 entidades federativas, con periodicidad mensual desde 2008.';
COMMENT ON COLUMN vw_rastros.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_rastros.entidad IS
    'Nombre de la entidad federativa a la que corresponden las cifras.';
COMMENT ON COLUMN vw_rastros.especie_ganadera IS
    'Especie ganadera sacrificada (ej. Ganado bovino, Ganado porcino).';
COMMENT ON COLUMN vw_rastros.numero_cabezas IS
    'Número de animales vivos que ingresan al rastro para su matanza, destinados a la producción de carne apta para consumo humano.';
COMMENT ON COLUMN vw_rastros.estatus_cabeza IS
    'Disponibilidad de la cifra de numero_cabezas.';
COMMENT ON COLUMN vw_rastros.produccion_carne IS
    'Volumen de carne en canal obtenida del sacrificio del ganado, en TONELADAS.';
COMMENT ON COLUMN vw_rastros.estatus_produccion IS
    'Disponibilidad de la cifra de produccion_carne.';
COMMENT ON COLUMN vw_rastros.vproduccion IS
    'Valor de la carne en canal producida, en MILES DE PESOS.';
COMMENT ON COLUMN vw_rastros.estatus_vproduccion IS
    'Disponibilidad de la cifra de vproduccion.';
COMMENT ON COLUMN vw_rastros.tipo_cifra IS
    'Indica si el registro corresponde a cifras definitivas o preliminares.';
COMMENT ON COLUMN vw_rastros.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';


CREATE OR REPLACE VIEW vw_rastros_jalisco AS
SELECT
    sr.fecha,
    e.nom_ent                       AS entidad,
    ceg.especie_ganadera,
    sr.numero_cabezas,
    ecbz.estatus                    AS estatus_cabeza,
    sr.produccion_carne,
    eprod.estatus                   AS estatus_produccion,
    sr.vproduccion,
    evprod.estatus                  AS estatus_vproduccion,
    tc.tipo_cifra,
    sr.fecha_actualizacion
FROM stg_rastros sr
LEFT JOIN cvegeo_states e            ON e.cve_ent    = sr.entidad_id
LEFT JOIN cat_especies_ganaderas ceg ON ceg.id       = sr.especie_ganadera_id
LEFT JOIN cat_estatus ecbz           ON ecbz.id      = sr.estatus_cabeza_id
LEFT JOIN cat_estatus eprod          ON eprod.id     = sr.estatus_produccion_id
LEFT JOIN cat_estatus evprod         ON evprod.id    = sr.estatus_vproduccion_id
LEFT JOIN cat_tipo_cifra tc          ON tc.id        = sr.tipo_cifra_id
WHERE sr.entidad_id = 14;

COMMENT ON VIEW vw_rastros_jalisco IS
    'Misma información que vw_rastros, acotada a Jalisco (clave de entidad 14).';
COMMENT ON COLUMN vw_rastros_jalisco.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_rastros_jalisco.entidad IS
    'Nombre de la entidad federativa; siempre Jalisco en esta vista.';
COMMENT ON COLUMN vw_rastros_jalisco.especie_ganadera IS
    'Especie ganadera sacrificada (ej. Ganado bovino, Ganado porcino).';
COMMENT ON COLUMN vw_rastros_jalisco.numero_cabezas IS
    'Número de animales vivos que ingresan al rastro para su matanza, destinados a la producción de carne apta para consumo humano.';
COMMENT ON COLUMN vw_rastros_jalisco.estatus_cabeza IS
    'Disponibilidad de la cifra de numero_cabezas.';
COMMENT ON COLUMN vw_rastros_jalisco.produccion_carne IS
    'Volumen de carne en canal obtenida del sacrificio del ganado, en TONELADAS.';
COMMENT ON COLUMN vw_rastros_jalisco.estatus_produccion IS
    'Disponibilidad de la cifra de produccion_carne.';
COMMENT ON COLUMN vw_rastros_jalisco.vproduccion IS
    'Valor de la carne en canal producida, en MILES DE PESOS.';
COMMENT ON COLUMN vw_rastros_jalisco.estatus_vproduccion IS
    'Disponibilidad de la cifra de vproduccion.';
COMMENT ON COLUMN vw_rastros_jalisco.tipo_cifra IS
    'Indica si el registro corresponde a cifras definitivas o preliminares.';
COMMENT ON COLUMN vw_rastros_jalisco.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';
