-- =============================================================================
-- V5__comments_enoe_microdatos.sql  |  Pipeline: enoe_microdatos
-- COMMENT ON TABLE / FOREIGN TABLE / MATERIALIZED VIEW y columnas
-- para todos los objetos del esquema enoe_microdatos.
-- =============================================================================

-- =============================================================================
-- TABLAS FORÁNEAS (FDW)
-- =============================================================================

COMMENT ON FOREIGN TABLE cvegeo_states IS
    'Tabla foránea (FDW → BD cvegeo) con el catálogo de entidades federativas de México. '
    'Se usa para resolver entidad_id a nombre en el gold layer.';
COMMENT ON COLUMN cvegeo_states.id IS 'Identificador interno.';
COMMENT ON COLUMN cvegeo_states.cve_ent IS 'Clave geoestadística de la entidad federativa (01-32).';
COMMENT ON COLUMN cvegeo_states.nom_ent IS 'Nombre oficial de la entidad federativa.';

COMMENT ON FOREIGN TABLE cvegeo_municipalities IS
    'Tabla foránea (FDW → BD cvegeo) con el catálogo de municipios de México. '
    'Se usa para resolver (entidad_id, municipio_id) a nombre en el gold layer.';
COMMENT ON COLUMN cvegeo_municipalities.id IS 'Identificador interno.';
COMMENT ON COLUMN cvegeo_municipalities.cvegeo IS 'Clave geoestadística completa de 5 dígitos (ent+mun).';
COMMENT ON COLUMN cvegeo_municipalities.cve_ent IS 'Clave de la entidad federativa.';
COMMENT ON COLUMN cvegeo_municipalities.cve_mun IS 'Clave del municipio dentro de la entidad.';
COMMENT ON COLUMN cvegeo_municipalities.nomgeo IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN cvegeo_municipalities.nom_ent IS 'Nombre de la entidad a la que pertenece el municipio.';

-- =============================================================================
-- CATÁLOGOS
-- =============================================================================

COMMENT ON TABLE cat_enoe_sector IS
    'Catálogo de sectores económicos de la ENOE (rama_est1). '
    'Clasifica la actividad del trabajo principal: Primario, Secundario, Terciario.';
COMMENT ON COLUMN cat_enoe_sector.id IS 'Identificador del sector (0=No aplica, 1=Primario, 2=Secundario, 3=Terciario, 4=No especificado).';
COMMENT ON COLUMN cat_enoe_sector.descripcion IS 'Nombre del sector económico.';

COMMENT ON TABLE cat_enoe_ocupacion IS
    'Catálogo de grupos de ocupación de la ENOE (c_ocu11c). '
    'Clasifica el tipo de trabajo en 12 grupos más No aplica y No especificado.';
COMMENT ON COLUMN cat_enoe_ocupacion.id IS 'Identificador del grupo de ocupación (0=No aplica, 1-12=grupos, 13=No especificado).';
COMMENT ON COLUMN cat_enoe_ocupacion.descripcion IS 'Descripción del grupo de ocupación (ej. Profesionales, técnicos y trabajadores del arte).';

COMMENT ON TABLE cat_enoe_situacion_trabajo IS
    'Catálogo de situación en el trabajo de la ENOE (pos_ocu). '
    'Clasifica la posición ocupacional: subordinado/remunerado, empleador, cuenta propia, sin pago.';
COMMENT ON COLUMN cat_enoe_situacion_trabajo.id IS 'Identificador de la situación (0=No aplica, 1=Subordinados remunerados, 2=Empleadores, 3=Cuenta propia, 4=Sin pago, 5=No especificado).';
COMMENT ON COLUMN cat_enoe_situacion_trabajo.descripcion IS 'Descripción de la situación en el trabajo.';

-- =============================================================================
-- TABLA PRINCIPAL
-- =============================================================================

COMMENT ON TABLE stg_enoe_microdatos IS
    'Tabla de staging de la Encuesta Nacional de Ocupación y Empleo (ENOE) — microdatos. '
    'Contiene registros individuales de personas a partir de los archivos SDEM, COE1 y COE2 '
    'publicados por INEGI. Filtrada a Jalisco (entidad_id=14). '
    'Fuente: https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/';

COMMENT ON COLUMN stg_enoe_microdatos.id IS 'Identificador interno autoincremental.';
COMMENT ON COLUMN stg_enoe_microdatos.anio IS 'Año de levantamiento de la encuesta.';
COMMENT ON COLUMN stg_enoe_microdatos.trimestre IS 'Trimestre de levantamiento (1-4).';

-- Diseño muestral
COMMENT ON COLUMN stg_enoe_microdatos.r_def IS 'Resultado definitivo de la entrevista.';
COMMENT ON COLUMN stg_enoe_microdatos.est IS 'Estrato de diseño muestral.';
COMMENT ON COLUMN stg_enoe_microdatos.est_d_tri IS 'Estrato de diseño muestral trimestral.';
COMMENT ON COLUMN stg_enoe_microdatos.est_d_men IS 'Estrato de diseño muestral mensual.';
COMMENT ON COLUMN stg_enoe_microdatos.ageb IS 'Clave del Área Geoestadística Básica (AGEB).';
COMMENT ON COLUMN stg_enoe_microdatos.upm IS 'Unidad Primaria de Muestreo.';
COMMENT ON COLUMN stg_enoe_microdatos.d_sem IS 'Semana de levantamiento.';
COMMENT ON COLUMN stg_enoe_microdatos.n_pro_viv IS 'Número progresivo de vivienda en la UPM.';
COMMENT ON COLUMN stg_enoe_microdatos.per IS 'Periodo de levantamiento dentro del trimestre.';
COMMENT ON COLUMN stg_enoe_microdatos.tipo IS 'Tipo de resultado de la entrevista.';
COMMENT ON COLUMN stg_enoe_microdatos.mes_cal IS 'Mes calendario de levantamiento.';

-- Identificadores de persona (clave natural)
COMMENT ON COLUMN stg_enoe_microdatos.cd_a IS 'Ciudad o área de levantamiento; parte de la clave natural del registro.';
COMMENT ON COLUMN stg_enoe_microdatos.entidad_id IS 'Clave de la entidad federativa (FK implícita a cvegeo_states.cve_ent). Siempre 14 (Jalisco).';
COMMENT ON COLUMN stg_enoe_microdatos.con IS 'Número de control del hogar; parte de la clave natural.';
COMMENT ON COLUMN stg_enoe_microdatos.v_sel IS 'Vivienda seleccionada; parte de la clave natural.';
COMMENT ON COLUMN stg_enoe_microdatos.n_hog IS 'Número del hogar dentro de la vivienda.';
COMMENT ON COLUMN stg_enoe_microdatos.h_mud IS 'Indica si el hogar se mudó (hogar sustituto).';
COMMENT ON COLUMN stg_enoe_microdatos.n_ent IS 'Número de la entrevista dentro del hogar.';
COMMENT ON COLUMN stg_enoe_microdatos.n_ren IS 'Número de renglón (persona dentro del hogar).';

-- Geografía
COMMENT ON COLUMN stg_enoe_microdatos.loc IS 'Clave de localidad (texto, puede contener letras).';
COMMENT ON COLUMN stg_enoe_microdatos.municipio_id IS 'Clave del municipio (FK implícita a cvegeo_municipalities.cve_mun).';
COMMENT ON COLUMN stg_enoe_microdatos.tipo_localidad_id IS 'Tamaño de localidad trimestral (clasificación INEGI).';
COMMENT ON COLUMN stg_enoe_microdatos.t_loc_men IS 'Tamaño de localidad mensual.';
COMMENT ON COLUMN stg_enoe_microdatos.ur IS 'Zona urbano/rural (1=Urbano, 2=Rural).';
COMMENT ON COLUMN stg_enoe_microdatos.zona IS 'Zona geográfica de la encuesta.';

-- Sociodemográfico
COMMENT ON COLUMN stg_enoe_microdatos.c_res IS 'Condición de residencia habitual en la vivienda.';
COMMENT ON COLUMN stg_enoe_microdatos.par_c IS 'Parentesco con el jefe del hogar (codificado).';
COMMENT ON COLUMN stg_enoe_microdatos.sex IS 'Sexo (1=Hombre, 2=Mujer).';
COMMENT ON COLUMN stg_enoe_microdatos.eda IS 'Edad en años cumplidos.';
COMMENT ON COLUMN stg_enoe_microdatos.nac_dia IS 'Día de nacimiento.';
COMMENT ON COLUMN stg_enoe_microdatos.nac_mes IS 'Mes de nacimiento.';
COMMENT ON COLUMN stg_enoe_microdatos.nac_anio IS 'Año de nacimiento.';
COMMENT ON COLUMN stg_enoe_microdatos.l_nac_c IS 'Entidad o país de nacimiento (codificado).';

-- Educación
COMMENT ON COLUMN stg_enoe_microdatos.cs_p12 IS 'Sabe leer y escribir (1=Sí, 2=No).';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p13_1 IS 'Asiste actualmente a la escuela (1=Sí, 2=No).';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p13_2 IS 'Ha asistido a la escuela anteriormente.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p14_c IS 'Último nivel de instrucción aprobado (codificado).';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p15 IS 'Último grado aprobado en el nivel de instrucción.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p16 IS 'Título o diploma obtenido (1=Sí, 2=No).';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p17 IS 'Área de estudio de la carrera o especialidad.';
COMMENT ON COLUMN stg_enoe_microdatos.niv_ins IS 'Nivel de instrucción recodificado.';
COMMENT ON COLUMN stg_enoe_microdatos.anios_esc IS 'Años de escolaridad aprobados.';

-- Hijos
COMMENT ON COLUMN stg_enoe_microdatos.n_hij IS 'Número de hijos nacidos vivos (mujeres).';
COMMENT ON COLUMN stg_enoe_microdatos.hij5c IS 'Número de hijos en categorías de 5 grupos.';

-- Estado civil
COMMENT ON COLUMN stg_enoe_microdatos.e_con IS 'Estado conyugal (1=Unido, 2=Separado, 3=Divorciado, 4=Viudo, 5=Soltero).';

-- Migración
COMMENT ON COLUMN stg_enoe_microdatos.cs_p20a_1 IS 'Entidad o país donde vivía hace 5 años.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p20a_c IS 'Clave de entidad/país de residencia hace 5 años.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p20b_1 IS 'Entidad o país donde nació.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p20b_c IS 'Clave de entidad/país de nacimiento.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p20c_1 IS 'Municipio de residencia hace 5 años.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_ad_mot IS 'Motivo de migración (codificado).';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p21_des IS 'Descripción abierta del motivo de migración.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_ad_des IS 'Motivo de migración recodificado.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_nr_mot IS 'Motivo por el que no reside habitualmente.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_p23_des IS 'Descripción abierta del motivo de no residencia.';
COMMENT ON COLUMN stg_enoe_microdatos.cs_nr_ori IS 'Entidad de origen del no residente habitual.';

-- Clasificación de actividad
COMMENT ON COLUMN stg_enoe_microdatos.clase1 IS 'Condición de actividad económica (1=PEA, 2=PNEA).';
COMMENT ON COLUMN stg_enoe_microdatos.clase2 IS 'Condición de ocupación (1=Ocupado, 2=Desocupado).';
COMMENT ON COLUMN stg_enoe_microdatos.clase3 IS 'Condición de ocupación desagregada (ocupado, desocupado, disponible, no disponible).';
COMMENT ON COLUMN stg_enoe_microdatos.seg_soc IS 'Acceso a servicios de salud por la ocupación principal (1=Con, 2=Sin).';
COMMENT ON COLUMN stg_enoe_microdatos.rama IS 'Rama de actividad económica (1 dígito SCIAN adaptado ENOE).';
COMMENT ON COLUMN stg_enoe_microdatos.rama_est2 IS 'Rama de actividad económica estrato 2 (versiones históricas).';
COMMENT ON COLUMN stg_enoe_microdatos.ing7c IS 'Ingreso laboral en 7 categorías.';
COMMENT ON COLUMN stg_enoe_microdatos.dur9c IS 'Horas trabajadas en 9 categorías.';
COMMENT ON COLUMN stg_enoe_microdatos.emple7c IS 'Tamaño del establecimiento en 7 categorías.';
COMMENT ON COLUMN stg_enoe_microdatos.medica5c IS 'Acceso a atención médica en 5 categorías.';
COMMENT ON COLUMN stg_enoe_microdatos.buscar5c IS 'Búsqueda de empleo en 5 categorías.';
COMMENT ON COLUMN stg_enoe_microdatos.dur_est IS 'Duración de la jornada laboral (categorías estrato).';
COMMENT ON COLUMN stg_enoe_microdatos.ambito1 IS 'Ámbito de la ocupación principal (1=Agropecuario, 2=No agropecuario).';
COMMENT ON COLUMN stg_enoe_microdatos.ambito2 IS 'Ámbito de la ocupación secundaria.';
COMMENT ON COLUMN stg_enoe_microdatos.scian IS 'Clave de subsector SCIAN de la actividad principal.';

-- Búsqueda y disponibilidad
COMMENT ON COLUMN stg_enoe_microdatos.dispo IS 'Disponibilidad para trabajar (población no ocupada).';
COMMENT ON COLUMN stg_enoe_microdatos.nodispo IS 'Razón de no disponibilidad para trabajar.';
COMMENT ON COLUMN stg_enoe_microdatos.c_inac5c IS 'Condición de inactividad en 5 categorías.';
COMMENT ON COLUMN stg_enoe_microdatos.pnea_est IS 'Estrato de la población no económicamente activa.';
COMMENT ON COLUMN stg_enoe_microdatos.busqueda IS 'Tipo de búsqueda de empleo realizada.';
COMMENT ON COLUMN stg_enoe_microdatos.d_ant_lab IS 'Tiene antecedentes laborales (1=Sí, 2=No).';
COMMENT ON COLUMN stg_enoe_microdatos.d_cexp_est IS 'Experiencia laboral estrato.';
COMMENT ON COLUMN stg_enoe_microdatos.dur_des IS 'Duración del desempleo en semanas.';

-- Informalidad (TIL1)
COMMENT ON COLUMN stg_enoe_microdatos.tue1 IS 'Componente 1 de la tasa de informalidad laboral (TIL1): sector informal.';
COMMENT ON COLUMN stg_enoe_microdatos.tue2 IS 'Componente 2 de TIL1: trabajo doméstico remunerado.';
COMMENT ON COLUMN stg_enoe_microdatos.tue3 IS 'Componente 3 de TIL1: empleos sin acceso a seguridad social.';
COMMENT ON COLUMN stg_enoe_microdatos.tue_ppal IS 'Trabajo informal en ocupación principal (1=Informal, 2=Formal). Base de TIL1.';
COMMENT ON COLUMN stg_enoe_microdatos.emp_ppal IS 'Características de la empresa en la ocupación principal.';
COMMENT ON COLUMN stg_enoe_microdatos.trans_ppal IS 'Tipo de transacción en la ocupación principal.';
COMMENT ON COLUMN stg_enoe_microdatos.sub_o IS 'Subocupación (1=Subocupado, 2=No subocupado).';
COMMENT ON COLUMN stg_enoe_microdatos.s_clasifi IS 'Clasificación del sector económico según informalidad.';
COMMENT ON COLUMN stg_enoe_microdatos.remune2c IS 'Remuneración en 2 categorías (con/sin remuneración).';
COMMENT ON COLUMN stg_enoe_microdatos.pre_asa IS 'Percibe prestaciones laborales (1=Sí, 2=No).';
COMMENT ON COLUMN stg_enoe_microdatos.tip_con IS 'Tipo de contrato laboral.';
COMMENT ON COLUMN stg_enoe_microdatos.sec_ins IS 'Sector institucional del empleador (público/privado/mixto).';
COMMENT ON COLUMN stg_enoe_microdatos.mh_fil2 IS 'Mujer de hogar: indicador fila 2.';
COMMENT ON COLUMN stg_enoe_microdatos.mh_col IS 'Mujer de hogar: indicador columna.';
COMMENT ON COLUMN stg_enoe_microdatos.t_tra IS 'Tipo de trabajo (remunerado/no remunerado/doméstico).';

-- Trabajo doméstico y edades derivadas
COMMENT ON COLUMN stg_enoe_microdatos.domestico IS 'Realiza trabajo doméstico no remunerado (1=Sí, 2=No).';
COMMENT ON COLUMN stg_enoe_microdatos.eda5c IS 'Edad en 5 grupos (15-24, 25-34, 35-44, 45-54, 55+).';
COMMENT ON COLUMN stg_enoe_microdatos.eda7c IS 'Edad en 7 grupos.';
COMMENT ON COLUMN stg_enoe_microdatos.eda12c IS 'Edad en 12 grupos.';
COMMENT ON COLUMN stg_enoe_microdatos.eda19c IS 'Edad en 19 grupos quinquenales.';

-- Horas e ingresos
COMMENT ON COLUMN stg_enoe_microdatos.hrsocup IS 'Horas trabajadas en la semana de referencia (ocupación principal).';
COMMENT ON COLUMN stg_enoe_microdatos.ingocup IS 'Ingreso mensual por trabajo (pesos corrientes).';
COMMENT ON COLUMN stg_enoe_microdatos.ing_x_hrs IS 'Ingreso por hora trabajada (pesos corrientes).';
COMMENT ON COLUMN stg_enoe_microdatos.salario IS 'Salario mínimo general diario de referencia.';

-- Tasas y complementos
COMMENT ON COLUMN stg_enoe_microdatos.tpg_p8a IS 'Tasa de participación en actividades no económicas.';
COMMENT ON COLUMN stg_enoe_microdatos.tcco IS 'Tasa de condición de ocupación.';
COMMENT ON COLUMN stg_enoe_microdatos.cp_anoc IS 'Complemento para análisis no ocupados.';
COMMENT ON COLUMN stg_enoe_microdatos.imssissste IS 'Acceso a IMSS o ISSSTE (1=IMSS, 2=ISSSTE, 3=Ambos, 4=Ninguno).';
COMMENT ON COLUMN stg_enoe_microdatos.ma48me1sm IS 'Trabajó más de 48 horas o menos de 1 salario mínimo (indicador de precariedad).';
COMMENT ON COLUMN stg_enoe_microdatos.p14apoyos IS 'Recibe apoyos gubernamentales (1=Sí, 2=No).';

-- Factor de expansión
COMMENT ON COLUMN stg_enoe_microdatos.fac IS 'Factor de expansión trimestral (fac_tri en versiones recientes).';
COMMENT ON COLUMN stg_enoe_microdatos.fac_men IS 'Factor de expansión mensual.';

-- FKs a catálogos
COMMENT ON COLUMN stg_enoe_microdatos.sector_id IS 'FK a cat_enoe_sector. Derivado de rama_est1 (sector económico de la ocupación principal).';
COMMENT ON COLUMN stg_enoe_microdatos.ocupacion_id IS 'FK a cat_enoe_ocupacion. Derivado de c_ocu11c (grupo ocupacional en 11 categorías).';
COMMENT ON COLUMN stg_enoe_microdatos.situacion_trabajo_id IS 'FK a cat_enoe_situacion_trabajo. Derivado de pos_ocu (posición en la ocupación: subordinado, empleador, cuenta propia, sin pago).';

-- COE1
COMMENT ON COLUMN stg_enoe_microdatos.p3b IS 'COE1 — Número de trabajadores en el establecimiento (codificado por rangos).';
COMMENT ON COLUMN stg_enoe_microdatos.p3i IS 'COE1 — Tiene contrato escrito (1=Sí indefinido, 2=Sí temporal, 3=No).';

-- COE2
COMMENT ON COLUMN stg_enoe_microdatos.p10b IS 'COE2 — Razón por la que no trabajó la semana de referencia.';

-- Indicadores derivados
COMMENT ON COLUMN stg_enoe_microdatos.es_pea IS 'TRUE si la persona pertenece a la Población Económicamente Activa (clase1=1).';
COMMENT ON COLUMN stg_enoe_microdatos.es_ocupado IS 'TRUE si la persona está ocupada (clase2=1).';
COMMENT ON COLUMN stg_enoe_microdatos.es_desocupado IS 'TRUE si la persona está desocupada (clase2=2).';
COMMENT ON COLUMN stg_enoe_microdatos.es_informal IS 'TRUE si el trabajo principal es informal según TIL1 (tue_ppal=1).';

-- =============================================================================
-- VISTA MATERIALIZADA
-- =============================================================================

COMMENT ON MATERIALIZED VIEW mv_enoe_microdatos IS
    'Vista materializada gold layer de la ENOE microdatos. '
    'Combina stg_enoe_microdatos con los catálogos de sector, ocupación y situación '
    'en el trabajo, y resuelve entidad y municipio vía FDW cvegeo. '
    'Filtrada a Jalisco (entidad_id=14). Incluye horas, ingresos, informalidad, '
    'variables COE1/COE2 y los cuatro indicadores derivados de condición de actividad.';

COMMENT ON COLUMN mv_enoe_microdatos.id IS 'Identificador interno del registro en stg_enoe_microdatos.';
COMMENT ON COLUMN mv_enoe_microdatos.anio IS 'Año de levantamiento.';
COMMENT ON COLUMN mv_enoe_microdatos.trimestre IS 'Trimestre de levantamiento (1-4).';
COMMENT ON COLUMN mv_enoe_microdatos.entidad IS 'Nombre de la entidad federativa (resuelto vía cvegeo_states).';
COMMENT ON COLUMN mv_enoe_microdatos.municipio IS 'Nombre del municipio (resuelto vía cvegeo_municipalities).';
COMMENT ON COLUMN mv_enoe_microdatos.ur IS 'Zona urbano/rural (1=Urbano, 2=Rural).';
COMMENT ON COLUMN mv_enoe_microdatos.zona IS 'Zona geográfica de la encuesta.';
COMMENT ON COLUMN mv_enoe_microdatos.sex IS 'Sexo (1=Hombre, 2=Mujer).';
COMMENT ON COLUMN mv_enoe_microdatos.eda IS 'Edad en años cumplidos.';
COMMENT ON COLUMN mv_enoe_microdatos.nac_anio IS 'Año de nacimiento.';
COMMENT ON COLUMN mv_enoe_microdatos.e_con IS 'Estado conyugal.';
COMMENT ON COLUMN mv_enoe_microdatos.niv_ins IS 'Nivel de instrucción recodificado.';
COMMENT ON COLUMN mv_enoe_microdatos.anios_esc IS 'Años de escolaridad aprobados.';
COMMENT ON COLUMN mv_enoe_microdatos.clase1 IS 'Condición de actividad (1=PEA, 2=PNEA).';
COMMENT ON COLUMN mv_enoe_microdatos.clase2 IS 'Condición de ocupación (1=Ocupado, 2=Desocupado).';
COMMENT ON COLUMN mv_enoe_microdatos.clase3 IS 'Condición de ocupación desagregada.';
COMMENT ON COLUMN mv_enoe_microdatos.sector IS 'Sector económico de la ocupación principal (resuelto de cat_enoe_sector).';
COMMENT ON COLUMN mv_enoe_microdatos.ocupacion IS 'Grupo de ocupación (resuelto de cat_enoe_ocupacion).';
COMMENT ON COLUMN mv_enoe_microdatos.situacion_trabajo IS 'Posición en la ocupación (resuelto de cat_enoe_situacion_trabajo).';
COMMENT ON COLUMN mv_enoe_microdatos.seg_soc IS 'Acceso a servicios de salud por ocupación principal.';
COMMENT ON COLUMN mv_enoe_microdatos.rama IS 'Rama de actividad económica (1 dígito SCIAN/ENOE).';
COMMENT ON COLUMN mv_enoe_microdatos.scian IS 'Clave de subsector SCIAN.';
COMMENT ON COLUMN mv_enoe_microdatos.ing7c IS 'Ingreso laboral en 7 categorías.';
COMMENT ON COLUMN mv_enoe_microdatos.dur9c IS 'Horas trabajadas en 9 categorías.';
COMMENT ON COLUMN mv_enoe_microdatos.emple7c IS 'Tamaño del establecimiento en 7 categorías.';
COMMENT ON COLUMN mv_enoe_microdatos.hrsocup IS 'Horas trabajadas en la semana de referencia.';
COMMENT ON COLUMN mv_enoe_microdatos.ingocup IS 'Ingreso mensual por trabajo (pesos corrientes).';
COMMENT ON COLUMN mv_enoe_microdatos.ing_x_hrs IS 'Ingreso por hora trabajada (pesos corrientes).';
COMMENT ON COLUMN mv_enoe_microdatos.salario IS 'Salario mínimo general diario de referencia.';
COMMENT ON COLUMN mv_enoe_microdatos.tpg_p8a IS 'Tasa de participación en actividades no económicas.';
COMMENT ON COLUMN mv_enoe_microdatos.tcco IS 'Tasa de condición de ocupación.';
COMMENT ON COLUMN mv_enoe_microdatos.cp_anoc IS 'Complemento para análisis de no ocupados.';
COMMENT ON COLUMN mv_enoe_microdatos.imssissste IS 'Acceso a IMSS o ISSSTE.';
COMMENT ON COLUMN mv_enoe_microdatos.ma48me1sm IS 'Indicador de precariedad: más de 48 hrs o menos de 1 salario mínimo.';
COMMENT ON COLUMN mv_enoe_microdatos.tue_ppal IS 'Informalidad en ocupación principal (1=Informal, 2=Formal).';
COMMENT ON COLUMN mv_enoe_microdatos.emp_ppal IS 'Características del empleador en ocupación principal.';
COMMENT ON COLUMN mv_enoe_microdatos.trans_ppal IS 'Tipo de transacción en ocupación principal.';
COMMENT ON COLUMN mv_enoe_microdatos.sub_o IS 'Subocupación (1=Subocupado, 2=No subocupado).';
COMMENT ON COLUMN mv_enoe_microdatos.mh_fil2 IS 'Mujer de hogar: indicador fila 2.';
COMMENT ON COLUMN mv_enoe_microdatos.mh_col IS 'Mujer de hogar: indicador columna.';
COMMENT ON COLUMN mv_enoe_microdatos.sec_ins IS 'Sector institucional del empleador.';
COMMENT ON COLUMN mv_enoe_microdatos.p3b IS 'COE1 — Número de trabajadores en el establecimiento.';
COMMENT ON COLUMN mv_enoe_microdatos.p3i IS 'COE1 — Tipo de contrato escrito.';
COMMENT ON COLUMN mv_enoe_microdatos.p10b IS 'COE2 — Razón por la que no trabajó la semana de referencia.';
COMMENT ON COLUMN mv_enoe_microdatos.es_pea IS 'TRUE si pertenece a la PEA.';
COMMENT ON COLUMN mv_enoe_microdatos.es_ocupado IS 'TRUE si está ocupado.';
COMMENT ON COLUMN mv_enoe_microdatos.es_desocupado IS 'TRUE si está desocupado.';
COMMENT ON COLUMN mv_enoe_microdatos.es_informal IS 'TRUE si el trabajo principal es informal (tue_ppal=1).';
COMMENT ON COLUMN mv_enoe_microdatos.fac IS 'Factor de expansión trimestral.';
COMMENT ON COLUMN mv_enoe_microdatos.fac_men IS 'Factor de expansión mensual.';
