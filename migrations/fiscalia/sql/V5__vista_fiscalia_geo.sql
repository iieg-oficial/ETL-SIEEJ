CREATE OR REPLACE VIEW mart_fiscalia_geo_vw AS
SELECT * FROM mart_fiscalia_vw
WHERE longitud IS NOT NULL AND latitud IS NOT NULL;
