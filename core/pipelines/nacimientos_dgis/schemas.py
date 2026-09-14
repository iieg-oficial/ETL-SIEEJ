from datetime import date, time

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T

DESCRIPCION_MAX_LEN = 255
CLAVE_TEXT_MAX_LEN = 11


class NacimientosDgisBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CodedCatalog(NacimientosDgisBase):
    """Catálogo de dominio cerrado: la clave SINAC vive en `clave`, no en `id`."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class TextCodedCatalog(NacimientosDgisBase):
    """Igual que CodedCatalog, para dominios cuya clave es alfanumérica."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(CLAVE_TEXT_MAX_LEN), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class CatSiNo(CodedCatalog):
    """Dominio SI/NO de SINAC: no es binario, distingue no aplica de se ignora."""

    __tablename__ = T.CAT_SI_NO


class CatSexo(CodedCatalog):
    __tablename__ = T.CAT_SEXO


class CatEstadoConyugal(CodedCatalog):
    __tablename__ = T.CAT_ESTADO_CONYUGAL


class CatEscolaridad(CodedCatalog):
    __tablename__ = T.CAT_ESCOLARIDAD


class CatAfiliacion(CodedCatalog):
    __tablename__ = T.CAT_AFILIACION


class CatOcupacionHabitual(CodedCatalog):
    __tablename__ = T.CAT_OCUPACION_HABITUAL


class CatLugarNacimiento(CodedCatalog):
    __tablename__ = T.CAT_LUGAR_NACIMIENTO


class CatProductoEmbarazo(CodedCatalog):
    __tablename__ = T.CAT_PRODUCTO_EMBARAZO


class CatResolucionEmbarazo(CodedCatalog):
    __tablename__ = T.CAT_RESOLUCION_EMBARAZO


class CatEntidad(CodedCatalog):
    __tablename__ = T.CAT_ENTIDAD


class CatMunicipio(CodedCatalog):
    """Clave compuesta `EEMMM`: SINAC publica el municipio por entidad."""

    __tablename__ = T.CAT_MUNICIPIO


class CatLocalidad(CodedCatalog):
    """Clave compuesta `EEMMMLLLL`."""

    __tablename__ = T.CAT_LOCALIDAD


class CatDiagnostico(TextCodedCatalog):
    """CIE-10 de la anomalía congénita del nacido vivo."""

    __tablename__ = T.CAT_DIAGNOSTICO


class CatEstablecimientoSalud(TextCodedCatalog):
    """CLUES del sitio de atención del parto."""

    __tablename__ = T.CAT_ESTABLECIMIENTO_SALUD


CODED_MODELS: dict[str, type[NacimientosDgisBase]] = {
    T.CAT_SI_NO: CatSiNo,
    T.CAT_SEXO: CatSexo,
    T.CAT_ESTADO_CONYUGAL: CatEstadoConyugal,
    T.CAT_ESCOLARIDAD: CatEscolaridad,
    T.CAT_AFILIACION: CatAfiliacion,
    T.CAT_OCUPACION_HABITUAL: CatOcupacionHabitual,
    T.CAT_LUGAR_NACIMIENTO: CatLugarNacimiento,
    T.CAT_PRODUCTO_EMBARAZO: CatProductoEmbarazo,
    T.CAT_RESOLUCION_EMBARAZO: CatResolucionEmbarazo,
    T.CAT_ENTIDAD: CatEntidad,
    T.CAT_MUNICIPIO: CatMunicipio,
    T.CAT_LOCALIDAD: CatLocalidad,
    T.CAT_DIAGNOSTICO: CatDiagnostico,
    T.CAT_ESTABLECIMIENTO_SALUD: CatEstablecimientoSalud,
}


class StgNacimientosEdadMadre(NacimientosDgisBase):
    """Agregado por año, municipio de residencia y edad de la madre.

    Alimenta la tasa de fecundidad general y las tasas específicas de madres
    de 10-14 y 15-19. El grano es el agregado, no el nacimiento.
    """

    __tablename__ = T.STG_NACIMIENTOS_EDAD_MADRE
    __table_args__ = (UniqueConstraint("anio", "cve_geo", "edad_madre", name="uq_nacimientos_anio_geo_edad"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cve_geo: Mapped[int] = mapped_column(Integer, nullable=False)
    edad_madre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    tot_nac: Mapped[int] = mapped_column(Integer, nullable=False)
    nac_padre_conocido: Mapped[int] = mapped_column(Integer, nullable=False)
    nac_padre_18_mas: Mapped[int] = mapped_column(Integer, nullable=False)
    nac_padre_25_mas: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class StgNacimientosCertificados(NacimientosDgisBase):
    """Microdato: una fila por certificado de nacimiento de madre residente en Jalisco."""

    __tablename__ = T.STG_NACIMIENTOS_CERTIFICADOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    hora_nacimiento: Mapped[time | None] = mapped_column(Time, nullable=True)

    cve_geo: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    localidad_residencia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDAD}.id"), nullable=True
    )

    edad_madre: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    edad_padre: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    se_considera_indigena_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_SI_NO}.id"), nullable=True
    )
    habla_lengua_indigena_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_SI_NO}.id"), nullable=True
    )
    estado_conyugal_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_ESTADO_CONYUGAL}.id"), nullable=True
    )
    escolaridad_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ESCOLARIDAD}.id"), nullable=True)
    interrumpio_estudios_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_SI_NO}.id"), nullable=True)
    ocupacion_habitual_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_OCUPACION_HABITUAL}.id"), nullable=True
    )
    trabaja_actualmente_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_SI_NO}.id"), nullable=True)
    afiliacion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_AFILIACION}.id"), nullable=True)

    numero_embarazos: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    atencion_prenatal_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_SI_NO}.id"), nullable=True)
    total_consultas: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sobrevivio_parto_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_SI_NO}.id"), nullable=True)

    sexo_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_SEXO}.id"), nullable=True)
    edad_gestacional: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    talla: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    peso: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    producto_embarazo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_PRODUCTO_EMBARAZO}.id"), nullable=True
    )
    orden_producto: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    total_productos: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    diagnostico_1_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_DIAGNOSTICO}.id"), nullable=True)
    diagnostico_2_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_DIAGNOSTICO}.id"), nullable=True)

    lugar_nacimiento_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LUGAR_NACIMIENTO}.id"), nullable=True
    )
    establecimiento_salud_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_ESTABLECIMIENTO_SALUD}.id"), nullable=True
    )
    tiempo_traslado_minutos: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    resolucion_embarazo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_RESOLUCION_EMBARAZO}.id"), nullable=True
    )

    entidad_parto_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ENTIDAD}.id"), nullable=True)
    municipio_parto_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_MUNICIPIO}.id"), nullable=True)
    localidad_parto_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LOCALIDAD}.id"), nullable=True)

    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
