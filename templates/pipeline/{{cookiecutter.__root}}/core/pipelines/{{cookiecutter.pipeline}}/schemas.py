from sqlalchemy.orm import DeclarativeBase


class {{cookiecutter.__class_prefix}}Base(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]
