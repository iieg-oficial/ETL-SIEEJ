from datetime import date
from typing import ClassVar

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.defunciones.attributes import DefuncionesTables as T
from core.pipelines.defunciones.constants import (
    CATALOG_FK_COLUMNS,
    CODED_SOURCE_COLUMNS,
    COLUMN_CATALOG,
    EDAD_DATASET,
    NOMBRE_EDAD_COL,
    VERSIONED_SOURCE_COLUMNS,
)

DESCRIPCION_MAX_LEN = 255
CLAVE_TEXT_MAX_LEN = 20


class DefuncionesBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatEdad(DefuncionesBase):
    __tablename__ = T.CAT_EDAD

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre_edad: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)


class CatAsistenciaMedica(DefuncionesBase):
    __tablename__ = T.CAT_ASISTENCIA_MEDICA
    keyword: ClassVar[str] = "asistencia_medica"
    exclude: ClassVar[tuple[str, ...]] = ()
    text_key: ClassVar[bool] = False

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class CatSexo(DefuncionesBase):
    __tablename__ = T.CAT_SEXO
    keyword: ClassVar[str] = "sexo"
    exclude: ClassVar[tuple[str, ...]] = ()
    text_key: ClassVar[bool] = False

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class CatCapituloGrupo(DefuncionesBase):
    __tablename__ = T.CAT_CAPITULO_GRUPO
    __table_args__ = (UniqueConstraint("cap", "gpo", name="uq_capitulo_grupo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cap: Mapped[int] = mapped_column(Integer, nullable=False)
    gpo: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class CatEdicion(DefuncionesBase):
    __tablename__ = T.CAT_EDICION

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class VersionedCatalog(DefuncionesBase):
    __abstract__ = True
    keyword: ClassVar[str] = ""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[int] = mapped_column(Integer, nullable=False)
    edicion_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_EDICION}.id"), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class CatOcupacion(VersionedCatalog):
    __tablename__ = T.CAT_OCUPACION
    __table_args__ = (UniqueConstraint("codigo", "edicion_id", name="uq_ocupacion_edicion"),)
    keyword: ClassVar[str] = "ocupacion"


class CatDerechohabiencia(VersionedCatalog):
    __tablename__ = T.CAT_DERECHO_HABIENCIA
    __table_args__ = (UniqueConstraint("codigo", "edicion_id", name="uq_derechohabiencia_edicion"),)
    keyword: ClassVar[str] = "derechohabiencia"


class CatPresuntaDefuncionViolenta(VersionedCatalog):
    __tablename__ = T.CAT_PRESUNTA_DEFUNCION_VIOLENTA
    __table_args__ = (UniqueConstraint("codigo", "edicion_id", name="uq_presunta_violenta_edicion"),)
    keyword: ClassVar[str] = "presunta"


class CatLocalidades(VersionedCatalog):
    __tablename__ = T.CAT_LOCALIDADES
    __table_args__ = (UniqueConstraint("codigo", "edicion_id", name="uq_localidades_edicion"),)
    keyword: ClassVar[str] = "entidad_municipio_localidad"

    cve_ent: Mapped[int] = mapped_column(Integer, nullable=False)
    cve_mun: Mapped[int] = mapped_column(Integer, nullable=False)
    cve_loc: Mapped[int] = mapped_column(Integer, nullable=False)


VERSIONED_MODELS: tuple[type[DefuncionesBase], ...] = (
    CatOcupacion,
    CatDerechohabiencia,
    CatPresuntaDefuncionViolenta,
)


class StgDefunciones(DefuncionesBase):
    __tablename__ = T.STG_DEFUNCIONES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entidad_registro: Mapped[int | None] = mapped_column(Integer, nullable=True)
    entidad_registro_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    municipio_regis: Mapped[int | None] = mapped_column(Integer, nullable=True)
    municipio_regis_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    tamanio_loc_regis_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_TAMANO_LOCALIDAD}.id"), nullable=True
    )
    localidad_regis_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    entidad_resid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    entidad_resid_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True)
    municipio_resid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tamanio_loc_resid_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_TAMANO_LOCALIDAD}.id"), nullable=True
    )
    localidad_resid_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    entidad_ocurr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    entidad_ocurr_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True)
    municipio_ocurr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tamanio_loc_ocurr_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_TAMANO_LOCALIDAD}.id"), nullable=True
    )
    localidad_ocurr_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    causa_defuncion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CAUSA_DEFUNCION}.id"), nullable=True
    )
    cod_adicional_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CODIGO_ADICIONAL}.id"), nullable=True
    )
    lista_mex_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LISTA_MEXICANA}.id"), nullable=True)
    sexo_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_SEXO}.id"), nullable=True)
    entidad_pais_nac_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_ENTIDAD_PAIS}.id"), nullable=True
    )
    afromex_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_AFROMEXICANO}.id"), nullable=True)
    cond_indigena_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CONDICION_INDIGENA}.id"), nullable=True
    )
    lengua_indigena_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LENGUA_INDIGENA}.id"), nullable=True
    )
    lenguas_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LENGUAS}.id"), nullable=True)
    nacionalid_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_NACIONALIDAD}.id"), nullable=True)
    origen_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ORIGEN}.id"), nullable=True)
    edad_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_EDAD}.id"), nullable=True)
    edad_gestacional_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_EDAD_GESTACIONAL}.id"), nullable=True
    )
    gramos_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_PESO_PRODUCTO}.id"), nullable=True)
    dia_ocurr_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_DIA}.id"), nullable=True)
    mes_ocurr_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_MES}.id"), nullable=True)
    anio_ocurr_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ANIO}.id"), nullable=True)
    dia_registro_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_DIA}.id"), nullable=True)
    mes_registro_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_MES}.id"), nullable=True)
    anio_registro_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ANIO}.id"), nullable=True)
    dia_nacimiento_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_DIA}.id"), nullable=True)
    mes_nacimiento_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_MES}.id"), nullable=True)
    anio_nacimiento_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ANIO}.id"), nullable=True)
    condicion_act_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CONDICION_ACTIVIDAD}.id"), nullable=True
    )
    ocupacion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_OCUPACION}.id"), nullable=True)
    escolaridad_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ESCOLARIDAD}.id"), nullable=True)
    edo_civil_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ESTADO_CIVIL}.id"), nullable=True)
    tipo_defuncion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_PRESUNTA_DEFUNCION_VIOLENTA}.id"), nullable=True
    )
    ocurr_trab_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_OCURRIO_TRABAJO}.id"), nullable=True)
    lugar_ocurr_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LUGAR_OCURRENCIA}.id"), nullable=True
    )
    parentesco_agre_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_PARENTESCO_AGRESOR}.id"), nullable=True
    )
    violencia_familiar_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_VIOLENCIA_FAMILIAR}.id"), nullable=True
    )
    asist_medica_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_ASISTENCIA_MEDICA}.id"), nullable=True
    )
    cirugia_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_CIRUGIA}.id"), nullable=True)
    accidental_vio_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_ACCIDENTAL_VIOLENTA}.id"), nullable=True
    )
    necropsia_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_NECROPSIA}.id"), nullable=True)
    uso_necropsia_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_USO_NECROPSIA}.id"), nullable=True
    )
    encefalica_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_MUERTE_ENCEFALICA}.id"), nullable=True
    )
    donador_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_DONADOR}.id"), nullable=True)
    sitio_ocur_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_SITIO_OCURRENCIA}.id"), nullable=True
    )
    certificante_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_CERTIFICANTE}.id"), nullable=True)
    derecho_hab_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_DERECHO_HABIENCIA}.id"), nullable=True
    )
    embarazo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CONDICION_EMBARAZO}.id"), nullable=True
    )
    rel_emba_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_RELACION_CON_EMBARAZO}.id"), nullable=True
    )
    horas_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_HORA}.id"), nullable=True)
    minutos_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_MINUTO}.id"), nullable=True)
    capitulo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grupo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capitulo_grupo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CAPITULO_GRUPO}.id"), nullable=True
    )
    lista_cie_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LISTA_CIE}.id"), nullable=True)
    gr_lismex_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_GRUPO_LISTA_MEXICANA}.id"), nullable=True
    )
    area_urbana_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_AREA_URBANA_RURAL}.id"), nullable=True
    )
    edad_agrupada_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_EDAD_AGRUPADA}.id"), nullable=True
    )
    complicaron_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_COMPLICARON_EMBARAZO}.id"), nullable=True
    )
    dia_certificacion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_DIA}.id"), nullable=True)
    mes_certificacion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_MES}.id"), nullable=True)
    anio_certificacion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ANIO}.id"), nullable=True)
    maternas_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_CAUSA_DEFUNCION}.id"), nullable=True)
    entidad_ocules: Mapped[int | None] = mapped_column(Integer, nullable=True)
    entidad_ocules_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True)
    municipio_ocules: Mapped[int | None] = mapped_column(Integer, nullable=True)
    municipio_ocules_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    localidad_ocules_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    razon_m_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_RAZON_MATERNA}.id"), nullable=True)
    dis_re_oax: Mapped[int | None] = mapped_column(Integer, nullable=True)

    municipio_resid_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    municipio_ocurr_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True
    )
    # cvegeo_municipalities is a foreign table (FDW); PostgreSQL forbids FKs to foreign tables.
    # These carry the geographic key/geometry for maps only, never the label.
    cvegeo_resid_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cvegeo_ocurr_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    edicion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_EDICION}.id"), nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class _CatalogBase(DefuncionesBase):
    __abstract__ = True

    keyword: ClassVar[str] = ""
    exclude: ClassVar[tuple[str, ...]] = ()
    text_key: ClassVar[bool] = False

    descripcion: Mapped[str] = mapped_column(String(DESCRIPCION_MAX_LEN), nullable=False)


class IntCatalog(_CatalogBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)


class CodedCatalog(_CatalogBase):
    __abstract__ = True
    text_key: ClassVar[bool] = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(CLAVE_TEXT_MAX_LEN), nullable=False, unique=True)


class CatEscolaridad(IntCatalog):
    __tablename__ = T.CAT_ESCOLARIDAD
    keyword: ClassVar[str] = "escolaridad"


class CatEstadoCivil(IntCatalog):
    __tablename__ = T.CAT_ESTADO_CIVIL
    keyword: ClassVar[str] = "estado_civil"


class CatNacionalidad(IntCatalog):
    __tablename__ = T.CAT_NACIONALIDAD
    keyword: ClassVar[str] = "nacionalidad"


class CatCondicionActividad(IntCatalog):
    __tablename__ = T.CAT_CONDICION_ACTIVIDAD
    keyword: ClassVar[str] = "condicion_actividad"


class CatAfromexicano(IntCatalog):
    __tablename__ = T.CAT_AFROMEXICANO
    keyword: ClassVar[str] = "afromexi"


class CatCondicionIndigena(IntCatalog):
    __tablename__ = T.CAT_CONDICION_INDIGENA
    keyword: ClassVar[str] = "conind"


class CatLenguaIndigena(IntCatalog):
    __tablename__ = T.CAT_LENGUA_INDIGENA
    keyword: ClassVar[str] = "lengua_indigena"


class CatLenguas(IntCatalog):
    __tablename__ = T.CAT_LENGUAS
    keyword: ClassVar[str] = "lenguas"


class CatEdadAgrupada(IntCatalog):
    __tablename__ = T.CAT_EDAD_AGRUPADA
    keyword: ClassVar[str] = "edad_agrupada"


class CatEdadGestacional(IntCatalog):
    __tablename__ = T.CAT_EDAD_GESTACIONAL
    keyword: ClassVar[str] = "edadgest"


class CatOrigen(IntCatalog):
    __tablename__ = T.CAT_ORIGEN
    keyword: ClassVar[str] = "paises"


class CatEntidadPais(IntCatalog):
    __tablename__ = T.CAT_ENTIDAD_PAIS
    keyword: ClassVar[str] = "paises"


class CatCausaDefuncion(CodedCatalog):
    __tablename__ = T.CAT_CAUSA_DEFUNCION
    keyword: ClassVar[str] = "causa_defuncion"


class CatCodigoAdicional(CodedCatalog):
    __tablename__ = T.CAT_CODIGO_ADICIONAL
    keyword: ClassVar[str] = "codigo_adicional"


class CatListaMexicana(CodedCatalog):
    __tablename__ = T.CAT_LISTA_MEXICANA
    keyword: ClassVar[str] = "lista_mexicana"
    exclude: ClassVar[tuple[str, ...]] = ("grupo",)


class CatGrupoListaMexicana(CodedCatalog):
    __tablename__ = T.CAT_GRUPO_LISTA_MEXICANA
    keyword: ClassVar[str] = "grupo_lista_mexicana"


class CatListaCie(IntCatalog):
    __tablename__ = T.CAT_LISTA_CIE
    keyword: ClassVar[str] = "lista1"


class CatLugarOcurrencia(IntCatalog):
    __tablename__ = T.CAT_LUGAR_OCURRENCIA
    keyword: ClassVar[str] = "lugar_ocurrencia"


class CatSitioOcurrencia(IntCatalog):
    __tablename__ = T.CAT_SITIO_OCURRENCIA
    keyword: ClassVar[str] = "sitio_ocurrencia"


class CatNecropsia(IntCatalog):
    __tablename__ = T.CAT_NECROPSIA
    keyword: ClassVar[str] = "necropsia"
    exclude: ClassVar[tuple[str, ...]] = ("uso",)


class CatUsoNecropsia(IntCatalog):
    __tablename__ = T.CAT_USO_NECROPSIA
    keyword: ClassVar[str] = "uso_necropsia"


class CatCertificante(IntCatalog):
    __tablename__ = T.CAT_CERTIFICANTE
    keyword: ClassVar[str] = "certificante"


class CatOcurrioTrabajo(IntCatalog):
    __tablename__ = T.CAT_OCURRIO_TRABAJO
    keyword: ClassVar[str] = "ocurrio_trabajo"


class CatAccidentalViolenta(IntCatalog):
    __tablename__ = T.CAT_ACCIDENTAL_VIOLENTA
    keyword: ClassVar[str] = "accidental_violenta"


class CatCirugia(IntCatalog):
    __tablename__ = T.CAT_CIRUGIA
    keyword: ClassVar[str] = "cirugia"


class CatMuerteEncefalica(IntCatalog):
    __tablename__ = T.CAT_MUERTE_ENCEFALICA
    keyword: ClassVar[str] = "encefalica"


class CatDonador(IntCatalog):
    __tablename__ = T.CAT_DONADOR
    keyword: ClassVar[str] = "donador"


class CatAreaUrbanaRural(IntCatalog):
    __tablename__ = T.CAT_AREA_URBANA_RURAL
    keyword: ClassVar[str] = "area_urbana_rural"


class CatTamanoLocalidad(IntCatalog):
    __tablename__ = T.CAT_TAMANO_LOCALIDAD
    keyword: ClassVar[str] = "tama"


class CatCondicionEmbarazo(IntCatalog):
    __tablename__ = T.CAT_CONDICION_EMBARAZO
    keyword: ClassVar[str] = "condicion_embarazo"


class CatRelacionConEmbarazo(IntCatalog):
    __tablename__ = T.CAT_RELACION_CON_EMBARAZO
    keyword: ClassVar[str] = "relacion_con_embarazo"


class CatComplicaronEmbarazo(IntCatalog):
    __tablename__ = T.CAT_COMPLICARON_EMBARAZO
    keyword: ClassVar[str] = "complicaron_embarazo"


class CatRazonMaterna(IntCatalog):
    __tablename__ = T.CAT_RAZON_MATERNA


class CatPesoProducto(CodedCatalog):
    __tablename__ = T.CAT_PESO_PRODUCTO
    keyword: ClassVar[str] = "pesoprod"


class CatViolenciaFamiliar(IntCatalog):
    __tablename__ = T.CAT_VIOLENCIA_FAMILIAR
    keyword: ClassVar[str] = "violencia_familiar"


class CatParentescoAgresor(IntCatalog):
    __tablename__ = T.CAT_PARENTESCO_AGRESOR
    keyword: ClassVar[str] = "parentesco_agresor"


class CatDia(IntCatalog):
    __tablename__ = T.CAT_DIA
    keyword: ClassVar[str] = "dia"


class CatMes(IntCatalog):
    __tablename__ = T.CAT_MES
    keyword: ClassVar[str] = "mes"


class CatAnio(IntCatalog):
    __tablename__ = T.CAT_ANIO
    keyword: ClassVar[str] = "año"
    exclude: ClassVar[tuple[str, ...]] = ("tama",)


class CatHora(IntCatalog):
    __tablename__ = T.CAT_HORA
    keyword: ClassVar[str] = "hora"


class CatMinuto(IntCatalog):
    __tablename__ = T.CAT_MINUTO
    keyword: ClassVar[str] = "minuto"


CATALOG_MODELS: tuple[type[DefuncionesBase], ...] = (
    CatSexo,
    CatAsistenciaMedica,
    CatEscolaridad,
    CatEstadoCivil,
    CatNacionalidad,
    CatCondicionActividad,
    CatAfromexicano,
    CatCondicionIndigena,
    CatLenguaIndigena,
    CatLenguas,
    CatEdadAgrupada,
    CatEdadGestacional,
    CatOrigen,
    CatEntidadPais,
    CatListaCie,
    CatLugarOcurrencia,
    CatSitioOcurrencia,
    CatNecropsia,
    CatUsoNecropsia,
    CatCertificante,
    CatOcurrioTrabajo,
    CatAccidentalViolenta,
    CatCirugia,
    CatMuerteEncefalica,
    CatDonador,
    CatAreaUrbanaRural,
    CatTamanoLocalidad,
    CatCondicionEmbarazo,
    CatRelacionConEmbarazo,
    CatComplicaronEmbarazo,
    CatViolenciaFamiliar,
    CatParentescoAgresor,
    CatDia,
    CatMes,
    CatAnio,
    CatHora,
    CatMinuto,
)

CODED_MODELS: tuple[type[DefuncionesBase], ...] = (
    CatCausaDefuncion,
    CatCodigoAdicional,
    CatListaMexicana,
    CatGrupoListaMexicana,
    CatPesoProducto,
)


OVERRIDE_MODELS: tuple[type[DefuncionesBase], ...] = (CatRazonMaterna,)


def _by_table(models: tuple[type, ...]) -> dict[str, type]:
    return {model.__tablename__: model for model in models}


def _fk_models(source_columns: dict[str, str], by_table: dict[str, type]) -> dict[str, type]:
    return {CATALOG_FK_COLUMNS[col]: by_table[table] for col, table in source_columns.items()}


CATALOG_SPECS: dict[str, tuple[type, str]] = {
    EDAD_DATASET: (CatEdad, NOMBRE_EDAD_COL),
    **{model.__tablename__: (model, "descripcion") for model in (*CATALOG_MODELS, *OVERRIDE_MODELS)},
}

FK_CATALOGS: dict[str, type] = _fk_models(
    {
        col: table
        for col, table in COLUMN_CATALOG.items()
        if col not in VERSIONED_SOURCE_COLUMNS and col not in CODED_SOURCE_COLUMNS
    },
    _by_table((CatEdad, *CATALOG_MODELS, *OVERRIDE_MODELS)),
)

VERSIONED_FK_MODELS: dict[str, type] = _fk_models(VERSIONED_SOURCE_COLUMNS, _by_table(VERSIONED_MODELS))

CODED_FK_MODELS: dict[str, type] = _fk_models(CODED_SOURCE_COLUMNS, _by_table(CODED_MODELS))
