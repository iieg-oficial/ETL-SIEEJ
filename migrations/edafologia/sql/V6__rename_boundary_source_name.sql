DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'fuentes_limites_municipales'
          AND column_name = 'nombre'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'fuentes_limites_municipales'
          AND column_name = 'nombre_fuente'
    ) THEN
        ALTER TABLE public.fuentes_limites_municipales
            RENAME COLUMN nombre TO nombre_fuente;
    END IF;
END
$$;

COMMENT ON COLUMN public.fuentes_limites_municipales.nombre_fuente IS
    'Nombre legible de la fuente de limite municipal.';
