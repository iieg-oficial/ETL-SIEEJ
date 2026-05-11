from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Index, Integer, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.pipelines.delitos_fuero_comun.attributes import DelitosFueroComunTables as T


class DelitosFueroComunBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatMunicipio(DelitosFueroComunBase):
    __tablename__ = T.CAT_MUNICIPIO
    __table_args__ = (UniqueConstraint("cve_municipio", name="uq_cat_municipio_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve_municipio: Mapped[str] = mapped_column(String(5), nullable=False)
    clave_ent: Mapped[str] = mapped_column(String(2), nullable=False)
    entidad: Mapped[str] = mapped_column(String(200), nullable=False)
    municipio: Mapped[str] = mapped_column(String(200), nullable=False)

    registros_hist: Mapped[list["StgDelitosFueroComunHistorico"]] = relationship(
        back_populates="municipio_rel",
        foreign_keys="StgDelitosFueroComunHistorico.cve_municipio",
    )
    registros_2026: Mapped[list["StgDelitosFueroComun2026"]] = relationship(
        back_populates="municipio_rel",
        foreign_keys="StgDelitosFueroComun2026.cve_municipio",
    )


class CatBienJuridicoAfectado(DelitosFueroComunBase):
    __tablename__ = T.CAT_BIEN_JURIDICO_AFECTADO
    __table_args__ = (UniqueConstraint("bien_juridico_afectado", name="uq_cat_bien_juridico_afectado"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bien_juridico_afectado: Mapped[str] = mapped_column(String(200), nullable=False)

    registros_hist: Mapped[list["StgDelitosFueroComunHistorico"]] = relationship(
        back_populates="bien_juridico_afectado_rel"
    )
    registros_2026: Mapped[list["StgDelitosFueroComun2026"]] = relationship(back_populates="bien_juridico_afectado_rel")


class CatTipoDelito(DelitosFueroComunBase):
    __tablename__ = T.CAT_TIPO_DELITO
    __table_args__ = (UniqueConstraint("tipo_delito", name="uq_cat_tipo_delito"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_delito: Mapped[str] = mapped_column(String(200), nullable=False)

    subtipos: Mapped[list["CatSubtipoDelito"]] = relationship(back_populates="tipo_delito_rel")
    registros_hist: Mapped[list["StgDelitosFueroComunHistorico"]] = relationship(back_populates="tipo_delito_rel")
    registros_2026: Mapped[list["StgDelitosFueroComun2026"]] = relationship(back_populates="tipo_delito_rel")


class CatSubtipoDelito(DelitosFueroComunBase):
    __tablename__ = T.CAT_SUBTIPO_DELITO
    __table_args__ = (UniqueConstraint("subtipo_delito", name="uq_cat_subtipo_delito"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subtipo_delito: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo_delito_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_TIPO_DELITO}.id"), nullable=False)

    tipo_delito_rel: Mapped["CatTipoDelito"] = relationship(back_populates="subtipos")
    modalidades: Mapped[list["CatModalidad"]] = relationship(back_populates="subtipo_delito_rel")
    registros_hist: Mapped[list["StgDelitosFueroComunHistorico"]] = relationship(back_populates="subtipo_delito_rel")
    registros_2026: Mapped[list["StgDelitosFueroComun2026"]] = relationship(back_populates="subtipo_delito_rel")


class CatModalidad(DelitosFueroComunBase):
    __tablename__ = T.CAT_MODALIDAD
    __table_args__ = (UniqueConstraint("modalidad", name="uq_cat_modalidad"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    modalidad: Mapped[str] = mapped_column(String(200), nullable=False)
    subtipo_delito_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{T.CAT_SUBTIPO_DELITO}.id"), nullable=True)

    subtipo_delito_rel: Mapped[Optional["CatSubtipoDelito"]] = relationship(back_populates="modalidades")
    registros_hist: Mapped[list["StgDelitosFueroComunHistorico"]] = relationship(back_populates="modalidad_rel")
    registros_2026: Mapped[list["StgDelitosFueroComun2026"]] = relationship(back_populates="modalidad_rel")


class StgDelitosFueroComunHistorico(DelitosFueroComunBase):
    __tablename__ = T.STG_DELITOS_FUERO_COMUN_2015_2025
    __table_args__ = (
        UniqueConstraint(
            "anio",
            "cve_municipio",
            "bien_juridico_afectado_id",
            "tipo_delito_id",
            "subtipo_delito_id",
            "modalidad_id",
            name="uq_stg_delitos_2015_2025_nk",
        ),
        Index("ix_stg_delitos_2015_2025_anio", "anio"),
        Index("ix_stg_delitos_2015_2025_municipio", "cve_municipio"),
        Index("ix_stg_delitos_2015_2025_tipo", "tipo_delito_id", "subtipo_delito_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    clave_ent: Mapped[str] = mapped_column(String(2), nullable=False)
    entidad: Mapped[str] = mapped_column(String(200), nullable=False)
    cve_municipio: Mapped[str] = mapped_column(
        String(5), ForeignKey(f"{T.CAT_MUNICIPIO}.cve_municipio"), nullable=False
    )
    municipio: Mapped[str] = mapped_column(String(200), nullable=False)
    bien_juridico_afectado_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_BIEN_JURIDICO_AFECTADO}.id"), nullable=False
    )
    tipo_delito_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_TIPO_DELITO}.id"), nullable=False)
    subtipo_delito_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_SUBTIPO_DELITO}.id"), nullable=False)
    modalidad_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_MODALIDAD}.id"), nullable=False)
    enero: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    febrero: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    marzo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    abril: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mayo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    junio: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    julio: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    agosto: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    septiembre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    octubre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    noviembre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    diciembre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    municipio_rel: Mapped["CatMunicipio"] = relationship(
        back_populates="registros_hist",
        foreign_keys=[cve_municipio],
    )
    bien_juridico_afectado_rel: Mapped["CatBienJuridicoAfectado"] = relationship(back_populates="registros_hist")
    tipo_delito_rel: Mapped["CatTipoDelito"] = relationship(back_populates="registros_hist")
    subtipo_delito_rel: Mapped["CatSubtipoDelito"] = relationship(back_populates="registros_hist")
    modalidad_rel: Mapped["CatModalidad"] = relationship(back_populates="registros_hist")


class StgDelitosFueroComun2026(DelitosFueroComunBase):
    __tablename__ = T.STG_DELITOS_FUERO_COMUN_2026
    __table_args__ = (
        UniqueConstraint(
            "anio",
            "cve_municipio",
            "bien_juridico_afectado_id",
            "tipo_delito_id",
            "subtipo_delito_id",
            "modalidad_id",
            name="uq_stg_delitos_2026_nk",
        ),
        Index("ix_stg_delitos_2026_anio", "anio"),
        Index("ix_stg_delitos_2026_municipio", "cve_municipio"),
        Index("ix_stg_delitos_2026_tipo", "tipo_delito_id", "subtipo_delito_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    clave_ent: Mapped[str] = mapped_column(String(2), nullable=False)
    entidad: Mapped[str] = mapped_column(String(200), nullable=False)
    cve_municipio: Mapped[str] = mapped_column(
        String(5), ForeignKey(f"{T.CAT_MUNICIPIO}.cve_municipio"), nullable=False
    )
    municipio: Mapped[str] = mapped_column(String(200), nullable=False)
    bien_juridico_afectado_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_BIEN_JURIDICO_AFECTADO}.id"), nullable=False
    )
    tipo_delito_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_TIPO_DELITO}.id"), nullable=False)
    subtipo_delito_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_SUBTIPO_DELITO}.id"), nullable=False)
    modalidad_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_MODALIDAD}.id"), nullable=False)
    enero: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    febrero: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    marzo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    abril: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mayo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    junio: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    julio: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    agosto: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    septiembre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    octubre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    noviembre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    diciembre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    municipio_rel: Mapped["CatMunicipio"] = relationship(
        back_populates="registros_2026",
        foreign_keys=[cve_municipio],
    )
    bien_juridico_afectado_rel: Mapped["CatBienJuridicoAfectado"] = relationship(back_populates="registros_2026")
    tipo_delito_rel: Mapped["CatTipoDelito"] = relationship(back_populates="registros_2026")
    subtipo_delito_rel: Mapped["CatSubtipoDelito"] = relationship(back_populates="registros_2026")
    modalidad_rel: Mapped["CatModalidad"] = relationship(back_populates="registros_2026")
