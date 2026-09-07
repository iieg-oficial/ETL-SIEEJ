-- INEGI publica estas dos listas en mayúsculas sostenidas. La convención del
-- proyecto (.claude/rules/databases.md) es capitalizar sólo la primera letra.
-- De paso se colapsan los espacios dobles que trae la fuente.
--
-- Los paréntesis llevan palabras normales ((PRIMARIOS), (MALARIA), (GRIPE)) y
-- sí se minusculizan; sólo sobreviven la sigla VIH y los nombres propios.

CREATE OR REPLACE FUNCTION pg_temp.sentence_case(texto text) RETURNS text AS $$
DECLARE
    limpio text;
    termino text;
BEGIN
    limpio := regexp_replace(btrim(texto), '\s+', ' ', 'g');
    limpio := upper(left(limpio, 1)) || lower(substr(limpio, 2));
    FOREACH termino IN ARRAY ARRAY['VIH', 'Hodgkin', 'Alzheimer', 'Zika'] LOOP
        limpio := regexp_replace(limpio, termino, termino, 'gi');
    END LOOP;
    RETURN limpio;
END;
$$ LANGUAGE plpgsql;

UPDATE cat_grupo_lista_mexicana SET descripcion = pg_temp.sentence_case(descripcion);

UPDATE cat_lista_cie SET descripcion = pg_temp.sentence_case(descripcion);
