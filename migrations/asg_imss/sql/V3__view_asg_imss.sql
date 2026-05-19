-- ============================================================
-- V3__view_asg_imss.sql
-- Pipeline: asg_imss
-- Description: Analytical view resolving all catalog codes to descriptions.
-- NOTE: cve_municipio uses IMSS-proprietary codes; no JOIN to cvegeo pending.
-- ============================================================

CREATE OR REPLACE VIEW public.v_asg_imss AS
SELECT
    d.id,
    d.fecha_corte,

    -- Entidad / Municipio (IMSS codes)
    d.cve_entidad,
    em.desc_entidad,
    d.cve_municipio,
    em.desc_municipio,

    -- Delegación / Subdelegación
    d.cve_delegacion,
    del.descripcion   AS desc_delegacion,
    d.cve_subdelegacion,
    sub.descripcion   AS desc_subdelegacion,

    -- Sector económico
    d.sector_economico_1,
    s1.descripcion    AS desc_sector_1,
    d.sector_economico_2,
    s2.descripcion    AS desc_sector_2,
    d.sector_economico_4,
    s4.descripcion    AS desc_sector_4,

    -- Dimensiones de empleo
    d.tamanio_patron,
    tp.descripcion    AS desc_tamanio_patron,
    d.sexo,
    sx.descripcion    AS desc_sexo,
    d.rango_edad,
    re.descripcion    AS desc_rango_edad,
    d.rango_salarial,
    rs.descripcion    AS desc_rango_salarial,
    d.rango_uma,
    ru.descripcion    AS desc_rango_uma,

    -- Métricas — conteos
    d.asegurados,
    d.no_trabajadores,
    d.ta,
    d.teu,
    d.tec,
    d.tpu,
    d.tpc,
    d.ta_sal,
    d.teu_sal,
    d.tec_sal,
    d.tpu_sal,
    d.tpc_sal,

    -- Métricas — masa salarial
    d.masa_sal_ta,
    d.masa_sal_teu,
    d.masa_sal_tec,
    d.masa_sal_tpu,
    d.masa_sal_tpc,

    d.created_at

FROM public.stg_asg_imss_datos                         d
LEFT JOIN public.stg_asg_imss_cat_entidad_municipio em  ON em.cve_municipio   = d.cve_municipio
LEFT JOIN public.stg_asg_imss_cat_delegacion        del ON del.cve_delegacion = d.cve_delegacion
LEFT JOIN public.stg_asg_imss_cat_subdelegacion     sub ON sub.cve_delegacion    = d.cve_delegacion
                                                       AND sub.cve_subdelegacion = d.cve_subdelegacion
LEFT JOIN public.stg_asg_imss_cat_sector_1          s1  ON s1.cve_sector_1 = d.sector_economico_1
LEFT JOIN public.stg_asg_imss_cat_sector_2          s2  ON s2.cve_sector_1 = d.sector_economico_1
                                                       AND s2.cve_sector_2 = d.sector_economico_2
LEFT JOIN public.stg_asg_imss_cat_sector_4          s4  ON s4.cve_sector_2 = d.sector_economico_2
                                                       AND s4.cve_sector_4 = d.sector_economico_4
LEFT JOIN public.stg_asg_imss_cat_tamanio_patron    tp  ON tp.cve = d.tamanio_patron
LEFT JOIN public.stg_asg_imss_cat_sexo              sx  ON sx.cve = d.sexo
LEFT JOIN public.stg_asg_imss_cat_rango_edad        re  ON re.cve = d.rango_edad
LEFT JOIN public.stg_asg_imss_cat_rango_salarial    rs  ON rs.cve = d.rango_salarial
LEFT JOIN public.stg_asg_imss_cat_rango_uma         ru  ON ru.cve = d.rango_uma;
