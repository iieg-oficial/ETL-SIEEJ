CREATE OR REPLACE VIEW vw_indice_shf_vivienda_global AS
SELECT
    s.nombre AS serie,
    s.tipo,
    g.fecha,
    g.anio,
    g.trimestre,
    g.indice
FROM stg_indice_shf_vivienda_global g
JOIN cat_serie_global s ON s.id = g.serie_global_id;

COMMENT ON VIEW vw_indice_shf_vivienda_global IS
    'Índice SHF de precios de la vivienda de las series sin desglose geográfico, con el nombre y el tipo de serie '
    'resueltos. Año base 2017 = 100.';
COMMENT ON COLUMN vw_indice_shf_vivienda_global.serie IS
    'Nombre de la serie tal como lo publica SHF.';
COMMENT ON COLUMN vw_indice_shf_vivienda_global.tipo IS
    'Concepto que agrupa a la serie: nacional, condicion, tipo_vivienda, segmento o zona_metropolitana.';
COMMENT ON COLUMN vw_indice_shf_vivienda_global.fecha IS
    'Primer día del trimestre de referencia.';
COMMENT ON COLUMN vw_indice_shf_vivienda_global.anio IS
    'Año de referencia de la medición.';
COMMENT ON COLUMN vw_indice_shf_vivienda_global.trimestre IS
    'Trimestre de referencia de la medición (1 a 4).';
COMMENT ON COLUMN vw_indice_shf_vivienda_global.indice IS
    'Valor del índice, con año base 2017 = 100.';


CREATE OR REPLACE VIEW vw_indice_shf_vivienda_estatal AS
SELECT
    e.cve_ent,
    c.nom_ent,
    e.fecha,
    e.anio,
    e.trimestre,
    e.indice
FROM stg_indice_shf_vivienda_estatal e
JOIN cvegeo_states c ON c.cve_ent = e.cve_ent;

COMMENT ON VIEW vw_indice_shf_vivienda_estatal IS
    'Índice SHF de precios de la vivienda por entidad federativa, con el nombre oficial del INEGI resuelto. '
    'Año base 2017 = 100.';
COMMENT ON COLUMN vw_indice_shf_vivienda_estatal.cve_ent IS
    'Clave de la entidad federativa (1 a 32) del INEGI.';
COMMENT ON COLUMN vw_indice_shf_vivienda_estatal.nom_ent IS
    'Nombre oficial de la entidad federativa.';
COMMENT ON COLUMN vw_indice_shf_vivienda_estatal.fecha IS
    'Primer día del trimestre de referencia.';
COMMENT ON COLUMN vw_indice_shf_vivienda_estatal.anio IS
    'Año de referencia de la medición.';
COMMENT ON COLUMN vw_indice_shf_vivienda_estatal.trimestre IS
    'Trimestre de referencia de la medición (1 a 4).';
COMMENT ON COLUMN vw_indice_shf_vivienda_estatal.indice IS
    'Valor del índice, con año base 2017 = 100.';


CREATE OR REPLACE VIEW vw_indice_shf_vivienda_municipal AS
SELECT
    m.cvegeo,
    c.nomgeo,
    m.cve_ent,
    c.nom_ent,
    m.fecha,
    m.anio,
    m.trimestre,
    m.indice
FROM stg_indice_shf_vivienda_municipal m
JOIN cvegeo_municipalities c ON c.cvegeo = m.cvegeo;

COMMENT ON VIEW vw_indice_shf_vivienda_municipal IS
    'Índice SHF de precios de la vivienda de los municipios que publica SHF, con los nombres oficiales del INEGI '
    'resueltos. Año base 2017 = 100.';
COMMENT ON COLUMN vw_indice_shf_vivienda_municipal.cvegeo IS
    'Clave geoestadística del municipio (cve_ent * 1000 + cve_mun).';
COMMENT ON COLUMN vw_indice_shf_vivienda_municipal.nomgeo IS
    'Nombre oficial del municipio.';
COMMENT ON COLUMN vw_indice_shf_vivienda_municipal.cve_ent IS
    'Clave de la entidad federativa a la que pertenece el municipio.';
COMMENT ON COLUMN vw_indice_shf_vivienda_municipal.nom_ent IS
    'Nombre oficial de la entidad federativa.';
COMMENT ON COLUMN vw_indice_shf_vivienda_municipal.fecha IS
    'Primer día del trimestre de referencia.';
COMMENT ON COLUMN vw_indice_shf_vivienda_municipal.anio IS
    'Año de referencia de la medición.';
COMMENT ON COLUMN vw_indice_shf_vivienda_municipal.trimestre IS
    'Trimestre de referencia de la medición (1 a 4).';
COMMENT ON COLUMN vw_indice_shf_vivienda_municipal.indice IS
    'Valor del índice, con año base 2017 = 100.';


CREATE OR REPLACE VIEW vw_indice_shf_vivienda_jalisco AS
SELECT
    'municipal' AS nivel,
    m.nomgeo AS serie,
    m.cvegeo,
    m.fecha,
    m.anio,
    m.trimestre,
    m.indice
FROM vw_indice_shf_vivienda_municipal m
WHERE m.cve_ent = 14
UNION ALL
SELECT
    'estatal' AS nivel,
    e.nom_ent AS serie,
    NULL::INTEGER AS cvegeo,
    e.fecha,
    e.anio,
    e.trimestre,
    e.indice
FROM vw_indice_shf_vivienda_estatal e
WHERE e.cve_ent = 14
UNION ALL
SELECT
    'global' AS nivel,
    g.serie,
    NULL::INTEGER AS cvegeo,
    g.fecha,
    g.anio,
    g.trimestre,
    g.indice
FROM vw_indice_shf_vivienda_global g
WHERE g.serie = 'ZM Guadalajara';

COMMENT ON VIEW vw_indice_shf_vivienda_jalisco IS
    'Corte de Jalisco: los municipios que SHF publica del estado (Guadalajara, Zapopan, San Pedro Tlaquepaque y '
    'Tlajomulco de Zúñiga), la entidad y la serie de la Zona Metropolitana de Guadalajara, apiladas en una sola '
    'serie de tiempo comparable. Año base 2017 = 100.';
COMMENT ON COLUMN vw_indice_shf_vivienda_jalisco.nivel IS
    'Nivel de desagregación de la fila: municipal, estatal o global.';
COMMENT ON COLUMN vw_indice_shf_vivienda_jalisco.serie IS
    'Nombre del municipio, de la entidad o de la serie global, según el nivel.';
COMMENT ON COLUMN vw_indice_shf_vivienda_jalisco.cvegeo IS
    'Clave geoestadística del municipio. Nula en los niveles estatal y global, que no desagregan a municipio.';
COMMENT ON COLUMN vw_indice_shf_vivienda_jalisco.fecha IS
    'Primer día del trimestre de referencia.';
COMMENT ON COLUMN vw_indice_shf_vivienda_jalisco.anio IS
    'Año de referencia de la medición.';
COMMENT ON COLUMN vw_indice_shf_vivienda_jalisco.trimestre IS
    'Trimestre de referencia de la medición (1 a 4).';
COMMENT ON COLUMN vw_indice_shf_vivienda_jalisco.indice IS
    'Valor del índice, con año base 2017 = 100.';
