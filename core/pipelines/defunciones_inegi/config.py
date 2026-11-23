from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

TEMPLATE_SEPARATOR = ","


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("defunciones_inegi"))

    DB_NAME: str = Field(default="defunciones_inegi")

    # Catálogo de descarga masiva que arma la pestaña "Datos abiertos" de
    # https://www.inegi.org.mx/programas/edr/. Es la fuente primaria de URLs:
    # INEGI publicó 2025 fuera de `defunciones/{year}/` y adivinar el nombre ya no basta.
    SOURCE_CATALOG_URL: str = Field(
        default=(
            "https://www.inegi.org.mx/app/api/descarga/componente/descargamasiva/lista/archivoscompaginacion"
            "?tema=0&subtema=0&areaGeografica=0&proyecto=0&anio=0&tipodocto=12"
            "&agrupacion=VG9kYXM%3D&idBiinegi=3358&desde=1&hasta=1000"
            "&textoBuscar=&ordenar=orden&ingles=0&datosAbiertos=1&orden=desc"
        )
    )

    # Prefijo que se antepone al `pathLogico` de cada registro del catálogo.
    SOURCE_CONTENT_URL: str = Field(default="https://www.inegi.org.mx/contenidos")

    CATALOG_TIMEOUT: int = Field(default=60)

    # Respaldo cuando el catálogo no responde o no trae la edición: se adivina
    # la URL con las plantillas de abajo, como antes de #379.
    SOURCE_BASE_URL: str = Field(default="https://www.inegi.org.mx/contenidos/programas/edr/datosabiertos/defunciones")

    # INEGI renombró el archivo tres veces sin cambiar la ruta; se prueban en
    # orden hasta que una responda un ZIP. Separadas por coma en el .env.
    SOURCE_URL_TEMPLATES: str = Field(
        default=(
            "{year}/conjunto_de_datos_edr{year}_csv.zip"
            ",{year}/conjunto_de_datos_defunciones_registradas_{year}_csv.zip"
            ",{year}/conjunto_de_datos_defunciones_generales_{year}_csv.zip"
        )
    )

    # Primera edición publicada en esta ruta; de 2016 hacia atrás sólo hay HTML.
    BACKFILL_MIN_YEAR: int = Field(default=2017)

    DOWNLOAD_TIMEOUT: int = Field(default=600)

    CHUNK_SIZE: int = Field(default=50_000)

    @property
    def source_url_templates(self) -> tuple[str, ...]:
        return tuple(t.strip() for t in self.SOURCE_URL_TEMPLATES.split(TEMPLATE_SEPARATOR) if t.strip())

    def edition_url(self, year: int, template: str) -> str:
        return f"{self.SOURCE_BASE_URL.rstrip('/')}/{template.format(year=year)}"

    def content_url(self, path: str) -> str:
        """URL absoluta de un `pathLogico` del catálogo (empieza con `/`)."""
        return f"{self.SOURCE_CONTENT_URL.rstrip('/')}/{path.lstrip('/')}"


settings = Settings()
