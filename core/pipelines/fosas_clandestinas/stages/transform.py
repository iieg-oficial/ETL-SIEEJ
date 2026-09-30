from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import pdfplumber

from core.pipelines.fosas_clandestinas.constants import (
    COUNT_COLS,
    EMPTY_VALUES,
    EN_PROCESO_TEXT,
    HEADER_KEYWORDS,
    MONTH_YEAR_RE,
    PDF_COLS,
    PIPELINE_NAME,
    PUBLICACIONES_FILE,
    STG_COLS,
    STG_FILE,
    TITLE_COLS,
    UNNUMBERED_CONSECUTIVO,
    UNDATED_VALUES,
    UNNUMBERED_SITE,
)
from core.pipelines.stage import Stage
from core.utils import normalize_text
from core.utils.accents import apply_accents
from core.utils.normalize import title_col


def clean_cell(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def header_columns(row: list[Any]) -> dict[int, str] | None:
    """Maps cell index to target column when the row is the table header."""
    labels = [(normalize_text(clean_cell(c)) or "").replace("_", " ") for c in row]
    if not any("municipio" == label for label in labels):
        return None
    columns = {0: "consecutivo"}
    for index, label in enumerate(labels[1:], start=1):
        target = next((col for key, col in HEADER_KEYWORDS if key in label), None)
        if target and target not in columns.values():
            columns[index] = target
    return columns


class FosasClandestinasTransform(Stage):
    def __init__(self):
        super().__init__(PIPELINE_NAME, "transform")
        self.extract_dir = Path(f"data/extract/{PIPELINE_NAME}")

    def _parse_month_year(self, value: str | None, context: str) -> date | None:
        if pd.isna(value) or value.upper() in UNDATED_VALUES:
            return None
        match = MONTH_YEAR_RE.match(value)
        if not match:
            self.logger.warning(f"[action] {context}: unparseable date {value!r}")
            return None
        month, year = int(match.group(1)), match.group(2)
        if len(year) == 3:
            # Typo like "04/206": the decade digit is missing
            fixed = f"{year[:2]}2{year[2]}"
            self.logger.warning(f"[action] {context}: year {year} fixed to {fixed}")
            year = fixed
        elif len(year) == 2:
            year = f"20{year}"
        return date(int(year), month, 1)

    def _parse_count(self, value: str | None, context: str) -> int | None:
        if pd.isna(value) or value in EMPTY_VALUES:
            return None
        if value.isdigit():
            return int(value)
        self.logger.warning(f"[action] {context}: non numeric count {value!r}")
        return None

    def _read_rows(self, path: Path) -> list[dict]:
        rows, columns = [], None
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    for raw in table:
                        header = header_columns(raw)
                        if header:
                            columns = header
                            continue
                        if columns is None or len(raw) <= max(columns):
                            continue
                        record = {col: clean_cell(raw[i]) for i, col in columns.items()}
                        # Data rows always carry a start date; titles and notes do not
                        if record.get("fecha_inicio") and MONTH_YEAR_RE.match(record["fecha_inicio"].split()[0]):
                            rows.append(record)
                        elif any(record.values()):
                            self.logger.debug(f"[action] {path.name}: skipped row {raw}")
        return rows

    def _publication(self, fecha_corte: date, path: Path) -> pd.DataFrame:
        df = pd.DataFrame(self._read_rows(path)).reindex(columns=PDF_COLS)
        tag = f"{fecha_corte:%Y-%m}"

        df["consecutivo"] = df["consecutivo"].replace(UNNUMBERED_SITE, str(UNNUMBERED_CONSECUTIVO))
        bad = df["consecutivo"].notna() & ~df["consecutivo"].fillna("").str.isdigit()
        if bad.any():
            self.logger.warning(f"[action] {tag}: non numeric consecutivo {df.loc[bad, 'consecutivo'].tolist()}")
            df.loc[bad, "consecutivo"] = None

        # Merged cells: continuation rows inherit the site attributes above
        site_cols = ["consecutivo", "denominacion", "municipio"]
        continuation = df["consecutivo"].isna()
        df[site_cols] = df[site_cols].ffill()
        df["fecha_fin"] = df["fecha_fin"].where(~continuation | df["fecha_fin"].notna(), df["fecha_fin"].ffill())
        df["consecutivo"] = df["consecutivo"].astype(int)
        df["periodo"] = df.groupby("consecutivo").cumcount() + 1

        fecha_fin = df["fecha_fin"].fillna("")
        df["en_proceso"] = fecha_fin.str.upper().str.contains(EN_PROCESO_TEXT)
        df["fecha_inicio"] = [self._parse_month_year(v, tag) for v in df["fecha_inicio"]]
        df["fecha_fin"] = [
            None if en_proceso else self._parse_month_year(v, tag)
            for v, en_proceso in zip(df["fecha_fin"], df["en_proceso"])
        ]

        loc = df["pre_victimas_loc"].fillna("")
        df["estatus_loc"] = loc.where(~loc.str.isdigit() & ~loc.isin(EMPTY_VALUES)).replace("", None)
        df["pre_victimas_loc"] = df["pre_victimas_loc"].where(df["estatus_loc"].isna())
        for col in COUNT_COLS:
            df[col] = pd.array([self._parse_count(v, f"{tag} {col}") for v in df[col]], dtype="Int64")

        df["fecha_corte"] = fecha_corte
        sites = df["consecutivo"].nunique()
        self.logger.info(f"[action] {tag}: {len(df)} rows, {sites} sites")
        return df[STG_COLS]

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        path = self.extract_dir / PUBLICACIONES_FILE
        publicaciones = pd.read_pickle(path) if path.exists() else pd.DataFrame()
        self.logger.info(f"[source] {len(publicaciones)} publications to transform")
        return publicaciones

    def action(self, input_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
        if input_data.empty:
            self.logger.info("[action] Empty input, skipping transform")
            return {"publicaciones": input_data, "stg": pd.DataFrame(columns=STG_COLS)}

        frames = [self._publication(pub.fecha_corte, Path(pub.ruta)) for pub in input_data.itertuples()]
        stg = pd.concat(frames, ignore_index=True)
        stg["municipio"] = stg["municipio"].map(normalize_text)
        for col in TITLE_COLS:
            title_col(stg, col)
            stg[col] = stg[col].apply(apply_accents)

        duplicated = stg.duplicated(["fecha_corte", "consecutivo", "periodo"])
        if duplicated.any():
            raise ValueError(f"Duplicated primary keys:\n{stg[duplicated]}")

        publicaciones = input_data[["fecha_corte", "archivo", "url", "modificado"]]
        return {"publicaciones": publicaciones, "stg": stg}

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        input_data["publicaciones"].to_pickle(self.work_dir / PUBLICACIONES_FILE)
        input_data["stg"].to_pickle(self.work_dir / STG_FILE)
        self.logger.info(f"[finalization] {len(input_data['stg'])} rows saved")
        return input_data
