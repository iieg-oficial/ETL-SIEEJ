-- Normaliza el catálogo de años: "Año 2019" -> "2019".
UPDATE cat_anio
SET descripcion = regexp_replace(descripcion, '^Año\s+', '')
WHERE descripcion ~ '^Año\s+';
