CREATE OR REPLACE VIEW v_establecimientos_jalisco AS
SELECT * FROM v_establecimientos
WHERE entidad = 'Jalisco';
