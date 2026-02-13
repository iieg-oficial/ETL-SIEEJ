from sqlalchemy import Column, DateTime, Float, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base

from core.pipelines.censos_economicos.consts import CE_ECONOMIC_COLUMNS

CeBase = declarative_base()


class CatCeCatalogoActividad(CeBase):
    """Catalogo de codigos de actividad SCIAN."""

    __tablename__ = "cat_ce_catalogo_actividad"
    __table_args__ = (UniqueConstraint("codigo", name="uq_cat_ce_catalogo_actividad_codigo"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10), nullable=False, unique=True)
    descripcion = Column(String(500), nullable=True)
    clasificador = Column(String(50), nullable=True)


class CatCeCatalogoEntidadMunicipio(CeBase):
    """Catalogo de entidad-municipio geografico."""

    __tablename__ = "cat_ce_catalogo_entidad_municipio"
    __table_args__ = (UniqueConstraint("cvegeo", name="uq_cat_ce_catalogo_geo_cvegeo"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    cvegeo = Column(String(6), nullable=False, unique=True)
    cve_ent = Column(String(2), nullable=True)
    nom_ent = Column(String(100), nullable=True)
    nom_abr = Column(String(20), nullable=True)
    cve_mun = Column(String(3), nullable=True)
    nom_mun = Column(String(100), nullable=True)


class CatCeCatalogoEstrato(CeBase):
    """Catalogo de estratos por tamanio de establecimiento."""

    __tablename__ = "cat_ce_catalogo_estrato"
    __table_args__ = (UniqueConstraint("id_estrato", name="uq_cat_ce_catalogo_estrato_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_estrato = Column(String(5), nullable=False, unique=True)
    descripcion = Column(String(200), nullable=True)


class StgCeDiccionarioDatos(CeBase):
    """Diccionario de datos - documentacion de columnas extraida del CSV de diccionario."""

    __tablename__ = "stg_ce_diccionario_datos"
    __table_args__ = (UniqueConstraint("year", "column_name", name="uq_stg_ce_diccionario_key"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    column_name = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    data_type = Column(String(50), nullable=True)
    length = Column(String(20), nullable=True)
    valid_codes = Column(Text, nullable=True)


class StgCeSourceFiles(CeBase):
    """Metadatos de archivos fuente y seguimiento de carga."""

    __tablename__ = "stg_ce_source_files"
    __table_args__ = (UniqueConstraint("year", "slug", "file_type", name="uq_stg_ce_source_files_key"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    slug = Column(String(10), nullable=False)
    filename = Column(String(200), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    sha256 = Column(String(64), nullable=True)
    source_url = Column(String(500), nullable=True)
    downloaded_at = Column(DateTime, nullable=True)
    row_count = Column(Integer, nullable=True)
    status = Column(String(20), nullable=True)
    error_message = Column(Text, nullable=True)
    loaded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class StgCeData(CeBase):
    """Tabla principal de hechos de Censos Economicos. Una fila por observacion censal."""

    __tablename__ = "stg_ce_data"
    __table_args__ = (
        UniqueConstraint("year", "e03", "e04", "codigo", "id_estrato", name="uq_stg_ce_data_natural_key"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)

    # Columnas clave - cadena vacia '' cuando estan ausentes (no NULL) para soportar restriccion unica
    e03 = Column(String(2), nullable=False, server_default="")
    e04 = Column(String(3), nullable=False, server_default="")
    codigo = Column(String(20), nullable=False, server_default="")
    id_estrato = Column(String(5), nullable=False, server_default="")

    # Jerarquia de clasificacion SCIAN
    sector = Column(String(5), nullable=True)
    subsector = Column(String(3), nullable=True)
    rama = Column(String(4), nullable=True)
    subrama = Column(String(5), nullable=True)
    clase = Column(String(6), nullable=True)

    # Clave geografica derivada para joins
    cvegeo = Column(String(6), nullable=True)


# Agregar dinamicamente 98 columnas de variables economicas a StgCeData
for _col_name in CE_ECONOMIC_COLUMNS:
    setattr(StgCeData, _col_name, Column(_col_name, Float, nullable=True))
