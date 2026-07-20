from typing import Final

CATALOG_PAGE_URL: Final[str] = "http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_defunciones_gobmx.html"
CATALOG_ZIP_PATTERN: Final[str] = r"CATALOGOS_DEFUN_[^\"']*\.zip[^\"']*"
REGISTRO_ZIP_PATTERN: Final[str] = r"registro/DEFUN_[^\"']*\.zip[^\"']*"

SOURCE_ENCODINGS: Final[tuple[str, ...]] = ("utf-8-sig", "latin-1")

DOWNLOAD_TIMEOUT: Final[int] = 120

MIRRORED_EDITION: Final[int] = 2021
MIRRORED_EDITION_FILENAME: Final[str] = "CATALOGOS_DEFUN_2021.zip"

CLAVE_ALIASES: Final[tuple[str, ...]] = ("clave", "cve")
DESCRIPCION_ALIASES: Final[tuple[str, ...]] = ("descrip", "descripcion")

CLAVE_COL: Final[str] = "clave"
DESCRIPCION_COL: Final[str] = "descripcion"
NOMBRE_EDAD_COL: Final[str] = "nombre_edad"

LOCALIDADES_KEYWORD: Final[str] = "entidad_municipio_localidad"
