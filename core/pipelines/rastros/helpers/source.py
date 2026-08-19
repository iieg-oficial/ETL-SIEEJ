from __future__ import annotations

from core.pipelines.rastros.config import settings
from core.pipelines.rastros.constants import ZIP_MAGIC
from core.utils.http import http_get
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def fetch_dataset() -> bytes:
    """Download the ESGRM monthly dataset and return the raw ZIP bytes.

    The published path is stable; what changes with every edition is the ZIP
    content (a new year is added inside), so there is nothing to resolve. What
    does need checking is that the answer really is the dataset: INEGI serves an
    HTML error page with status 200 when a path no longer exists, so the status
    code cannot tell a live path from a dead one and only the file signature can.

    Raises:
        FileNotFoundError: if the URL no longer serves a ZIP.
    """
    url = settings.ESGRM_URL
    logger.info(f"Downloading ESGRM dataset: {url}")
    response = http_get(url, timeout=settings.DOWNLOAD_TIMEOUT)

    if response.status_code != 200 or not response.content.startswith(ZIP_MAGIC):
        raise FileNotFoundError(
            f"{url} did not serve a ZIP (status {response.status_code}). INEGI most likely moved "
            f"the publication: check the program page and update ESGRM_URL in "
            f"core/pipelines/{settings.PIPELINE_NAME}/.env."
        )

    logger.info(f"ESGRM dataset downloaded ({len(response.content):,} bytes)")
    return response.content
