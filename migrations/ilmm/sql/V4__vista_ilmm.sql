-- ---------------------------------------------------------------------------
-- Vista materializada: porcentaje de ocupación en el sector informal
-- indicador derivado: valor = informales(est=1), error_estandar = informales(est=2)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vw_ocupacion_informal AS
SELECT
    s1.id,
    s1.fecha,
    s1.clave_municipio,
    LPAD(m.cvegeo::text, 5, '0')          AS cvegeo,
    m.nomgeo                               AS nom_municipio,
    m.nom_ent,
    'porcentaje_ocupacion_informal'::TEXT  AS indicador,
    s1.informales                          AS valor,
    s2.informales                          AS error_estandar
FROM stg_ilmm s1
JOIN stg_ilmm s2
    ON  s1.clave_municipio = s2.clave_municipio
    AND s1.fecha           = s2.fecha
    AND s1.estimador_id    = 1
    AND s2.estimador_id    = 2
LEFT JOIN cvegeo_municipalities m
    ON LPAD(m.cvegeo::text, 5, '0') = s1.clave_municipio;

CREATE UNIQUE INDEX idx_mvw_ocupacion_informal_id ON vw_ocupacion_informal (id);

COMMENT ON MATERIALIZED VIEW vw_ocupacion_informal IS 'Porcentaje de ocupación en el sector informal por municipio y fecha (indicador: porcentaje_ocupacion_informal).';

-- ---------------------------------------------------------------------------
-- Vista materializada: tasa de desocupación
-- indicador derivado: valor = 100 - ocupados(est=1), error_estandar = ocupados(est=2)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vw_tasa_desocupacion AS
SELECT
    s1.id,
    s1.fecha,
    s1.clave_municipio,
    LPAD(m.cvegeo::text, 5, '0')  AS cvegeo,
    m.nomgeo                       AS nom_municipio,
    m.nom_ent,
    'tasa_desocupacion'::TEXT      AS indicador,
    (100 - s1.ocupados)            AS valor,
    s2.ocupados                    AS error_estandar
FROM stg_ilmm s1
JOIN stg_ilmm s2
    ON  s1.clave_municipio = s2.clave_municipio
    AND s1.fecha           = s2.fecha
    AND s1.estimador_id    = 1
    AND s2.estimador_id    = 2
LEFT JOIN cvegeo_municipalities m
    ON LPAD(m.cvegeo::text, 5, '0') = s1.clave_municipio;

CREATE UNIQUE INDEX idx_mvw_tasa_desocupacion_id ON vw_tasa_desocupacion (id);

COMMENT ON MATERIALIZED VIEW vw_tasa_desocupacion IS 'Tasa de desocupación por municipio y fecha (indicador: tasa_desocupacion).';
