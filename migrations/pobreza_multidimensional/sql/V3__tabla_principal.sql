-- =======================================================================
-- V3__tabla_principal.sql  |  Pipeline: pobreza_multidimensional
-- Microdatos CONEVAL — Medición de la Pobreza Multidimensional (MMP).
-- Años: 2016, 2018, 2020, 2022.
-- =======================================================================

CREATE TABLE IF NOT EXISTS public.stg_pobreza_multidimensional_datos (
    id           SERIAL PRIMARY KEY,
    anio         SMALLINT NOT NULL,
    folioviv     BIGINT   NOT NULL,
    foliohog     INTEGER  NOT NULL,
    numren       INTEGER  NOT NULL,

    -- Variables de diseño muestral
    est_dis      INTEGER,
    upm          INTEGER,
    factor       FLOAT,

    -- Localidad y área
    tam_loc      SMALLINT,
    rururb       FLOAT,

    -- Geografía
    ent          INTEGER,
    ubica_geo    INTEGER,
    municipio_id INTEGER,   -- resuelto desde cvegeo_municipalities

    -- Datos demográficos
    edad         INTEGER,
    sexo         SMALLINT,
    parentesco   INTEGER,
    anac_e       INTEGER,

    -- Indicadores de carencia
    ic_rezedu    FLOAT,
    inas_esc     FLOAT,
    niv_ed       FLOAT,
    ic_asalud    FLOAT,
    ic_segsoc    FLOAT,
    sa_dir       FLOAT,
    ss_dir       FLOAT,
    s_salud      FLOAT,
    par          FLOAT,
    jef_ss       FLOAT,
    cony_ss      FLOAT,
    hijo_ss      FLOAT,
    pea          FLOAT,
    jub          FLOAT,
    pam          FLOAT,
    ing_pam      FLOAT,
    ic_cv        FLOAT,
    icv_pisos    FLOAT,
    icv_muros    FLOAT,
    icv_techos   FLOAT,
    icv_hac      FLOAT,
    ic_sbv       FLOAT,
    isb_agua     FLOAT,
    isb_dren     FLOAT,
    isb_luz      FLOAT,
    isb_combus   FLOAT,
    ic_ali_nc    FLOAT,
    id_men       FLOAT,
    tot_iaad     FLOAT,
    tot_iamen    FLOAT,
    ins_ali      FLOAT,
    ic_ali       FLOAT,

    -- Indicadores de bienestar y pobreza
    lca          FLOAT,
    dch          FLOAT,
    plp_e        FLOAT,
    plp          FLOAT,
    pobreza      FLOAT,
    pobreza_e    FLOAT,
    pobreza_m    FLOAT,
    vul_car      FLOAT,
    vul_ing      FLOAT,
    no_pobv      FLOAT,
    i_privacion  FLOAT,
    carencias    FLOAT,
    carencias3   FLOAT,
    cuadrantes   SMALLINT,

    -- Indicadores de profundidad e intensidad
    prof1        FLOAT,
    prof_e1      FLOAT,
    profun       FLOAT,
    int_pob      FLOAT,
    int_pobe     FLOAT,
    int_vulcar   FLOAT,
    int_caren    FLOAT,

    -- Ingreso y hogar
    tamhogesc    FLOAT,
    ictpc        FLOAT,
    ict          FLOAT,
    ing_mon      FLOAT,
    ing_lab      FLOAT,
    ing_ren      FLOAT,
    ing_tra      FLOAT,
    nomon        FLOAT,
    pago_esp     FLOAT,
    reg_esp      FLOAT,

    -- Lengua indígena y discapacidad (ausentes en 2016/2018)
    hli          FLOAT,
    discap       FLOAT,

    CONSTRAINT uq_pm_datos_llave UNIQUE (folioviv, foliohog, numren, anio)
);

CREATE INDEX IF NOT EXISTS ix_pm_datos_anio
    ON public.stg_pobreza_multidimensional_datos (anio);

CREATE INDEX IF NOT EXISTS ix_pm_datos_ubica_geo
    ON public.stg_pobreza_multidimensional_datos (ubica_geo);

CREATE INDEX IF NOT EXISTS ix_pm_datos_municipio_id
    ON public.stg_pobreza_multidimensional_datos (municipio_id);

CREATE INDEX IF NOT EXISTS ix_pm_datos_ent
    ON public.stg_pobreza_multidimensional_datos (ent);
