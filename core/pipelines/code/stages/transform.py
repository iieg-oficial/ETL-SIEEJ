from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.code.constants import CATALOGS_FILENAME, MANIFEST_FILENAME, PIPELINE_NAME
from core.pipelines.code.datasets import ACADEMIAS, MAIN_FRAMES, POLIDEPORTIVOS, RETO
from core.pipelines.code.helpers.academias import transform_academias
from core.pipelines.code.helpers.polideportivos import transform_polideportivos
from core.pipelines.code.helpers.reto import transform_reto
from core.pipelines.stage import Stage
from core.utils.files import clean_directory, read_json
from core.utils.logger import get_logger


class CodeTransform(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, dict[str, Any]]:
        extract_dir = Path("data/extract") / PIPELINE_NAME
        manifest = read_json(extract_dir / MANIFEST_FILENAME) or {}

        loaded = {}
        for key, entry in manifest.items():
            frames = {path.stem: pd.read_pickle(path) for path in sorted((extract_dir / key).glob("*.pkl"))}
            if frames:
                loaded[key] = {"frames": frames, "manifest": entry}

        if loaded:
            self.logger.info(f"[source] Loaded {sorted(loaded)} from extract")
            return loaded

        if input_data:
            return input_data

        self.logger.info("[source] No data to transform")
        return {}

    def action(self, input_data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        if not input_data:
            self.logger.info("[action] Nothing to transform")
            return {}

        handlers = {
            RETO: transform_reto,
            ACADEMIAS: transform_academias,
            POLIDEPORTIVOS: transform_polideportivos,
        }

        transformed = {}
        for key, entry in input_data.items():
            frames, catalogs = handlers[key](entry["frames"], entry["manifest"])
            if frames[MAIN_FRAMES[key]].empty:
                raise ValueError(f"{key}: the source has no rows")
            for name, df in frames.items():
                self.logger.info(f"[action] {key}/{name}: {len(df):,} rows prepared")
            transformed[key] = {"frames": frames, "manifest": entry["manifest"], "catalogs": catalogs}

        return transformed

    def finalization(self, input_data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        for key, entry in input_data.items():
            folder = self.work_dir / key
            folder.mkdir(parents=True, exist_ok=True)
            clean_directory(folder, self.logger)
            for name, df in entry["frames"].items():
                df.to_pickle(folder / f"{name}.pkl")
                self.logger.info(f"[finalization] {key}/{name}: {len(df):,} rows saved")

            pd.to_pickle(entry["catalogs"], folder / CATALOGS_FILENAME)
            self.logger.info(f"[finalization] {key}: {len(entry['catalogs'])} catalog(s) saved")

        return input_data
