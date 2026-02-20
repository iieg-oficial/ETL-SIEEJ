CREATE OR REPLACE VIEW v_establecimientos_activos_jalisco AS
SELECT * FROM v_establecimientos
WHERE entidad = 'Jalisco' AND estatus_establecimiento = 'En Operación';
