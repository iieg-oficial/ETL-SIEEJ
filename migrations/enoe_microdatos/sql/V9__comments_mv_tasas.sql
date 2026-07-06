-- COMMENT ON para mv_enoe_tasas y mv_enoe_tasas_jalisco

-- =============================================================================
-- mv_enoe_tasas
-- =============================================================================

COMMENT ON MATERIALIZED VIEW mv_enoe_tasas IS
    'Indicadores trimestrales de ocupación y empleo ENOE por municipio de Jalisco. '
    'Contiene las 11 tasas oficiales INEGI y poblaciones base, desagregadas por total y sexo. '
    'Fuente: INEGI ENOE microdatos 15 años y más. '
    'Nota: ENOE no es representativa a nivel municipio; el diseño muestral opera por cd_a (ciudad/área). '
    'Para cifras que coincidan con valores oficiales INEGI usar mv_enoe_tasas_jalisco.';

COMMENT ON COLUMN mv_enoe_tasas.anio IS 'Año de levantamiento de la encuesta.';
COMMENT ON COLUMN mv_enoe_tasas.trimestre IS 'Trimestre de levantamiento (1–4).';
COMMENT ON COLUMN mv_enoe_tasas.municipio_id IS 'Clave del municipio (cve_mun INEGI).';
COMMENT ON COLUMN mv_enoe_tasas.municipio IS 'Nombre oficial del municipio (de cvegeo_municipalities).';

-- Poblaciones totales
COMMENT ON COLUMN mv_enoe_tasas.p15ymas IS 'Población de 15 años y más expandida (SUM fac, criterio general).';
COMMENT ON COLUMN mv_enoe_tasas.pea IS 'Población Económicamente Activa (clase1=1).';
COMMENT ON COLUMN mv_enoe_tasas.pd IS 'Población Desocupada (clase2=2).';
COMMENT ON COLUMN mv_enoe_tasas.po IS 'Población Ocupada (clase2=1).';
COMMENT ON COLUMN mv_enoe_tasas.pona IS 'Población Ocupada No Agropecuaria (clase2=1 y ambito1<>1).';

-- Tasas totales
COMMENT ON COLUMN mv_enoe_tasas.tp IS 'Tasa de Participación: PEA / P15yMAS × 100.';
COMMENT ON COLUMN mv_enoe_tasas.td IS 'Tasa de Desocupación: PD / PEA × 100.';
COMMENT ON COLUMN mv_enoe_tasas.topd IS 'Tasa de Ocupación Parcial y Desocupación: (PD + O<15hrs) / PEA × 100.';
COMMENT ON COLUMN mv_enoe_tasas.tprg IS 'Tasa de Presión General: (PD + POBOT) / PEA × 100.';
COMMENT ON COLUMN mv_enoe_tasas.tta IS 'Tasa de Trabajo Asalariado: PASA / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas.tsub IS 'Tasa de Subocupación: PSUB_O / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas.tcco IS 'Tasa de Condiciones Críticas de Ocupación: PCCO / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas.tosi1 IS 'Tasa de Ocupación en el Sector Informal 1: POSI / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas.til1 IS 'Tasa de Informalidad Laboral 1: POI (emp_ppal=1) / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas.tosi2 IS 'Tasa de Ocupación en el Sector Informal 2: POSI / PONA × 100.';
COMMENT ON COLUMN mv_enoe_tasas.til2 IS 'Tasa de Informalidad Laboral 2: POINA / PONA × 100.';

-- Poblaciones por sexo
COMMENT ON COLUMN mv_enoe_tasas.p15ymas_h IS 'Población de 15 años y más — hombres (sex=1).';
COMMENT ON COLUMN mv_enoe_tasas.p15ymas_m IS 'Población de 15 años y más — mujeres (sex=2).';
COMMENT ON COLUMN mv_enoe_tasas.pea_h IS 'PEA — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.pea_m IS 'PEA — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.pd_h IS 'Población Desocupada — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.pd_m IS 'Población Desocupada — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.po_h IS 'Población Ocupada — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.po_m IS 'Población Ocupada — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.pona_h IS 'Población Ocupada No Agropecuaria — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.pona_m IS 'Población Ocupada No Agropecuaria — mujeres.';

-- Tasas por sexo
COMMENT ON COLUMN mv_enoe_tasas.tp_h IS 'Tasa de Participación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.tp_m IS 'Tasa de Participación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.td_h IS 'Tasa de Desocupación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.td_m IS 'Tasa de Desocupación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.topd_h IS 'Tasa de Ocupación Parcial y Desocupación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.topd_m IS 'Tasa de Ocupación Parcial y Desocupación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.tprg_h IS 'Tasa de Presión General — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.tprg_m IS 'Tasa de Presión General — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.tta_h IS 'Tasa de Trabajo Asalariado — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.tta_m IS 'Tasa de Trabajo Asalariado — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.tsub_h IS 'Tasa de Subocupación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.tsub_m IS 'Tasa de Subocupación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.tcco_h IS 'Tasa de Condiciones Críticas de Ocupación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.tcco_m IS 'Tasa de Condiciones Críticas de Ocupación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.tosi1_h IS 'Tasa de Ocupación en el Sector Informal 1 — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.tosi1_m IS 'Tasa de Ocupación en el Sector Informal 1 — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.til1_h IS 'Tasa de Informalidad Laboral 1 — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.til1_m IS 'Tasa de Informalidad Laboral 1 — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.tosi2_h IS 'Tasa de Ocupación en el Sector Informal 2 — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.tosi2_m IS 'Tasa de Ocupación en el Sector Informal 2 — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas.til2_h IS 'Tasa de Informalidad Laboral 2 — hombres.';
COMMENT ON COLUMN mv_enoe_tasas.til2_m IS 'Tasa de Informalidad Laboral 2 — mujeres.';

-- =============================================================================
-- mv_enoe_tasas_jalisco
-- =============================================================================

COMMENT ON MATERIALIZED VIEW mv_enoe_tasas_jalisco IS
    'Indicadores trimestrales de ocupación y empleo ENOE a nivel estado de Jalisco. '
    'Contiene las 11 tasas oficiales INEGI y poblaciones base, desagregadas por total y sexo. '
    'Los valores replican las cifras oficiales INEGI al aplicar el criterio general: '
    'r_def=0, c_res IN (1,3), eda BETWEEN 15 AND 98, SUM(fac). '
    'Fuente: INEGI ENOE microdatos 15 años y más.';

COMMENT ON COLUMN mv_enoe_tasas_jalisco.anio IS 'Año de levantamiento de la encuesta.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.trimestre IS 'Trimestre de levantamiento (1–4).';

-- Poblaciones totales
COMMENT ON COLUMN mv_enoe_tasas_jalisco.p15ymas IS 'Población de 15 años y más expandida (SUM fac, criterio general).';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pea IS 'Población Económicamente Activa (clase1=1).';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pd IS 'Población Desocupada (clase2=2).';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.po IS 'Población Ocupada (clase2=1).';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pona IS 'Población Ocupada No Agropecuaria (clase2=1 y ambito1<>1).';

-- Tasas totales
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tp IS 'Tasa de Participación: PEA / P15yMAS × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.td IS 'Tasa de Desocupación: PD / PEA × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.topd IS 'Tasa de Ocupación Parcial y Desocupación: (PD + O<15hrs) / PEA × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tprg IS 'Tasa de Presión General: (PD + POBOT) / PEA × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tta IS 'Tasa de Trabajo Asalariado: PASA / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tsub IS 'Tasa de Subocupación: PSUB_O / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tcco IS 'Tasa de Condiciones Críticas de Ocupación: PCCO / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tosi1 IS 'Tasa de Ocupación en el Sector Informal 1: POSI / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.til1 IS 'Tasa de Informalidad Laboral 1: POI (emp_ppal=1) / PO × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tosi2 IS 'Tasa de Ocupación en el Sector Informal 2: POSI / PONA × 100.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.til2 IS 'Tasa de Informalidad Laboral 2: POINA / PONA × 100.';

-- Poblaciones por sexo
COMMENT ON COLUMN mv_enoe_tasas_jalisco.p15ymas_h IS 'Población de 15 años y más — hombres (sex=1).';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.p15ymas_m IS 'Población de 15 años y más — mujeres (sex=2).';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pea_h IS 'PEA — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pea_m IS 'PEA — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pd_h IS 'Población Desocupada — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pd_m IS 'Población Desocupada — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.po_h IS 'Población Ocupada — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.po_m IS 'Población Ocupada — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pona_h IS 'Población Ocupada No Agropecuaria — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.pona_m IS 'Población Ocupada No Agropecuaria — mujeres.';

-- Tasas por sexo
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tp_h IS 'Tasa de Participación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tp_m IS 'Tasa de Participación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.td_h IS 'Tasa de Desocupación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.td_m IS 'Tasa de Desocupación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.topd_h IS 'Tasa de Ocupación Parcial y Desocupación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.topd_m IS 'Tasa de Ocupación Parcial y Desocupación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tprg_h IS 'Tasa de Presión General — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tprg_m IS 'Tasa de Presión General — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tta_h IS 'Tasa de Trabajo Asalariado — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tta_m IS 'Tasa de Trabajo Asalariado — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tsub_h IS 'Tasa de Subocupación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tsub_m IS 'Tasa de Subocupación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tcco_h IS 'Tasa de Condiciones Críticas de Ocupación — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tcco_m IS 'Tasa de Condiciones Críticas de Ocupación — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tosi1_h IS 'Tasa de Ocupación en el Sector Informal 1 — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tosi1_m IS 'Tasa de Ocupación en el Sector Informal 1 — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.til1_h IS 'Tasa de Informalidad Laboral 1 — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.til1_m IS 'Tasa de Informalidad Laboral 1 — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tosi2_h IS 'Tasa de Ocupación en el Sector Informal 2 — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.tosi2_m IS 'Tasa de Ocupación en el Sector Informal 2 — mujeres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.til2_h IS 'Tasa de Informalidad Laboral 2 — hombres.';
COMMENT ON COLUMN mv_enoe_tasas_jalisco.til2_m IS 'Tasa de Informalidad Laboral 2 — mujeres.';
