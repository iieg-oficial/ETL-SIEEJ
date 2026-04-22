from sqlalchemy import Column, DateTime, Float, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase

from core.pipelines.censos_economicos.consts import CE_ECONOMIC_COLUMNS


class CeBase(DeclarativeBase):
    pass


class CeCatalogosActividades(CeBase):
    """Catalogo de codigos de actividad SCIAN."""

    __tablename__ = "ce_catalogos_actividades"
    __table_args__ = (UniqueConstraint("codigo", name="uq_ce_catalogos_actividades_codigo"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10), nullable=False, unique=True)
    descripcion = Column(String(500), nullable=True)
    clasificador = Column(String(50), nullable=True)


class CeCatalogosEntidadesMunicipios(CeBase):
    """Catalogo de entidad-municipio geografico."""

    __tablename__ = "ce_catalogos_entidades_municipios"
    __table_args__ = (UniqueConstraint("cvegeo", name="uq_ce_catalogos_entidades_municipios_cvegeo"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    cvegeo = Column(String(6), nullable=False, unique=True)
    cve_ent = Column(String(2), nullable=True)
    nom_ent = Column(String(100), nullable=True)
    nom_abr = Column(String(20), nullable=True)
    cve_mun = Column(String(3), nullable=True)
    nom_mun = Column(String(100), nullable=True)


class CeCatalogosEstratos(CeBase):
    """Catalogo de estratos por tamanio de establecimiento."""

    __tablename__ = "ce_catalogos_estratos"
    __table_args__ = (UniqueConstraint("id_estrato", name="uq_ce_catalogos_estratos_id_estrato"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_estrato = Column(String(5), nullable=False, unique=True)
    descripcion = Column(String(200), nullable=True)


class CeDiccionariosDatos(CeBase):
    """Diccionario de datos - documentacion de columnas extraida del CSV de diccionario."""

    __tablename__ = "ce_diccionarios_datos"
    __table_args__ = (UniqueConstraint("anio", "nombre_columna", name="uq_ce_diccionarios_datos_clave"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    anio = Column(Integer, nullable=False)
    nombre_columna = Column(String(20), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_dato = Column(String(50), nullable=True)
    longitud = Column(String(20), nullable=True)
    codigos_validos = Column(Text, nullable=True)


class CeArchivosFuente(CeBase):
    """Metadatos de archivos fuente y seguimiento de carga."""

    __tablename__ = "ce_archivos_fuente"
    __table_args__ = (UniqueConstraint("anio", "slug", "tipo_archivo", name="uq_ce_archivos_fuente_clave"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    anio = Column(Integer, nullable=False)
    slug = Column(String(10), nullable=False)
    nombre_archivo = Column(String(200), nullable=False)
    tipo_archivo = Column(String(50), nullable=False)
    ruta_archivo = Column(String(500), nullable=True)
    tamanio_archivo = Column(Integer, nullable=True)
    sha256 = Column(String(64), nullable=True)
    url_fuente = Column(String(500), nullable=True)
    descargado_en = Column(DateTime, nullable=True)
    conteo_filas = Column(Integer, nullable=True)
    estado = Column(String(20), nullable=True)
    mensaje_error = Column(Text, nullable=True)
    cargado_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, server_default=func.now())


class CeDatos(CeBase):
    """Tabla principal de hechos de Censos Economicos. Una fila por observacion censal."""

    __tablename__ = "ce_datos"
    __table_args__ = (UniqueConstraint("anio", "e03", "e04", "codigo", "id_estrato", name="uq_ce_datos_clave_natural"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    anio = Column(Integer, nullable=False)

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


# Agregar dinamicamente 98 columnas de variables economicas a CeDatos
for _col_name in CE_ECONOMIC_COLUMNS:
    setattr(CeDatos, _col_name, Column(_col_name, Float, nullable=True))
