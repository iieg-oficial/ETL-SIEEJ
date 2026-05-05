CREATE OR REPLACE VIEW v_efipem AS
SELECT
    f.id,
    f.anio,
    t.name           AS trimestre,
    f.cve_ent,
    s.nom_ent        AS entidad,
    tm.name          AS tema,
    cl.name          AS clasificador,
    cp.name          AS concepto,
    f.valor,
    es.name          AS estatus,
    f.row_hash,
    f.valid_from,
    f.valid_to,
    f.is_current,
    f.created_at
FROM stg_efipem_finanzas_trimestral f
JOIN stg_efipem_cat_trimestre    t  ON t.id  = f.trimestre_id
JOIN stg_efipem_cat_tema         tm ON tm.id = f.tema_id
JOIN stg_efipem_cat_clasificador cl ON cl.id = f.clasificador_id
JOIN stg_efipem_cat_concepto     cp ON cp.id = f.concepto_id
JOIN stg_efipem_cat_estatus      es ON es.id = f.estatus_id
LEFT JOIN cvegeo_states          s  ON s.cve_ent = f.cve_ent
WHERE f.is_current = TRUE;

COMMENT ON VIEW v_efipem IS 'Vista de integración del pipeline efipem. Expone la versión activa de cada registro con nombres resueltos de catálogos y entidad federativa.';
