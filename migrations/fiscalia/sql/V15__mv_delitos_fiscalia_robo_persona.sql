-- Materialized view: delitos_fiscalia_robo_persona
-- Mirrors seguridad_y_proteccion_ciudadana.delitos_fiscalia_robo_persona on the server.
-- Unique index on fid enables REFRESH MATERIALIZED VIEW CONCURRENTLY
-- (mapalab reads these views live; concurrent refresh avoids read locks).

CREATE MATERIALIZED VIEW delitos_fiscalia_robo_persona AS
SELECT
    ROW_NUMBER() OVER ()  AS fid,
    fecha,
    entidad,
    municipio,
    x_6368,
    y_6368,
    bien_juridico,
    delito,
    modalidad,
    dia_semana,
    rango_hora,
    geom
FROM vw_mapalab_fiscalia
WHERE  delito = 'Robo a persona'
  AND  x_6368 IS NOT NULL AND y_6368 IS NOT NULL
  AND  x_6368 != 0        AND y_6368 != 0
ORDER BY municipio;

CREATE UNIQUE INDEX ux_delitos_fiscalia_robo_persona_fid ON delitos_fiscalia_robo_persona (fid);
