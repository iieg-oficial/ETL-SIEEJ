CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS cvegeo_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    dbname '${fdw_dbname}',
    host '${fdw_host}',
    port '${fdw_port}'
);

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
SERVER cvegeo_server
OPTIONS (
    user '${fdw_user}',
    password '${fdw_password}'
);

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id INTEGER,
    cvegeo INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo VARCHAR,
    nom_ent VARCHAR,
    geom_iieg geometry(MultiPolygon, 6368),
    geom_inegi geometry(MultiPolygon, 6368)
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

DO $$
DECLARE
    jalisco_count INTEGER;
    distinct_municipalities INTEGER;
BEGIN
    SELECT count(*), count(DISTINCT cve_mun)
    INTO jalisco_count, distinct_municipalities
    FROM cvegeo_municipalities
    WHERE cve_ent = 14;

    IF jalisco_count <> 125 OR distinct_municipalities <> 125 THEN
        RAISE EXCEPTION
            'Invalid cvegeo Jalisco catalog: rows=%, distinct cve_mun=%; expected 125 and 125',
            jalisco_count,
            distinct_municipalities;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM cvegeo_municipalities
        WHERE cve_ent = 14
          AND (cvegeo IS NULL OR cve_mun IS NULL OR cvegeo <> 14000 + cve_mun)
    ) THEN
        RAISE EXCEPTION 'Invalid cvegeo Jalisco catalog: null or incoherent cvegeo/cve_mun values';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM cvegeo_municipalities
        WHERE cve_ent = 14
        GROUP BY cve_ent, cve_mun
        HAVING count(*) <> 1 OR count(DISTINCT cvegeo) <> 1
    ) THEN
        RAISE EXCEPTION 'Ambiguous cvegeo Jalisco mapping for (cve_ent, cve_mun)';
    END IF;
END
$$;

DROP VIEW edafologia_resumenes_municipales;

CREATE VIEW edafologia_resumenes_municipales AS
SELECT
    f.fuente_limite_municipal_id,
    f.municipality_id,
    m.cvegeo,
    e.version_fuente,
    e.grupo_edafologico_id,
    e.calificador_primario_id,
    e.calificador_secundario_id,
    SUM(f.superficie_m2)::DOUBLE PRECISION AS superficie_m2,
    SUM(f.superficie_ha)::DOUBLE PRECISION AS superficie_ha,
    SUM(f.porcentaje_municipio_total)::DOUBLE PRECISION AS porcentaje_municipio,
    COUNT(*)::INTEGER AS cantidad_fragmentos
FROM edafologia_fragmentos_municipales AS f
JOIN edafologias AS e
    ON e.id = f.edafologia_id
JOIN cvegeo_municipalities AS m
    ON f.municipality_id = m.cve_mun
    AND m.cve_ent = 14
GROUP BY
    f.fuente_limite_municipal_id,
    f.municipality_id,
    m.cvegeo,
    e.version_fuente,
    e.grupo_edafologico_id,
    e.calificador_primario_id,
    e.calificador_secundario_id;

COMMENT ON FOREIGN TABLE cvegeo_municipalities IS
    'Catalogo territorial remoto de cvegeo consultado mediante postgres_fdw; no se duplica localmente.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.municipality_id IS
    'Clave cve_mun de Jalisco. Relacion logica con cvegeo_municipalities mediante municipality_id = cve_mun y cve_ent = 14; no es una FK fisica ni el id remoto.';
COMMENT ON VIEW edafologia_resumenes_municipales IS
    'Vista SQL no materializada que agrega fragmentos y resuelve cvegeo mediante municipality_id = cve_mun y cve_ent = 14.';
COMMENT ON COLUMN edafologia_resumenes_municipales.fuente_limite_municipal_id IS
    'Fuente territorial del resumen, heredada de los fragmentos municipales.';
COMMENT ON COLUMN edafologia_resumenes_municipales.municipality_id IS
    'Clave cve_mun del municipio dentro de Jalisco.';
COMMENT ON COLUMN edafologia_resumenes_municipales.cvegeo IS
    'Clave geoestadistica EEMMM expuesta desde cvegeo_municipalities para consulta y trazabilidad.';
COMMENT ON COLUMN edafologia_resumenes_municipales.version_fuente IS
    'Version de la fuente edafologica resumida.';
COMMENT ON COLUMN edafologia_resumenes_municipales.grupo_edafologico_id IS
    'Grupo edafologico principal de la categoria resumida.';
COMMENT ON COLUMN edafologia_resumenes_municipales.calificador_primario_id IS
    'Calificador en rol primario de la categoria resumida.';
COMMENT ON COLUMN edafologia_resumenes_municipales.calificador_secundario_id IS
    'Calificador en rol secundario de la categoria resumida.';
COMMENT ON COLUMN edafologia_resumenes_municipales.superficie_m2 IS
    'Suma de superficie_m2 de los fragmentos del grupo de agregacion.';
COMMENT ON COLUMN edafologia_resumenes_municipales.superficie_ha IS
    'Suma de superficie_ha de los fragmentos del grupo de agregacion.';
COMMENT ON COLUMN edafologia_resumenes_municipales.porcentaje_municipio IS
    'Suma de porcentaje_municipio_total de los fragmentos del grupo de agregacion.';
COMMENT ON COLUMN edafologia_resumenes_municipales.cantidad_fragmentos IS
    'Numero de fragmentos persistentes incluidos en el agregado.';
