from sqlalchemy import String, Text, ForeignKey, Date, Float, UniqueConstraint, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date

from core.pipelines.establecimientos_de_salud.attributes.establecimientos import EstablecimientosTables as T


class SaludBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]

class Localidades(SaludBase):
    __tablename__ = T.LOCALIDADES
    __table_args__ = (
        UniqueConstraint("municipio_id", "entidad_id", "clave_localidad", name="uq_localidades_clave"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave_localidad: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_municipalities
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)    # ref. cvegeo_states
    localidad: Mapped[str | None] = mapped_column(Text, nullable=True)


class Jurisdicciones(SaludBase):
    __tablename__ = T.JURISDICCIONES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    jurisdiccion: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_municipalities
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)    # ref. cvegeo_states

class Instituciones(SaludBase):
    __tablename__ = T.INSTITUCIONES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institucion: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class TiposEstablecimiento(SaludBase):
    __tablename__ = T.TIPOS_ESTABLECIMIENTO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tipo_establecimiento: Mapped[str] = mapped_column(Text, nullable=False)

class Tipologias(SaludBase):
    __tablename__ = T.TIPOLOGIAS

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipologia: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class Subtipologias(SaludBase):
    __tablename__ = T.SUBTIPOLOGIAS

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subtipologia: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class TiposVialidad(SaludBase):
    __tablename__ = T.TIPOS_VIALIDAD

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_vialidad: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class Vialidades(SaludBase):
    __tablename__ = T.VIALIDADES
    __table_args__ = (
        UniqueConstraint("vialidad", "tipo_vialidad_id", name="uq_vialidades_nombre_tipo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vialidad: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_vialidad_id: Mapped[int] = mapped_column(ForeignKey(f"{T.TIPOS_VIALIDAD}.id"), nullable=False)

class TiposAsentamiento(SaludBase):
    __tablename__ = T.TIPOS_ASENTAMIENTO

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_asentamiento: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class EstatusEstablecimiento(SaludBase):
    __tablename__ = T.ESTATUS_ESTABLECIMIENTO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    estatus_establecimiento: Mapped[str] = mapped_column(Text, nullable=False)

class NivelAtencion(SaludBase):
    __tablename__ = T.NIVEL_ATENCION

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nivel_atencion: Mapped[str] = mapped_column(Text, nullable=False)

class EstratoUnidad(SaludBase):
    __tablename__ = T.ESTRATO_UNIDAD

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    estrato_unidad: Mapped[str] = mapped_column(Text, nullable=False)

class TiposObra(SaludBase):
    __tablename__ = T.TIPOS_OBRA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_obra: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class RfcEstablecimientos(SaludBase):
    __tablename__ = T.RFC_ESTABLECIMIENTOS

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rfc: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class MarcasMoviles(SaludBase):
    __tablename__ = T.MARCAS_MOVILES
    __table_args__ = (
        UniqueConstraint("marca", "marca_especifica", "modelo", name="uq_marcas_moviles"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    marca: Mapped[str] = mapped_column(Text, nullable=False)
    marca_especifica: Mapped[str | None] = mapped_column(Text, nullable=True)
    modelo: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProgramasMoviles(SaludBase):
    __tablename__ = T.PROGRAMAS_MOVILES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    programa_movil: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class UnidadesMoviles(SaludBase):
    __tablename__ = T.UNIDADES_MOVILES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre_unidad_movil: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    nombre_comercial: Mapped[str | None] = mapped_column(Text, nullable=True)


class TiposUnidadMovil(SaludBase):
    __tablename__ = T.TIPOS_UNIDAD_MOVIL

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_unidad_movil: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class TipologiasMoviles(SaludBase):
    __tablename__ = T.TIPOLOGIAS_MOVILES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipologia_movil: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class InstitutosAdministracion(SaludBase):
    __tablename__ = T.INSTITUTOS_ADMINISTRACION

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instituto_administracion: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class Movimientos(SaludBase):
    __tablename__ = T.MOVIMIENTOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    movimiento: Mapped[str] = mapped_column(Text, nullable=False)


class MotivosBaja(SaludBase):
    __tablename__ = T.MOTIVOS_BAJA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    motivo_baja: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

class Establecimientos(SaludBase):
    __tablename__ = T.ESTABLECIMIENTOS

    clues: Mapped[str] = mapped_column(String(11), primary_key=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, primary_key=True)
    institucion_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.INSTITUCIONES}.id"), nullable=True)
    entidad_id: Mapped[int | None] = mapped_column(Integer, nullable=True)     # ref. cvegeo_states
    municipio_id: Mapped[int | None] = mapped_column(Integer, nullable=True)   # ref. cvegeo_municipalities
    localidad_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.LOCALIDADES}.id"), nullable=True)
    jurisdiccion_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.JURISDICCIONES}.id"), nullable=True)
    tipo_establecimiento_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.TIPOS_ESTABLECIMIENTO}.id"), nullable=True)
    tipologia_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.TIPOLOGIAS}.id"), nullable=True)
    subtipologia_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.SUBTIPOLOGIAS}.id"), nullable=True)
    unidad_movil_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.UNIDADES_MOVILES}.id"), nullable=True)
    vialidad_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.VIALIDADES}.id"), nullable=True)
    numero_exterior: Mapped[str | None] = mapped_column(Text, nullable=True)
    numero_interior: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo_asentamiento_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.TIPOS_ASENTAMIENTO}.id"), nullable=True)
    estatus_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.ESTATUS_ESTABLECIMIENTO}.id"), nullable=True)
    nivel_atencion_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.NIVEL_ATENCION}.id"), nullable=True)
    estrato_unidad_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.ESTRATO_UNIDAD}.id"), nullable=True)
    tipo_obra_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.TIPOS_OBRA}.id"), nullable=True)
    instituto_adm_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.INSTITUTOS_ADMINISTRACION}.id"), nullable=True)
    rfc_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.RFC_ESTABLECIMIENTOS}.id"), nullable=True)
    marca_movil_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.MARCAS_MOVILES}.id"), nullable=True)
    programa_movil_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.PROGRAMAS_MOVILES}.id"), nullable=True)
    tipo_unidad_movil_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.TIPOS_UNIDAD_MOVIL}.id"), nullable=True)
    tipologia_movil_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.TIPOLOGIAS_MOVILES}.id"), nullable=True)
    movimiento_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.MOVIMIENTOS}.id"), nullable=True)
    fecha_ultimo_movimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    motivo_baja_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.MOTIVOS_BAJA}.id"), nullable=True)
    fecha_efectiva_baja: Mapped[date | None] = mapped_column(Date, nullable=True)
    telefono_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    extension_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefono_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    extension_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_construccion: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_inicio_operacion: Mapped[date | None] = mapped_column(Date, nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
