-- =======================================================================
-- V4__vista.sql  |  Pipeline: etef
-- Vista analítica con nombres humanos y resolución de entidad
-- =======================================================================

CREATE OR REPLACE VIEW public.vw_etef_datos AS
SELECT
    d.id,
    d.anio,
    d.trimestre,
    d.mes,
    d.cve_ent,
    c.cvegeo,
    c.nom_ent,
    d.codigo_scian_id,
    sc.codigo          AS codigo_scian,
    sc.descripcion     AS subsector,
    sc.version         AS version_scian,
    d.val_usd,
    d.estatus_cifra,
    d.estatus,
    d.created_at,
    d.updated_at
FROM public.stg_etef_datos d
LEFT JOIN public.stg_etef_cat_codigo_scian sc
    ON sc.id = d.codigo_scian_id
LEFT JOIN public.cvegeo_municipalities c
    ON c.cve_ent = d.cve_ent AND c.cve_mun = 0;  -- cve_mun=0 para entidad completa
