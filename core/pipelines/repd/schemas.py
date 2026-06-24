from datetime import date, datetime
from typing import Optional

from sqlalchemy import Index, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class RepdBase(DeclarativeBase):
    pass


# Catalogos


class CatSex(RepdBase):
    __tablename__ = "stg_repd_cat_sex"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_sex_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)


class CatNationality(RepdBase):
    __tablename__ = "stg_repd_cat_nationality"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_nationality_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class CatAgeRange(RepdBase):
    __tablename__ = "stg_repd_cat_age_range"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_age_range_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class CatStatus(RepdBase):
    __tablename__ = "stg_repd_cat_status"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_status_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class CatLocationCondition(RepdBase):
    __tablename__ = "stg_repd_cat_location_condition"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_location_condition_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)


class CatLocationClassification(RepdBase):
    __tablename__ = "stg_repd_cat_location_classification"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_location_classification_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class CatClosureType(RepdBase):
    __tablename__ = "stg_repd_cat_closure_type"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_closure_type_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


# Tabla actual: una fila vigente por FEB


class CaseCurrent(RepdBase):
    __tablename__ = "stg_repd_case_current"
    __table_args__ = (
        UniqueConstraint("feb", name="uq_repd_case_current_feb"),
        Index("ix_repd_case_current_feb", "feb", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    feb: Mapped[str] = mapped_column(String(64), unique=True)
    sex_id: Mapped[int]
    nationality_id: Mapped[int]
    age_range_id: Mapped[int]
    report_date: Mapped[date]
    disappearance_date: Mapped[Optional[date]]
    disappearance_state_name: Mapped[Optional[str]] = mapped_column(String(100))
    disappearance_municipality_id: Mapped[Optional[int]]
    status_id: Mapped[int]
    location_date: Mapped[Optional[date]]
    location_condition_id: Mapped[Optional[int]]
    location_classification_id: Mapped[Optional[int]]
    location_state_name: Mapped[Optional[str]] = mapped_column(String(100))
    location_municipality_id: Mapped[Optional[int]]
    closure_date: Mapped[Optional[date]]
    closure_type_id: Mapped[Optional[int]]
    linked_feb: Mapped[Optional[str]] = mapped_column(String(64))
    has_investigation_folder: Mapped[Optional[bool]]
    record_hash: Mapped[str] = mapped_column(String(64))
    current_version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())


# Tabla historial: snapshot por version


class CaseHistory(RepdBase):
    __tablename__ = "stg_repd_case_history"
    __table_args__ = (
        UniqueConstraint("feb", "version_num", name="uq_repd_case_history_feb_version"),
        Index("ix_repd_case_history_feb", "feb"),
        Index("ix_repd_case_history_is_current", "is_current"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_current_id: Mapped[Optional[int]]
    feb: Mapped[str] = mapped_column(String(64))
    version_num: Mapped[int]
    is_current: Mapped[bool] = mapped_column(default=True)
    valid_from: Mapped[datetime] = mapped_column(server_default=func.now())
    valid_to: Mapped[Optional[datetime]]
    sex_id: Mapped[int]
    nationality_id: Mapped[int]
    age_range_id: Mapped[int]
    report_date: Mapped[date]
    disappearance_date: Mapped[Optional[date]]
    disappearance_state_name: Mapped[Optional[str]] = mapped_column(String(100))
    disappearance_municipality_id: Mapped[Optional[int]]
    status_id: Mapped[int]
    location_date: Mapped[Optional[date]]
    location_condition_id: Mapped[Optional[int]]
    location_classification_id: Mapped[Optional[int]]
    location_state_name: Mapped[Optional[str]] = mapped_column(String(100))
    location_municipality_id: Mapped[Optional[int]]
    closure_date: Mapped[Optional[date]]
    closure_type_id: Mapped[Optional[int]]
    linked_feb: Mapped[Optional[str]] = mapped_column(String(64))
    has_investigation_folder: Mapped[Optional[bool]]
    record_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())


# Registro de modelos catalogo para iteracion dinamica

CATALOG_MODELS = {
    "sex": CatSex,
    "nationality": CatNationality,
    "age_range": CatAgeRange,
    "status": CatStatus,
    "location_condition": CatLocationCondition,
    "location_classification": CatLocationClassification,
    "closure_type": CatClosureType,
}
