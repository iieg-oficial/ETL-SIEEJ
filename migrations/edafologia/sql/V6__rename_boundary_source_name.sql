DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'fuentes_limites_municipales'
          AND column_name = 'nombre_fuente'
    ) THEN
        RAISE EXCEPTION 'La columna fuentes_limites_municipales.nombre_fuente no existe';
    END IF;
END
$$;

COMMENT ON COLUMN public.fuentes_limites_municipales.nombre_fuente IS
    'Nombre legible de la fuente de limite municipal.';
