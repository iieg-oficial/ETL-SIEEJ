CREATE OR REPLACE VIEW vw_cuadernillos_edafologia_estadistica_detalle AS
WITH fragmentos AS (
    SELECT
        m.nomgeo AS nombre,
        g.descripcion AS categoria,
        f.superficie_ha,
        ST_Area(m.geom_iieg) / 10000 AS superficie_municipio_ha
    FROM edafologia_fragmentos_municipales AS f
    JOIN edafologias AS e
        ON e.id = f.edafologia_id
    JOIN grupos_edafologicos AS g
        ON g.id = e.grupo_edafologico_id
    JOIN fuentes_limites_municipales AS l
        ON l.id = f.fuente_limite_municipal_id
    JOIN cvegeo_municipalities AS m
        ON f.municipio_id = m.cve_mun
        AND m.cve_ent = 14
    WHERE l.clave = 'iieg'
),
por_categoria AS (
    SELECT
        nombre,
        categoria,
        ROUND(SUM(superficie_ha)::NUMERIC, 2)::DOUBLE PRECISION AS superficie_ha,
        ROUND(MIN(superficie_municipio_ha)::NUMERIC, 2)::DOUBLE PRECISION AS superficie_municipio_ha,
        ROUND((100 * SUM(superficie_ha) / MIN(superficie_municipio_ha))::NUMERIC, 2)::DOUBLE PRECISION AS porcentaje
    FROM fragmentos
    GROUP BY nombre, categoria
)
SELECT
    nombre,
    categoria,
    superficie_ha,
    superficie_municipio_ha,
    porcentaje,
    ROW_NUMBER() OVER (PARTITION BY nombre ORDER BY superficie_ha DESC, categoria)::BIGINT AS orden_pct,
    (ROW_NUMBER() OVER (PARTITION BY nombre ORDER BY superficie_ha DESC, categoria) = 1)::INTEGER::BIGINT AS es_dominante
FROM por_categoria;

CREATE OR REPLACE VIEW vw_cuadernillos_edafologia_cobertura_municipal AS
WITH fragmentos AS (
    SELECT
        m.nomgeo AS nombre,
        f.superficie_ha,
        ST_Area(m.geom_iieg) / 10000 AS superficie_municipio_ha
    FROM edafologia_fragmentos_municipales AS f
    JOIN fuentes_limites_municipales AS l
        ON l.id = f.fuente_limite_municipal_id
    JOIN cvegeo_municipalities AS m
        ON f.municipio_id = m.cve_mun
        AND m.cve_ent = 14
    WHERE l.clave = 'iieg'
)
SELECT
    nombre,
    ROUND(MIN(superficie_municipio_ha)::NUMERIC, 2)::DOUBLE PRECISION AS superficie_municipio_ha,
    ROUND(SUM(superficie_ha)::NUMERIC, 2)::DOUBLE PRECISION AS superficie_tematica_total_ha,
    ROUND((100 * SUM(superficie_ha) / MIN(superficie_municipio_ha))::NUMERIC, 2)::DOUBLE PRECISION
        AS pct_cobertura_tematica
FROM fragmentos
GROUP BY nombre;

CREATE OR REPLACE VIEW vw_cuadernillos_edafologia_estadistica_resumen AS
SELECT
    c.nombre,
    d.categoria AS max_categoria,
    d.superficie_ha AS max_categoria_ha,
    d.porcentaje AS max_categoria_pct,
    c.superficie_municipio_ha,
    c.superficie_tematica_total_ha,
    c.pct_cobertura_tematica
FROM vw_cuadernillos_edafologia_cobertura_municipal AS c
JOIN vw_cuadernillos_edafologia_estadistica_detalle AS d
    ON d.nombre = c.nombre
    AND d.es_dominante = 1;

CREATE OR REPLACE VIEW vw_cuadernillos_edafologia_variables_texto AS
WITH demas AS (
    SELECT
        nombre,
        STRING_AGG(categoria, ', ' ORDER BY orden_pct) AS ed_demas,
        ROUND(SUM(porcentaje)::NUMERIC, 2)::DOUBLE PRECISION AS ed_demas_pct
    FROM vw_cuadernillos_edafologia_estadistica_detalle
    WHERE orden_pct > 2
    GROUP BY nombre
)
SELECT
    c.nombre,
    dom.categoria AS ed_dominante,
    dom.porcentaje AS ed_dominante_pct,
    sec.categoria AS ed_secundario,
    sec.porcentaje AS ed_secundario_pct,
    demas.ed_demas,
    demas.ed_demas_pct
FROM vw_cuadernillos_edafologia_cobertura_municipal AS c
LEFT JOIN vw_cuadernillos_edafologia_estadistica_detalle AS dom
    ON dom.nombre = c.nombre
    AND dom.orden_pct = 1
LEFT JOIN vw_cuadernillos_edafologia_estadistica_detalle AS sec
    ON sec.nombre = c.nombre
    AND sec.orden_pct = 2
LEFT JOIN demas
    ON demas.nombre = c.nombre;

COMMENT ON VIEW vw_cuadernillos_edafologia_estadistica_detalle IS
    'Insumo para la generacion de cuadernillos municipales: superficie y porcentaje por municipio y grupo edafologico sobre limites IIEG.';
COMMENT ON VIEW vw_cuadernillos_edafologia_cobertura_municipal IS
    'Insumo para la generacion de cuadernillos municipales: cobertura edafologica total por municipio sobre limites IIEG.';
COMMENT ON VIEW vw_cuadernillos_edafologia_estadistica_resumen IS
    'Insumo para la generacion de cuadernillos municipales: grupo edafologico dominante y cobertura por municipio.';
COMMENT ON VIEW vw_cuadernillos_edafologia_variables_texto IS
    'Insumo para la generacion de cuadernillos municipales: grupos dominante, secundario y resto redactados como texto por municipio.';
