from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

TEMPLATE_SEPARATOR = ","


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("defunciones_inegi"))

    DB_NAME: str = Field(default="defunciones_inegi")

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


settings = Settings()
