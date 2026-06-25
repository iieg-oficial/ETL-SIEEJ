CREATE TABLE IF NOT EXISTS stg_enoe (
    id                    SERIAL    PRIMARY KEY,
    anio                  SMALLINT  NOT NULL,
    trimestre             SMALLINT  NOT NULL,
    -- Identificadores de persona (clave natural ENOE)
    entidad_id            SMALLINT  NOT NULL,
    municipio_id          SMALLINT,
    tipo_localidad_id     SMALLINT  REFERENCES cat_tipo_localidad(id),
    cd_a                  SMALLINT  NOT NULL,
    con                   INTEGER   NOT NULL,
    v_sel                 SMALLINT  NOT NULL,
    n_hog                 SMALLINT  NOT NULL,
    h_mud                 SMALLINT  NOT NULL,
    n_ent                 SMALLINT  NOT NULL,
    n_ren                 SMALLINT  NOT NULL,
    -- Sociodemográfico
    eda                   SMALLINT,
    nac_anio              SMALLINT,
    sex                   SMALLINT,
    habla_lengua_indigena BOOLEAN,
    n_inf                 SMALLINT,
    estado_civil_id       SMALLINT  REFERENCES cat_estado_civil(id),
    nivel_educativo_id    SMALLINT  REFERENCES cat_nivel_educativo(id),
    cs_p13_2              SMALLINT,
    -- Condición de empleo
    clase1                SMALLINT,
    clase2                SMALLINT,
    clase3                SMALLINT,
    dur9c                 SMALLINT,
    hrsocup               REAL,
    ingocup               REAL,
    ma48me1sm             REAL,
    emp_ppal              SMALLINT,
    sector_id             SMALLINT  REFERENCES cat_sector(id),
    ocupacion_id          SMALLINT  REFERENCES cat_ocupacion(id),
    situacion_trabajo_id  SMALLINT  REFERENCES cat_situacion_trabajo(id),
    seg_soc               SMALLINT,
    pre_asa               SMALLINT,
    -- Factor de expansión
    fac                   REAL,
    -- Indicadores derivados (INEGI TIL1)
    es_pea                BOOLEAN,
    es_ocupado            BOOLEAN,
    es_desocupado         BOOLEAN,
    es_informal           BOOLEAN,
    CONSTRAINT uq_stg_enoe_persona UNIQUE (anio, trimestre, cd_a, entidad_id, con, v_sel, n_hog, h_mud, n_ent, n_ren)
);

COMMENT ON TABLE stg_enoe IS 'Microdatos ENOE a nivel persona para Jalisco (ent=14). Fuente: INEGI, tabla SDEM. Un registro por persona entrevistada por trimestre.';

COMMENT ON COLUMN stg_enoe.id                    IS 'Llave primaria autoincremental';
COMMENT ON COLUMN stg_enoe.anio                  IS 'Año de levantamiento';
COMMENT ON COLUMN stg_enoe.trimestre             IS 'Trimestre de levantamiento (1–4)';
COMMENT ON COLUMN stg_enoe.entidad_id            IS 'Clave de entidad federativa INEGI (siempre 14 = Jalisco)';
COMMENT ON COLUMN stg_enoe.municipio_id          IS 'Clave de municipio INEGI (variable mun)';
COMMENT ON COLUMN stg_enoe.tipo_localidad_id     IS 'Tamaño de localidad de residencia (variable t_loc_tri)';
COMMENT ON COLUMN stg_enoe.cd_a                  IS 'Ciudad o área de levantamiento (componente de clave de persona)';
COMMENT ON COLUMN stg_enoe.con                   IS 'Número de conglomerado (componente de clave de persona)';
COMMENT ON COLUMN stg_enoe.v_sel                 IS 'Número de vivienda seleccionada (componente de clave de persona)';
COMMENT ON COLUMN stg_enoe.n_hog                 IS 'Número de hogar dentro de la vivienda (componente de clave de persona)';
COMMENT ON COLUMN stg_enoe.h_mud                 IS 'Indicador de mudanza del hogar (componente de clave de persona)';
COMMENT ON COLUMN stg_enoe.n_ent                 IS 'Número de entrevista del hogar (componente de clave de persona)';
COMMENT ON COLUMN stg_enoe.n_ren                 IS 'Número de renglón (identificador de persona dentro del hogar)';
COMMENT ON COLUMN stg_enoe.eda                   IS 'Edad en años cumplidos al momento del levantamiento';
COMMENT ON COLUMN stg_enoe.nac_anio              IS 'Año de nacimiento';
COMMENT ON COLUMN stg_enoe.sex                   IS 'Sexo (1=hombre, 2=mujer)';
COMMENT ON COLUMN stg_enoe.habla_lengua_indigena IS 'Habla alguna lengua indígena (derivado de cs_p17=1)';
COMMENT ON COLUMN stg_enoe.n_inf                 IS 'Número de hijos nacidos vivos (mujeres; variable n_hij)';
COMMENT ON COLUMN stg_enoe.estado_civil_id       IS 'Estado civil o conyugal (variable e_con)';
COMMENT ON COLUMN stg_enoe.nivel_educativo_id    IS 'Nivel de instrucción máximo alcanzado (variable cs_p13_1)';
COMMENT ON COLUMN stg_enoe.cs_p13_2             IS 'Grado cursado dentro del nivel educativo (variable cs_p13_2)';
COMMENT ON COLUMN stg_enoe.clase1                IS 'Clasificación de actividad económica: 1=PEA, 2=PNEA (variable clase1 SDEM)';
COMMENT ON COLUMN stg_enoe.clase2                IS 'Subclasificación: 1=ocupado, 2=desocupado, 3=PNEA disponible, 4=PNEA no disponible (variable clase2 SDEM)';
COMMENT ON COLUMN stg_enoe.clase3                IS 'Subclasificación adicional de condición de actividad (variable clase3 SDEM)';
COMMENT ON COLUMN stg_enoe.dur9c                 IS 'Horas trabajadas en la semana de referencia agrupadas en 9 categorías (variable dur9c)';
COMMENT ON COLUMN stg_enoe.hrsocup               IS 'Horas trabajadas en el empleo principal durante la semana de referencia';
COMMENT ON COLUMN stg_enoe.ingocup               IS 'Ingreso mensual por ocupación en pesos corrientes (variable ingocup)';
COMMENT ON COLUMN stg_enoe.ma48me1sm             IS 'Múltiplo del salario mínimo mensual correspondiente al ingreso (variable ma48me1sm)';
COMMENT ON COLUMN stg_enoe.emp_ppal              IS 'Posición en el trabajo principal (variable emp_ppal): obrero, empleador, cuenta propia, etc.';
COMMENT ON COLUMN stg_enoe.sector_id             IS 'Sector económico del empleo principal agrupado (variable rama_est1)';
COMMENT ON COLUMN stg_enoe.ocupacion_id          IS 'Grupo de ocupación principal en 11 categorías (variable c_ocu11c)';
COMMENT ON COLUMN stg_enoe.situacion_trabajo_id  IS 'Clasificación informal/formal del empleo principal (variable tue_ppal). Clave para TIL1 INEGI';
COMMENT ON COLUMN stg_enoe.seg_soc               IS 'Acceso a seguridad social por el trabajo: 1=con acceso, 2=sin acceso, 3=no especificado (variable seg_soc)';
COMMENT ON COLUMN stg_enoe.pre_asa               IS 'Prestaciones laborales: 1=con prestaciones, 2=sin prestaciones, 3=no especificado (variable pre_asa)';
COMMENT ON COLUMN stg_enoe.fac                   IS 'Factor de expansión trimestral (variable fac_tri). Pondera al universo de población';
COMMENT ON COLUMN stg_enoe.es_pea                IS 'Pertenece a la Población Económicamente Activa (clase1=1)';
COMMENT ON COLUMN stg_enoe.es_ocupado            IS 'Está ocupado (clase2=1)';
COMMENT ON COLUMN stg_enoe.es_desocupado         IS 'Está desocupado dentro de la PEA (clase2=2)';
COMMENT ON COLUMN stg_enoe.es_informal           IS 'Empleo informal según metodología TIL1 INEGI: ocupado (clase2=1) en el sector informal (tue_ppal=1)';
