import pytest

from core.pipelines.pendientes.helpers.download import _progress_message, _progress_milestone


@pytest.mark.parametrize(
    ("downloaded", "expected", "milestone"),
    [
        (0, 1000, 0),
        (40, 1000, 0),
        (50, 1000, 1),
        (990, 1000, 19),
        (1000, 1000, 20),
    ],
)
def test_small_file_advances_every_five_percent(downloaded: int, expected: int, milestone: int) -> None:
    assert _progress_milestone(downloaded, expected) == milestone


@pytest.mark.parametrize(
    ("downloaded", "milestone"),
    [
        (0, 0),
        (99 * 1024 * 1024, 0),
        (100 * 1024 * 1024, 1),
        (250 * 1024 * 1024, 2),
    ],
)
def test_unknown_size_advances_every_hundred_megabytes(downloaded: int, milestone: int) -> None:
    assert _progress_milestone(downloaded, None) == milestone


def test_message_reports_percentage_when_size_is_known() -> None:
    assert _progress_message(50 * 1024 * 1024, 100 * 1024 * 1024) == "Downloading: 50% (50/100 MB)"


def test_message_omits_percentage_when_size_is_unknown() -> None:
    assert _progress_message(50 * 1024 * 1024, None) == "Downloading: 50 MB"


def test_large_file_falls_back_to_hundred_megabyte_steps() -> None:
    """5% of a 9 GB source would be ~456 MB, far too coarse to show progress."""
    nine_gigabytes = 9558702510

    assert _progress_milestone(99 * 1024 * 1024, nine_gigabytes) == 0
    assert _progress_milestone(100 * 1024 * 1024, nine_gigabytes) == 1
    assert _progress_milestone(456 * 1024 * 1024, nine_gigabytes) == 4
