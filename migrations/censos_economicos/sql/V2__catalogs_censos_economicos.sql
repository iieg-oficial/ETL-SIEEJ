CREATE TABLE IF NOT EXISTS cat_censos (
    id               SERIAL PRIMARY KEY,
    anio             INTEGER NOT NULL UNIQUE,
    descripcion      TEXT    NOT NULL,
    fecha_publicacion DATE   NOT NULL,
    fuente           TEXT
);

COMMENT ON TABLE  cat_censos IS 'Catalogo de censos economicos INEGI';
COMMENT ON COLUMN cat_censos.anio IS 'Anio del censo economico';
COMMENT ON COLUMN cat_censos.descripcion IS 'Descripcion del censo';
COMMENT ON COLUMN cat_censos.fecha_publicacion IS 'Fecha de publicacion oficial';
COMMENT ON COLUMN cat_censos.fuente IS 'Institucion fuente del dato';

CREATE TABLE IF NOT EXISTS cat_clasificadores_codigos (
    id            INTEGER PRIMARY KEY,
    clasificador  TEXT NOT NULL
);

COMMENT ON TABLE  cat_clasificadores_codigos IS 'Niveles de clasificacion SCIAN: Gran sector, Sector, Subsector, Rama, Subrama, Clase';
COMMENT ON COLUMN cat_clasificadores_codigos.id IS 'Nivel jerarquico (1=Gran sector, 6=Clase)';
COMMENT ON COLUMN cat_clasificadores_codigos.clasificador IS 'Nombre del nivel de clasificacion';

CREATE TABLE IF NOT EXISTS cat_actividades_economicas (
    id          SERIAL PRIMARY KEY,
    censo_id    INTEGER NOT NULL REFERENCES cat_censos(id),
    codigo      TEXT,
    descripcion TEXT    NOT NULL,
    codigo_id   INTEGER NOT NULL REFERENCES cat_clasificadores_codigos(id),
    CONSTRAINT uq_actividad_codigo_clas_censo UNIQUE (codigo, codigo_id, censo_id)
);

COMMENT ON TABLE  cat_actividades_economicas IS 'Codigos de actividad economica SCIAN por censo';
COMMENT ON COLUMN cat_actividades_economicas.censo_id IS 'Referencia al censo economico';
COMMENT ON COLUMN cat_actividades_economicas.codigo IS 'Codigo SCIAN de la actividad economica';
COMMENT ON COLUMN cat_actividades_economicas.descripcion IS 'Descripcion de la actividad economica';
COMMENT ON COLUMN cat_actividades_economicas.codigo_id IS 'Nivel jerarquico del codigo SCIAN';

CREATE TABLE IF NOT EXISTS cat_estratos (
    id          INTEGER PRIMARY KEY,
    codigo      INTEGER,
    descripcion TEXT NOT NULL
);

COMMENT ON TABLE  cat_estratos IS 'Estratos de tamano de establecimientos por numero de personal ocupado';
COMMENT ON COLUMN cat_estratos.id IS 'Identificador interno';
COMMENT ON COLUMN cat_estratos.codigo IS 'Clave INEGI del estrato (null = Suma de estratos)';
COMMENT ON COLUMN cat_estratos.descripcion IS 'Descripcion del estrato';
