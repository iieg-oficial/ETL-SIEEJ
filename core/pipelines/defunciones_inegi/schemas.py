from datetime import date, time

from sqlalchemy import (
    CHAR,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.defunciones_inegi.attributes import DefuncionesInegiTables as T

DESCRIPCION_MAX_LEN = 255
LOCALIDAD_MAX_LEN = 150
CLAVE_TEXT_MAX_LEN = 4


class DefuncionesInegiBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CodedCatalog(DefuncionesInegiBase):
    """Catálogo de dominio cerrado: la clave INEGI vive en `clave`, no en `id`."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class TextCodedCatalog(DefuncionesInegiBase):
    """Igual que CodedCatalog, para dominios cuya clave es alfanumérica."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(CLAVE_TEXT_MAX_LEN), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class CatAccidentalViolenta(CodedCatalog):
    __tablename__ = T.CAT_ACCIDENTAL_VIOLENTA


class CatAfromexicano(CodedCatalog):
    __tablename__ = T.CAT_AFROMEXICANO


class CatAreaUrbanaRural(CodedCatalog):
    __tablename__ = T.CAT_AREA_URBANA_RURAL


class CatAsistenciaMedica(CodedCatalog):
    __tablename__ = T.CAT_ASISTENCIA_MEDICA


class CatCertificante(CodedCatalog):
    __tablename__ = T.CAT_CERTIFICANTE


class CatCirugia(CodedCatalog):
    __tablename__ = T.CAT_CIRUGIA


class CatComplicaronEmbarazo(CodedCatalog):
    __tablename__ = T.CAT_COMPLICARON_EMBARAZO


class CatCondicionActividad(CodedCatalog):
    __tablename__ = T.CAT_CONDICION_ACTIVIDAD


class CatCondicionEmbarazo(CodedCatalog):
    __tablename__ = T.CAT_CONDICION_EMBARAZO


class CatCondicionIndigena(CodedCatalog):
    __tablename__ = T.CAT_CONDICION_INDIGENA


class CatDonador(CodedCatalog):
    __tablename__ = T.CAT_DONADOR


class CatEdadAgrupada(CodedCatalog):
    __tablename__ = T.CAT_EDAD_AGRUPADA


class CatEscolaridad(CodedCatalog):
    __tablename__ = T.CAT_ESCOLARIDAD


class CatEstadoCivil(CodedCatalog):
    __tablename__ = T.CAT_ESTADO_CIVIL


class CatLengua(CodedCatalog):
    __tablename__ = T.CAT_LENGUA


class CatLenguaIndigena(CodedCatalog):
    __tablename__ = T.CAT_LENGUA_INDIGENA


class CatListaCie(CodedCatalog):
    __tablename__ = T.CAT_LISTA_CIE


class CatListaMexicana(CodedCatalog):
    __tablename__ = T.CAT_LISTA_MEXICANA


class CatLugarOcurrencia(CodedCatalog):
    __tablename__ = T.CAT_LUGAR_OCURRENCIA


class CatMuerteEncefalica(CodedCatalog):
    __tablename__ = T.CAT_MUERTE_ENCEFALICA


class CatNacionalidad(CodedCatalog):
    __tablename__ = T.CAT_NACIONALIDAD


class CatNecropsia(CodedCatalog):
    __tablename__ = T.CAT_NECROPSIA


class CatOcurrioTrabajo(CodedCatalog):
    __tablename__ = T.CAT_OCURRIO_TRABAJO


class CatParentescoAgresor(CodedCatalog):
    __tablename__ = T.CAT_PARENTESCO_AGRESOR


class CatPresuntaDefuncionViolenta(CodedCatalog):
    __tablename__ = T.CAT_PRESUNTA_DEFUNCION_VIOLENTA


class CatRazonMaterna(CodedCatalog):
    __tablename__ = T.CAT_RAZON_MATERNA


class CatRelacionEmbarazo(CodedCatalog):
    __tablename__ = T.CAT_RELACION_EMBARAZO


class CatSexo(CodedCatalog):
    __tablename__ = T.CAT_SEXO


class CatSitioOcurrencia(CodedCatalog):
    __tablename__ = T.CAT_SITIO_OCURRENCIA


class CatTamanioLocalidad(CodedCatalog):
    __tablename__ = T.CAT_TAMANIO_LOCALIDAD


class CatUsoNecropsia(CodedCatalog):
    __tablename__ = T.CAT_USO_NECROPSIA


class CatViolenciaFamiliar(CodedCatalog):
    __tablename__ = T.CAT_VIOLENCIA_FAMILIAR


class CatGrupoListaMexicana(TextCodedCatalog):
    __tablename__ = T.CAT_GRUPO_LISTA_MEXICANA


class CatDistritoOaxaca(CodedCatalog):
    """Los 30 distritos de Oaxaca (901-930), único nivel geográfico intermedio del país."""

    __tablename__ = T.CAT_DISTRITO_OAXACA


class CatPais(DefuncionesInegiBase):
    __tablename__ = T.CAT_PAIS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    nombre_pais: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class CatCapituloGrupo(DefuncionesInegiBase):
    __tablename__ = T.CAT_CAPITULO_GRUPO
    __table_args__ = (UniqueConstraint("capitulo", "grupo", name="uq_capitulo_grupo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    capitulo: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    grupo: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class CatEdicion(DefuncionesInegiBase):
    __tablename__ = T.CAT_EDICION

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False, unique=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class CatOcupacion(DefuncionesInegiBase):
    __tablename__ = T.CAT_OCUPACION
    __table_args__ = (UniqueConstraint("clave", "edicion_id", name="uq_ocupacion_edicion"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)
    edicion_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_EDICION}.id"), nullable=False)


class CatDerechohabiencia(DefuncionesInegiBase):
    __tablename__ = T.CAT_DERECHOHABIENCIA
    __table_args__ = (UniqueConstraint("clave", "edicion_id", name="uq_derechohabiencia_edicion"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)
    edicion_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_EDICION}.id"), nullable=False)


class CatCie10(DefuncionesInegiBase):
    """CIE-10: alimenta causa de defunción, código adicional y causa materna."""

    __tablename__ = T.CAT_CIE10
    __table_args__ = (UniqueConstraint("clave", "edicion_id", name="uq_cie10_edicion"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(CHAR(CLAVE_TEXT_MAX_LEN), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)
    edicion_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_EDICION}.id"), nullable=False)


class CatLocalidad(DefuncionesInegiBase):
    """Sólo localidades. Entidad y municipio se resuelven contra cvegeo (FDW)."""

    __tablename__ = T.CAT_LOCALIDAD
    __table_args__ = (UniqueConstraint("cvegeo", "edicion_id", name="uq_localidad_edicion"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cvegeo: Mapped[int] = mapped_column(Integer, nullable=False)
    cve_ent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cve_mun: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cve_loc: Mapped[int] = mapped_column(Integer, nullable=False)
    localidad: Mapped[str] = mapped_column(String(LOCALIDAD_MAX_LEN), nullable=False)
    edicion_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_EDICION}.id"), nullable=False)


CODED_MODELS: tuple[type[DefuncionesInegiBase], ...] = (
    CatAccidentalViolenta,
    CatAfromexicano,
    CatAreaUrbanaRural,
    CatAsistenciaMedica,
    CatCertificante,
    CatCirugia,
    CatComplicaronEmbarazo,
    CatCondicionActividad,
    CatCondicionEmbarazo,
    CatCondicionIndigena,
    CatDistritoOaxaca,
    CatDonador,
    CatEdadAgrupada,
    CatEscolaridad,
    CatEstadoCivil,
    CatGrupoListaMexicana,
    CatLengua,
    CatLenguaIndigena,
    CatListaCie,
    CatListaMexicana,
    CatLugarOcurrencia,
    CatMuerteEncefalica,
    CatNacionalidad,
    CatNecropsia,
    CatOcurrioTrabajo,
    CatParentescoAgresor,
    CatPresuntaDefuncionViolenta,
    CatRazonMaterna,
    CatRelacionEmbarazo,
    CatSexo,
    CatSitioOcurrencia,
    CatTamanioLocalidad,
    CatUsoNecropsia,
    CatViolenciaFamiliar,
)

VERSIONED_MODELS: tuple[type[DefuncionesInegiBase], ...] = (
    CatOcupacion,
    CatDerechohabiencia,
)


class StgDefunciones(DefuncionesInegiBase):
    """Variables presentes en todas las ediciones (2017 en adelante)."""

    __tablename__ = T.STG_DEFUNCIONES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    edicion_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_EDICION}.id"), nullable=False, index=True)

    # Códigos crudos INEGI: se unen contra cvegeo_states / cvegeo_municipalities
    # (FDW), que no admite FK. Conservan los centinelas 88/99/999 que cvegeo
    # desconoce.
    entidad_registro_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, index=True)
    municipio_registro_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    entidad_residencia_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, index=True)
    municipio_residencia_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    entidad_ocurrencia_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, index=True)
    municipio_ocurrencia_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    entidad_lesion_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, index=True)
    municipio_lesion_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    localidad_residencia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDAD}.id"), nullable=True
    )
    localidad_ocurrencia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDAD}.id"), nullable=True
    )
    localidad_lesion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LOCALIDAD}.id"), nullable=True)
    tamanio_localidad_residencia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_TAMANIO_LOCALIDAD}.id"), nullable=True
    )
    tamanio_localidad_ocurrencia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_TAMANIO_LOCALIDAD}.id"), nullable=True
    )

    # Cada fecha se guarda completa y además desarmada: INEGI publica el año sin
    # el día o el mes con frecuencia, y la fecha nula perdía ese año.
    fecha_ocurrencia: Mapped[date | None] = mapped_column(Date, nullable=True)
    dia_ocurrencia: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mes_ocurrencia: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    anio_ocurrencia: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, index=True)
    fecha_registro: Mapped[date | None] = mapped_column(Date, nullable=True)
    dia_registro: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mes_registro: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    anio_registro: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    dia_nacimiento: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mes_nacimiento: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    anio_nacimiento: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    fecha_certificacion: Mapped[date | None] = mapped_column(Date, nullable=True)
    dia_certificacion: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mes_certificacion: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    anio_certificacion: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    hora_defuncion: Mapped[time | None] = mapped_column(Time, nullable=True)

    # `edad` viene codificada como unidad + cantidad en cuatro dígitos.
    edad_cantidad: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    edad_unidad: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    causa_defuncion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_CIE10}.id"), nullable=True)
    causa_materna_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_CIE10}.id"), nullable=True)
    capitulo_grupo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CAPITULO_GRUPO}.id"), nullable=True
    )
    lista_cie_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LISTA_CIE}.id"), nullable=True)
    lista_mexicana_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LISTA_MEXICANA}.id"), nullable=True
    )
    grupo_lista_mexicana_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_GRUPO_LISTA_MEXICANA}.id"), nullable=True
    )

    sexo_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_SEXO}.id"), nullable=True)
    edad_agrupada_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_EDAD_AGRUPADA}.id"), nullable=True
    )
    escolaridad_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ESCOLARIDAD}.id"), nullable=True)
    estado_civil_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ESTADO_CIVIL}.id"), nullable=True)
    ocupacion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_OCUPACION}.id"), nullable=True)
    condicion_actividad_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CONDICION_ACTIVIDAD}.id"), nullable=True
    )
    nacionalidad_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_NACIONALIDAD}.id"), nullable=True)
    lengua_indigena_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LENGUA_INDIGENA}.id"), nullable=True
    )
    derechohabiencia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_DERECHOHABIENCIA}.id"), nullable=True
    )
    area_urbana_rural_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_AREA_URBANA_RURAL}.id"), nullable=True
    )

    asistencia_medica_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_ASISTENCIA_MEDICA}.id"), nullable=True
    )
    necropsia_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_NECROPSIA}.id"), nullable=True)
    sitio_ocurrencia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_SITIO_OCURRENCIA}.id"), nullable=True
    )
    lugar_ocurrencia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LUGAR_OCURRENCIA}.id"), nullable=True
    )
    certificante_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_CERTIFICANTE}.id"), nullable=True)
    presunta_defuncion_violenta_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_PRESUNTA_DEFUNCION_VIOLENTA}.id"), nullable=True
    )
    ocurrio_trabajo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_OCURRIO_TRABAJO}.id"), nullable=True
    )
    violencia_familiar_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_VIOLENCIA_FAMILIAR}.id"), nullable=True
    )
    parentesco_agresor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_PARENTESCO_AGRESOR}.id"), nullable=True
    )

    condicion_embarazo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CONDICION_EMBARAZO}.id"), nullable=True
    )
    relacion_embarazo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_RELACION_EMBARAZO}.id"), nullable=True
    )
    complicaron_embarazo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_COMPLICARON_EMBARAZO}.id"), nullable=True
    )
    razon_materna_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_RAZON_MATERNA}.id"), nullable=True
    )

    distrito_registro_oaxaca_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_DISTRITO_OAXACA}.id"), nullable=True
    )
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class StgDefuncionesAmpliacion(DefuncionesInegiBase):
    """Variables que INEGI agregó en 2022. Sin filas para ediciones anteriores."""

    __tablename__ = T.STG_DEFUNCIONES_AMPLIACION

    defuncion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.STG_DEFUNCIONES}.id"), primary_key=True, autoincrement=False
    )

    codigo_adicional_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_CIE10}.id"), nullable=True)

    # `ent_nac` mezcla entidades federativas y países en un solo campo; aquí se
    # separan y son mutuamente excluyentes.
    entidad_nacimiento_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    pais_nacimiento_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_PAIS}.id"), nullable=True)
    pais_nacionalidad_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_PAIS}.id"), nullable=True)

    lengua_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LENGUA}.id"), nullable=True)
    localidad_registro_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDAD}.id"), nullable=True
    )
    tamanio_localidad_registro_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_TAMANIO_LOCALIDAD}.id"), nullable=True
    )

    afromexicano_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_AFROMEXICANO}.id"), nullable=True)
    condicion_indigena_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CONDICION_INDIGENA}.id"), nullable=True
    )
    cirugia_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_CIRUGIA}.id"), nullable=True)
    accidental_violenta_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_ACCIDENTAL_VIOLENTA}.id"), nullable=True
    )
    uso_necropsia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_USO_NECROPSIA}.id"), nullable=True
    )
    muerte_encefalica_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_MUERTE_ENCEFALICA}.id"), nullable=True
    )
    donador_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_DONADOR}.id"), nullable=True)

    semanas_gestacion: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    peso_gramos: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)


# Tabla -> modelo, para que el load no tenga que ramificar por nombre.
STABLE_MODELS: dict[str, type[DefuncionesInegiBase]] = {model.__tablename__: model for model in CODED_MODELS}
CATALOG_MODELS: dict[str, type[DefuncionesInegiBase]] = {
    model.__tablename__: model for model in (*CODED_MODELS, *VERSIONED_MODELS)
}
