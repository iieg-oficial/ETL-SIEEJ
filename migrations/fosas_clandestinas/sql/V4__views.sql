CREATE OR REPLACE VIEW vw_fosas_clandestinas AS
SELECT
    p.fecha_corte,
    f.consecutivo,
    f.periodo,
    f.denominacion,
    m.cvegeo,
    m.nomgeo AS municipio,
    f.fecha_inicio,
    f.fecha_fin,
    f.en_proceso,
    f.pre_victimas_loc,
    f.pre_victimas_ide,
    f.pre_hom_ide,
    f.pre_muj_ide,
    f.estatus_loc
FROM stg_fosas_clandestinas f
JOIN cat_publicaciones p
    ON p.id = f.publicacion_id
LEFT JOIN cvegeo_municipalities m
    ON m.cve_mun = f.cve_mun
    AND m.cve_ent = f.cve_ent
WHERE p.fecha_corte = (SELECT MAX(fecha_corte) FROM cat_publicaciones);

COMMENT ON VIEW vw_fosas_clandestinas IS
    'Último corte del Registro Estatal de Fosas Clandestinas con el municipio resuelto contra cvegeo.';

CREATE OR REPLACE VIEW vw_fosas_clandestinas_municipio AS
SELECT
    p.fecha_corte,
    m.cvegeo,
    m.nomgeo AS municipio,
    COUNT(DISTINCT f.consecutivo)          AS sitios,
    COUNT(*) FILTER (WHERE f.en_proceso)   AS periodos_en_proceso,
    SUM(f.pre_victimas_loc)                AS pre_victimas_loc,
    SUM(f.pre_victimas_ide)                AS pre_victimas_ide,
    SUM(f.pre_hom_ide)                     AS pre_hom_ide,
    SUM(f.pre_muj_ide)                     AS pre_muj_ide
FROM stg_fosas_clandestinas f
JOIN cat_publicaciones p
    ON p.id = f.publicacion_id
LEFT JOIN cvegeo_municipalities m
    ON m.cve_mun = f.cve_mun
    AND m.cve_ent = f.cve_ent
GROUP BY p.fecha_corte, m.cvegeo, m.nomgeo;

COMMENT ON VIEW vw_fosas_clandestinas_municipio IS
    'Sitios y víctimas preliminares por municipio y corte; las sumas omiten los renglones sin cifra numérica.';
