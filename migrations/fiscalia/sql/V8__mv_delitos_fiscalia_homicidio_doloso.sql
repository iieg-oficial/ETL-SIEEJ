-- Materialized view: delitos_fiscalia_homicidio_doloso
-- Mirrors seguridad_y_proteccion_ciudadana.delitos_fiscalia_homicidio_doloso on the server.
-- Unique index on fid enables REFRESH MATERIALIZED VIEW CONCURRENTLY
-- (mapalab reads these views live; concurrent refresh avoids read locks).

CREATE MATERIALIZED VIEW delitos_fiscalia_homicidio_doloso AS
SELECT
    ROW_NUMBER() OVER ()  AS fid,
    fecha,
    entidad,
    municipio,
    x_6368,
    y_6368,
    bien_juridico,
    delito,
    dia_semana,
    rango_hora,
    geom
FROM vw_mapalab_fiscalia
WHERE  delito = 'Homicidio doloso'
  AND  x_6368 IS NOT NULL AND y_6368 IS NOT NULL
  AND  x_6368 != 0        AND y_6368 != 0
ORDER BY municipio;

CREATE UNIQUE INDEX ux_delitos_fiscalia_homicidio_doloso_fid ON delitos_fiscalia_homicidio_doloso (fid);
