-- V4: FDW hacia la base cvegeo + enriquecimiento de vw_asg_imss.
--
-- Registra la base cvegeo como servidor FDW y expone las tablas
-- cvegeo_states / cvegeo_municipalities como tablas foráneas locales.
-- Reemplaza vw_asg_imss (V3) con una versión enriquecida que agrega
-- cvegeo (clave INEGI de 5 dígitos) junto a cve_municipio (clave IMSS),
-- sin IDs internos y sin vista auxiliar adicional.

CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS cvegeo_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (
        dbname '${fdw_dbname}',
        host   '${fdw_host}',
        port   '${fdw_port}'
    );

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
    SERVER cvegeo_server
    OPTIONS (
        user     '${fdw_user}',
        password '${fdw_password}'
    );

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_states (
    id      INTEGER,
    cve_ent INTEGER,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_states');

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id      INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

-- Reemplaza vw_asg_imss (V3): agrega cvegeo (clave INEGI 5 dígitos) junto
-- a cve_municipio (clave IMSS). Elimina f.id (ID interno). El join a
-- cvegeo_municipalities se resuelve por nombre normalizado (unaccent+lower).
DROP VIEW IF EXISTS vw_asg_imss;
CREATE VIEW vw_asg_imss AS
SELECT
    f.fecha_corte,
    d.clave   AS cve_delegacion,
    sd.clave  AS cve_subdelegacion,
    e.clave   AS cve_entidad,
    m.clave   AS cve_municipio,
    c.cvegeo  AS cvegeo,
    s1.clave  AS sector_economico_1,
    s2.clave  AS sector_economico_2,
    s4.clave  AS sector_economico_4,
    trp.clave AS tamano_patron,
    sx.clave  AS sexo,
    re.clave  AS rango_edad,
    rs.clave  AS rango_salario,
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
JOIN      cat_rango_uma                ru  ON ru.id  = f.rango_uma_id
LEFT JOIN cvegeo_municipalities        c   ON lower(unaccent(m.descripcion)) = lower(unaccent(c.nomgeo))
                                         AND c.cve_ent = 14;

COMMENT ON VIEW vw_asg_imss IS
    'Datos ASG-IMSS (Jalisco) con claves IMSS (cve_municipio) e INEGI (cvegeo). '
    'cvegeo NULL = municipio sin correspondencia en cvegeo_municipalities.';
