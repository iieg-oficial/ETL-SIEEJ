-- Snapshot per publication: each PDF reissues the full register since 2018.
-- cve_ent + cve_mun: logical reference to cvegeo_municipalities (foreign tables admit no FK).
CREATE TABLE IF NOT EXISTS stg_fosas_clandestinas (
    publicacion_id   INTEGER  NOT NULL REFERENCES cat_publicaciones(id) ON DELETE CASCADE,
    consecutivo      INTEGER  NOT NULL,
    periodo          SMALLINT NOT NULL,
    denominacion     TEXT,
    cve_ent          SMALLINT NOT NULL,
    cve_mun          SMALLINT,
    fecha_inicio     DATE,
    fecha_fin        DATE,
    en_proceso       BOOLEAN  NOT NULL,
    pre_victimas_loc INTEGER,
    pre_victimas_ide INTEGER,
    pre_hom_ide      INTEGER,
    pre_muj_ide      INTEGER,
    estatus_loc      TEXT,
    PRIMARY KEY (publicacion_id, consecutivo, periodo)
);

CREATE INDEX IF NOT EXISTS idx_stg_fosas_clandestinas_municipio ON stg_fosas_clandestinas (cve_ent, cve_mun);

COMMENT ON TABLE stg_fosas_clandestinas IS
    'Sitios de inhumación clandestina en Jalisco, un renglón por sitio, periodo de procesamiento y publicación. Cifras preliminares y revisables.';
COMMENT ON COLUMN stg_fosas_clandestinas.publicacion_id IS 'Publicación (corte) de la que proviene el renglón.';
COMMENT ON COLUMN stg_fosas_clandestinas.consecutivo IS 'Número del sitio en la publicación; 0 para el sitio impreso como "oct-18".';
COMMENT ON COLUMN stg_fosas_clandestinas.periodo IS 'Número del periodo de procesamiento dentro del sitio (celdas combinadas en el PDF).';
COMMENT ON COLUMN stg_fosas_clandestinas.denominacion IS 'Nombre del sitio; NULL en ediciones que no lo publican (octubre 2022).';
COMMENT ON COLUMN stg_fosas_clandestinas.cve_ent IS 'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN stg_fosas_clandestinas.cve_mun IS 'Clave del municipio dentro de la entidad.';
COMMENT ON COLUMN stg_fosas_clandestinas.fecha_inicio IS 'Mes de inicio del procesamiento.';
COMMENT ON COLUMN stg_fosas_clandestinas.fecha_fin IS 'Mes de fin del procesamiento; NULL si sigue en proceso o no se publica.';
COMMENT ON COLUMN stg_fosas_clandestinas.en_proceso IS 'Verdadero cuando el PDF indica que el procesamiento no ha concluido.';
COMMENT ON COLUMN stg_fosas_clandestinas.pre_victimas_loc IS 'Total preliminar de víctimas localizadas (PFSI, osamentas y segmentos de una persona).';
COMMENT ON COLUMN stg_fosas_clandestinas.pre_victimas_ide IS 'Total preliminar de víctimas identificadas.';
COMMENT ON COLUMN stg_fosas_clandestinas.pre_hom_ide IS 'Hombres preliminarmente identificados.';
COMMENT ON COLUMN stg_fosas_clandestinas.pre_muj_ide IS 'Mujeres preliminarmente identificadas.';
COMMENT ON COLUMN stg_fosas_clandestinas.estatus_loc IS 'Texto publicado en lugar del total de víctimas localizadas (ej. COMPETENCIA FGR, IJCF PROCESANDO).';
