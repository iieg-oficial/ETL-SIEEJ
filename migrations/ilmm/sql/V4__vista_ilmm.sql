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
-- Vista filtrada: porcentaje de ocupación en el sector informal
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_ocupacion_informal AS
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

COMMENT ON VIEW vw_ocupacion_informal IS 'Porcentaje de ocupación en el sector informal por municipio y fecha (indicador: porcentaje_ocupacion_informal).';

-- ---------------------------------------------------------------------------
-- Vista filtrada: tasa de desocupación
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_tasa_desocupacion AS
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

COMMENT ON VIEW vw_tasa_desocupacion IS 'Tasa de desocupación por municipio y fecha (indicador: tasa_desocupacion).';
