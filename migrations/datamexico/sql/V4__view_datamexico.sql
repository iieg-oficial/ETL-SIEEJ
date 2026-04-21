CREATE OR REPLACE VIEW v_flujo_comercio AS
SELECT
    fc.id,
    p.codigo_pais,
    p.nombre_pais,
    cs.nom_ent AS entidad,
    per.anio,
    per.trimestre,
    per.etiqueta_trimestre,
    tf.flujo,
    prod.descripcion AS producto,
    fc.valor_comercio
FROM flujo_comercio fc
LEFT JOIN paises p                     ON fc.pais_id       = p.id
LEFT JOIN cvegeo_states cs             ON fc.entidad_id    = cs.cve_ent
LEFT JOIN periodos per                 ON fc.periodo_id    = per.id
LEFT JOIN tipos_flujos_comerciales tf  ON fc.tipo_flujo_id = tf.id
LEFT JOIN productos prod               ON fc.producto_id   = prod.id;
