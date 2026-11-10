from dataclasses import dataclass
from typing import Final

from core.acervo import normalize
from core.pipelines.code.constants import (
    ACADEMIAS_FRAME,
    DATA_FIELD,
    POLIDEPORTIVOS_FRAME,
    PUNTOS_FRAME,
    UPLOAD_FIELD,
)

RETO: Final[str] = "reto"
ACADEMIAS: Final[str] = "academias"
POLIDEPORTIVOS: Final[str] = "polideportivos"


@dataclass(frozen=True)
class Dataset:
    key: str
    # Stored in cargas_acervo.conjunto, so the watermark is per dataset.
    label: str
    field: str
    # Other names the form may carry for the dataset; the label always matches.
    aliases: tuple[str, ...] = ()

    def accepts(self, name: str) -> bool:
        """Exact match on the normalized name: free text, so case, accents and blanks do not count."""
        return normalize(name) in {normalize(self.label), *(normalize(alias) for alias in self.aliases)}


DATASETS: Final[tuple[Dataset, ...]] = (
    Dataset(
        RETO,
        "Puntos de activación del programa Reto, Reactivación para Todas y Todos",
        UPLOAD_FIELD,
    ),
    Dataset(ACADEMIAS, "Academias deportivas, Espacios para la Paz", DATA_FIELD),
    Dataset(POLIDEPORTIVOS, "Polideportivos", DATA_FIELD),
)

BY_KEY: Final[dict[str, Dataset]] = {dataset.key: dataset for dataset in DATASETS}

# Main frame of each dataset: what an empty-source guard and finalization read.
MAIN_FRAMES: Final[dict[str, str]] = {
    RETO: PUNTOS_FRAME,
    ACADEMIAS: ACADEMIAS_FRAME,
    POLIDEPORTIVOS: POLIDEPORTIVOS_FRAME,
}
