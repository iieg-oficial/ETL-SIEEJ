-- =======================================================================
-- V4: Vista analitica EFIPEM -- resuelve catalogos y entidad cvegeo.
-- =======================================================================

CREATE OR REPLACE VIEW stg_efipem_finanzas_trimestral_vw AS
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
    f.created_at,
    f.updated_at
FROM stg_efipem_finanzas_trimestral f
LEFT JOIN stg_efipem_cat_trimestre    t  ON t.id  = f.trimestre_id
LEFT JOIN stg_efipem_cat_tema         tm ON tm.id = f.tema_id
LEFT JOIN stg_efipem_cat_clasificador cl ON cl.id = f.clasificador_id
LEFT JOIN stg_efipem_cat_concepto     cp ON cp.id = f.concepto_id
LEFT JOIN stg_efipem_cat_estatus      es ON es.id = f.estatus_id
LEFT JOIN cvegeo_states               s  ON s.id  = f.entidad_id;
