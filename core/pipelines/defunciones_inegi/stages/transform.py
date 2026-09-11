import zipfile
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.defunciones_inegi.attributes import DefuncionesInegiTables as T
from core.pipelines.defunciones_inegi.config import settings
from core.pipelines.defunciones_inegi.constants import (
    CATALOG_DIR,
    CATALOG_KEYS,
    CATALOGS_FILE,
    CODED_CATALOG_TABLES,
    CODIGO_ADICIONAL_ALIAS,
    DEFAULT_CATALOG_KEY,
    EDITION_COLUMN,
    FACTS_DIR,
    MANIFEST_NAME,
    PIPELINE_NAME,
    SENTENCE_CASE_TABLES,
    TEXT_KEY_TABLES,
    VERSIONED_TABLES,
)
from core.pipelines.defunciones_inegi.helpers.catalogs import (
    capitulo_grupo_records,
    catalog_records,
    distrito_oaxaca_records,
    localidad_records,
    pais_records,
    razon_materna_records,
)
from core.pipelines.defunciones_inegi.helpers.facts import normalize_facts
from core.pipelines.defunciones_inegi.helpers.source import fact_member, read_fact_chunks
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class DefuncionesInegiTransform(Stage):
    """Consolida los catálogos de todas las ediciones y normaliza los hechos.

    Los hechos se escriben por edición: son millones de filas y no caben en
    memoria todas juntas.
    """

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.extract_dir = Path("data/extract") / PIPELINE_NAME
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[int, Path]:
        manifest = pd.read_pickle(self.extract_dir / MANIFEST_NAME)
        return {int(year): Path(path) for year, path in manifest.items()}

    def action(self, input_data: dict[int, Path]) -> dict[str, Any]:
        if not input_data:
            self.logger.warning("[action] Sin ediciones que transformar")
            return {"catalogs": {}, "editions": []}

        return {
            "catalogs": self._build_catalogs(sorted(input_data)),
            "editions": self._build_facts(input_data),
        }

    def _edition_catalog(self, year: int, name: str) -> pd.DataFrame | None:
        path = self.extract_dir / CATALOG_DIR / str(year) / f"{name}.pkl"
        return pd.read_pickle(path) if path.exists() else None

    def _build_catalogs(self, years: list[int]) -> dict[str, list[dict]]:
        catalogs: dict[str, list[dict]] = {str(table): [] for table in T.catalogs()}

        for year in years:
            for table in CODED_CATALOG_TABLES:
                df = self._edition_catalog(year, str(table))
                if df is not None:
                    catalogs[table].extend(self._stamp(self._coded_records(table, df), table, year))

            catalogs[T.CAT_CIE10].extend(self._stamp(self._cie10_records(year), T.CAT_CIE10, year))

            localidades = self._edition_catalog(year, str(T.CAT_LOCALIDAD))
            if localidades is not None:
                catalogs[T.CAT_LOCALIDAD].extend(self._stamp(localidad_records(localidades), T.CAT_LOCALIDAD, year))
                catalogs[T.CAT_DISTRITO_OAXACA].extend(distrito_oaxaca_records(localidades))

            paises = self._edition_catalog(year, str(T.CAT_PAIS))
            if paises is not None:
                catalogs[T.CAT_PAIS].extend(pais_records(paises))

            capitulos = self._edition_catalog(year, str(T.CAT_CAPITULO_GRUPO))
            if capitulos is not None:
                catalogs[T.CAT_CAPITULO_GRUPO].extend(capitulo_grupo_records(capitulos))

        return {table: self._deduplicate(table, records) for table, records in catalogs.items()}

    @staticmethod
    def _coded_records(table: str, df: pd.DataFrame) -> list[dict]:
        if table == T.CAT_RAZON_MATERNA:
            return razon_materna_records(df)
        return catalog_records(
            df,
            numeric_key=table not in TEXT_KEY_TABLES,
            to_sentence_case=table in SENTENCE_CASE_TABLES,
        )

    def _cie10_records(self, year: int) -> list[dict]:
        """Causa de defunción y código adicional son el mismo dominio CIE-10."""
        records: list[dict] = []
        for name in (str(T.CAT_CIE10), CODIGO_ADICIONAL_ALIAS):
            df = self._edition_catalog(year, name)
            if df is not None:
                records.extend(catalog_records(df, numeric_key=False))
        return records

    @staticmethod
    def _stamp(records: list[dict], table: str, year: int) -> list[dict]:
        if table not in VERSIONED_TABLES:
            return records
        return [record | {EDITION_COLUMN: year} for record in records]

    @staticmethod
    def _deduplicate(table: str, records: list[dict]) -> list[dict]:
        if not records:
            return []
        keys = CATALOG_KEYS.get(table, DEFAULT_CATALOG_KEY)
        if table in VERSIONED_TABLES:
            keys = [*keys, EDITION_COLUMN]
        # La edición más reciente gana cuando INEGI corrige una descripción.
        frame = pd.DataFrame(records).drop_duplicates(subset=keys, keep="last")
        # Pasar por DataFrame convierte los None en NaN, que psycopg2 manda como float.
        return frame.astype(object).where(frame.notna(), None).to_dict("records")

    def _build_facts(self, zip_paths: dict[int, Path]) -> list[int]:
        facts_dir = self.work_dir / FACTS_DIR
        facts_dir.mkdir(parents=True, exist_ok=True)

        for year, zip_path in sorted(zip_paths.items()):
            with zipfile.ZipFile(zip_path) as archive:
                member = fact_member(archive)
                chunks = [
                    normalize_facts(chunk).assign(**{EDITION_COLUMN: year})
                    for chunk in read_fact_chunks(archive, member, settings.CHUNK_SIZE)
                ]
            frame = pd.concat(chunks, ignore_index=True)
            frame.to_pickle(facts_dir / f"{year}.pkl")
            self.logger.info(f"[action] {year}: {len(frame):,} defunciones normalizadas")

        return sorted(zip_paths)

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        catalogs = input_data["catalogs"]
        pd.to_pickle(catalogs, self.work_dir / CATALOGS_FILE)
        for table, records in sorted(catalogs.items()):
            self.logger.info(f"[finalization] {table}: {len(records)} registros")
        return {"editions": input_data["editions"]}
