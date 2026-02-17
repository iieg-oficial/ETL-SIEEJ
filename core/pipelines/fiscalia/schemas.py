from sqlalchemy import String, ForeignKey, Date, Float, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from core.pipelines.fiscalia.attributes.fiscalia import FiscaliaTables
from datetime import date

class FiscaliaBase(DeclarativeBase):
    pass

class ZonasGeograficas(FiscaliaBase):
    __tablename__ = FiscaliaTables.ZONAS_GEOGRAFICAS

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    zona_geografica: Mapped[str] = mapped_column(String(10), nullable=False)
class Colonias(FiscaliaBase):
    __tablename__ = FiscaliaTables.COLONIAS

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    colonia: Mapped[str] = mapped_column(String(400), nullable=False, unique=True)

class Calles(FiscaliaBase):
    __tablename__ = FiscaliaTables.CALLES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calle: Mapped[str] = mapped_column(String(400), nullable=False, unique=True)

class Cruces(FiscaliaBase):
    __tablename__ = FiscaliaTables.CRUCES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cruce: Mapped[str] = mapped_column(String(400), nullable=False, unique=True)

class EsViolencia(FiscaliaBase):
    __tablename__ = FiscaliaTables.VIOLENCIA

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    violencia: Mapped[str] = mapped_column(String(15), nullable=False)

class Delitos(FiscaliaBase):
    __tablename__ = FiscaliaTables.DELITOS

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = False)
    delito: Mapped[str] =  mapped_column(String(99), nullable=False)
    bien_afectado_id: Mapped[int] = mapped_column(ForeignKey(f"{FiscaliaTables.BIEN_AFECTADO}.id"), nullable = False)


class BienesAfectados(FiscaliaBase):
    __tablename__ = FiscaliaTables.BIEN_AFECTADO

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement=False)
    bien_afectado: Mapped[str] = mapped_column(String(200), nullable=False)

class Casos(FiscaliaBase):
    __tablename__  = FiscaliaTables.CASOS
    __table_args__ = (
        UniqueConstraint("delitos_id", "fecha_denuncia", "hora", "longitud", "latitud", name="uq_casos_natural_key"),
    )

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    delitos_id: Mapped[int] = mapped_column(ForeignKey(f"{FiscaliaTables.DELITOS}.id"), nullable = False)
    violencia_id: Mapped[int] = mapped_column(ForeignKey(f"{FiscaliaTables.VIOLENCIA}.id"), nullable = True)
    zonas_geograficas_id: Mapped[int] = mapped_column(ForeignKey(f"{FiscaliaTables.ZONAS_GEOGRAFICAS}.id"), nullable = True)
    municipios_id: Mapped[int | None] = mapped_column(nullable=True)
    colonias_id: Mapped[int] = mapped_column(ForeignKey(f"{FiscaliaTables.COLONIAS}.id"), nullable = True)
    calles_id: Mapped[int] = mapped_column(ForeignKey(f"{FiscaliaTables.CALLES}.id"), nullable = True)
    cruces_id: Mapped[int] = mapped_column(ForeignKey(f"{FiscaliaTables.CRUCES}.id"), nullable = True)
    hora: Mapped[str] = mapped_column(String(5), nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_denuncia: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
