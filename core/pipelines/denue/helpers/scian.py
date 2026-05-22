from pathlib import Path

from core.utils.files import load_csv_lookups
from core.utils.gdrive import download_public_file
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def download_scian(work_dir: Path, file_id: str, csv_name: str) -> None:
    scian_path = work_dir / csv_name
    if scian_path.exists():
        return
    logger.info("[download_scian] Downloading SCIAN CSV from Drive")
    download_public_file(file_id, scian_path)
    logger.info(f"[download_scian] Saved to {scian_path}")


def load_scian_lookups(extract_dir: Path, csv_name: str) -> dict[str, dict[str, str]]:
    scian_path = extract_dir / csv_name
    return load_csv_lookups(scian_path, "nivel", "codigo", "descripcion")
