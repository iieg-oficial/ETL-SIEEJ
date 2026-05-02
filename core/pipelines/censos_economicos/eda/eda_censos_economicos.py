"""EDA script for the Censos Economicos pipeline (CE 2019 and CE 2024).

Steps:
    1. Load source files (downloads if missing).
    2. Show first rows and dtypes.
    3. Report dataset dimensions.
    4. Identify key columns (IDs, codes, strata).
    5. Count unique values per column to flag catalog candidates.
    6. Analyze geographic level distribution.
    7. Analyze nulls, blanks and suppressed-value markers.
    8. Compare 2019 vs 2024 columns and catalogs.

Final artifact: ``reporte_eda.json``.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from datetime import date
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd

from core.pipelines.censos_economicos.constants import (
    CE_YEARS_CONFIG,
    NULL_VALUES,
    RENAME_COLS_2024,
)
from core.utils.logger import get_logger
from core.utils.normalize import strip_accents

logger = get_logger("censos_economicos.eda")

PIPELINE_DIR = Path(__file__).resolve().parents[1]
DATA_EXTRACT_DIR = Path("data/extract/censos_economicos")
EDA_DIR = PIPELINE_DIR / "eda"
REPORT_PATH = EDA_DIR / "reporte_eda.json"

EDA_SLUGS: dict[int, list[str]] = {
    2019: ["nac", "jal"],
    2024: ["nac", "jal"],
}

SUPPRESSED_MARKERS: tuple[str, ...] = ("*", "X")
GEO_COL_2019_ENT = "ENTIDAD"
GEO_COL_2019_MUN = "MUNICIPIO"
GEO_COL_2024_ENT = "E03"
GEO_COL_2024_MUN = "E04"

DTYPE_HOMOLOGATION: dict[str, str] = {
    "object": "VARCHAR",
    "string": "VARCHAR",
    "int64": "INT",
    "Int64": "INT",
    "int32": "INT",
    "float64": "FLOAT",
    "float32": "FLOAT",
    "bool": "BOOLEAN",
    "datetime64[ns]": "TIMESTAMP",
}


def download_zip(url: str, target_dir: Path) -> None:
    """Download a ZIP and extract it into target_dir if not already present."""
    if target_dir.exists() and any(target_dir.iterdir()):
        logger.info("Skip download, already present: %s", target_dir)
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading %s", url)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        archive.extractall(target_dir)
    logger.info("Extracted to %s", target_dir)


def slug_dir(year: int, slug: str) -> Path:
    """Return the directory where the year/slug ZIP contents live."""
    return DATA_EXTRACT_DIR / str(year) / slug


def ensure_sources(year: int, slugs: list[str]) -> None:
    """Ensure that the sample slugs for ``year`` are downloaded and extracted."""
    config = CE_YEARS_CONFIG[year]
    for slug in slugs:
        target = slug_dir(year, slug)
        if target.exists() and any(target.rglob("*.csv")):
            continue
        url = config["url_template"].format(slug=slug)
        download_zip(url, target)


def load_data_csv(year: int, slug: str) -> pd.DataFrame:
    """Load the main fact CSV for the given year and slug.

    The 2019 CSVs have a trailing comma in every data row (one extra field versus
    the header). Without ``index_col=False`` pandas would silently promote the
    first column to the dataframe index, shifting every value one position left
    and corrupting the geographic columns (ENTIDAD/MUNICIPIO).
    """
    config = CE_YEARS_CONFIG[year]
    relative = config["data_csv_pattern"].format(slug=slug)
    csv_path = slug_dir(year, slug) / relative
    logger.info("Reading %s", csv_path)
    return pd.read_csv(
        csv_path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        index_col=False,
    )


def load_dictionary(year: int, slug: str) -> pd.DataFrame:
    """Load the data dictionary CSV for the given year and slug.

    The 2019 dictionary has a trailing comma so pandas would promote the
    first column to the index by default. ``index_col=False`` keeps the
    column structure intact.
    """
    config = CE_YEARS_CONFIG[year]
    base = slug_dir(year, slug) / "diccionario_de_datos"
    if year == 2024:
        path = slug_dir(year, slug) / config["diccionario"]
    else:
        candidates = sorted(base.glob("*.csv"))
        if not candidates:
            return pd.DataFrame()
        path = candidates[0]
    logger.info("Reading dictionary %s", path)
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        index_col=False,
    )


def load_catalog(year: int, slug: str, kind: str) -> pd.DataFrame:
    """Load a catalog CSV (kind in {'actividad', 'estrato'})."""
    config = CE_YEARS_CONFIG[year]
    key = "catalog_actividad" if kind == "actividad" else "catalog_estrato"
    path = slug_dir(year, slug) / config[key]
    if not path.exists():
        return pd.DataFrame()
    logger.info("Reading catalog %s", path)
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def homologate_dtype(pandas_dtype: str, sample_values: list[str]) -> str:
    """Map a pandas dtype to the project's homologated SQL type label."""
    label = DTYPE_HOMOLOGATION.get(pandas_dtype)
    if label:
        return label
    if pandas_dtype.startswith("float"):
        return "FLOAT"
    if pandas_dtype.startswith("int"):
        return "INT"
    return "VARCHAR"


def looks_numeric(values: list[str]) -> bool:
    """Return True if non-null sample values can be parsed as numbers."""
    cleaned = [v for v in values if v not in NULL_VALUES and v.strip() != ""]
    if not cleaned:
        return False
    parsed = 0
    for value in cleaned:
        try:
            float(value)
            parsed += 1
        except ValueError:
            continue
    return parsed / len(cleaned) >= 0.9


def column_profile(df: pd.DataFrame, name: str) -> dict[str, Any]:
    """Build a per-column profile entry for the EDA report."""
    series = df[name]
    total = len(series)
    null_mask = series.isna() | series.astype(str).isin(NULL_VALUES) | (series.astype(str).str.strip() == "")
    nulls_pct = round(float(null_mask.sum()) / total * 100, 2) if total else 0.0
    non_null = series[~null_mask].astype(str)
    unique_count = int(non_null.nunique())
    sample = non_null.drop_duplicates().head(5).tolist()
    is_numeric = looks_numeric(non_null.head(200).tolist())
    pandas_dtype = str(series.dtype)
    if is_numeric:
        homologated = "FLOAT" if any("." in v for v in non_null.head(50)) else "INT"
    else:
        homologated = homologate_dtype(pandas_dtype, sample)
    is_catalog = unique_count > 0 and unique_count < 100 and not is_numeric
    is_key = name.lower() in {
        "entidad",
        "municipio",
        "codigo",
        "id_estrato",
        "e03",
        "e04",
        "sector",
        "subsector",
        "rama",
        "subrama",
        "clase",
    }
    return {
        "nombre_original": name,
        "tipo_original": pandas_dtype,
        "tipo_homologado": homologated,
        "es_clave": is_key,
        "es_catalogo": is_catalog,
        "valores_unicos": unique_count,
        "nulos_pct": nulls_pct,
        "muestra_valores": sample,
    }


def classify_geo_level(df: pd.DataFrame, ent_col: str, mun_col: str) -> dict[str, int]:
    """Classify each row as nacional, estatal or municipal.

    Per-row logic (the strict ``str.strip() != ""`` check is required because
    a Series.str.strip() result is non-NaN even when the stripped value is
    an empty string, so ``notna()`` would always be True):

        mun = str(row[municipio_col]).strip() if pd.notna(row[municipio_col]) else ""
        ent = str(row[entidad_col]).strip()   if pd.notna(row[entidad_col])   else ""
        if mun != "":
            return "municipal"
        elif ent != "":
            return "estatal"
        else:
            return "nacional"

    Counts are mutually exclusive and sum to len(df).
    """
    if ent_col not in df.columns or mun_col not in df.columns:
        return {"nacional": 0, "estatal": 0, "municipal": 0, "total": int(len(df))}
    ent_clean = df[ent_col].fillna("").astype(str).str.strip()
    mun_clean = df[mun_col].fillna("").astype(str).str.strip()
    mun_filled = mun_clean != ""
    ent_filled = ent_clean != ""
    municipal = int(mun_filled.sum())
    estatal = int((~mun_filled & ent_filled).sum())
    nacional = int((~mun_filled & ~ent_filled).sum())
    return {
        "nacional": nacional,
        "estatal": estatal,
        "municipal": municipal,
        "total": int(len(df)),
    }


SNAKE_TRIM_PUNCT = re.compile(r"[^a-z0-9]+")
STOPWORDS_ES = {"de", "del", "la", "el", "los", "las", "y", "en", "por", "para", "a", "al"}


def slugify_description(description: str, max_words: int = 8) -> str:
    """Derive a snake_case identifier from a Spanish dictionary description.

    Takes the leading phrase before ':' or '.', strips accents, lowercases,
    drops short stopwords, and joins up to ``max_words`` significant tokens.
    """
    if not description:
        return ""
    head = re.split(r"[:\.]", description, maxsplit=1)[0]
    head = strip_accents(head).lower()
    head = head.replace("(", " ").replace(")", " ").replace(",", " ").replace("/", " ")
    tokens = [t for t in SNAKE_TRIM_PUNCT.split(head) if t]
    tokens = [t for t in tokens if t not in STOPWORDS_ES]
    if not tokens:
        return ""
    return "_".join(tokens[:max_words])


def build_dictionary_rename_2019(
    dictionary: pd.DataFrame,
    columns_2019: list[str],
    base_2024: dict[str, str],
) -> dict[str, str]:
    """Build the full RENAME_COLS_2019 covering all 186 columns.

    Reuses RENAME_COLS_2024 for shared codes (case-insensitive) and derives a snake_case
    name from the 2019 dictionary description for the remaining columns.
    Ensures uniqueness by appending a numeric suffix on collisions.
    """
    proposal: dict[str, str] = {}
    used: set[str] = set()
    lower_2024 = {k.lower(): v for k, v in base_2024.items()}

    desc_by_col: dict[str, str] = {}
    if not dictionary.empty:
        cols = {c.lower(): c for c in dictionary.columns}
        col_name = cols.get("columna")
        col_desc = cols.get("descripcion")
        if col_name and col_desc:
            for _, row in dictionary.iterrows():
                key = str(row[col_name]).strip()
                if key:
                    desc_by_col[key] = str(row[col_desc]).strip()

    for col in columns_2019:
        key = col.lower()
        if key in lower_2024:
            target = lower_2024[key]
        else:
            target = slugify_description(desc_by_col.get(col, "")) or key
        candidate = target
        suffix = 2
        while candidate in used:
            candidate = f"{target}_{suffix}"
            suffix += 1
        used.add(candidate)
        proposal[col] = candidate
    return proposal


def count_suppressed(df: pd.DataFrame) -> dict[str, int]:
    """Count how many cells contain suppressed-value markers."""
    counts = {marker: 0 for marker in SUPPRESSED_MARKERS}
    for marker in SUPPRESSED_MARKERS:
        counts[marker] = int((df.astype(str) == marker).sum().sum())
    counts["filas_con_marcador"] = int(df.astype(str).isin(SUPPRESSED_MARKERS).any(axis=1).sum())
    return counts


def diff_columns(cols_a: list[str], cols_b: list[str]) -> dict[str, list[str]]:
    """Return columns only in A, only in B, and shared (case-insensitive comparison)."""
    set_a = {c.lower(): c for c in cols_a}
    set_b = {c.lower(): c for c in cols_b}
    only_a = sorted(set_a[k] for k in set_a.keys() - set_b.keys())
    only_b = sorted(set_b[k] for k in set_b.keys() - set_a.keys())
    shared = sorted(set_a[k] for k in set_a.keys() & set_b.keys())
    return {"solo_2019": only_a, "solo_2024": only_b, "comunes": shared}


def catalog_summary(
    df_2019: pd.DataFrame,
    df_2024: pd.DataFrame,
    label: str,
    use_censo_id: bool = False,
) -> dict[str, Any]:
    """Compare a catalog dataframe across years."""
    summary: dict[str, Any] = {
        "catalogo": label,
        "columnas_2019": list(df_2019.columns) if not df_2019.empty else [],
        "columnas_2024": list(df_2024.columns) if not df_2024.empty else [],
        "filas_2019": int(len(df_2019)),
        "filas_2024": int(len(df_2024)),
        "iguales_columnas": (
            [c.lower() for c in df_2019.columns] == [c.lower() for c in df_2024.columns]
            if not df_2019.empty and not df_2024.empty
            else False
        ),
    }
    if use_censo_id:
        summary["estrategia_carga"] = "un catalogo por anio, particionado por censo_id (FK -> cat_censo)"
    return summary


def build_year_section(year: int) -> dict[str, Any]:
    """Run the analysis for a single census year and return its report section."""
    config = CE_YEARS_CONFIG[year]
    slugs = EDA_SLUGS[year]
    ensure_sources(year, slugs)

    samples: dict[str, pd.DataFrame] = {slug: load_data_csv(year, slug) for slug in slugs}
    reference_slug = "nac" if "nac" in samples else slugs[0]
    df_main = samples[reference_slug]

    logger.info("[%s] columns=%d rows=%d slug=%s", year, df_main.shape[1], df_main.shape[0], reference_slug)
    logger.info("[%s] head:\n%s", year, df_main.head().to_string(max_cols=10))
    logger.info("[%s] dtypes:\n%s", year, df_main.dtypes.astype(str).to_string())

    columns_profile = [column_profile(df_main, c) for c in df_main.columns]

    if year == 2019:
        ent_col, mun_col = GEO_COL_2019_ENT, GEO_COL_2019_MUN
    else:
        ent_col, mun_col = GEO_COL_2024_ENT, GEO_COL_2024_MUN

    geo_distribution = {slug: classify_geo_level(samples[slug], ent_col, mun_col) for slug in slugs}
    suppressed = {slug: count_suppressed(samples[slug]) for slug in slugs}

    return {
        "anio": year,
        "slug_referencia": reference_slug,
        "url_ejemplo_nac": config["url_template"].format(slug="nac"),
        "filas_referencia": int(len(df_main)),
        "columnas_referencia": int(df_main.shape[1]),
        "columnas": columns_profile,
        "columnas_lista": list(df_main.columns),
        "geografia": {
            "columna_entidad": ent_col,
            "columna_municipio": mun_col,
            "distribucion_por_slug": geo_distribution,
        },
        "valores_suprimidos": suppressed,
    }


def build_report() -> dict[str, Any]:
    """Build the full EDA JSON report covering 2019 and 2024."""
    year_2019 = build_year_section(2019)
    year_2024 = build_year_section(2024)

    column_diff = diff_columns(year_2019["columnas_lista"], year_2024["columnas_lista"])
    dictionary_2019 = load_dictionary(2019, "jal")
    rename_2019_proposal = build_dictionary_rename_2019(dictionary_2019, year_2019["columnas_lista"], RENAME_COLS_2024)
    rename_2019_solo = {
        col: rename_2019_proposal[col] for col in column_diff["solo_2019"] if col in rename_2019_proposal
    }

    cat_actividad = catalog_summary(
        load_catalog(2019, "jal", "actividad"),
        load_catalog(2024, "jal", "actividad"),
        "cat_censo_actividad_economica",
        use_censo_id=True,
    )
    cat_actividad["unique_constraint"] = "(codigo, clasificador_id, censo_id)"
    cat_actividad["filas_por_anio"] = {
        "2019": cat_actividad["filas_2019"],
        "2024": cat_actividad["filas_2024"],
    }
    cat_estrato = catalog_summary(
        load_catalog(2019, "jal", "estrato"),
        load_catalog(2024, "jal", "estrato"),
        "cat_censo_estrato",
        use_censo_id=True,
    )

    flat_columns = [{**c, "anio": 2019} for c in year_2019["columnas"]] + [
        {**c, "anio": 2024} for c in year_2024["columnas"]
    ]

    geographic_columns = sorted(
        {
            c["nombre_original"]
            for c in flat_columns
            if c["nombre_original"].lower() in {"entidad", "municipio", "e03", "e04"}
        }
    )

    geo_level = "nacional+estatal+municipal (mezclados en el mismo CSV)"

    notas = (
        "Los CSV traen registros nacionales, estatales y municipales mezclados en el mismo archivo. "
        "Logica de separacion geografica confirmada (D5): aplicar strip a ENTIDAD/E03 y MUNICIPIO/E04 antes de evaluar; "
        '(1) si MUNICIPIO/E04 tiene valor (str.strip() != "") -> fila MUNICIPAL '
        "(la entidad se conoce por el slug del archivo en 2019); "
        "(2) si ENTIDAD/E03 tiene valor pero MUNICIPIO/E04 vacio -> fila ESTATAL; "
        "(3) si ambos vacios -> fila NACIONAL. "
        "En 2019 los CSV contienen espacios en blanco (' ', '\\t ', '   ') en lugar de cadenas vacias, "
        "por lo que el strip es indispensable. La condicion correcta es 'str.strip() != \"\"'; "
        "'str.strip().notna()' siempre retorna True aunque el resultado sea ''. "
        "Quirk del CSV 2019: cada fila de datos tiene una coma final extra (187 campos vs 186 del header). "
        "Si pandas se invoca sin index_col=False, promueve la primera columna al indice y desplaza los valores "
        "una posicion a la izquierda, corrompiendo ENTIDAD/MUNICIPIO. El loader del EDA usa index_col=False. "
        "2019 usa columnas ENTIDAD/MUNICIPIO; 2024 usa E03/E04 (mayusculas en CSV crudo). "
        "2024 expone 5 columnas adicionales SECTOR/SUBSECTOR/RAMA/SUBRAMA/CLASE; en 2019 estos niveles estan implicitos en la columna CODIGO. "
        "Valores suprimidos por confidencialidad ('*' y 'X'): no se detectaron en las muestras nac/jal de ningun anio; "
        "los faltantes se manifiestan como cadenas vacias o espacios. NULL_VALUES los mantiene listados para entidades que pudieran usarlos. "
        "Decision D4: las tablas stg_economico_*_2019 cargaran las 186 columnas (vs 107 de 2024). "
        "RENAME_COLS_2019 cubre las 186 columnas: 100 reusan los nombres de RENAME_COLS_2024 (match case-insensitive) y "
        "86 son exclusivas de 2019 con nombres derivados del diccionario_de_datos_ce2019.csv (slugificacion de la descripcion). "
        "Decision D6: el catalogo de actividad se carga por separado con censo_id; cat_censo_actividad_economica tendra "
        "UNIQUE (codigo, clasificador_id, censo_id). 2019 aporta 1849 codigos y 2024 aporta 1933 codigos. "
        "El catalogo de actividad 2024 trae una columna espuria 'Unnamed: 3' (separador final del CSV) que debe ignorarse. "
        "cat_censo_estrato tambien usa censo_id: misma estructura (ID_ESTRATO, DESC_ESTRATO) pero descripciones distintas entre anios."
    )

    return {
        "flujo": "censos_economicos",
        "fecha_analisis": date.today().isoformat(),
        "fuente": {
            "url": CE_YEARS_CONFIG[2024]["url_template"].format(slug="nac"),
            "formato": "csv (en zip)",
            "num_archivos": 2 * 33,
            "periodicidad": "quinquenal",
        },
        "dimensiones": {
            "filas": year_2019["filas_referencia"] + year_2024["filas_referencia"],
            "columnas": max(year_2019["columnas_referencia"], year_2024["columnas_referencia"]),
        },
        "columnas": flat_columns,
        "geografia": {
            "nivel": geo_level,
            "columnas_geo": geographic_columns,
        },
        "comparativa_anios": {
            "2019": {
                "filas_nac": year_2019["filas_referencia"],
                "columnas": year_2019["columnas_lista"],
                "geo_distribucion": year_2019["geografia"]["distribucion_por_slug"],
                "valores_suprimidos": year_2019["valores_suprimidos"],
            },
            "2024": {
                "filas_nac": year_2024["filas_referencia"],
                "columnas": year_2024["columnas_lista"],
                "geo_distribucion": year_2024["geografia"]["distribucion_por_slug"],
                "valores_suprimidos": year_2024["valores_suprimidos"],
            },
            "diff_columnas": column_diff,
            "rename_cols_2019_propuesto": rename_2019_proposal,
            "rename_cols_2019_solo_exclusivas": rename_2019_solo,
            "decisiones": {
                "D4_columnas_exclusivas_2019": (
                    "Cargar las 186 columnas en stg_economico_*_2019. Las 86 exclusivas tienen nombre "
                    "derivado del diccionario_de_datos_ce2019.csv."
                ),
                "D5_logica_separacion_geografica_2019": (
                    "Cargar el CSV con index_col=False para evitar corrimiento por la coma final. "
                    "Aplicar str.strip() a ENTIDAD y MUNICIPIO; usar la condicion 'str.strip() != \"\"' "
                    "(no 'notna()'). Si MUNICIPIO tiene valor -> municipal "
                    "(entidad implicita por slug del archivo); solo ENTIDAD -> estatal; ambos vacios -> nacional."
                ),
                "D6_catalogo_actividad": (
                    "cat_censo_actividad_economica con censo_id (FK -> cat_censo). "
                    "UNIQUE (codigo, clasificador_id, censo_id). Un set de codigos por anio."
                ),
            },
        },
        "catalogos": {
            "actividad": cat_actividad,
            "estrato": cat_estrato,
        },
        "periodicidad": {
            "anios_disponibles": [2019, 2024],
            "frecuencia": "Cada 5 anios",
            "intervalo_anios": 5,
        },
        "notas": notas,
    }


def main() -> None:
    """Run EDA over downloaded CE 2019 and CE 2024 sources and emit reporte_eda.json."""
    logger.info("Starting EDA for censos_economicos")
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    with REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    logger.info("Report written to %s", REPORT_PATH)


if __name__ == "__main__":
    main()
