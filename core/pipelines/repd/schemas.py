from datetime import date, datetime
from typing import Optional

from sqlalchemy import Index, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class RepdBase(DeclarativeBase):
    pass


# Catalogos


class CatSexo(RepdBase):
    __tablename__ = "cat_sexo"
    __table_args__ = (UniqueConstraint("nombre", name="uq_cat_sexo_nombre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True)


class CatNacionalidad(RepdBase):
    __tablename__ = "cat_nacionalidad"
    __table_args__ = (UniqueConstraint("nombre", name="uq_cat_nacionalidad_nombre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)


class CatRangoEdad(RepdBase):
    __tablename__ = "cat_rango_edad"
    __table_args__ = (UniqueConstraint("nombre", name="uq_cat_rango_edad_nombre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)


class CatEstatus(RepdBase):
    __tablename__ = "cat_estatus"
    __table_args__ = (UniqueConstraint("nombre", name="uq_cat_estatus_nombre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)


class CatCondicionLocalizacion(RepdBase):
    __tablename__ = "cat_condicion_localizacion"
    __table_args__ = (UniqueConstraint("nombre", name="uq_cat_condicion_localizacion_nombre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True)


class CatClasificacionLocalizacion(RepdBase):
    __tablename__ = "cat_clasificacion_localizacion"
    __table_args__ = (UniqueConstraint("nombre", name="uq_cat_clasificacion_localizacion_nombre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)


class CatTipoCierre(RepdBase):
    __tablename__ = "cat_tipo_cierre"
    __table_args__ = (UniqueConstraint("nombre", name="uq_cat_tipo_cierre_nombre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)


# Tabla actual: una fila vigente por FEB


class Casos(RepdBase):
    __tablename__ = "stg_repd_casos"
    __table_args__ = (
        UniqueConstraint("feb", name="uq_repd_casos_feb"),
        Index("ix_repd_casos_feb", "feb", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    feb: Mapped[str] = mapped_column(String(64), unique=True)
    sexo_id: Mapped[int]
    nacionalidad_id: Mapped[int]
    rango_edad_id: Mapped[int]
    fecha_reporte: Mapped[date]
    fecha_desaparicion: Mapped[Optional[date]]
    estado_desaparicion: Mapped[Optional[str]] = mapped_column(String(100))
    municipio_desaparicion_id: Mapped[Optional[int]]
    estatus_id: Mapped[int]
    fecha_localizacion: Mapped[Optional[date]]
    condicion_localizacion_id: Mapped[Optional[int]]
    clasificacion_localizacion_id: Mapped[Optional[int]]
    estado_localizacion: Mapped[Optional[str]] = mapped_column(String(100))
    municipio_localizacion_id: Mapped[Optional[int]]
    fecha_cierre: Mapped[Optional[date]]
    tipo_cierre_id: Mapped[Optional[int]]
    feb_vinculado: Mapped[Optional[str]] = mapped_column(String(64))
    tiene_carpeta_investigacion: Mapped[Optional[bool]]
    record_hash: Mapped[str] = mapped_column(String(64))
    version_actual: Mapped[int] = mapped_column(default=1)
    fecha_creacion: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    fecha_actualizacion: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())


# Tabla historial: snapshot por version


class CasosHistorial(RepdBase):
    __tablename__ = "stg_repd_casos_historial"
    __table_args__ = (
        UniqueConstraint("feb", "numero_version", name="uq_repd_casos_historial_feb_version"),
        Index("ix_repd_casos_historial_feb", "feb"),
        Index("ix_repd_casos_historial_es_vigente", "es_vigente"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    caso_id: Mapped[Optional[int]]
    feb: Mapped[str] = mapped_column(String(64))
    numero_version: Mapped[int]
    es_vigente: Mapped[bool] = mapped_column(default=True)
    vigente_desde: Mapped[datetime] = mapped_column(server_default=func.now())
    vigente_hasta: Mapped[Optional[datetime]]
    sexo_id: Mapped[int]
    nacionalidad_id: Mapped[int]
    rango_edad_id: Mapped[int]
    fecha_reporte: Mapped[date]
    fecha_desaparicion: Mapped[Optional[date]]
    estado_desaparicion: Mapped[Optional[str]] = mapped_column(String(100))
    municipio_desaparicion_id: Mapped[Optional[int]]
    estatus_id: Mapped[int]
    fecha_localizacion: Mapped[Optional[date]]
    condicion_localizacion_id: Mapped[Optional[int]]
    clasificacion_localizacion_id: Mapped[Optional[int]]
    estado_localizacion: Mapped[Optional[str]] = mapped_column(String(100))
    municipio_localizacion_id: Mapped[Optional[int]]
    fecha_cierre: Mapped[Optional[date]]
    tipo_cierre_id: Mapped[Optional[int]]
    feb_vinculado: Mapped[Optional[str]] = mapped_column(String(64))
    tiene_carpeta_investigacion: Mapped[Optional[bool]]
    record_hash: Mapped[str] = mapped_column(String(64))
    fecha_creacion: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())


# Registro de modelos catalogo para iteracion dinamica

CATALOG_MODELS = {
    "sexo": CatSexo,
    "nacionalidad": CatNacionalidad,
    "rango_edad": CatRangoEdad,
    "estatus": CatEstatus,
    "condicion_localizacion": CatCondicionLocalizacion,
    "clasificacion_localizacion": CatClasificacionLocalizacion,
    "tipo_cierre": CatTipoCierre,
}
