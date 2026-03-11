# Correccion de nombres: texto normalizado del Excel -> texto en cvegeo
# Las claves usan texto ya normalizado (sin acentos, lower, espacios como _)
# Se aplica ANTES de buscar en el cache de municipios
MUNICIPALITY_NAME_FIXES: dict[str, str] = {
    "tlajomulco_de_zuniga": "tlajomulco_de_zuniga",
}

# Municipios que NO deben resolverse contra cvegeo
SKIP_MUNICIPALITY_VALUES = frozenset({
    "SE IGNORA",
    "EXTRANJERO",
})
