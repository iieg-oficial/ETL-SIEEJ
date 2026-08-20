from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

# Tipos permitidos para los parámetros de un indicador y su equivalente en Python.
TIPOS = {"str": str, "int": int}


class Cobertura(BaseModel):
    model_config = ConfigDict(extra="forbid")

    geografica: str
    temporal: str


class Parametro(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    tipo: Literal["str", "int"]
    requerido: bool = False
    descripcion: str


class Indicador(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    nombre: str
    tema: str
    definicion: str
    unidad: str
    fuente: str
    pipeline: str
    origen: str
    nivel: Literal["nacional", "estatal", "municipal"]
    periodicidad: str
    cobertura: Cobertura
    notas: Optional[str] = None
    parametros: list[Parametro] = []
    sql: str

    def metadata(self) -> dict:
        """Metadata sin el SQL, que es lo único que se expone a un agente."""
        return self.model_dump(exclude={"sql"})
