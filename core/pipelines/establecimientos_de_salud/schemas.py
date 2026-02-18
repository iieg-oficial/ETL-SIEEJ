from sqlalchemy import String, ForeignKey, Date, Float, UniqueConstraint, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date


class SaludBase(DeclarativeBase):
    pass

class Localidades(SaludBase):
    __tablename__ = "localidades"
    __table_args__ = (
        UniqueConstraint("municipio_id", "entidad_id", "clave_localidad", name="uq_localidades_clave"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave_localidad: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_municipalities
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)    # ref. cvegeo_states
    localidad: Mapped[str] = mapped_column(String(200), nullable=False)


class Jurisdicciones(SaludBase):
    __tablename__ = "jurisdicciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    jurisdiccion: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_municipalities
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)    # ref. cvegeo_states

class Instituciones(SaludBase):
    __tablename__ = "instituciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institucion: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)


class TiposEstablecimiento(SaludBase):
    __tablename__ = "tipos_establecimiento"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, autoincrement=False)
    tipo_establecimiento: Mapped[str] = mapped_column(String(200), nullable=False)


class Tipologias(SaludBase):
    __tablename__ = "tipologias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipologia: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)


class Subtipologias(SaludBase):
    __tablename__ = "subtipologias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subtipologia: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)


class TiposVialidad(SaludBase):
    __tablename__ = "tipos_vialidad"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_vialidad: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class Vialidades(SaludBase):
    __tablename__ = "vialidades"
    __table_args__ = (
        UniqueConstraint("vialidad", "tipo_vialidad_id", name="uq_vialidades_nombre_tipo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vialidad: Mapped[str] = mapped_column(String(400), nullable=False)
    tipo_vialidad_id: Mapped[int] = mapped_column(ForeignKey("tipos_vialidad.id"), nullable=False)


class TiposAsentamiento(SaludBase):
    __tablename__ = "tipos_asentamiento"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, autoincrement=False)
    tipo_asentamiento: Mapped[str] = mapped_column(String(150), nullable=False)


class EstatusEstablecimiento(SaludBase):
    __tablename__ = "estatus_establecimiento"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, autoincrement=False)
    estatus_establecimiento: Mapped[str] = mapped_column(String(150), nullable=False)


class NivelAtencion(SaludBase):
    __tablename__ = "nivel_atencion"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, autoincrement=False)
    nivel_atencion: Mapped[str] = mapped_column(String(150), nullable=False)


class EstratoUnidad(SaludBase):
    __tablename__ = "estrato_unidad"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, autoincrement=False)
    estrato_unidad: Mapped[str] = mapped_column(String(150), nullable=False)


class TiposObra(SaludBase):
    __tablename__ = "tipos_obra"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, autoincrement=False)
    tipo_obra: Mapped[str] = mapped_column(String(150), nullable=False)


class RfcEstablecimientos(SaludBase):
    __tablename__ = "rfc_establecimientos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rfc: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)


class MarcasMoviles(SaludBase):
    __tablename__ = "marcas_moviles"
    __table_args__ = (
        UniqueConstraint("marca", "marca_especifica", "modelo", name="uq_marcas_moviles"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    marca: Mapped[str] = mapped_column(String(200), nullable=False)
    marca_especifica: Mapped[str | None] = mapped_column(String(200), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(200), nullable=True)


class ProgramasMoviles(SaludBase):
    __tablename__ = "programas_moviles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    programa_movil: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)


class TiposUnidadMovil(SaludBase):
    __tablename__ = "tipos_unidad_movil"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_unidad_movil: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)


class TipologiasMoviles(SaludBase):
    __tablename__ = "tipologias_moviles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipologia_movil: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)


class InstitutosAdministracion(SaludBase):
    __tablename__ = "institutos_administracion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instituto_administracion: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)


class Movimientos(SaludBase):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movimiento: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)


class MotivosBaja(SaludBase):
    __tablename__ = "motivos_baja"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    motivo_baja: Mapped[str] = mapped_column(String(400), nullable=False, unique=True)

class Establecimientos(SaludBase):
    __tablename__ = "establecimientos"

    clues: Mapped[str] = mapped_column(String(11), primary_key=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, primary_key=True)

    institucion_id: Mapped[int] = mapped_column(ForeignKey("instituciones.id"), nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)     # ref. cvegeo_states
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)   # ref. cvegeo_municipalities
    localidad_id: Mapped[int] = mapped_column(ForeignKey("localidades.id"), nullable=False)
    jurisdiccion_id: Mapped[int | None] = mapped_column(ForeignKey("jurisdicciones.id"), nullable=True)

    tipo_establecimiento_id: Mapped[str | None] = mapped_column(ForeignKey("tipos_establecimiento.id"), nullable=True)
    tipologia_id: Mapped[int | None] = mapped_column(ForeignKey("tipologias.id"), nullable=True)
    subtipologia_id: Mapped[int | None] = mapped_column(ForeignKey("subtipologias.id"), nullable=True)

    nombre_unidad: Mapped[str] = mapped_column(String(400), nullable=False)
    nombre_comercial: Mapped[str | None] = mapped_column(String(400), nullable=True)

    vialidad_id: Mapped[int | None] = mapped_column(ForeignKey("vialidades.id"), nullable=True)
    numero_exterior: Mapped[str | None] = mapped_column(String(30), nullable=True)
    numero_interior: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tipo_asentamiento_id: Mapped[str | None] = mapped_column(ForeignKey("tipos_asentamiento.id"), nullable=True)

    estatus_id: Mapped[str | None] = mapped_column(ForeignKey("estatus_establecimiento.id"), nullable=True)
    nivel_atencion_id: Mapped[str | None] = mapped_column(ForeignKey("nivel_atencion.id"), nullable=True)
    estrato_unidad_id: Mapped[str | None] = mapped_column(ForeignKey("estrato_unidad.id"), nullable=True)
    tipo_obra_id: Mapped[str | None] = mapped_column(ForeignKey("tipos_obra.id"), nullable=True)
    instituto_adm_id: Mapped[int | None] = mapped_column(ForeignKey("institutos_administracion.id"), nullable=True)

    rfc_id: Mapped[int | None] = mapped_column(ForeignKey("rfc_establecimientos.id"), nullable=True)

    marca_movil_id: Mapped[int | None] = mapped_column(ForeignKey("marcas_moviles.id"), nullable=True)
    programa_movil_id: Mapped[int | None] = mapped_column(ForeignKey("programas_moviles.id"), nullable=True)
    tipo_unidad_movil_id: Mapped[int | None] = mapped_column(ForeignKey("tipos_unidad_movil.id"), nullable=True)
    tipologia_movil_id: Mapped[int | None] = mapped_column(ForeignKey("tipologias_moviles.id"), nullable=True)

    movimiento_id: Mapped[int | None] = mapped_column(ForeignKey("movimientos.id"), nullable=True)
    fecha_ultimo_movimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    motivo_baja_id: Mapped[int | None] = mapped_column(ForeignKey("motivos_baja.id"), nullable=True)
    fecha_efectiva_baja: Mapped[date | None] = mapped_column(Date, nullable=True)

    telefono_1: Mapped[str | None] = mapped_column(String(20), nullable=True)
    extension_1: Mapped[str | None] = mapped_column(String(10), nullable=True)
    telefono_2: Mapped[str | None] = mapped_column(String(20), nullable=True)
    extension_2: Mapped[str | None] = mapped_column(String(10), nullable=True)

    fecha_construccion: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_inicio_operacion: Mapped[date | None] = mapped_column(Date, nullable=True)

    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
