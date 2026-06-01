from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("ilmm"))

    ILMM_BASE_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/ilmm/datosabiertos/conjunto_de_datos_ilmm_{year}_1t_csv.zip"
    )
    CSV_INNER_PATH: str = Field(
        default="conjunto_de_datos/conjunto_de_datos_ilmm_{year}_1t.csv"
    )
    BOOTSTRAP_YEARS: list[int] = Field(default=[2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])

    @field_validator("BOOTSTRAP_YEARS", mode="before")
    @classmethod
    def parse_years(cls, v):
        if isinstance(v, str):
            return [int(y.strip()) for y in v.split(",")]
        return v


settings = Settings()
