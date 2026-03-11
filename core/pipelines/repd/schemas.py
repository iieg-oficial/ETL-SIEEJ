from sqlalchemy import Boolean, Column, Date, DateTime, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase


class RepdBase(DeclarativeBase):
    pass


# Catalogos

class CatSex(RepdBase):
    __tablename__ = "stg_repd_cat_sex"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_sex_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False, unique=True)


class CatNationality(RepdBase):
    __tablename__ = "stg_repd_cat_nationality"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_nationality_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)


class CatAgeRange(RepdBase):
    __tablename__ = "stg_repd_cat_age_range"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_age_range_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)


class CatStatus(RepdBase):
    __tablename__ = "stg_repd_cat_status"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_status_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)


class CatLocationCondition(RepdBase):
    __tablename__ = "stg_repd_cat_location_condition"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_location_condition_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False, unique=True)


class CatLocationClassification(RepdBase):
    __tablename__ = "stg_repd_cat_location_classification"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_location_classification_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)


class CatClosureType(RepdBase):
    __tablename__ = "stg_repd_cat_closure_type"
    __table_args__ = (UniqueConstraint("name", name="uq_repd_cat_closure_type_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)


# Tabla actual: una fila vigente por FEB

class CaseCurrent(RepdBase):
    __tablename__ = "stg_repd_case_current"
    __table_args__ = (
        UniqueConstraint("feb", name="uq_repd_case_current_feb"),
        Index("ix_repd_case_current_feb", "feb", unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    feb = Column(String(64), nullable=False, unique=True)
    sex_id = Column(Integer, nullable=False)
    nationality_id = Column(Integer, nullable=False)
    age_range_id = Column(Integer, nullable=False)
    report_date = Column(Date, nullable=False)
    disappearance_date = Column(Date, nullable=True)
    disappearance_state_name = Column(String(100), nullable=True)
    disappearance_municipality_id = Column(Integer, nullable=True)
    status_id = Column(Integer, nullable=False)
    location_date = Column(Date, nullable=True)
    location_condition_id = Column(Integer, nullable=True)
    location_classification_id = Column(Integer, nullable=True)
    location_state_name = Column(String(100), nullable=True)
    location_municipality_id = Column(Integer, nullable=True)
    closure_date = Column(Date, nullable=True)
    closure_type_id = Column(Integer, nullable=True)
    linked_feb = Column(String(64), nullable=True)
    has_investigation_folder = Column(Boolean, nullable=True)
    record_hash = Column(String(64), nullable=False)
    current_version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# Tabla historial: snapshot por version

class CaseHistory(RepdBase):
    __tablename__ = "stg_repd_case_history"
    __table_args__ = (
        UniqueConstraint("feb", "version_num", name="uq_repd_case_history_feb_version"),
        Index("ix_repd_case_history_feb", "feb"),
        Index("ix_repd_case_history_is_current", "is_current"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_current_id = Column(Integer, nullable=True)
    feb = Column(String(64), nullable=False)
    version_num = Column(Integer, nullable=False)
    is_current = Column(Boolean, nullable=False, default=True)
    valid_from = Column(DateTime, nullable=False, server_default=func.now())
    valid_to = Column(DateTime, nullable=True)
    sex_id = Column(Integer, nullable=False)
    nationality_id = Column(Integer, nullable=False)
    age_range_id = Column(Integer, nullable=False)
    report_date = Column(Date, nullable=False)
    disappearance_date = Column(Date, nullable=True)
    disappearance_state_name = Column(String(100), nullable=True)
    disappearance_municipality_id = Column(Integer, nullable=True)
    status_id = Column(Integer, nullable=False)
    location_date = Column(Date, nullable=True)
    location_condition_id = Column(Integer, nullable=True)
    location_classification_id = Column(Integer, nullable=True)
    location_state_name = Column(String(100), nullable=True)
    location_municipality_id = Column(Integer, nullable=True)
    closure_date = Column(Date, nullable=True)
    closure_type_id = Column(Integer, nullable=True)
    linked_feb = Column(String(64), nullable=True)
    has_investigation_folder = Column(Boolean, nullable=True)
    record_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


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
