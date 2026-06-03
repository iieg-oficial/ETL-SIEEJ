CREATE UNLOGGED TABLE IF NOT EXISTS stg_est_jal (
    id INTEGER NOT NULL,
    actualizacion_id INTEGER NOT NULL REFERENCES cat_actualizaciones(id),
    clee TEXT NOT NULL,
    nombre_establecimiento TEXT,
    razon_social TEXT,
    latitud FLOAT,
    longitud FLOAT,
    fecha_alta DATE,
    nombre_asentamiento TEXT,
    ageb TEXT,
    localidad_id INTEGER REFERENCES cat_localidades(id),
    sector_id INTEGER REFERENCES cat_sectores(id),
    subsector_id INTEGER REFERENCES cat_subsectores(id),
    rama_id INTEGER REFERENCES cat_ramas(id),
    subrama_id INTEGER REFERENCES cat_subramas(id),
    clase_actividad_id INTEGER REFERENCES cat_clases_actividad(id),
    rango_personal_id INTEGER REFERENCES cat_rangos_personal(id),
    tipo_establecimiento_id INTEGER REFERENCES cat_tipos_establecimientos(id),
    PRIMARY KEY (id, actualizacion_id)
);

COMMENT ON TABLE stg_est_jal IS 'Establecimientos DENUE de Jalisco a nivel municipio y localidad';
COMMENT ON COLUMN stg_est_jal.id IS 'Identificador DENUE del establecimiento';
COMMENT ON COLUMN stg_est_jal.actualizacion_id IS 'Periodo de actualización DENUE';
COMMENT ON COLUMN stg_est_jal.clee IS 'Clave Única de Establecimiento (CLEE)';
COMMENT ON COLUMN stg_est_jal.nombre_establecimiento IS 'Nombre del establecimiento';
COMMENT ON COLUMN stg_est_jal.razon_social IS 'Razón social';
COMMENT ON COLUMN stg_est_jal.latitud IS 'Latitud geográfica';
COMMENT ON COLUMN stg_est_jal.longitud IS 'Longitud geográfica';
COMMENT ON COLUMN stg_est_jal.fecha_alta IS 'Fecha de alta del establecimiento en DENUE';
COMMENT ON COLUMN stg_est_jal.nombre_asentamiento IS 'Nombre del asentamiento humano';
COMMENT ON COLUMN stg_est_jal.ageb IS 'Área geoestadística básica (AGEB)';
COMMENT ON COLUMN stg_est_jal.localidad_id IS 'Localidad del establecimiento';
COMMENT ON COLUMN stg_est_jal.sector_id IS 'Sector económico SCIAN';
COMMENT ON COLUMN stg_est_jal.subsector_id IS 'Subsector económico SCIAN';
COMMENT ON COLUMN stg_est_jal.rama_id IS 'Rama económica SCIAN';
COMMENT ON COLUMN stg_est_jal.subrama_id IS 'Subrama económica SCIAN';
COMMENT ON COLUMN stg_est_jal.clase_actividad_id IS 'Clase de actividad económica SCIAN';
COMMENT ON COLUMN stg_est_jal.rango_personal_id IS 'Rango de personal ocupado';
COMMENT ON COLUMN stg_est_jal.tipo_establecimiento_id IS 'Tipo de unidad económica (fijo o semifijo)';

CREATE UNLOGGED TABLE IF NOT EXISTS stg_est_ent (
    id SERIAL PRIMARY KEY,
    entidad_id INTEGER NOT NULL,
    actualizacion_id INTEGER NOT NULL REFERENCES cat_actualizaciones(id),
    sector_id INTEGER REFERENCES cat_sectores(id),
    subsector_id INTEGER REFERENCES cat_subsectores(id),
    rama_id INTEGER REFERENCES cat_ramas(id),
    subrama_id INTEGER REFERENCES cat_subramas(id),
    clase_actividad_id INTEGER REFERENCES cat_clases_actividad(id),
    num_establecimientos INTEGER NOT NULL,
    CONSTRAINT uq_resumen_entidad_act_clase UNIQUE (entidad_id, actualizacion_id, clase_actividad_id)
);

COMMENT ON TABLE stg_est_ent IS 'Resumen de establecimientos DENUE por entidad y clase de actividad económica';
COMMENT ON COLUMN stg_est_ent.entidad_id IS 'Clave de la entidad federativa (1-32)';
COMMENT ON COLUMN stg_est_ent.actualizacion_id IS 'Periodo de actualización DENUE';
COMMENT ON COLUMN stg_est_ent.sector_id IS 'Sector económico SCIAN';
COMMENT ON COLUMN stg_est_ent.subsector_id IS 'Subsector económico SCIAN';
COMMENT ON COLUMN stg_est_ent.rama_id IS 'Rama económica SCIAN';
COMMENT ON COLUMN stg_est_ent.subrama_id IS 'Subrama económica SCIAN';
COMMENT ON COLUMN stg_est_ent.clase_actividad_id IS 'Clase de actividad económica SCIAN';
COMMENT ON COLUMN stg_est_ent.num_establecimientos IS 'Número de establecimientos';
