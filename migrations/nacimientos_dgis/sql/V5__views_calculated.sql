CREATE OR REPLACE VIEW vw_tasa_fecundidad AS
SELECT
    t.fecha,
    m.nomgeo  AS municipio,
    s.nom_ent AS entidad,
    t.municipio_id,
    t.pob_mujeres_15_49,
    t.nacimientos,
    t.tasa_fec_gen
FROM stg_tasa_fecundidad t
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = t.municipio_id::integer
LEFT JOIN cvegeo_states s ON s.cve_ent = 14;

CREATE OR REPLACE VIEW vw_nacimientos_adolescentes AS
SELECT
    t.fecha,
    m.nomgeo  AS municipio,
    s.nom_ent AS entidad,
    t.municipio_id,
    t.nac_madres_10_14,
    t.tasa_esp_fec_madres_10_14,
    t.pct_padres_18_mas_madres_10_14,
    t.pct_edad_padre_sin_dato_madres_10_14,
    t.nac_madres_15_19,
    t.tasa_esp_fec_madres_15_19,
    t.pct_padres_25_mas_madres_15_19,
    t.pct_edad_padre_sin_dato_madres_15_19
FROM stg_nacimientos_adolescentes t
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = t.municipio_id::integer
LEFT JOIN cvegeo_states s ON s.cve_ent = 14;
