"""Static catalog values and the name fixes the source needs to cross against cvegeo.

The 15 global series are seeded instead of derived from the data so their ids
never shift between editions: stg_indice_shf_vivienda_global references them and
SHF publishes them in a fixed order (the "Consecutivo" 1-15 of every quarter).

The 'tipo' column exists because the source packs five different concepts into a
single "Global" column. Without it, asking for "todas las zonas metropolitanas"
means matching on the "ZM " prefix of a free-text name.
"""

SERIE_GLOBAL_SEED: list[dict[str, str]] = [
    {"nombre": "Nacional", "tipo": "nacional"},
    {"nombre": "Nueva", "tipo": "condicion"},
    {"nombre": "Usada", "tipo": "condicion"},
    {"nombre": "Casa sola", "tipo": "tipo_vivienda"},
    {"nombre": "Casa en condominio - depto.", "tipo": "tipo_vivienda"},
    {"nombre": "Económica - Social", "tipo": "segmento"},
    {"nombre": "Media - Residencial", "tipo": "segmento"},
    {"nombre": "ZM Valle México", "tipo": "zona_metropolitana"},
    {"nombre": "ZM Guadalajara", "tipo": "zona_metropolitana"},
    {"nombre": "ZM Monterrey", "tipo": "zona_metropolitana"},
    {"nombre": "ZM PueblaTlax", "tipo": "zona_metropolitana"},
    {"nombre": "ZM Toluca", "tipo": "zona_metropolitana"},
    {"nombre": "ZM Tijuana", "tipo": "zona_metropolitana"},
    {"nombre": "ZM León", "tipo": "zona_metropolitana"},
    {"nombre": "ZM Querétaro", "tipo": "zona_metropolitana"},
]

# SHF publica nombres de uso común para tres entidades; cvegeo guarda los del
# Marco Geoestadístico del INEGI.
#
# Aplica SOLO a la columna de entidad, nunca a la de municipio: "Veracruz" es a
# la vez el nombre corto de la entidad y el nombre completo del municipio del
# puerto, así que traducirlo en el nivel municipal deja 86 filas sin clave.
ENTITY_NAME_ALIASES: dict[str, str] = {
    "Coahuila": "Coahuila de Zaragoza",
    "Michoacán": "Michoacán de Ocampo",
    "Veracruz": "Veracruz de Ignacio de la Llave",
}
