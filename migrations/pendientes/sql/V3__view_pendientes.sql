CREATE OR REPLACE VIEW vw_pendientes_estadisticas_municipales AS
SELECT
    e.*,
    m.nomgeo AS nombre_geo,
    f.clave AS fuente_limite
FROM estadisticas_pendiente_municipales AS e
JOIN cvegeo_municipalities AS m
  ON m.cve_ent = 14
 AND m.cve_mun = e.municipality_id
JOIN fuentes_limites_municipales AS f
  ON f.id = e.fuente_limite_municipal_id;

COMMENT ON TABLE estadisticas_pendiente_municipales IS
    'Estadisticas zonales de los productos continuos de pendientes, por municipio y fuente territorial.';
COMMENT ON COLUMN estadisticas_pendiente_municipales.municipality_id IS
    'Identidad cve_mun de Jalisco; no es el id remoto de cvegeo.';
COMMENT ON VIEW vw_pendientes_estadisticas_municipales IS
    'Consulta municipal de pendientes con identidad cvegeo y fuente territorial IIEG/INEGI.';
