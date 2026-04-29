-- =============================================================================
-- V2__{flujo}__geo.sql
-- Conexión con la base de datos cve_geo mediante Foreign Data Wrapper (FDW).
-- Solo incluir esta migración si geografia.nivel es "municipal" o "estatal".
-- El FDW cve_geo debe estar configurado previamente en el servidor.
-- =============================================================================

-- Importar las tablas de cve_geo que necesite el pipeline.
-- Adaptar los nombres de esquema y tabla según la estructura real de cve_geo.

-- Ejemplo: importar vista de municipios
IMPORT FOREIGN SCHEMA public
    LIMIT TO (municipios, entidades)
    FROM SERVER cve_geo
    INTO public;

-- Si el FDW ya está importado en el esquema público, omitir este paso
-- y referenciar directamente las tablas cve_geo en las vistas (V4).

-- Nota: no crear tablas locales de municipios ni entidades.
-- Toda referencia geográfica debe apuntar a cve_geo.
