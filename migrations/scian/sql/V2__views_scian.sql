CREATE OR REPLACE VIEW view_scian_estructura AS
SELECT
    sec.codigo      AS codigo_sector,
    sec.descripcion AS sector,
    sub.codigo      AS codigo_subsector,
    sub.descripcion AS subsector,
    ram.codigo      AS codigo_rama,
    ram.descripcion AS rama,
    sbr.codigo      AS codigo_subrama,
    sbr.descripcion AS subrama,
    cla.codigo      AS codigo_clase,
    cla.descripcion AS clase
FROM clases cla
JOIN subramas    sbr ON sbr.id = cla.subrama_id
JOIN ramas       ram ON ram.id = sbr.rama_id
JOIN subsectores sub ON sub.id = ram.subsector_id
JOIN sectores    sec ON sec.id = sub.sector_id;
