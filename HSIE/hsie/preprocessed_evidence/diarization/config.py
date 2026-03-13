"""
Diarization configuration definition and Pipeline initialization.

This module defines the immutable configuration used by
DiarizationService and provides pyannote Pipeline creation.
"""

from pydantic import BaseModel

from pyannote.audio import Pipeline


def create_pipeline() -> Pipeline:
    """
    Create pyannote speaker diarization pipeline.

    Requires HuggingFace authentication (huggingface-cli login or HF_TOKEN env).
    Accept model terms at https://huggingface.co/pyannote/speaker-diarization

    Returns:
        Pipeline: pyannote speaker-diarization pipeline
    """
    try:
        return Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=True,
        )
    except TypeError:
        # pyannote 3.x: use_auth_token removed, use token= instead
        return Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=True,
        )


class DiarizationConfig(BaseModel):
    """
    Configuration schema for speaker diarization.

    Attributes:
        model_name: HuggingFace model identifier for pyannote pipeline.
        hf_token_env_var: Environment variable name that stores HF token.
        speaker_prefix: Prefix used when generating internal speaker IDs.
        time_decimal_precision: Decimal precision used when converting
            float timestamps to Decimal.
        use_local_cache: Whether to rely on HuggingFace local cache.
    """

    model_name: str
    hf_token_env_var: str = "HF_TOKEN"
    speaker_prefix: str = "speaker_"
    time_decimal_precision: int = 6
    use_local_cache: bool = True