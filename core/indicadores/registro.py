import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from pydantic_settings import SettingsConfigDict
from sqlalchemy import text

from core.config import BaseConfig, env_path
from core.db import Database
from core.indicadores.modelo import TIPOS, Indicador

CATALOGO = Path(__file__).parent / "catalogo"
LIMITE = 5000
COLUMNAS = ("cve_geo", "nombre_geo", "periodo", "valor", "categoria")

# Binds de SQLAlchemy (:param) ignorando los casts de PostgreSQL (valor::numeric).
BINDS = re.compile(r"(?<!:):([a-zA-Z_][a-zA-Z0-9_]*)")


def _validar(ind: Indicador, ruta: Path) -> None:
    sql = ind.sql.lstrip().upper()
    if not (sql.startswith("SELECT") or sql.startswith("WITH")):
        raise ValueError(f"{ruta}: el sql debe empezar con SELECT o WITH")

    faltantes = [col for col in COLUMNAS if f"AS {col}" not in ind.sql]
    if faltantes:
        raise ValueError(f"{ruta}: el sql no proyecta las columnas {faltantes}")

    declarados = {p.nombre for p in ind.parametros}
    usados = set(BINDS.findall(ind.sql))
    if declarados != usados:
        raise ValueError(
            f"{ruta}: desajuste entre parametros y binds del sql "
            f"(declarados sin usar: {sorted(declarados - usados)}, "
            f"usados sin declarar: {sorted(usados - declarados)})"
        )


@lru_cache(maxsize=1)
def _catalogo() -> dict[str, Indicador]:
    """Carga y valida todo el catálogo. Cualquier error revienta aquí, al importar."""
    indicadores: dict[str, Indicador] = {}
    for ruta in sorted(CATALOGO.glob("*/*.yaml")):
        ind = Indicador(**yaml.safe_load(ruta.read_text(encoding="utf-8")))
        if ind.id in indicadores:
            raise ValueError(f"{ruta}: id duplicado '{ind.id}'")
        _validar(ind, ruta)
        indicadores[ind.id] = ind
    return indicadores


class _ConexionConfig(BaseConfig):
    """Del .env de un pipeline solo interesan las DB_*; el resto de sus variables se ignora."""

    model_config = SettingsConfigDict(extra="ignore")


@lru_cache(maxsize=None)
def _db(pipeline: str) -> Database:
    cfg = _ConexionConfig(_env_file=env_path(pipeline))
    db = Database(pipeline, cfg.database_url)
    db.connect()
    return db


def _binds(ind: Indicador, params: dict) -> dict:
    """Valida los params contra los declarados y rellena con None los ausentes."""
    declarados = {p.nombre: p for p in ind.parametros}
    desconocidos = set(params) - set(declarados)
    if desconocidos:
        raise ValueError(f"{ind.id}: parámetros desconocidos {sorted(desconocidos)}")

    binds = {}
    for nombre, p in declarados.items():
        valor = params.get(nombre)
        if valor is None:
            if p.requerido:
                raise ValueError(f"{ind.id}: falta el parámetro requerido '{nombre}'")
            binds[nombre] = None
        else:
            binds[nombre] = TIPOS[p.tipo](valor)
    return binds


def listar(tema: Optional[str] = None, nivel: Optional[str] = None) -> list[dict]:
    """Metadata de los indicadores (sin sql), filtrable por tema y nivel."""
    return [
        ind.metadata()
        for ind in _catalogo().values()
        if (tema is None or ind.tema == tema) and (nivel is None or ind.nivel == nivel)
    ]


def obtener(id: str) -> Indicador:
    try:
        return _catalogo()[id]
    except KeyError:
        raise ValueError(f"Indicador '{id}' no existe en el catálogo") from None


def ejecutar(id: str, **params) -> list[dict]:
    """Ejecuta el indicador y devuelve las filas en formato largo."""
    ind = obtener(id)
    binds = _binds(ind, params)
    # Se pide una fila de más para distinguir "cabe justo" de "está truncado".
    consulta = text(f"SELECT * FROM (\n{ind.sql.rstrip().rstrip(';')}\n) _banco LIMIT {LIMITE + 1}")

    with _db(ind.pipeline).engine.connect() as conn:
        conn = conn.execution_options(postgresql_readonly=True)
        filas = [dict(fila) for fila in conn.execute(consulta, binds).mappings()]

    if len(filas) > LIMITE:
        raise ValueError(
            f"{ind.id}: la consulta excede {LIMITE} filas; acota con {sorted(p.nombre for p in ind.parametros)}"
        )
    return filas
