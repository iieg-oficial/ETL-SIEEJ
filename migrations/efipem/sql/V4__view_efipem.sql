CREATE OR REPLACE VIEW vw_efipem AS
SELECT
    f.id,
    f.anio,
    f.cvegeo,
    f.cve_ent,
    f.cve_mun,
    tm.name          AS tema,
    cl.name          AS clasificador,
    cp.name          AS concepto,
    f.valor,
    es.name          AS estatus,
    f.created_at
FROM stg_efipem f
JOIN cat_tema         tm ON tm.id = f.tema_id
JOIN cat_clasificador cl ON cl.id = f.clasificador_id
JOIN cat_concepto     cp ON cp.id = f.concepto_id
JOIN cat_estatus      es ON es.id = f.estatus_id;

COMMENT ON VIEW vw_efipem IS 'Vista de integración del pipeline efipem. Expone las finanzas municipales anuales de Jalisco (cve_ent=14) con nombres de catálogos resueltos.';
