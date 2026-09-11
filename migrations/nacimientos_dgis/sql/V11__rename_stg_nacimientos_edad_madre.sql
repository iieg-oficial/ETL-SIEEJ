-- =======================================================================
-- V11: stg_nacimientos pasa a stg_nacimientos_edad_madre
-- =======================================================================
-- La tabla nunca guardó nacimientos: guarda conteos por año, municipio y
-- edad de la madre. Con la llegada del microdato del certificado el nombre
-- pelado dejaba de ser ambiguo para volverse falso.
--
-- El rename no rompe las vistas: Postgres guarda sus dependencias por OID,
-- así que vw_nacimientos y las materializadas siguen resolviendo, y los
-- COMMENT ON de V9 viajan con la tabla.

ALTER TABLE stg_nacimientos RENAME TO stg_nacimientos_edad_madre;

ALTER VIEW vw_nacimientos RENAME TO vw_nacimientos_edad_madre;

COMMENT ON TABLE stg_nacimientos_edad_madre IS
    'Agregado de nacimientos por año, municipio de residencia y edad de la madre. '
    'El grano es el agregado, no el nacimiento. Fuente: SINAC/DGIS.';

COMMENT ON VIEW vw_nacimientos_edad_madre IS
    'Vista del agregado por edad de la madre con nombres de municipio y entidad.';
