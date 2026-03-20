from sqlalchemy import String, Float, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.datamexico.attributes import DataMexicoTables as T


class DataMexicoBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class Paises(DataMexicoBase):
    __tablename__ = T.PAISES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_pais: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)
    nombre_pais: Mapped[str] = mapped_column(String, nullable=False)


class Periodos(DataMexicoBase):
    __tablename__ = T.PERIODOS

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    trimestre: Mapped[int] = mapped_column(Integer, nullable=False)
    etiqueta_trimestre: Mapped[str] = mapped_column(String(7), nullable=False)


class TiposFlujoComercial(DataMexicoBase):
    __tablename__ = T.TIPOS_FLUJOS_COMERCIALES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    flujo: Mapped[str] = mapped_column(String, nullable=False)


class Productos(DataMexicoBase):
    __tablename__ = T.PRODUCTOS

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(String, nullable=False)


class FlujoComercio(DataMexicoBase):
    __tablename__ = T.FLUJO_COMERCIO

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pais_id: Mapped[int] = mapped_column(ForeignKey(f"{T.PAISES}.id"), nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    periodo_id: Mapped[int] = mapped_column(ForeignKey(f"{T.PERIODOS}.id"), nullable=False)
    tipo_flujo_id: Mapped[int] = mapped_column(ForeignKey(f"{T.TIPOS_FLUJOS_COMERCIALES}.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey(f"{T.PRODUCTOS}.id"), nullable=False)
    valor_comercio: Mapped[float] = mapped_column(Float, nullable=False)
