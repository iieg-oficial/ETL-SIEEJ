CREATE OR REPLACE VIEW vw_economico_nacional_2019 AS
SELECT
    s.*,
    ae.codigo      AS actividad_codigo,
    ae.descripcion AS actividad,
    e.codigo       AS estrato_codigo,
    e.descripcion  AS estrato
FROM stg_economico_nacional_2019 s
LEFT JOIN cat_actividades_economicas ae ON ae.id = s.actividad_economica_id
LEFT JOIN cat_estratos e ON e.id = s.estrato_id;


CREATE OR REPLACE VIEW vw_economico_estatal_2019 AS
SELECT
    s.*,
    st.nom_ent,
    ae.codigo      AS actividad_codigo,
    ae.descripcion AS actividad,
    e.codigo       AS estrato_codigo,
    e.descripcion  AS estrato
FROM stg_economico_estatal_2019 s
LEFT JOIN cvegeo_states st ON st.cve_ent = s.cve_ent
LEFT JOIN cat_actividades_economicas ae ON ae.id = s.actividad_economica_id
LEFT JOIN cat_estratos e ON e.id = s.estrato_id;


CREATE OR REPLACE VIEW vw_economico_municipal_2019 AS
SELECT
    s.*,
    m.nomgeo       AS municipio,
    m.nom_ent,
    ae.codigo      AS actividad_codigo,
    ae.descripcion AS actividad,
    e.codigo       AS estrato_codigo,
    e.descripcion  AS estrato
FROM stg_economico_municipal_2019 s
LEFT JOIN cvegeo_municipalities m ON m.cve_ent = s.cve_ent AND m.cve_mun = s.cve_mun
LEFT JOIN cat_actividades_economicas ae ON ae.id = s.actividad_economica_id
LEFT JOIN cat_estratos e ON e.id = s.estrato_id;


CREATE OR REPLACE VIEW vw_economico_nacional_2024 AS
SELECT
    s.*,
    ae.codigo      AS actividad_codigo,
    ae.descripcion AS actividad,
    e.codigo       AS estrato_codigo,
    e.descripcion  AS estrato
FROM stg_economico_nacional_2024 s
LEFT JOIN cat_actividades_economicas ae ON ae.id = s.actividad_economica_id
LEFT JOIN cat_estratos e ON e.id = s.estrato_id;


CREATE OR REPLACE VIEW vw_economico_estatal_2024 AS
SELECT
    s.*,
    st.nom_ent,
    ae.codigo      AS actividad_codigo,
    ae.descripcion AS actividad,
    e.codigo       AS estrato_codigo,
    e.descripcion  AS estrato
FROM stg_economico_estatal_2024 s
LEFT JOIN cvegeo_states st ON st.cve_ent = s.cve_ent
LEFT JOIN cat_actividades_economicas ae ON ae.id = s.actividad_economica_id
LEFT JOIN cat_estratos e ON e.id = s.estrato_id;


CREATE OR REPLACE VIEW vw_economico_municipal_2024 AS
SELECT
    s.*,
    m.nomgeo       AS municipio,
    m.nom_ent,
    ae.codigo      AS actividad_codigo,
    ae.descripcion AS actividad,
    e.codigo       AS estrato_codigo,
    e.descripcion  AS estrato
FROM stg_economico_municipal_2024 s
LEFT JOIN cvegeo_municipalities m ON m.cve_ent = s.cve_ent AND m.cve_mun = s.cve_mun
LEFT JOIN cat_actividades_economicas ae ON ae.id = s.actividad_economica_id
LEFT JOIN cat_estratos e ON e.id = s.estrato_id;
