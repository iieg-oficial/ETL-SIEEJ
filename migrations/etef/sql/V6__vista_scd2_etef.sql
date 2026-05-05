-- =======================================================================
-- V6__vista_scd2_etef.sql  |  Pipeline: etef
-- Reemplaza vw_etef_datos para incluir columnas SCD2
-- La vista expone solo la versión activa (is_current = TRUE)
-- =======================================================================

CREATE OR REPLACE VIEW public.vw_etef_datos AS
SELECT
    d.id,
    d.anio,
    d.trimestre,
    d.mes,
    d.prod_est,
    d.cobertura,
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
    d.row_hash,
    d.valid_from,
    d.valid_to,
    d.is_current,
    d.created_at,
    d.updated_at
FROM public.stg_etef_datos d
LEFT JOIN public.stg_etef_cat_codigo_scian sc
    ON sc.id = d.codigo_scian_id
LEFT JOIN public.cvegeo_municipalities c
    ON c.cve_ent = d.cve_ent AND c.cve_mun = 0  -- cve_mun=0 para entidad completa
WHERE d.is_current = TRUE;
