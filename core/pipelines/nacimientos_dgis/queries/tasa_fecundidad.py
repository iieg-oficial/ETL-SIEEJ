from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T

INSERT_TASA_FECUNDIDAD = f"""
DELETE FROM stg_tasa_fecundidad;

INSERT INTO stg_tasa_fecundidad (
    fecha, entidad_id, municipio_id,
    pob_mujeres_15_49, nacimientos, tasa_fec_gen
)
SELECT
    make_date(n.anio, 1, 1)         AS fecha,
    '14'                             AS entidad_id,
    LPAD(n.cve_geo::text, 5, '0')   AS municipio_id,
    (c.pob_15_19 + c.pob_20_24 + c.pob_25_29 + c.pob_30_34
     + c.pob_35_39 + c.pob_40_44 + c.pob_45_49)
                                     AS pob_mujeres_15_49,
    SUM(n.tot_nac)                   AS nacimientos,
    ROUND(
        SUM(n.tot_nac)::numeric
        / NULLIF(c.pob_15_19 + c.pob_20_24 + c.pob_25_29 + c.pob_30_34
                 + c.pob_35_39 + c.pob_40_44 + c.pob_45_49, 0)
        * 1000, 2
    )                                AS tasa_fec_gen
FROM {T.STG_NACIMIENTOS_EDAD_MADRE} n
JOIN conapo_poblacion c
    ON c.municipio_id = n.cve_geo
    AND c.anio = n.anio
    AND c.sexo_id = 2
GROUP BY n.anio, n.cve_geo,
         c.pob_15_19, c.pob_20_24, c.pob_25_29, c.pob_30_34,
         c.pob_35_39, c.pob_40_44, c.pob_45_49;
"""
