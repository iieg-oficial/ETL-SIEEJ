CREATE OR REPLACE VIEW v_etef AS
SELECT
    d.id,
    d.anio,
    d.trimestre,
    d.mes,
    d.prod_est,
    d.cobertura,
    d.cve_ent,
    s.nom_ent,
    d.codigo_scian_id,
    sc.codigo      AS codigo_scian,
    sc.descripcion AS subsector,
    d.val_usd,
    d.estatus_cifra,
    d.estatus,
    d.row_hash,
    d.valid_from,
    d.valid_to,
    d.is_current,
    d.created_at
FROM stg_etef_datos d
JOIN stg_etef_cat_codigo_scian sc ON sc.id = d.codigo_scian_id
LEFT JOIN cvegeo_states s ON s.cve_ent = d.cve_ent
WHERE d.is_current = TRUE;

COMMENT ON VIEW v_etef IS 'Vista de integración del pipeline etef. Expone la versión activa de cada registro con nombres de entidad federativa.';
