from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T

INSERT_NACIMIENTOS_ADOLESCENTES = f"""
DELETE FROM stg_nacimientos_adolescentes;

INSERT INTO stg_nacimientos_adolescentes (
    fecha, entidad_id, municipio_id,
    nac_madres_10_14, tasa_esp_fec_madres_10_14,
    pct_padres_18_mas_madres_10_14, pct_edad_padre_sin_dato_madres_10_14,
    nac_madres_15_19, tasa_esp_fec_madres_15_19,
    pct_padres_25_mas_madres_15_19, pct_edad_padre_sin_dato_madres_15_19
)
SELECT
    make_date(n.anio, 1, 1)          AS fecha,
    '14'                              AS entidad_id,
    LPAD(n.cve_geo::text, 5, '0')    AS municipio_id,

    SUM(CASE WHEN n.edad_madre BETWEEN 10 AND 14 THEN n.tot_nac END)::numeric
        AS nac_madres_10_14,
    ROUND(
        SUM(CASE WHEN n.edad_madre BETWEEN 10 AND 14 THEN n.tot_nac END)::numeric
        / NULLIF(c.pob_10_14, 0) * 1000, 2
    )   AS tasa_esp_fec_madres_10_14,
    ROUND(
        SUM(CASE WHEN n.edad_madre BETWEEN 10 AND 14 THEN n.nac_padre_18_mas END)::numeric
        / NULLIF(SUM(CASE WHEN n.edad_madre BETWEEN 10 AND 14 THEN n.tot_nac END), 0) * 100, 2
    )   AS pct_padres_18_mas_madres_10_14,
    ROUND(
        (SUM(CASE WHEN n.edad_madre BETWEEN 10 AND 14 THEN n.tot_nac END)
         - SUM(CASE WHEN n.edad_madre BETWEEN 10 AND 14 THEN n.nac_padre_conocido END))::numeric
        / NULLIF(SUM(CASE WHEN n.edad_madre BETWEEN 10 AND 14 THEN n.tot_nac END), 0) * 100, 2
    )   AS pct_edad_padre_sin_dato_madres_10_14,

    SUM(CASE WHEN n.edad_madre BETWEEN 15 AND 19 THEN n.tot_nac END)::numeric
        AS nac_madres_15_19,
    ROUND(
        SUM(CASE WHEN n.edad_madre BETWEEN 15 AND 19 THEN n.tot_nac END)::numeric
        / NULLIF(c.pob_15_19, 0) * 1000, 2
    )   AS tasa_esp_fec_madres_15_19,
    ROUND(
        SUM(CASE WHEN n.edad_madre BETWEEN 15 AND 19 THEN n.nac_padre_25_mas END)::numeric
        / NULLIF(SUM(CASE WHEN n.edad_madre BETWEEN 15 AND 19 THEN n.tot_nac END), 0) * 100, 2
    )   AS pct_padres_25_mas_madres_15_19,
    ROUND(
        (SUM(CASE WHEN n.edad_madre BETWEEN 15 AND 19 THEN n.tot_nac END)
         - SUM(CASE WHEN n.edad_madre BETWEEN 15 AND 19 THEN n.nac_padre_conocido END))::numeric
        / NULLIF(SUM(CASE WHEN n.edad_madre BETWEEN 15 AND 19 THEN n.tot_nac END), 0) * 100, 2
    )   AS pct_edad_padre_sin_dato_madres_15_19

FROM {T.STG_NACIMIENTOS_EDAD_MADRE} n
JOIN conapo_poblacion c
    ON c.municipio_id = n.cve_geo
    AND c.anio = n.anio
    AND c.sexo_id = 2
WHERE n.edad_madre BETWEEN 10 AND 19
GROUP BY n.anio, n.cve_geo, c.pob_10_14, c.pob_15_19;
"""
