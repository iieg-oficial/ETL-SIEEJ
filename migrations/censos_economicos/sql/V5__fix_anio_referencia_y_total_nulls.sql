-- Issue #158: corregir el anio de referencia. El INEGI levanta el censo un anio
-- (edicion) pero mide el ejercicio anterior: CE 2019 -> datos 2018, CE 2024 -> datos 2023.

-- 1. Renombrar tablas de staging al anio de referencia.
ALTER TABLE stg_economico_nacional_2019  RENAME TO stg_economico_nacional_2018;
ALTER TABLE stg_economico_estatal_2019   RENAME TO stg_economico_estatal_2018;
ALTER TABLE stg_economico_municipal_2019 RENAME TO stg_economico_municipal_2018;
ALTER TABLE stg_economico_nacional_2024  RENAME TO stg_economico_nacional_2023;
ALTER TABLE stg_economico_estatal_2024   RENAME TO stg_economico_estatal_2023;
ALTER TABLE stg_economico_municipal_2024 RENAME TO stg_economico_municipal_2023;

-- 2. Renombrar las vistas correspondientes.
ALTER VIEW vw_economico_nacional_2019  RENAME TO vw_economico_nacional_2018;
ALTER VIEW vw_economico_estatal_2019   RENAME TO vw_economico_estatal_2018;
ALTER VIEW vw_economico_municipal_2019 RENAME TO vw_economico_municipal_2018;
ALTER VIEW vw_economico_nacional_2024  RENAME TO vw_economico_nacional_2023;
ALTER VIEW vw_economico_estatal_2024   RENAME TO vw_economico_estatal_2023;
ALTER VIEW vw_economico_municipal_2024 RENAME TO vw_economico_municipal_2023;

-- 3. Corregir el anio de referencia en el catalogo de censos.
UPDATE cat_censos
SET anio = 2018, descripcion = 'Censos Economicos 2019 (datos 2018)'
WHERE anio = 2019;
UPDATE cat_censos
SET anio = 2023, descripcion = 'Censos Economicos 2024 (datos 2023)'
WHERE anio = 2024;
