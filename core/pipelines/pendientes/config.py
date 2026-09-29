from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict
from sqlalchemy.engine import make_url

from core.config import BaseConfig, env_path
from core.pipelines.pendientes.constants import (
    ALLOWED_BOUNDARY_GEOMETRY_COLUMNS,
    AOI_BUFFER_M,
    CVEGEO_DATABASE_NAME,
    DEFAULT_BOUNDARY_GEOMETRY_COLUMN,
    SOURCE_ZIP_FILENAME,
    TARGET_RESOLUTION_M,
    TARGET_SRID,
)


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("pendientes"))

    DB_NAME: str = Field(default="pendientes")
    SOURCE_URL: str | None = Field(default=None)
    SOURCE_TIFF_PATH: Path | None = Field(default=None)
    CVEGEO_MUNICIPAL_BOUNDARY_SNAPSHOT_PATH: Path | None = Field(default=None)
    SOURCE_ZIP_FILENAME: str = Field(default=SOURCE_ZIP_FILENAME)
    FORCE_DOWNLOAD: bool = Field(default=False)
    DOWNLOAD_RETRIES: int = Field(default=5, ge=1)
    DOWNLOAD_CONNECT_TIMEOUT: int = Field(default=30, ge=1)
    DOWNLOAD_READ_TIMEOUT: int = Field(default=600, ge=1)
    DOWNLOAD_CHUNK_SIZE: int = Field(default=1024 * 1024, ge=1024)

    TARGET_SRID: int = Field(default=TARGET_SRID)
    TARGET_RESOLUTION_M: float = Field(default=TARGET_RESOLUTION_M, gt=0)
    AOI_BUFFER_M: float = Field(default=AOI_BUFFER_M, gt=0)
    BOUNDARY_GEOMETRY_COLUMN: str = Field(default=DEFAULT_BOUNDARY_GEOMETRY_COLUMN)
    STATS_MAX_CELLS: int = Field(default=5_000_000, ge=1)
    DIAGNOSTIC_SAMPLE_MAX_CELLS: int = Field(default=2_000_000, ge=1)

    @field_validator("SOURCE_URL", "SOURCE_TIFF_PATH", "CVEGEO_MUNICIPAL_BOUNDARY_SNAPSHOT_PATH", mode="before")
    @classmethod
    def blank_means_unset(cls, value: object) -> object:
        """A bare `KEY=` in the .env is an unset optional, not the current directory."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("BOUNDARY_GEOMETRY_COLUMN")
    @classmethod
    def validate_boundary_geometry_column(cls, value: str) -> str:
        if value not in ALLOWED_BOUNDARY_GEOMETRY_COLUMNS:
            raise ValueError(f"BOUNDARY_GEOMETRY_COLUMN must be one of {ALLOWED_BOUNDARY_GEOMETRY_COLUMNS}")
        return value

    @property
    def cvegeo_database_url(self) -> str:
        """Select the shared cvegeo database while preserving the common PostgreSQL connection."""
        return make_url(self.database_url).set(database=CVEGEO_DATABASE_NAME).render_as_string(hide_password=False)


settings = Settings()
