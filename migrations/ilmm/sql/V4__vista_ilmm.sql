CREATE OR REPLACE VIEW vw_ilmm AS
SELECT
    s.id,
    s.fecha,
    s.clave_municipio,
    LPAD(m.cvegeo::text, 5, '0')  AS cvegeo,
    m.nomgeo                       AS nom_municipio,
    m.nom_ent,
    i.indicador,
    s.valor,
    s.error_estandar
FROM stg_ilmm s
JOIN cat_ilmm_indicador i ON i.id = s.indicador_id
LEFT JOIN cvegeo_municipalities m ON LPAD(m.cvegeo::text, 5, '0') = s.clave_municipio;

COMMENT ON VIEW vw_ilmm IS 'Vista de integración del pipeline ilmm. Expone indicadores del mercado de trabajo municipal con nombres geográficos.';

-- ---------------------------------------------------------------------------
-- Vista materializada: porcentaje de ocupación en el sector informal
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vw_ocupacion_informal AS
SELECT
    id,
    fecha,
    clave_municipio,
    cvegeo,
    nom_municipio,
    nom_ent,
    indicador,
    valor,
    error_estandar
FROM vw_ilmm
WHERE indicador = 'porcentaje_ocupacion_informal';

CREATE UNIQUE INDEX idx_mvw_ocupacion_informal_id ON vw_ocupacion_informal (id);

COMMENT ON MATERIALIZED VIEW vw_ocupacion_informal IS 'Porcentaje de ocupación en el sector informal por municipio y fecha (indicador: porcentaje_ocupacion_informal).';

-- ---------------------------------------------------------------------------
-- Vista materializada: tasa de desocupación
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vw_tasa_desocupacion AS
SELECT
    id,
    fecha,
    clave_municipio,
    cvegeo,
    nom_municipio,
    nom_ent,
    indicador,
    valor,
    error_estandar
FROM vw_ilmm
WHERE indicador = 'tasa_desocupacion';

CREATE UNIQUE INDEX idx_mvw_tasa_desocupacion_id ON vw_tasa_desocupacion (id);

COMMENT ON MATERIALIZED VIEW vw_tasa_desocupacion IS 'Tasa de desocupación por municipio y fecha (indicador: tasa_desocupacion).';
