from __future__ import annotations

import requests
from requests.exceptions import ChunkedEncodingError, ConnectionError, HTTPError, Timeout
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)

RETRY_ATTEMPTS = 5
SERVER_ERROR_STATUS = 500


def _is_transient(exception: BaseException) -> bool:
    if isinstance(exception, ConnectionError | Timeout | ChunkedEncodingError):
        return True
    if isinstance(exception, HTTPError) and exception.response is not None:
        return exception.response.status_code >= SERVER_ERROR_STATUS
    return False


def _log_retry(state) -> None:
    logger.warning(f"Retry attempt {state.attempt_number} after {state.outcome.exception()}")


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception(_is_transient),
    before_sleep=_log_retry,
    reraise=True,
)
def http_get(url: str, timeout: int) -> requests.Response:
    """GET a URL, retrying transient failures (connection, timeout, 5xx).

    Client errors (4xx) are returned as-is so callers can handle them —
    a 404 usually means "edition not published yet", not a failure.
    """
    response = requests.get(url, timeout=timeout)
    if response.status_code >= SERVER_ERROR_STATUS:
        response.raise_for_status()
    return response
