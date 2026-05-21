-- =======================================================================
-- V3: Vista vw_asg_imss.
--
-- Espejo del CSV original publicado por IMSS: expone únicamente las
-- claves secundarias (códigos `clave`) resueltas vía JOIN, sin
-- descripciones, y agrega `fecha_corte`. Mantiene los nombres de columna
-- tal como aparecen en el header del CSV (post-normalización del
-- caracter de reemplazo en `tamano_patron`).
-- =======================================================================

CREATE OR REPLACE VIEW vw_asg_imss AS
SELECT
    f.id,
    f.fecha_corte,
    d.clave   AS cve_delegacion,
    sd.clave  AS cve_subdelegacion,
    e.clave   AS cve_entidad,
    m.clave   AS cve_municipio,
    s1.clave  AS sector_economico_1,
    s2.clave  AS sector_economico_2,
    s4.clave  AS sector_economico_4,
    trp.clave AS tamano_patron,
    sx.clave  AS sexo,
    re.clave  AS rango_edad,
    rs.clave  AS rango_salarial,
    ru.clave  AS rango_uma,
    f.asegurados,
    f.no_trabajadores,
    f.ta,
    f.teu,
    f.tec,
    f.tpu,
    f.tpc,
    f.ta_sal,
    f.teu_sal,
    f.tec_sal,
    f.tpu_sal,
    f.tpc_sal,
    f.masa_sal_ta,
    f.masa_sal_teu,
    f.masa_sal_tec,
    f.masa_sal_tpu,
    f.masa_sal_tpc
FROM stg_asg_imss f
JOIN      cat_subdelegacion            sd  ON sd.id  = f.subdelegacion_id
JOIN      cat_delegacion               d   ON d.id   = sd.delegacion_id
JOIN      cat_municipio                m   ON m.id   = f.municipio_id
JOIN      cat_entidad                  e   ON e.id   = m.entidad_id
LEFT JOIN cat_sector_4                 s4  ON s4.id  = f.sector_4_id
LEFT JOIN cat_sector_2                 s2  ON s2.id  = s4.sector_2_id
LEFT JOIN cat_sector_1                 s1  ON s1.id  = s2.sector_1_id
JOIN      cat_tamano_registro_patronal trp ON trp.id = f.tamano_registro_patronal_id
JOIN      cat_sexo                     sx  ON sx.id  = f.sexo_id
JOIN      cat_rango_edad               re  ON re.id  = f.rango_edad_id
JOIN      cat_rango_salario            rs  ON rs.id  = f.rango_salario_id
JOIN      cat_rango_uma                ru  ON ru.id  = f.rango_uma_id;

COMMENT ON VIEW vw_asg_imss IS
    'Espejo del CSV publicado por IMSS: devuelve las claves secundarias (códigos) resueltas vía JOIN sin descripciones. Agrega fecha_corte (último día del mes publicado).';
