from core.pipelines.edafologia.constants import ALLOWED_PIPELINE_MODES, BOOTSTRAP_MODE, PIPELINE_NAME


def validate_bootstrap_mode(mode: str) -> str:
    """Validate that Edafologia runs only as an on-demand bootstrap pipeline."""
    if mode not in ALLOWED_PIPELINE_MODES:
        allowed = ", ".join(ALLOWED_PIPELINE_MODES)
        raise ValueError(
            f"{PIPELINE_NAME} only supports mode={BOOTSTRAP_MODE!r}. "
            f"Received {mode!r}; incremental updates are not implemented for this historical source. "
            f"Allowed modes: {allowed}."
        )
    return mode
