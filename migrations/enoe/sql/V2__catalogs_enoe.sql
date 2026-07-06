CREATE TABLE IF NOT EXISTS cat_sector (
    id          INTEGER PRIMARY KEY,
    descripcion TEXT    NOT NULL
);

COMMENT ON TABLE  cat_sector            IS 'Sector económico del empleo principal (variable rama_est1 ENOE): primario, secundario, terciario';
COMMENT ON COLUMN cat_sector.id          IS 'Código ENOE rama_est1 (0=no aplica, 1=primario, 2=secundario, 3=terciario, 4=no especificado)';
COMMENT ON COLUMN cat_sector.descripcion IS 'Nombre del sector económico';

-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cat_ocupacion (
    id          INTEGER PRIMARY KEY,
    descripcion TEXT    NOT NULL
);

COMMENT ON TABLE  cat_ocupacion            IS 'Clasificación de ocupación principal en 11 grandes grupos (variable c_ocu11c ENOE)';
COMMENT ON COLUMN cat_ocupacion.id          IS 'Código ENOE c_ocu11c (0=no aplica, 1–11 grupos de ocupación)';
COMMENT ON COLUMN cat_ocupacion.descripcion IS 'Nombre del grupo de ocupación';

-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cat_situacion_trabajo (
    id          INTEGER PRIMARY KEY,
    descripcion TEXT    NOT NULL
);

COMMENT ON TABLE  cat_situacion_trabajo            IS 'Situación del empleo respecto al sector informal (variable tue_ppal ENOE). Base para el cálculo de TIL1 del INEGI';
COMMENT ON COLUMN cat_situacion_trabajo.id          IS 'Código ENOE tue_ppal (0=no aplica, 1=sector informal, 2=fuera del sector informal)';
COMMENT ON COLUMN cat_situacion_trabajo.descripcion IS 'Descripción de la situación de trabajo';

-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cat_tipo_localidad (
    id          INTEGER PRIMARY KEY,
    descripcion TEXT    NOT NULL
);

COMMENT ON TABLE  cat_tipo_localidad            IS 'Tamaño de localidad de residencia del entrevistado (variable t_loc_tri ENOE)';
COMMENT ON COLUMN cat_tipo_localidad.id          IS 'Código ENOE t_loc_tri (1=≥100k hab, 2=15k-99k, 3=2.5k-14k, 4=<2.5k)';
COMMENT ON COLUMN cat_tipo_localidad.descripcion IS 'Rango de tamaño de la localidad';

-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cat_estado_civil (
    id          INTEGER PRIMARY KEY,
    descripcion TEXT    NOT NULL
);

COMMENT ON TABLE  cat_estado_civil            IS 'Estado civil o conyugal del entrevistado (variable e_con ENOE)';
COMMENT ON COLUMN cat_estado_civil.id          IS 'Código ENOE e_con (1=unión libre, 2=separado, 3=divorciado, 4=viudo, 5=casado, 6=soltero, 9=no sabe)';
COMMENT ON COLUMN cat_estado_civil.descripcion IS 'Descripción del estado civil';

-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cat_nivel_educativo (
    id          INTEGER PRIMARY KEY,
    descripcion TEXT    NOT NULL
);

COMMENT ON TABLE  cat_nivel_educativo            IS 'Nivel de instrucción del entrevistado (variable cs_p13_1 ENOE)';
COMMENT ON COLUMN cat_nivel_educativo.id          IS 'Código ENOE cs_p13_1 (0=ninguno, 1=preescolar, 2=primaria, 3=secundaria, 4=preparatoria, 5=normal, 6=carrera técnica, 7=profesional, 8=maestría, 9=doctorado, 99=no sabe)';
COMMENT ON COLUMN cat_nivel_educativo.descripcion IS 'Nombre del nivel educativo';
