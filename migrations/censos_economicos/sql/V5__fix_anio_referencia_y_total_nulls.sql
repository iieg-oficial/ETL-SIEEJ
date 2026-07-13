-- Issue #158: corregir el anio de referencia (CE 2019 -> datos 2018, CE 2024 -> datos 2023)
-- y arreglar el renglon de total (Gran sector) que llega sin codigo (codigo IS NULL):
-- duplicaba el catalogo y dejaba huerfano el total en staging.

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

-- 4. Repuntar el staging al renglon de total canonico (MIN(id) por censo) antes de
--    borrar duplicados, e incluir los renglones de total que quedaron huerfanos (NULL).
UPDATE stg_economico_nacional_2018 s
SET actividad_economica_id = k.keep_id
FROM (SELECT censo_id, MIN(id) AS keep_id FROM cat_actividades_economicas
      WHERE codigo IS NULL AND codigo_id = 1 GROUP BY censo_id) k
WHERE k.censo_id = s.censo_id
  AND (s.actividad_economica_id IS NULL
       OR s.actividad_economica_id IN
          (SELECT id FROM cat_actividades_economicas WHERE codigo IS NULL AND codigo_id = 1));

UPDATE stg_economico_estatal_2018 s
SET actividad_economica_id = k.keep_id
FROM (SELECT censo_id, MIN(id) AS keep_id FROM cat_actividades_economicas
      WHERE codigo IS NULL AND codigo_id = 1 GROUP BY censo_id) k
WHERE k.censo_id = s.censo_id
  AND (s.actividad_economica_id IS NULL
       OR s.actividad_economica_id IN
          (SELECT id FROM cat_actividades_economicas WHERE codigo IS NULL AND codigo_id = 1));

UPDATE stg_economico_municipal_2018 s
SET actividad_economica_id = k.keep_id
FROM (SELECT censo_id, MIN(id) AS keep_id FROM cat_actividades_economicas
      WHERE codigo IS NULL AND codigo_id = 1 GROUP BY censo_id) k
WHERE k.censo_id = s.censo_id
  AND (s.actividad_economica_id IS NULL
       OR s.actividad_economica_id IN
          (SELECT id FROM cat_actividades_economicas WHERE codigo IS NULL AND codigo_id = 1));

UPDATE stg_economico_nacional_2023 s
SET actividad_economica_id = k.keep_id
FROM (SELECT censo_id, MIN(id) AS keep_id FROM cat_actividades_economicas
      WHERE codigo IS NULL AND codigo_id = 1 GROUP BY censo_id) k
WHERE k.censo_id = s.censo_id
  AND (s.actividad_economica_id IS NULL
       OR s.actividad_economica_id IN
          (SELECT id FROM cat_actividades_economicas WHERE codigo IS NULL AND codigo_id = 1));

UPDATE stg_economico_estatal_2023 s
SET actividad_economica_id = k.keep_id
FROM (SELECT censo_id, MIN(id) AS keep_id FROM cat_actividades_economicas
      WHERE codigo IS NULL AND codigo_id = 1 GROUP BY censo_id) k
WHERE k.censo_id = s.censo_id
  AND (s.actividad_economica_id IS NULL
       OR s.actividad_economica_id IN
          (SELECT id FROM cat_actividades_economicas WHERE codigo IS NULL AND codigo_id = 1));

UPDATE stg_economico_municipal_2023 s
SET actividad_economica_id = k.keep_id
FROM (SELECT censo_id, MIN(id) AS keep_id FROM cat_actividades_economicas
      WHERE codigo IS NULL AND codigo_id = 1 GROUP BY censo_id) k
WHERE k.censo_id = s.censo_id
  AND (s.actividad_economica_id IS NULL
       OR s.actividad_economica_id IN
          (SELECT id FROM cat_actividades_economicas WHERE codigo IS NULL AND codigo_id = 1));

-- 5. Borrar los duplicados del catalogo, conservando el canonico por censo.
DELETE FROM cat_actividades_economicas a
USING (SELECT censo_id, MIN(id) AS keep_id FROM cat_actividades_economicas
       WHERE codigo IS NULL AND codigo_id = 1 GROUP BY censo_id) k
WHERE a.codigo IS NULL AND a.codigo_id = 1
  AND a.censo_id = k.censo_id AND a.id <> k.keep_id;

-- 6. Recrear la constraint para que los NULL se traten como iguales (Postgres >= 15),
--    de modo que la constraint y el ON CONFLICT del load dejen de duplicar el total.
ALTER TABLE cat_actividades_economicas
    DROP CONSTRAINT uq_actividad_codigo_clas_censo;
ALTER TABLE cat_actividades_economicas
    ADD CONSTRAINT uq_actividad_codigo_clas_censo
    UNIQUE NULLS NOT DISTINCT (codigo, codigo_id, censo_id);
